import math
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt5.QtWidgets import QApplication

from nexus.ui.knob import Knob


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
                self.assertAlmostEqual(center.x(), size / 2)
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


if __name__ == "__main__":
    unittest.main()
