"""Control assignment and tempo panel."""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QStackedWidget, QButtonGroup, QSpinBox, QStyle, QStyleOptionButton,
    QStylePainter,
)
from PyQt5.QtCore import QRect, QSize, pyqtSignal
from .tempo_panel import TempoPanel
from .i18n import translate


class _VerticalButton(QPushButton):
    def sizeHint(self):
        size = super().sizeHint()
        return QSize(size.height(), size.width())

    def minimumSizeHint(self):
        return self.sizeHint()

    def paintEvent(self, event):
        option = QStyleOptionButton()
        self.initStyleOption(option)
        painter = QStylePainter(self)
        label = option.text
        option.text = ""
        painter.drawControl(QStyle.CE_PushButton, option)
        option.text = label
        option.rect = QRect(0, 0, self.height(), self.width())
        painter.translate(self.width(), 0)
        painter.rotate(90)
        painter.drawControl(QStyle.CE_PushButtonLabel, option)


class ControlPanel(QWidget):
    """Right-side controls with a vertical navigation rail."""

    stomp_assigned = pyqtSignal(str, int)          # ctrl, slot (or -1 to clear)
    expression_assigned = pyqtSignal(str, int, str, int, int)  # ctrl, slot, param, min, max
    lfo_assigned = pyqtSignal(int, str, int, int, int, int)    # slot, param, min, max, speed, waveform
    wah_level = pyqtSignal(int)                    # value
    pedal = pyqtSignal(int)                        # value

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.navigation = QWidget()
        self.navigation.setFixedWidth(40)
        self.navigation.setStyleSheet(
            "QWidget{background:#202020;}"
            "QPushButton{background:transparent;color:#aaa;border:0;"
            "border-left:3px solid transparent;text-align:center;padding:6px 10px;}"
            "QPushButton:hover{background:#292929;color:#eee;}"
            "QPushButton:checked{background:#181818;color:#ffb000;"
            "border-left:3px solid #ffb000;}"
            "QPushButton:focus{border-bottom:1px solid #ffb000;}"
        )
        self.nav_layout = QVBoxLayout(self.navigation)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_layout.setSpacing(0)
        self.nav_buttons = QButtonGroup(self)
        self.nav_buttons.setExclusive(True)
        content = QWidget()
        content.setStyleSheet("background:#181818;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        self.heading = QLabel()
        self.heading.setStyleSheet(
            "color:#ffb000;font-weight:bold;padding:10px 9px;"
            "border-bottom:1px solid #333;"
        )
        content_layout.addWidget(self.heading)
        self.pages = QStackedWidget()
        content_layout.addWidget(self.pages, 1)
        layout.addWidget(content, 1)
        layout.addWidget(self.navigation)
        self._build_stomp()
        self._build_expression()
        self._build_lfo()
        self._build_wah()
        self.tempo = TempoPanel()
        self._add_page(self.tempo, "Tempo", "Tempo")
        self.nav_layout.addStretch()
        self.nav_buttons.button(0).setChecked(True)
        self.heading.setText(translate("Stompbox"))
        self.expr_slot.currentIndexChanged.connect(self._populate_expr_params)
        self.lfo_slot.currentIndexChanged.connect(self._populate_lfo_params)

    def _add_page(self, page, label, title):
        index = self.pages.addWidget(page)
        button = _VerticalButton(translate(label))
        button.setCheckable(True)
        button.setToolTip(translate(title))
        button.setAccessibleName(translate(title))
        button.clicked.connect(lambda: self._select_page(index, title))
        self.nav_buttons.addButton(button, index)
        self.nav_layout.addWidget(button)

    def _select_page(self, index, title):
        self.pages.setCurrentIndex(index)
        self.heading.setText(translate(title))

    # ---------------------------------------------------------- stompbox
    def _build_stomp(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        self.stomp_combo = QComboBox()
        self.stomp_combo.addItems(["ctrlA", "ctrlB", "ctrlC", "ctrlVSw"])
        self.stomp_combo.setStyleSheet(self._combo_style())
        lay.addWidget(QLabel(translate("Footswitch")))
        lay.addWidget(self.stomp_combo)

        self.stomp_slot = QComboBox()
        self.stomp_slot.setStyleSheet(self._combo_style())
        lay.addWidget(QLabel(translate("Asignar a pedal")))
        lay.addWidget(self.stomp_slot)
        for i in range(10):
            self.stomp_slot.addItem(translate("Slot {slot}").format(slot=i + 1), i)
        self.stomp_slot.addItem(translate("— Ninguno —"), -1)
        self.stomp_slot.currentIndexChanged.connect(self._on_stomp)

        clear = QPushButton(translate("Quitar asignación"))
        clear.clicked.connect(self._clear_stomp)
        lay.addWidget(clear)
        lay.addStretch()
        self._add_page(w, "Stompbox", "Stompbox")

    def _on_stomp(self):
        idx = self.stomp_slot.currentData()
        ctrl = self.stomp_combo.currentText()
        self.stomp_assigned.emit(ctrl, idx)

    def _clear_stomp(self):
        self.stomp_slot.blockSignals(True)
        self.stomp_slot.setCurrentIndex(self.stomp_slot.count() - 1)
        self.stomp_slot.blockSignals(False)
        self.stomp_assigned.emit(self.stomp_combo.currentText(), -1)

    # -------------------------------------------------------- expression
    def _build_expression(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        self.expr_ctrl = QComboBox()
        self.expr_ctrl.addItems(["treadle", "altTreadle"])
        self.expr_ctrl.setStyleSheet(self._combo_style())
        lay.addWidget(QLabel(translate("Pedal de expresión")))
        lay.addWidget(self.expr_ctrl)

        self.expr_slot = QComboBox()
        self.expr_slot.setStyleSheet(self._combo_style())
        lay.addWidget(QLabel(translate("Asignar a slot")))
        lay.addWidget(self.expr_slot)

        self.expr_param = QComboBox()
        self.expr_param.setStyleSheet(self._combo_style())
        lay.addWidget(QLabel(translate("Parámetro")))
        lay.addWidget(self.expr_param)

        self.expr_min = QSpinBox(); self.expr_min.setRange(0, 99)
        self.expr_max = QSpinBox(); self.expr_max.setRange(0, 99); self.expr_max.setValue(99)
        lay.addWidget(QLabel(translate("Min")))
        lay.addWidget(self.expr_min)
        lay.addWidget(QLabel(translate("Max")))
        lay.addWidget(self.expr_max)

        self.expr_slot.currentIndexChanged.connect(self._populate_params)
        assign = QPushButton(translate("Asignar"))
        assign.clicked.connect(self._assign_expression)
        lay.addWidget(assign)
        lay.addStretch()
        self._add_page(w, "Expression", "Expression Link")

    def _populate_params(self):
        self.expr_param.clear()

    def _assign_expression(self):
        ctrl = self.expr_ctrl.currentText()
        slot = self.expr_slot.currentData()
        param = self.expr_param.currentText()
        if slot is None or not param:
            return
        self.expression_assigned.emit(ctrl, slot, param, self.expr_min.value(), self.expr_max.value())

    # ------------------------------------------------------------- lfo
    def _build_lfo(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        self.lfo_slot = QComboBox()
        self.lfo_slot.setStyleSheet(self._combo_style())
        lay.addWidget(QLabel(translate("Asignar a slot")))
        lay.addWidget(self.lfo_slot)

        self.lfo_param = QComboBox()
        self.lfo_param.setStyleSheet(self._combo_style())
        lay.addWidget(QLabel(translate("Parámetro")))
        lay.addWidget(self.lfo_param)

        self.lfo_min = QSpinBox(); self.lfo_min.setRange(0, 99)
        self.lfo_max = QSpinBox(); self.lfo_max.setRange(0, 99); self.lfo_max.setValue(99)
        lay.addWidget(QLabel(translate("Min")))
        lay.addWidget(self.lfo_min)
        lay.addWidget(QLabel(translate("Max")))
        lay.addWidget(self.lfo_max)

        self.lfo_speed = QSpinBox(); self.lfo_speed.setRange(0, 185); self.lfo_speed.setValue(74)
        self.lfo_wave = QComboBox()
        for wave in ("TRIANGLE", "SINE", "SQUARE"):
            self.lfo_wave.addItem(translate(wave), wave)
        lay.addWidget(QLabel(translate("Speed")))
        lay.addWidget(self.lfo_speed)
        lay.addWidget(QLabel(translate("Wave")))
        lay.addWidget(self.lfo_wave)

        self.lfo_slot.currentIndexChanged.connect(lambda _: self._populate_params())
        assign = QPushButton(translate("Asignar"))
        assign.clicked.connect(self._assign_lfo)
        lay.addWidget(assign)
        lay.addStretch()
        self._add_page(w, "LFO", "LFO Link")

    def _assign_lfo(self):
        slot = self.lfo_slot.currentData()
        param = self.lfo_param.currentText()
        if slot is None or not param:
            return
        wave = {"TRIANGLE": 0, "SINE": 1, "SQUARE": 2}[self.lfo_wave.currentData()]
        self.lfo_assigned.emit(slot, param, self.lfo_min.value(), self.lfo_max.value(),
                               self.lfo_speed.value(), wave)

    # ------------------------------------------------------------ wah
    def _build_wah(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        self.wah_level_spin = QSpinBox(); self.wah_level_spin.setRange(0, 12); self.wah_level_spin.setValue(6)
        self.wah_level_spin.valueChanged.connect(self._on_wah_level)
        lay.addWidget(QLabel("WAH LEVL"))
        lay.addWidget(self.wah_level_spin)
        self.pedal_spin = QSpinBox(); self.pedal_spin.setRange(0, 99); self.pedal_spin.setValue(0)
        self.pedal_spin.valueChanged.connect(self._on_pedal)
        lay.addWidget(QLabel("PEDAL"))
        lay.addWidget(self.pedal_spin)
        lay.addStretch()
        self._add_page(w, "Wah", "Wah Settings")

    def _on_wah_level(self, v):
        self.wah_level_value = v
        self.wah_level.emit(v)

    def _on_pedal(self, v):
        self.pedal_value = v
        self.pedal.emit(v)

    # ----------------------------------------------------------- helpers
    def _combo_style(self):
        return "QComboBox{background:#222;color:#ddd;border:1px solid #444;border-radius:4px;padding:4px;}"

    def set_effect_slots(self, slots):
        """Populate slot combos with the current effects and their params."""
        self._slots = slots
        items = []
        for idx, slot in sorted(slots.items()):
            name = slot.model.split(".")[-1]
            items.append((f"{idx+1}: {name}", idx))
        for combo in (self.expr_slot, self.lfo_slot):
            combo.blockSignals(True)
            combo.clear()
            for label, data in items:
                combo.addItem(label, data)
            combo.blockSignals(False)
        self._populate_expr_params()
        self._populate_lfo_params()

    def _params_for_combo(self, combo):
        idx = combo.currentData()
        if idx is None or not hasattr(self, "_slots"):
            return []
        slot = self._slots.get(idx)
        if slot is None:
            return []
        return [p for p in slot.params.keys()]

    def _populate_expr_params(self):
        self.expr_param.blockSignals(True)
        self.expr_param.clear()
        self.expr_param.addItems(self._params_for_combo(self.expr_slot))
        self.expr_param.blockSignals(False)

    def _populate_lfo_params(self):
        self.lfo_param.blockSignals(True)
        self.lfo_param.clear()
        self.lfo_param.addItems(self._params_for_combo(self.lfo_slot))
        self.lfo_param.blockSignals(False)