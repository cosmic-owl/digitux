"""Pedal widget — stylized cartoon pedal with rotary knobs + ON/OFF LED."""
from PyQt5.QtWidgets import QWidget, QMenu
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPixmap, QPainter, QColor, QPen, QFont

from .knob import Knob
from .i18n import translate
from ..effects_db import visible_pedal_params
from ..runtime import img_path

SRC_W = 220.0
SRC_H = 364.0
DISP_W = 180
DISP_H = 298
EQ_DISP_W = 282


class BandwidthSwitch(QWidget):
    valueChanged = pyqtSignal(int)
    _choices = ("WIDE", "MEDIUM", "NARROW")

    def __init__(self, name, value, parent=None):
        super().__init__(parent)
        self.name = name
        self._value = None
        self.setFixedSize(78, 59)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(name)
        self.setToolTip(f"{name}: {translate('Wide, Medium or Narrow')}")
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value if type(value) is int and 0 <= value < 3 else None
        self.setAccessibleDescription(
            translate(self._choices[self._value]) if self._value is not None
            else translate("Unknown")
        )
        self.update()

    def paintEvent(self, a0):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(105, 105, 105), 1))
        p.setBrush(QColor(18, 18, 20))
        p.drawRoundedRect(8, 3, 13, 35, 6, 6)
        if self._value is not None:
            p.setPen(QColor(40, 35, 25))
            p.setBrush(QColor(255, 176, 0))
            p.drawEllipse(9, 3 + self._value * 12, 11, 11)
        else:
            p.setPen(QColor(255, 190, 60))
            p.drawText(QRect(8, 3, 13, 35), Qt.AlignmentFlag.AlignCenter, "?")
        p.setFont(QFont("Sans", 7, QFont.Bold))
        for i, text in enumerate(self._choices):
            p.setPen(QColor(255, 190, 60) if i == self._value else QColor(180, 180, 180))
            p.drawText(QRect(25, i * 12, 53, 14),
                       Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                       translate(text))
        p.setPen(QColor(225, 225, 225))
        p.setFont(QFont("Sans", 8, QFont.Bold))
        p.drawText(QRect(0, 40, 78, 18), Qt.AlignmentFlag.AlignCenter, self.name)
        if self.hasFocus():
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(QColor(255, 176, 0), 1, Qt.PenStyle.DotLine))
            p.drawRoundedRect(1, 1, 75, 56, 4, 4)

    def mousePressEvent(self, a0):
        if a0 is not None:
            if a0.button() == Qt.MouseButton.LeftButton:
                self.setFocus(Qt.FocusReason.MouseFocusReason)
                if 0 <= a0.pos().y() < 39:
                    self._select(min(a0.pos().y() // 12, 2))
            a0.accept()

    def mouseReleaseEvent(self, a0):
        if a0 is not None:
            a0.accept()

    def keyPressEvent(self, a0):
        if a0 is None:
            return
        if a0.key() in (Qt.Key.Key_Up, Qt.Key.Key_Left, Qt.Key.Key_Down, Qt.Key.Key_Right):
            direction = -1 if a0.key() in (Qt.Key.Key_Up, Qt.Key.Key_Left) else 1
            current = self._value if self._value is not None else 1
            self._select(max(0, min(2, current + direction)))
            a0.accept()
        else:
            super().keyPressEvent(a0)

    def _select(self, value):
        if value != self._value:
            self.value = value
            self.valueChanged.emit(value)


class PedalWidget(QWidget):
    """A single effect 'pedal' on the signal chain."""

    param_changed = pyqtSignal(int, str, int)   # slot index, param, value
    enable_toggled = pyqtSignal(int, bool)      # slot index, enabled
    delete_requested = pyqtSignal(int)
    change_requested = pyqtSignal(int)

    def __init__(self, index, slot, db, parent=None):
        super().__init__(parent)
        self.index = index
        self.slot = slot
        self.db = db
        self._pixmap = None
        self._knobs = {}
        self._switches = {}
        self.setFixedSize(EQ_DISP_W if slot.model == "eq.EQ" else DISP_W, DISP_H)
        self._load_pixmap()
        self._build_knobs()

    # -------------------------------------------------------------- setup
    def _load_pixmap(self):
        addr = self.slot.model.split(".")[-1] if "." in self.slot.model else self.slot.model
        effect = self.db.by_address(addr)
        fn = effect["image"] if effect else None
        if not fn:
            return
        base = img_path()
        for sub in ("amps", "pedals", "cabs"):
            fp = base / sub / fn
            if fp.exists():
                pm = QPixmap(str(fp))
                if not pm.isNull():
                    pm = pm.scaled(DISP_W, DISP_H, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    if self.slot.model == "eq.EQ":
                        self._pixmap = QPixmap(self.width(), DISP_H)
                        self._pixmap.fill(Qt.GlobalColor.transparent)
                        painter = QPainter(self._pixmap)
                        extra = (self.width() - DISP_W) // 2
                        for left, right, dest_left, dest_right in (
                            (0, 30, 0, 30),
                            (30, 58, 30, 58 + extra),
                            (58, 122, 58 + extra, 122 + extra),
                            (122, 150, 122 + extra, 150 + 2 * extra),
                            (150, DISP_W, 150 + 2 * extra, self.width()),
                        ):
                            painter.drawPixmap(QRect(dest_left, 0, dest_right - dest_left, DISP_H),
                                               pm, QRect(left, 0, right - left, DISP_H))
                        painter.end()
                    else:
                        self._pixmap = pm
                return

    def _build_knobs(self):
        addr = self.slot.model.split(".")[-1] if "." in self.slot.model else self.slot.model
        effect = self.db.by_address(addr)
        if not effect:
            return
        if self.slot.model == "eq.EQ":
            self._build_eq_controls(effect)
            return
        # parámetros del efecto (excluyendo ENABLE)
        params = visible_pedal_params(effect)
        if not params:
            return
        # grilla fija de hasta 6 perillas (2 columnas x 3 filas), en coords fuente 220x364
        # dentro de la placa
        sx = DISP_W / SRC_W
        sy = DISP_H / SRC_H
        kw = 40
        n = len(params)
        if n == 1:
            # una sola perilla (p.ej. Volume) -> centrada
            positions = [(110, 96)]   # centro de la placa, en coords fuente
        else:
            grid = [(60, 60), (160, 60), (60, 130), (160, 130), (60, 200), (160, 200)]
            positions = grid[:n]
        for i, plist in enumerate(params):
            name = plist["address"]
            kx, ky = positions[i]
            knob = Knob(name, plist.get("min", 0), plist.get("max", 99),
                        int(self.slot.params.get(name, plist.get("default", 0))),
                        plist.get("unit", ""), size=kw,
                        knob_type=plist.get("knobType"), parent=self)
            px = int(kx * sx) - knob.width() // 2
            py = int(ky * sy) - kw // 2
            knob.move(px, py)
            knob.valueChanged.connect(
                lambda v, n=name, i=self.index: self.param_changed.emit(i, n, v)
            )
            self._knobs[name] = knob
            knob.show()

    def _build_eq_controls(self, effect):
        params = {p["address"]: p for p in effect.get("params", [])}
        bands = (
            ("LOW LEVL", "LOW FREQ", "LOW BW"),
            ("MID LEVL", "MID FREQ", "MID BW"),
            ("HIGHLEVL", "HIGHFREQ", "HIGH BW"),
        )
        for x, (level, frequency, bandwidth) in zip((55, 141, 227), bands):
            for y, name in ((27, level), (88, frequency)):
                p = params[name]
                knob = Knob(name, p["min"], p["max"],
                            int(self.slot.params.get(name, p["default"])),
                            p.get("unit", ""), size=40, parent=self)
                knob.move(x - knob.width() // 2, y)
                knob.valueChanged.connect(
                    lambda value, n=name: self.param_changed.emit(self.index, n, value)
                )
                self._knobs[name] = knob
                knob.show()
            switch = BandwidthSwitch(bandwidth, self.slot.params.get(bandwidth), self)
            if bandwidth not in self.slot.params:
                switch.setEnabled(False)
                switch.setToolTip(f"{bandwidth}: {translate('parameter unavailable')}")
            switch.move(x - switch.width() // 2, 149)
            switch.valueChanged.connect(
                lambda value, n=bandwidth: self.param_changed.emit(self.index, n, value)
            )
            self._switches[bandwidth] = switch
            switch.show()

    def update_param(self, name, value):
        control = self._knobs.get(name) or self._switches.get(name)
        if control is not None:
            control.value = int(value)

    # ------------------------------------------------------------ painting
    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        # press offset: pedal dips down a few px while pressed
        dy = 6 if getattr(self, "_pressed", False) else 0
        r = QRect(0, dy, self.width(), DISP_H)
        if self._pixmap:
            p.drawPixmap(r, self._pixmap)
        else:
            p.fillRect(r, QColor(50, 50, 50))
            p.setPen(QColor(255, 176, 0))
            p.setFont(QFont("Sans", 12, QFont.Bold))
            p.drawText(r, Qt.AlignCenter, self.slot.model.split(".")[-1])
        # border highlight when enabled
        enabled = bool(self.slot.enable)
        if enabled:
            p.setPen(QPen(QColor(255, 176, 0, 160), 2))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(1 + dy // 2, 1 + dy, self.width() - 3, DISP_H - 3, 12, 12)
        # ON/OFF LED + footswitch (bottom-right, part of the animated press)
        lx = self.width() - 30
        ly = DISP_H - 46 + dy
        if enabled:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(110, 220, 80, 120))
            p.drawEllipse(lx - 4, ly - 4, 24, 24)
            p.setBrush(QColor(150, 240, 110))
            p.setPen(QPen(QColor(40, 90, 30), 1))
        else:
            p.setBrush(QColor(56, 56, 56))
            p.setPen(QPen(QColor(28, 28, 28), 1))
        p.drawEllipse(lx, ly, 16, 16)
        # footswitch ring below LED
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor(30, 30, 30), 2))
        p.drawEllipse(lx - 6, ly + 22, 28, 28)
        p.end()

    # ------------------------------------------------------------ events
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._pressed = True
            self._drag_start = e.pos()
            self.update()
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if getattr(self, "_pressed", False) and getattr(self, "_drag_start", None) is not None:
            if (e.pos() - self._drag_start).manhattanLength() > 12:
                self._pressed = False
                self.update()
                cb = getattr(self, "_on_drag_requested", None)
                if cb:
                    cb(self.index, self)
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and getattr(self, "_pressed", False):
            self._pressed = False
            self.update()
            # toggle on/off
            self.slot.enable = not bool(self.slot.enable)
            self.enable_toggled.emit(self.index, bool(self.slot.enable))
        super().mouseReleaseEvent(e)

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        menu.addAction(translate("Cambiar efecto..."), lambda: self.change_requested.emit(self.index))
        menu.addAction(translate("Eliminar"), lambda: self.delete_requested.emit(self.index))
        menu.exec_(e.globalPos())