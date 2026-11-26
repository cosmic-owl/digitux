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
from nexus.ui.knob import Knob
from nexus.ui.pedal_widget import DISP_H, DISP_W, SRC_H, SRC_W, PedalWidget


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
        for address, names in (("EQ", ("LOW LEVL", "LOW FREQ")),
                               ("LEX HALL", ("PREDELAY", "DECAY"))):
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


if __name__ == "__main__":
    unittest.main()
