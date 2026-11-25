import copy
import json
import os
import queue
import threading
import time
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest

from nexus.model import Preset
from nexus.protocol import Protocol
from nexus.runtime import data_path
from nexus.transport import CHAN_DATA, Packet, SEND_CHUNK, Transport, TransportError
from nexus.ui.main_window import MainWindow, Worker


def fixture_preset():
    with data_path("nexus_factory_presets.json").open() as source:
        return Preset.from_json(json.load(source)[0]["data"])


class SyncUITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.device = Mock()
        with patch("nexus.ui.main_window.Device", return_value=self.device), \
             patch("nexus.ui.main_window.QTimer.singleShot"):
            self.window = MainWindow()
        self.window.worker = Worker(self.device)
        self.window._connected = True
        self.window._display_preset(fixture_preset())
        self.device.reset_mock()

    def tearDown(self):
        self.window.close()
        self.app.processEvents()

    def test_notifications_update_controls_without_device_writes_or_rebuilds(self):
        w = self.window
        pedal = w.pedalboard.pedals[2]
        knob = pedal._knobs["DRIVE"]
        amp_knob = next(k for k in w.amp_block.amp_view._knobs if k.name == "GAIN")
        with patch.object(w.pedalboard, "rebuild") as rebuild:
            w._on_notif(["np", 1, "preset/fxc/2/fx/DRIVE", 34])
            w._on_notif(["np", 2, "preset/fxc/2/ENABLE", 0])
            w._on_notif(["np", 3, "preset/fxc/3/fx/GAIN", 25])
            w._on_notif(["np", 4, "preset/fxc/3/fx/CABINET", 5])
            w._on_notif(["np", 5, "preset/fxc/6/VOLUME", 44])
            w._on_notif(["np", 6, "preset/fxc/0/fx/PEDAL", 31])
            w._on_notif(["np", 7, "preset/PRS LEVL", 42])
            w._on_notif(["np", 8, "preset/name", "Live"])
        self.assertEqual(knob.value, 34)
        self.assertFalse(w.preset.slots[2].enable)
        self.assertEqual(amp_knob.value, 25)
        self.assertEqual(w.amp_block.cab_combo.currentIndex(), 5)
        self.assertEqual(w.preset.slots[6].params["VOLUME"], 44)
        self.assertEqual(w.control_panel.pedal_spin.value(), 31)
        self.assertEqual(w.level_slider.value(), 42)
        self.assertEqual(w.preset_name.text(), "Live")
        rebuild.assert_not_called()
        self.device.assert_not_called()
        self.device.set_param.assert_not_called()
        self.device.set_preset_level.assert_not_called()

    def test_structural_notifications_coalesce_and_stale_snapshots_are_rejected(self):
        w = self.window
        w._on_notif(["cm", 0])
        w._on_notif(["nsc", 0, "preset/fxc"])
        self.assertTrue(w._sync_timer.isActive())
        w._sync_timer.stop()
        old_revision = w.worker.invalidate()
        w._sync_busy = True
        w._sync_requested = True
        w.worker.invalidate()
        stale = fixture_preset()
        stale.name = "Stale"
        w._on_snapshot(stale, old_revision)
        self.assertNotEqual(w.preset.name, "Stale")
        self.assertTrue(w._sync_timer.isActive())

    def test_poll_updates_values_without_rebuilding_and_rebuilds_for_model_change(self):
        w = self.window
        updated = fixture_preset()
        updated.slots[2].params["DRIVE"] = 20
        updated.slots[2].enable = False
        updated.prs_levl = 37
        with patch.object(w.pedalboard, "rebuild", wraps=w.pedalboard.rebuild) as rebuild:
            w._apply_snapshot(updated)
            self.assertEqual(w.pedalboard.pedals[2]._knobs["DRIVE"].value, 20)
            self.assertFalse(w.preset.slots[2].enable)
            self.assertEqual(w.level_slider.value(), 37)
            rebuild.assert_not_called()
            changed = copy.deepcopy(updated)
            changed.slots[2].model = "dist.OTHER"
            w._apply_snapshot(changed)
            rebuild.assert_called_once()

    def test_local_edit_invalidates_a_read_started_during_the_write(self):
        w = self.window
        revisions = []
        self.device.set_param.side_effect = lambda *a, **k: revisions.append(w.worker.invalidate())
        w._set_param(2, "DRIVE", 17)
        self.assertFalse(w.worker.is_current(revisions[0]))
        self.assertEqual(w.preset.slots[2].params["DRIVE"], 17)
        self.device.set_param.assert_called_once_with(2, "DRIVE", 17, flat=False)

    def test_sustained_local_edits_do_not_starve_unrelated_snapshot_values(self):
        w = self.window
        entered = threading.Event()
        release = threading.Event()
        snapshot = fixture_preset()
        snapshot.slots[3].params["GAIN"] = 22

        def read_preset():
            entered.set()
            if not release.wait(2):
                raise RuntimeError("test read timed out")
            return snapshot

        self.device.get_active_preset.side_effect = read_preset
        w.worker.snapshot.connect(w._on_snapshot)
        w.worker.failed.connect(w._on_sync_error)
        w._request_sync()
        self.assertTrue(entered.wait(1))
        for value in range(30, 50):
            w._set_param(2, "DRIVE", value)
        release.set()
        for _ in range(100):
            QTest.qWait(10)
            if not w._sync_busy:
                break
        self.assertEqual(w.preset.slots[2].params["DRIVE"], 49)
        self.assertEqual(w.preset.slots[3].params["GAIN"], 22)
        self.assertEqual(w.pedalboard.pedals[2]._knobs["DRIVE"].value, 49)
        self.assertEqual(self.device.set_param.call_count, 20)

    def test_wah_and_cabinet_user_changes_send_commands(self):
        w = self.window
        w.control_panel.pedal_spin.setValue(30)
        self.device.set_param.assert_called_with(0, "PEDAL", 30, flat=False)
        self.device.reset_mock()
        self.device.get_active_preset.return_value = fixture_preset()
        w.amp_block.cab_combo.setCurrentIndex(5)
        self.device.set_param.assert_called_once_with(3, "CABINET", 5)

    def test_disconnect_stops_polling(self):
        w = self.window
        w._poll_timer.start()
        w._sync_timer.start()
        w._on_disconnect("cable removed")
        self.assertFalse(w._poll_timer.isActive())
        self.assertFalse(w._sync_timer.isActive())
        w._request_sync()
        self.device.get_active_preset.assert_not_called()

    def test_worker_notifications_and_background_reconciliation(self):
        w = self.window
        entered = threading.Event()
        release = threading.Event()
        changed = fixture_preset()
        changed.name = "Changed on pedal"

        def read_preset():
            entered.set()
            if not release.wait(2):
                raise RuntimeError("test read timed out")
            return changed

        self.device.get_active_preset.side_effect = read_preset
        w.worker.notif.connect(w._on_notif)
        w.worker.snapshot.connect(w._on_snapshot)
        w.worker.failed.connect(w._on_sync_error)
        w.worker.start()
        w._request_sync()
        self.assertTrue(entered.wait(1))
        w.worker._notification(["np", 1, "preset/fxc/2/fx/DRIVE", 13])
        QTest.qWait(20)
        self.assertEqual(w.preset.slots[2].params["DRIVE"], 13)
        release.set()
        for _ in range(50):
            QTest.qWait(10)
            if not w._sync_busy:
                break
        self.assertFalse(w._sync_busy)
        self.assertEqual(w.preset.name, changed.name)
        self.assertEqual(w.preset.slots[2].params["DRIVE"], 13)
        w._request_sync()
        for _ in range(50):
            QTest.qWait(10)
            if not w._sync_busy:
                break
        self.assertEqual(w.preset.name, changed.name)
        self.assertEqual(self.device.get_active_preset.call_count, 2)

    def test_snapshot_replays_property_notifications_and_ignores_queued_older_events(self):
        w = self.window
        entered = threading.Event()
        release = threading.Event()
        snapshot = fixture_preset()
        snapshot.slots[3].params["GAIN"] = 22

        def read_preset():
            entered.set()
            if not release.wait(2):
                raise RuntimeError("test read timed out")
            return snapshot

        self.device.get_active_preset.side_effect = read_preset
        w.worker.snapshot.connect(w._on_snapshot)
        w._request_sync()
        self.assertTrue(entered.wait(1))
        w.worker._notification(["np", 1, "preset/fxc/2/fx/DRIVE", 13])
        first_revision = w.worker._revision
        w.worker._notification(["np", 2, "preset/fxc/2/fx/DRIVE", 14])
        release.set()
        for _ in range(100):
            QTest.qWait(10)
            if not w._sync_busy:
                break
        self.assertEqual(w.preset.slots[3].params["GAIN"], 22)
        self.assertEqual(w.preset.slots[2].params["DRIVE"], 14)
        w._on_notif(["np", 1, "preset/fxc/2/fx/DRIVE", 13], first_revision)
        self.assertEqual(w.preset.slots[2].params["DRIVE"], 14)
        w._on_notif(["np", 3, "preset/fxc/2/fx/DRIVE", 15], w.worker._revision + 1)
        self.assertEqual(w.preset.slots[2].params["DRIVE"], 15)

    def test_preset_switch_during_read_rejects_snapshot_and_retries(self):
        w = self.window
        old_revision = w.worker._revision
        w.worker._notification(["cm", 1, "banks/user/2", "preset"])
        stale = fixture_preset()
        stale.name = "Obsolete"
        w._sync_busy = True
        w._on_snapshot(stale, old_revision)
        self.assertNotEqual(w.preset.name, "Obsolete")
        self.assertTrue(w._sync_timer.isActive())

    def test_unmergeable_change_rejects_snapshot_and_retries(self):
        w = self.window
        revision = w.worker._revision
        w.worker.record_change("preset/fxc/99/fx/DRIVE", 10)
        w._sync_busy = True
        w._on_snapshot(fixture_preset(), revision)
        self.assertTrue(w._sync_timer.isActive())

    def test_edit_before_background_read_starts_does_not_cancel_read(self):
        worker = self.window.worker
        revision = worker._revision
        worker.record_change("preset/fxc/2/fx/DRIVE", 13)
        snapshot = fixture_preset()
        self.device.get_active_preset.return_value = snapshot
        received = []
        worker.snapshot.connect(lambda preset, seq: received.append((preset, seq)))
        worker._read_preset(revision)
        self.assertEqual(received, [(snapshot, revision)])
        self.assertIsNotNone(worker.merge_snapshot(snapshot, revision))
        self.assertEqual(snapshot.slots[2].params["DRIVE"], 13)

    def test_preset_change_notifications_trigger_one_coalesced_read(self):
        w = self.window
        changed = fixture_preset()
        changed.name = "Footswitch preset"
        self.device.get_active_preset.return_value = changed
        w.worker.snapshot.connect(w._on_snapshot)
        w.worker.failed.connect(w._on_sync_error)
        for _ in range(10):
            w._on_notif(["cm", 0])
        for _ in range(50):
            QTest.qWait(10)
            if w.preset.name == changed.name:
                break
        self.assertEqual(w.preset.name, changed.name)
        self.device.get_active_preset.assert_called_once_with()


class ProtocolSyncTest(unittest.TestCase):
    def test_notifications_do_not_block_response_dispatch_or_overlap_commands(self):
        class FakeTransport:
            def __init__(self):
                self.rx = queue.Queue()
                self.sent = queue.Queue()

            def recv(self, timeout):
                try:
                    return self.rx.get(timeout=timeout)
                except queue.Empty:
                    return None

            def send(self, payload, on_progress=None):
                self.sent.put(json.loads(payload))

            def incoming(self, msg):
                self.rx.put(Packet(CHAN_DATA, 0, json.dumps(msg).encode()))

        transport = FakeTransport()
        protocol = Protocol(transport)
        notifications = []
        protocol.on_notification(notifications.append)
        results = []
        first = threading.Thread(target=lambda: results.append(protocol.send_command("rc", "preset")))
        second = threading.Thread(target=lambda: results.append(protocol.send_command("sp", "preset/name", "x")))
        first.start()
        first_command = transport.sent.get(timeout=1)
        second.start()
        with self.assertRaises(queue.Empty):
            transport.sent.get(timeout=0.05)
        transport.incoming(["np", 1, "preset/PRS LEVL", 33])
        transport.incoming(["rcr", 2, first_command[1], {"preset": {}}])
        second_command = transport.sent.get(timeout=1)
        transport.incoming(["ack", 3, second_command[1]])
        first.join(1)
        second.join(1)
        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertEqual(notifications, [["np", 1, "preset/PRS LEVL", 33]])
        self.assertIn({"preset": {}}, results)

    def test_missing_fragment_ack_stops_transfer_and_cleans_pending(self):
        transport = Transport()
        transport._port = Mock()
        with patch("threading.Event.wait", return_value=False):
            with self.assertRaises(TransportError):
                transport.send(b"x" * (SEND_CHUNK + 1))
        self.assertEqual(transport._port.write.call_count, 1)
        self.assertEqual(transport._dack_pending, {})

    def test_send_failure_clears_protocol_pending_request(self):
        transport = Mock()
        transport.recv.side_effect = lambda timeout: time.sleep(0.01)
        transport.send.side_effect = TransportError("write failed")
        protocol = Protocol(transport)
        with self.assertRaises(TransportError):
            protocol.send_command("sp", "preset/name", "x")
        self.assertEqual(protocol._pending, {})


if __name__ == "__main__":
    unittest.main()
