"""Session-local tap tempo and rhythmic subdivision controls."""

import time
from collections import deque

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox,
    QDoubleSpinBox,
)


SUBDIVISIONS = (
    ("Off", None),
    ("Half", 2.0),
    ("Quarter", 1.0),
    ("Dotted eighth", 0.75),
    ("Eighth", 0.5),
    ("Eighth triplet", 1.0 / 3.0),
    ("Sixteenth", 0.25),
)


def delay_ms(bpm, beats):
    return round(60000 * beats / bpm)


def lfo_speed(bpm, beats):
    """Approximate the device's encoded speed using its documented anchor points."""
    hz = bpm / (60 * beats)
    if not 0.05 <= hz <= 10:
        raise ValueError(f"LFO: {hz:.2f} Hz fuera del rango 0.05–10 Hz")
    if hz <= 1:
        return round((hz - 0.05) * 100)
    return round(95 + (hz - 1) * 10)


class TempoPanel(QWidget):
    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._taps = deque(maxlen=5)
        lay = QVBoxLayout(self)
        self.bpm = QDoubleSpinBox()
        self.bpm.setRange(20, 300)
        self.bpm.setDecimals(1)
        self.bpm.setValue(120)
        self.bpm.setSuffix(" BPM")
        self.bpm.setToolTip("Tempo de esta sesión; no se lee del pedal")
        self.tap = QPushButton("Tap")
        self.tap.setToolTip("Pulsa al ritmo; una pausa de 3 segundos reinicia la medición")
        self.tap.clicked.connect(self._tap)
        lay.addWidget(self.bpm)
        lay.addWidget(self.tap)
        self.delay = self._subdivision(lay, "Delay")
        self.lfo = self._subdivision(lay, "LFO")
        self.lfo.setToolTip("La conversión a velocidad LFO es aproximada")
        self.readout = QLabel()
        self.readout.setWordWrap(True)
        lay.addWidget(self.readout)
        info = QLabel("Off conserva los valores del preset. "
                      "La sincronización se aplica al cambiar el tempo.")
        info.setWordWrap(True)
        lay.addWidget(info)
        lay.addStretch()
        self.bpm.valueChanged.connect(self._manual_tempo)
        self.delay.currentIndexChanged.connect(self._update)
        self.lfo.currentIndexChanged.connect(self._update)
        self._display()

    def _subdivision(self, layout, label):
        layout.addWidget(QLabel(label))
        combo = QComboBox()
        for name, beats in SUBDIVISIONS:
            combo.addItem(name, beats)
        layout.addWidget(combo)
        return combo

    def _manual_tempo(self):
        self._taps.clear()
        self._update()

    def _display(self):
        bpm = self.bpm.value()
        parts = []
        if self.delay.currentData() is not None:
            parts.append(f"Delay: {delay_ms(bpm, self.delay.currentData())} ms")
        if self.lfo.currentData() is not None:
            hz = bpm / (60 * self.lfo.currentData())
            parts.append(f"LFO: ~{hz:.2f} Hz")
        self.readout.setText("  |  ".join(parts))

    def _update(self):
        self._display()
        self.changed.emit()

    def _tap(self):
        now = time.monotonic()
        if self._taps and (now - self._taps[-1] > 3 or now <= self._taps[-1]):
            self._taps.clear()
        self._taps.append(now)
        if len(self._taps) < 2:
            return
        bpm = 60 * (len(self._taps) - 1) / (self._taps[-1] - self._taps[0])
        if not self.bpm.minimum() <= bpm <= self.bpm.maximum():
            self._taps.clear()
            self._taps.append(now)
            self.readout.setText("Tempo fuera del rango 20–300 BPM; vuelve a marcar")
            return
        blocked = self.bpm.blockSignals(True)
        self.bpm.setValue(bpm)
        self.bpm.blockSignals(blocked)
        self._update()
