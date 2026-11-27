"""Illustrative response of the preset's three-band EQ."""

import math

from PyQt5.QtCore import QPointF, QRect, QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QWidget
from .i18n import translate


# Endpoints and the intermediate points were read from an RP360XP. Values
# between them, and the band shapes, are estimates rather than measurements.
_BANDS = (
    ("LOW LEVL", "LOW FREQ", "LOW BW", ((0, 60), (9, 100), (37, 500))),
    ("MID LEVL", "MID FREQ", "MID BW", ((0, 300), (45, 4000))),
    ("HIGHLEVL", "HIGHFREQ", "HIGH BW", ((0, 2000), (14, 4500), (24, 8000))),
)
_WIDTHS = (1.5, 0.9, 0.5)  # illustrative standard deviations in octaves


def _frequency(value, anchors):
    for (lo, hz_lo), (hi, hz_hi) in zip(anchors, anchors[1:]):
        if lo <= value <= hi:
            return hz_lo * (hz_hi / hz_lo) ** ((value - lo) / (hi - lo))
    raise ValueError("EQ frequency outside known range")


def eq_bands(slot):
    """Return estimated (frequency, gain, width) bands, or None if invalid."""
    bands = []
    for level, frequency, width, anchors in _BANDS:
        gain = slot.params.get(level)
        freq = slot.params.get(frequency)
        bw = slot.params.get(width)
        if (type(gain) is not int or not 0 <= gain <= 24
                or type(freq) is not int or not anchors[0][0] <= freq <= anchors[-1][0]
                or type(bw) is not int or not 0 <= bw < len(_WIDTHS)):
            return None
        bands.append((_frequency(freq, anchors), gain - 12, _WIDTHS[bw]))
    return bands


def eq_response(frequency, bands):
    return sum(gain * math.exp(-0.5 * (math.log2(frequency / center) / width) ** 2)
               for center, gain, width in bands)


class EqDisplay(QWidget):
    """Read-only EQ estimate, not the complete preset response."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.slot = None
        self.setMinimumSize(164, 125)
        self.resize(164, 125)
        self.setToolTip(translate(
            "EQ effect only. Frequency mappings are interpolated and filter "
            "shapes are illustrative; this is not a measured response. "
            "The vertical scale adjusts to the curve."
        ))

    def set_slot(self, slot):
        self.slot = slot
        self.update()

    def paintEvent(self, a0):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor("#90a7c3"), 1))
        p.setBrush(QColor("#192b43"))
        width, height = self.width(), self.height()
        p.drawRoundedRect(QRectF(0.5, 0.5, width - 1, height - 1), 7, 7)
        p.setPen(QColor("#e8eef5"))
        p.setFont(QFont("Sans", 8, QFont.Bold))
        p.drawText(QRect(10, 7, width - 20, 18),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                   translate("EQ ESTIMATE"))
        p.setPen(QColor("#546980"))
        p.drawLine(10, 26, width - 10, 26)

        bands = eq_bands(self.slot) if self.slot is not None and self.slot.enable is True else None
        if self.slot is None:
            message = translate("NO EQ")
        elif self.slot.enable is False:
            message = translate("EQ BYPASSED")
        elif self.slot.enable is not True:
            message = translate("EQ UNAVAILABLE")
        else:
            message = translate("EQ UNAVAILABLE") if bands is None else None
        if bands is None:
            p.setPen(QColor("#b9c9dc"))
            p.drawText(QRect(8, 35, width - 16, height - 50),
                       Qt.AlignmentFlag.AlignCenter, message)
            return

        left, right, top, bottom = 38, width - 12, 42, height - 40
        samples = []
        for x in range(left, right + 1):
            frequency = 60 * (8000 / 60) ** ((x - left) / (right - left))
            samples.append(eq_response(frequency, bands))
        scale = max(12, math.ceil(max(abs(gain) for gain in samples)))
        ticks = [(round(left + (right - left) * math.log(hz / 60) / math.log(8000 / 60)),
                  label)
                 for hz, label in ((100, "100"), (1000, "1k"), (8000, "8k Hz"))]

        p.setPen(QColor("#425570"))
        for y in (top, (top + bottom) // 2, bottom):
            p.drawLine(left, y, right, y)
        for x in (left, *(x for x, _ in ticks)):
            p.drawLine(x, top, x, bottom)
        p.setFont(QFont("Sans", 7, QFont.Bold))
        p.setPen(QColor("#b9c9dc"))
        p.drawText(QRect(width - 35, 7, 25, 18),
                   Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "dB")
        for y, label in ((top, f"+{scale}"), ((top + bottom) // 2, "0"),
                         (bottom, f"-{scale}")):
            p.drawText(QRect(2, y - 7, left - 6, 14),
                       Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, label)
        for x, label in ticks:
            label_left = min(max(x - 22, 2), width - 46)
            p.drawText(QRect(label_left, bottom + 3, 44, 14),
                       Qt.AlignmentFlag.AlignCenter, label)
        for x, text in ((left + 7, "LOW"), ((left + right) // 2, "MID"),
                        (right - 12, "HIGH")):
            p.drawText(QRect(x - 22, height - 18, 44, 14), Qt.AlignmentFlag.AlignCenter,
                       translate(text))

        path = QPainterPath()
        for x, gain in enumerate(samples, left):
            y = (top + bottom) / 2 - gain * (bottom - top) / (2 * scale)
            point = QPointF(x, y)
            if x == left:
                path.moveTo(point)
            else:
                path.lineTo(point)
        p.save()
        p.setClipRect(QRect(left, top, right - left + 1, bottom - top + 1))
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor("#ffb534"), 2))
        p.drawPath(path)
        p.restore()

    def mousePressEvent(self, a0):
        if a0 is not None:
            a0.accept()
