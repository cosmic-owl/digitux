import os
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication

from nexus.model import Ctrl
from nexus.ui.i18n import translate
from nexus.ui.main_window import MainWindow, Worker
from nexus.ui.tempo_panel import TempoPanel, delay_ms, lfo_speed
from test_realtime_sync import fixture_preset


class TempoTest(unittest.TestCase):
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
        preset = fixture_preset()
        preset.ctrls["lfo1"] = Ctrl(lnk="../../fxc/2/fx/DRIVE", min=0, max=99,
                                    speed=74, waveform=0)
        self.window._display_preset(preset)
        self.device.reset_mock()

    def tearDown(self):
        self.window.close()
        self.app.processEvents()

    def test_tap_tempo_and_reset(self):
        panel = TempoPanel()
        changes = Mock()
        panel.changed.connect(changes)
        with patch("nexus.ui.tempo_panel.time.monotonic",
                   side_effect=[10, 10.5, 11, 15, 15.75]):
            panel.tap.click()
            self.assertEqual(changes.call_count, 0)
            panel.tap.click()
            panel.tap.click()
            self.assertEqual(panel.bpm.value(), 120)
            panel.tap.click()
            self.assertEqual(changes.call_count, 2)
            panel.tap.click()
            self.assertEqual(panel.bpm.value(), 80)
        panel.bpm.setValue(100)
        self.assertEqual(len(panel._taps), 0)

    def test_out_of_range_taps_are_reported_without_changing_tempo(self):
        panel = TempoPanel()
        with patch("nexus.ui.tempo_panel.time.monotonic", side_effect=[10, 10.1]):
            panel.tap.click()
            panel.tap.click()
        self.assertEqual(panel.bpm.value(), 120)
        self.assertEqual(
            panel.readout.text(),
            translate("Tempo fuera del rango 20–300 BPM; vuelve a marcar"),
        )

    def test_sync_writes_delay_and_assigned_lfo(self):
        w = self.window
        tempo = w.control_panel.tempo
        tempo.delay.setCurrentIndex(3)
        self.device.set_param.assert_called_once_with(8, "TIME", 375, flat=False)
        self.assertEqual(w.preset.slots[8].params["TIME"], 375)
        self.assertEqual(w.pedalboard.pedals[8]._knobs["TIME"].value, 375)
        tempo.lfo.setCurrentIndex(2)
        self.device.set_ctrl_field.assert_called_once_with("lfo1", "SPEED", 105)
        self.assertEqual(w.preset.ctrls["lfo1"].speed, 105)
        self.assertEqual(w.control_panel.lfo_speed.value(), 105)
        self.assertIn("375 ms", tempo.readout.text())
        self.assertIn("2.00 Hz", tempo.readout.text())
        self.device.reset_mock()
        tempo.bpm.setValue(60)
        self.device.set_param.assert_called_once_with(8, "TIME", 750, flat=False)
        self.device.set_ctrl_field.assert_called_once_with("lfo1", "SPEED", 95)

    def test_rejects_unsupported_and_out_of_range_targets(self):
        w = self.window
        w.preset.slots[8].model = "dly.ECHOPLEX"
        w.control_panel.tempo.bpm.setValue(20)
        w.control_panel.tempo.delay.setCurrentIndex(1)
        self.device.set_param.assert_not_called()
        delay_value = delay_ms(20, w.control_panel.tempo.delay.currentData())
        low, high = w.db.param_range("ECHOPLEX", "TIME")
        self.assertIn(
            translate(
                "Delay: {value} ms fuera del rango {low}–{high} ms"
            ).format(value=delay_value, low=low, high=high),
            w.status.currentMessage(),
        )
        w.preset.slots[8].model = "dly.DM DELAY"
        w.preset.slots[8].params.pop("TIME")
        w.control_panel.tempo.bpm.setValue(100)
        self.assertIn(
            translate("Delay sin parámetro TIME compatible"),
            w.status.currentMessage(),
        )
        self.device.set_param.assert_not_called()
        w.preset.ctrls["lfo1"] = Ctrl()
        w.control_panel.tempo.delay.setCurrentIndex(0)
        w.control_panel.tempo.lfo.setCurrentIndex(2)
        self.assertIn(translate("LFO sin asignar"), w.status.currentMessage())
        self.device.set_ctrl_field.assert_not_called()

    def test_off_does_not_write_and_snapshots_do_not_apply_tempo(self):
        w = self.window
        w.control_panel.tempo.bpm.setValue(90)
        self.device.set_param.assert_not_called()
        self.device.set_ctrl_field.assert_not_called()
        w.control_panel.tempo.delay.setCurrentIndex(2)
        self.device.reset_mock()
        w._display_preset(fixture_preset())
        self.device.set_param.assert_not_called()
        self.device.set_ctrl_field.assert_not_called()

    def test_lfo_assignment_uses_selected_subdivision(self):
        w = self.window
        w.control_panel.tempo.lfo.setCurrentIndex(2)
        self.device.reset_mock()
        with patch.object(w, "_reload"):
            w._assign_lfo(2, "DRIVE", 0, 99, 74, 0)
        self.device.assign_lfo.assert_called_once_with(2, "DRIVE", 0, 99, 105, 0, flat=False)

    def test_failed_lfo_write_invalidates_snapshots_and_is_reported(self):
        w = self.window
        revision = w.worker._revision
        self.device.set_ctrl_field.side_effect = RuntimeError("offline")
        w.control_panel.tempo.lfo.setCurrentIndex(2)
        self.assertEqual(w.preset.ctrls["lfo1"].speed, 74)
        self.assertFalse(w.worker.is_current(revision))
        self.assertIn("offline", w.status.currentMessage())

    def test_conversions(self):
        self.assertEqual(delay_ms(120, 0.75), 375)
        self.assertEqual(lfo_speed(47.4, 1), 74)
        self.assertEqual(lfo_speed(318, 1), 138)
        self.assertEqual(lfo_speed(600, 1), 185)
        with self.assertRaises(ValueError):
            lfo_speed(120, 0.1)


if __name__ == "__main__":
    unittest.main()
