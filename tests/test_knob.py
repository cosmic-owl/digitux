import math
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtCore import QEvent, QPoint, QPointF, Qt
from PyQt5.QtGui import QFont, QFontMetrics, QImage, QMouseEvent
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from nexus.effects_db import EffectsDB, visible_pedal_params
from nexus.model import FxSlot
from nexus.runtime import img_path
from nexus.ui.amp_cab_block import AMP_DISP_W, AmpView
from nexus.ui.eq_display import eq_bands, eq_response
from nexus.ui.knob import Knob
from nexus.ui.pedal_widget import DISP_H, DISP_W, EQ_DISP_W, SRC_H, SRC_W, PedalWidget


class KnobDrawingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def drawing(self, size, value):
        knob = Knob("TEST", min_val=20, max_val=80, value=value, size=size)
        with patch("nexus.ui.knob.QPainter") as painter:
            knob.paintEvent(None)
        return painter.return_value

    def test_ticks_are_evenly_spaced_and_centered_on_body(self):
        for size in (40, 42, 56):
            with self.subTest(size=size):
                painter = self.drawing(size, 50)
                circle = painter.drawEllipse.call_args.args[0]
                center = circle.center()
                radius = circle.width() / 2
                self.assertAlmostEqual(circle.width(), circle.height())
                self.assertAlmostEqual(center.x(), max(size, 78) / 2)
                self.assertAlmostEqual(center.y(), size / 2)
                lines = painter.drawLine.call_args_list
                self.assertEqual(len(lines), 12)
                for index, call in enumerate(lines[:11]):
                    outer, inner = call.args
                    dx = outer.x() - center.x()
                    dy = outer.y() - center.y()
                    angle = math.degrees(math.atan2(dy, dx)) % 360
                    self.assertAlmostEqual(angle, (120 + index * 30) % 360)
                    self.assertAlmostEqual(math.hypot(dx, dy), radius - 2)
                    self.assertAlmostEqual(
                        math.hypot(inner.x() - center.x(), inner.y() - center.y()),
                        radius - 5)

    def test_pointer_matches_minimum_midpoint_and_maximum(self):
        for value, expected in ((20, 120), (50, 270), (80, 60)):
            with self.subTest(value=value):
                painter = self.drawing(42, value)
                center, end = painter.drawLine.call_args_list[-1].args
                angle = math.degrees(math.atan2(end.y() - center.y(),
                                                end.x() - center.x())) % 360
                self.assertAlmostEqual(angle, expected)

    def test_pedal_labels_fit_without_changing_knob_centers(self):
        db = EffectsDB()
        metrics = QFontMetrics(QFont("Sans", 8, QFont.Bold))
        for address, names in (("LEX HALL", ("PREDELAY", "DECAY")),):
            with self.subTest(address=address):
                slot = FxSlot.from_json(0, db.build_slot_data(address))
                pedal = PedalWidget(0, slot, db)
                left, right = (pedal._knobs[name] for name in names)
                self.assertEqual(left.x() + left.width() // 2, int(60 * DISP_W / SRC_W))
                self.assertEqual(right.x() + right.width() // 2, int(160 * DISP_W / SRC_W))
                self.assertLess(left.geometry().right(), right.geometry().left())
                for knob in pedal._knobs.values():
                    self.assertLessEqual(metrics.horizontalAdvance(knob.name), knob.width())

    def test_multirow_pedal_artwork_keeps_title_below_all_knobs(self):
        db = EffectsDB()
        for category in db.categories():
            if category == "Amplifier":
                continue
            for effect in db.by_category(category):
                if len(visible_pedal_params(effect)) < 5:
                    continue
                with self.subTest(model=effect["model"]):
                    image = QImage(str(img_path("pedals", effect["image"])))
                    self.assertFalse(image.isNull())
                    self.assertEqual(image.pixelColor(110, 220).getRgb()[:3], (42, 42, 46))
                    title_rows = [y for y in range(175, 320)
                                  if any(min(image.pixelColor(x, y).getRgb()[:3]) > 200
                                         for x in range(30, 190))]
                    self.assertTrue(title_rows)
                    slot = FxSlot.from_json(0, db.build_slot_data(effect["address"]))
                    pedal = PedalWidget(0, slot, db)
                    bottom = max(knob.geometry().bottom() for knob in pedal._knobs.values())
                    self.assertGreater(int(min(title_rows) * DISP_H / SRC_H), bottom)
                    self.assertLess(max(title_rows), 317)

        short = QImage(str(img_path("pedals", db.by_address("LEX HALL")["image"])))
        self.assertNotEqual(short.pixelColor(110, 180).getRgb()[:3], (42, 42, 46))

    def test_cabinet_speakers_are_centered_inside_grille(self):
        db = EffectsDB()
        speaker_colors = {(48, 46, 42), (20, 18, 16), (200, 196, 188)}
        for index, name in enumerate(db.cabinet_names()):
            with self.subTest(cabinet=name):
                image = QImage(str(img_path("cabs", db.cabinet_at(index)["image"])))
                self.assertFalse(image.isNull())
                pixels = {(x, y) for x in range(29, 172) for y in range(57, 156)
                          if image.pixelColor(x, y).getRgb()[:3] in speaker_colors}
                components = []
                while pixels:
                    pending = [pixels.pop()]
                    component = set(pending)
                    while pending:
                        x, y = pending.pop()
                        for point in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                            if point in pixels:
                                pixels.remove(point)
                                component.add(point)
                                pending.append(point)
                    components.append(component)
                expected = int(name[0]) if name.startswith(("1x", "2x", "4x")) else 1
                self.assertEqual(len(components), expected)
                points = set().union(*components)
                left, right = min(x for x, _ in points), max(x for x, _ in points)
                top, bottom = min(y for _, y in points), max(y for _, y in points)
                self.assertGreater(left, 29)
                self.assertLess(right, 171)
                self.assertGreater(top, 57)
                self.assertLess(bottom, 155)
                self.assertEqual(left + right, 200)
                self.assertEqual(top + bottom, 212)
                bounds = [(min(x for x, _ in part), max(x for x, _ in part),
                           min(y for _, y in part), max(y for _, y in part))
                          for part in components]
                self.assertEqual(len({(right - left, bottom - top)
                                      for left, right, top, bottom in bounds}), 1)
                centers = {(left + right, top + bottom) for left, right, top, bottom in bounds}
                if expected == 2:
                    self.assertEqual(len({y for _, y in centers}), 1)
                if expected == 4:
                    xs = {x for x, _ in centers}
                    ys = {y for _, y in centers}
                    self.assertEqual(len(xs), 2)
                    self.assertEqual(len(ys), 2)
                    self.assertEqual(centers, {(x, y) for x in xs for y in ys})

    def test_amplifier_knobs_stay_centered_and_interactive(self):
        db = EffectsDB()
        view = AmpView(db)
        view.set_slot(FxSlot.from_json(3, db.build_slot_data("68 PLEXI")))
        for knob, (x, _) in zip(view._knobs, view.KNOB_SRC):
            self.assertEqual(knob.x() + knob.width() // 2, int(x * AMP_DISP_W / 572))
        first, second = view._knobs[:2]
        self.assertLess(first.geometry().right(), second.geometry().left())
        changes = []
        first.valueChanged.connect(changes.append)
        view.show()
        self.app.processEvents()
        center = QPoint(first.width() // 2, 20)
        QTest.mousePress(first, Qt.LeftButton, pos=center)
        end = center - QPoint(0, 5)
        move = QMouseEvent(QEvent.MouseMove, QPointF(end), QPointF(first.mapToGlobal(end)),
                           Qt.NoButton, Qt.LeftButton, Qt.NoModifier)
        QApplication.sendEvent(first, move)
        QTest.mouseRelease(first, Qt.LeftButton, pos=end)
        self.assertTrue(changes)
        view.close()

    def test_amplifier_indicator_switch_and_labels_share_a_column(self):
        db = EffectsDB()
        view = AmpView(db)
        view.set_slot(FxSlot.from_json(3, db.build_slot_data("DIGBRGHT")))
        for enabled in (True, False):
            with self.subTest(enabled=enabled):
                view.slot.enable = enabled
                with patch("nexus.ui.amp_cab_block.QPainter") as painter:
                    view.paintEvent(None)
                draw = painter.return_value
                indicator, switch = (call.args for call in draw.drawPixmap.call_args_list[-2:])
                center = view._switch_rect().center().x()
                for x, _, pixmap in (indicator, switch):
                    self.assertLessEqual(abs(x + pixmap.width() / 2 - center), 0.5)
                self.assertGreater(indicator[0], int(480 * AMP_DISP_W / 572))
                for call in draw.drawText.call_args_list:
                    rect, _, text = call.args
                    if text in ("ON", "Bypass"):
                        self.assertEqual(rect.center().x(), center)
                        self.assertTrue(view._switch_rect().contains(rect.center()))
                self.assertTrue(view._switch_rect().contains(
                    QPoint(switch[0] + switch[2].width() // 2,
                           switch[1] + switch[2].height() // 2)))

    def test_amplifier_switch_hit_area_follows_controls(self):
        db = EffectsDB()
        view = AmpView(db)
        view.set_slot(FxSlot.from_json(3, db.build_slot_data("DIGBRGHT")))
        toggles, changes = [], []
        view.bypass_toggled.connect(lambda slot, bypass: toggles.append((slot, bypass)))
        view.change_requested.connect(changes.append)
        view.show()
        self.app.processEvents()
        QTest.mouseClick(view, Qt.LeftButton, pos=view._switch_rect().center())
        self.assertEqual(toggles, [(3, bool(view.slot.enable))])
        QTest.mouseClick(view, Qt.LeftButton, pos=QPoint(int(450 * AMP_DISP_W / 572), 40))
        self.assertEqual(changes, [3])
        self.assertEqual(len(toggles), 1)
        view.slot.enable = False
        QTest.mouseClick(view, Qt.LeftButton, pos=view._switch_rect().center())
        self.assertEqual(toggles[-1], (3, False))
        view.close()

    def test_eq_estimate_uses_device_values_and_rejects_unknown_values(self):
        slot = FxSlot(4, "eq.EQ", {
            "LOW LEVL": 12, "LOW FREQ": 9, "LOW BW": 1,
            "MID LEVL": 15, "MID FREQ": 45, "MID BW": 1,
            "HIGHLEVL": 3, "HIGHFREQ": 14, "HIGH BW": 0,
        })
        bands = eq_bands(slot)
        self.assertEqual([(frequency, gain) for frequency, gain, _ in bands],
                         [(100, 0), (4000, 3), (4500, -9)])
        self.assertLess(eq_response(4500, bands), 0)
        flat = [(frequency, 0, width) for frequency, _, width in bands]
        self.assertEqual(eq_response(1000, flat), 0)
        slot.params["HIGHFREQ"] = 25
        self.assertIsNone(eq_bands(slot))
        del slot.params["HIGHFREQ"]
        self.assertIsNone(eq_bands(slot))

    def test_eq_display_fits_and_does_not_open_amp_picker(self):
        view = AmpView(EffectsDB())
        view.set_slot(FxSlot.from_json(3, EffectsDB().build_slot_data("DIGBRGHT")))
        eq = view.eq_display
        self.assertLess(view._knobs[-1].geometry().right(), eq.geometry().left())
        self.assertLess(eq.geometry().right(), view._switch_rect().left())
        changes = []
        view.change_requested.connect(changes.append)
        view.show()
        self.app.processEvents()
        QTest.mouseClick(eq, Qt.LeftButton)
        self.assertEqual(changes, [])
        view.close()

    def test_eq_display_renders_changes_and_bypass(self):
        db = EffectsDB()
        slot = FxSlot.from_json(4, db.build_slot_data("EQ"))
        slot.enable = True
        view = AmpView(db)
        display = view.eq_display
        display.set_slot(slot)
        view.show()
        self.app.processEvents()
        flat = display.grab().toImage()
        slot.params["LOW LEVL"] = 20
        display.update()
        changed = display.grab().toImage()
        self.assertNotEqual(flat, changed)
        slot.enable = False
        display.update()
        bypassed = display.grab().toImage()
        self.assertNotEqual(changed, bypassed)
        display.set_slot(None)
        self.assertNotEqual(bypassed, display.grab().toImage())
        view.close()

    def test_eq_knobs_use_encoded_parameter_ranges(self):
        db = EffectsDB()
        slot = FxSlot.from_json(4, db.build_slot_data("EQ"))
        pedal = PedalWidget(4, slot, db)
        for name, maximum in (("LOW LEVL", 24), ("LOW FREQ", 37),
                              ("MID LEVL", 24), ("MID FREQ", 45),
                              ("HIGHLEVL", 24), ("HIGHFREQ", 24)):
            knob = pedal._knobs[name]
            self.assertEqual((knob.min_val, knob.max_val), (0, maximum))

    def test_eq_pedal_displays_all_three_bands_without_overlaps(self):
        db = EffectsDB()
        pedal = PedalWidget(4, FxSlot.from_json(4, db.build_slot_data("EQ")), db)
        self.assertEqual(pedal.width(), EQ_DISP_W)
        self.assertEqual(set(pedal._knobs),
                         {"LOW LEVL", "LOW FREQ", "MID LEVL", "MID FREQ",
                          "HIGHLEVL", "HIGHFREQ"})
        self.assertEqual(set(pedal._switches), {"LOW BW", "MID BW", "HIGH BW"})
        previous = None
        for level, frequency, bandwidth in (
                ("LOW LEVL", "LOW FREQ", "LOW BW"),
                ("MID LEVL", "MID FREQ", "MID BW"),
                ("HIGHLEVL", "HIGHFREQ", "HIGH BW")):
            controls = [pedal._knobs[level], pedal._knobs[frequency],
                        pedal._switches[bandwidth]]
            self.assertEqual(len({control.geometry().center().x() for control in controls}), 1)
            self.assertLess(controls[0].geometry().bottom(), controls[1].geometry().top())
            self.assertLess(controls[1].geometry().bottom(), controls[2].geometry().top())
            self.assertLess(controls[2].geometry().bottom(), int(256 * DISP_H / SRC_H))
            if previous is not None:
                self.assertLess(previous.geometry().right(), controls[0].geometry().left())
            previous = controls[0]
            for control in controls:
                self.assertTrue(pedal.rect().contains(control.geometry()))

    def test_eq_bandwidth_switch_is_discrete_and_does_not_toggle_pedal(self):
        db = EffectsDB()
        slot = FxSlot.from_json(4, db.build_slot_data("EQ"))
        pedal = PedalWidget(4, slot, db)
        changes, toggles = [], []
        pedal.param_changed.connect(lambda *args: changes.append(args))
        pedal.enable_toggled.connect(lambda *args: toggles.append(args))
        pedal.show()
        self.app.processEvents()
        for name, switch in pedal._switches.items():
            for y, expected in ((4, 0), (16, 1), (28, 2)):
                QTest.mouseClick(switch, Qt.LeftButton, pos=QPoint(30, y))
                self.assertEqual(switch.value, expected)
                self.assertEqual(changes[-1], (4, name, expected))
        switch = pedal._switches["HIGH BW"]
        QTest.keyClick(switch, Qt.Key_Up)
        self.assertEqual(changes[-1], (4, "HIGH BW", 1))
        self.assertEqual(toggles, [])
        pedal.update_param("HIGH BW", 9)
        self.assertIsNone(switch.value)
        self.assertEqual(switch.accessibleDescription(), "Unknown")
        self.assertEqual(changes[-1], (4, "HIGH BW", 1))
        pedal.close()


if __name__ == "__main__":
    unittest.main()
