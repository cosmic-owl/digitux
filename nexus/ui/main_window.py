"""Main window — faithful Nexus clone for Linux."""
import json
from pathlib import Path
import logging
import threading

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QLineEdit, QTabBar, QMessageBox, QStatusBar, QMenu,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QColor, QPalette, QPixmap, QPainter, QLinearGradient

from ..device import Device
from ..effects_db import EffectsDB
from .pedalboard_view import PedalboardView, reordered_slots
from .amp_cab_block import AmpCabBlock
from .control_panel import ControlPanel
from .tempo_panel import delay_ms, lfo_speed
from .i18n import translate
from ..runtime import img_path, data_path

log = logging.getLogger(__name__)
POLL_INTERVAL_MS = 5000


class _TitleBar(QWidget):
    """Custom title bar with a dark gradient."""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(54)

    def paintEvent(self, a0):
        p = QPainter(self)
        g = QLinearGradient(0, 0, 0, self.height())
        g.setColorAt(0, QColor(0x1e1e1e))
        g.setColorAt(0.5, QColor(0x141414))
        g.setColorAt(1, QColor(0x0d0d0d))
        p.fillRect(self.rect(), g)
        p.setPen(QColor(0x333333))
        p.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        p.end()


class Worker(QObject):
    notif = pyqtSignal(list, int)
    snapshot = pyqtSignal(object, int)
    failed = pyqtSignal(str)
    disconnected = pyqtSignal(str)

    def __init__(self, device):
        super().__init__()
        self.dev = device
        self._lock = threading.Lock()
        self._revision = 0
        self._structural_revision = 0
        self._changes = {}
        self._stopped = False

    def start(self):
        self.dev.on_notification(self._notification)
        self.dev.on_disconnect(self._disconnect)

    def invalidate(self):
        with self._lock:
            self._revision += 1
            self._structural_revision = self._revision
            return self._revision

    def record_change(self, path, value):
        with self._lock:
            self._revision += 1
            self._changes[path] = (self._revision, value)
            return self._revision

    def is_current(self, revision):
        with self._lock:
            return not self._stopped and revision == self._revision

    def stop(self):
        with self._lock:
            self._stopped = True
            self._revision += 1

    def _notification(self, msg):
        with self._lock:
            if self._stopped:
                return
            self._revision += 1
            revision = self._revision
            if (len(msg) >= 4 and msg[0] == "np" and isinstance(msg[2], str)
                    and self._is_scalar_path(msg[2], msg[3])):
                self._changes[msg[2]] = (revision, msg[3])
            elif (len(msg) >= 4 and msg[0] == "np" and isinstance(msg[2], str)
                  and not msg[2].startswith("preset") and msg[2] != "system/LAST PRES"):
                pass
            else:
                self._structural_revision = revision
        self.notif.emit(msg, revision)

    @staticmethod
    def _is_scalar_path(path, value):
        if path == "preset/name":
            return isinstance(value, str)
        if path == "preset/PRS LEVL":
            return isinstance(value, int)
        parts = path.split("/")
        return (len(parts) in (4, 5) and parts[:2] == ["preset", "fxc"]
                and parts[2].isdigit() and isinstance(value, int)
                and (len(parts) == 4 and parts[3] != "name"
                     or len(parts) == 5 and parts[3] == "fx" and parts[4] != "name"))

    def merge_snapshot(self, preset, revision):
        with self._lock:
            if self._stopped or self._structural_revision > revision:
                return None
            # Only properties changed since this read began need replaying.
            changes = [(path, value) for path, (seq, value) in self._changes.items()
                       if seq > revision]
            watermark = self._revision
            for path, value in changes:
                if not self._merge_change(preset, path, value):
                    return None
            return watermark

    @staticmethod
    def _merge_change(preset, path, value):
        if path == "preset/name":
            preset.name = value
            return True
        if path == "preset/PRS LEVL":
            preset.prs_levl = value
            return True
        parts = path.split("/")
        slot = preset.slots.get(int(parts[2]))
        if slot is None:
            return False
        name = parts[-1]
        if len(parts) == 4 and name == "ENABLE":
            slot.enable = bool(value)
            return True
        if ((len(parts) == 5) != slot._use_fx_subdict or name not in slot.params):
            return False
        slot.params[name] = value
        return True

    def _disconnect(self, exc):
        self.stop()
        self.disconnected.emit(str(exc))

    def read_preset(self):
        with self._lock:
            revision = self._revision
            self._changes.clear()
        threading.Thread(target=self._read_preset, args=(revision,), daemon=True).start()

    def _read_preset(self, revision):
        with self._lock:
            valid = not self._stopped and self._structural_revision <= revision
        if not valid:
            self.snapshot.emit(None, revision)
            return
        try:
            preset = self.dev.get_active_preset()
        except Exception as exc:
            log.exception("Could not reconcile active preset")
            self.failed.emit(str(exc))
        else:
            self.snapshot.emit(preset, revision)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(translate("DigiTux — RP360/XP Editor"))
        self.resize(1360, 820)
        self.db = EffectsDB()
        self.dev = Device()
        self._sync_busy = False
        self._sync_requested = False
        self._connected = False
        self._session_open = False
        self._snapshot_watermark = -1
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(POLL_INTERVAL_MS)
        self._poll_timer.timeout.connect(self._request_sync)
        self._sync_timer = QTimer(self)
        self._sync_timer.setSingleShot(True)
        self._sync_timer.setInterval(100)
        self._sync_timer.timeout.connect(self._request_sync)
        self._setup_ui()
        self._apply_theme()
        QTimer.singleShot(100, self._connect)

    # ---------------------------------------------------------------- UI
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Left: preset browser
        self.browser = self._build_browser()
        root.addWidget(self.browser)

        # Right: amp-cab + pedalboard
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(10, 10, 10, 10)
        rl.setSpacing(10)

        self.title_bar = self._build_title_bar()
        rl.addWidget(self.title_bar)

        self.amp_block = AmpCabBlock(self.db)
        self.amp_block.param_changed.connect(self._set_param)
        self.amp_block.cabinet_changed.connect(self._set_cabinet)
        self.amp_block.change_requested.connect(self._change_model)
        self.amp_block.bypass_toggled.connect(self._set_amp_bypass)
        rl.addWidget(self.amp_block)

        self.pedalboard = PedalboardView()
        self.pedalboard.param_changed.connect(self._set_param)
        self.pedalboard.enable_toggled.connect(self._set_enable)
        self.pedalboard.delete_requested.connect(self._delete_slot)
        self.pedalboard.change_requested.connect(self._change_model)
        self.pedalboard.reorder_requested.connect(self._reorder)
        rl.addWidget(self.pedalboard, 1)

        root.addWidget(right, 1)

        # Right: control assignment panel
        self.control_panel = ControlPanel(self.db)
        self.control_panel.setFixedWidth(240)
        self.control_panel.stomp_assigned.connect(self._assign_stomp)
        self.control_panel.expression_assigned.connect(self._assign_expression)
        self.control_panel.lfo_assigned.connect(self._assign_lfo)
        self.control_panel.tempo.changed.connect(self._sync_tempo)
        self.control_panel.wah_level.connect(
            lambda value: self._set_wah_param("WAH LEVL", value))
        self.control_panel.pedal.connect(
            lambda value: self._set_wah_param("PEDAL", value))
        root.addWidget(self.control_panel)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage(translate("Conectando..."))
        self._build_menubar()

    def _build_title_bar(self):
        bar = _TitleBar()
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(18, 0, 18, 0)
        lay.setSpacing(12)

        # DigiTux logo
        logo_lbl = QLabel()
        logo_path = img_path("menu", "digitux_logo.png")
        if logo_path.exists():
            pm = QPixmap(str(logo_path))
            if not pm.isNull():
                logo_lbl.setPixmap(pm)
        lay.addWidget(logo_lbl)

        sep = QLabel("·")
        sep.setStyleSheet("color:#444; font-size:18px;")
        lay.addWidget(sep)

        self.preset_name = QLabel("—")
        self.preset_name.setStyleSheet("color:#fff; font-size:24px; font-weight:bold;")
        lay.addWidget(self.preset_name)
        lay.addStretch()

        # Preset Level
        from PyQt5.QtWidgets import QSlider
        lvl_lbl = QLabel(translate("Level"))
        lvl_lbl.setStyleSheet("color:#bbb; font-size:12px;")
        lay.addWidget(lvl_lbl)
        self.level_slider = QSlider(Qt.Orientation.Horizontal)
        self.level_slider.setRange(0, 99)
        self.level_slider.setFixedWidth(120)
        self.level_slider.setStyleSheet(
            "QSlider::groove:horizontal{height:4px;background:#333;border-radius:2px;}"
            "QSlider::handle:horizontal{background:#ffb000;width:12px;margin:-4px 0;border-radius:6px;}"
        )
        self.level_slider.valueChanged.connect(self._set_preset_level)
        lay.addWidget(self.level_slider)
        self.level_value = QLabel("65")
        self.level_value.setStyleSheet("color:#ffb000; font-size:12px; font-weight:bold; min-width:24px;")
        lay.addWidget(self.level_value)

        for text, slot, kind in [
            (translate("Guardar"), self._store, "save"),
            (translate("Recargar"), self._reload, "reload"),
            (translate("+ Pedal"), self._add_effect, "add"),
        ]:
            b = QPushButton(text)
            b.setFixedHeight(30)
            color = {"save": "#2d7d3d", "reload": "#2d5d7d", "add": "#8a6d2d"}[kind]
            b.setStyleSheet(
                f"QPushButton{{background:{color};color:#fff;border:none;border-radius:5px;"
                f"padding:0 14px;font-weight:bold;font-size:12px;}}"
                f"QPushButton:hover{{opacity:0.9;}}"
            )
            b.clicked.connect(slot)
            lay.addWidget(b)
        return bar

    def _build_browser(self):
        w = QWidget()
        w.setFixedWidth(300)
        w.setStyleSheet("background:#181818;border-right:1px solid #2a2a2a;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)

        title = QLabel(translate("MIS TONOS"))
        title.setStyleSheet("color:#ffb000; font-weight:bold; font-size:13px;")
        lay.addWidget(title)

        self.search = QLineEdit()
        self.search.setPlaceholderText(translate("Buscar..."))
        self.search.setStyleSheet(
            "QLineEdit{background:#222;border:1px solid #333;border-radius:4px;"
            "color:#ddd;padding:4px 8px;}"
        )
        self.search.textChanged.connect(self._filter)
        lay.addWidget(self.search)

        self.tabs = QTabBar()
        for t in ("User", "Factory", "Library"):
            self.tabs.addTab(translate(t))
        self.tabs.currentChanged.connect(self._on_tab)
        lay.addWidget(self.tabs)

        self.list = QListWidget()
        self.list.setStyleSheet(
            "QListWidget{background:transparent;border:none;color:#ddd;}"
            "QListWidget::item{padding:7px;border-radius:4px;}"
            "QListWidget::item:selected{background:#ffb000;color:#111;}"
            "QListWidget::item:hover{background:#333;}"
        )
        self.list.itemDoubleClicked.connect(self._on_select)
        self.list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self._preset_context_menu)
        lay.addWidget(self.list, 1)

        self.library_presets = []
        return w

    def _apply_theme(self):
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if not isinstance(app, QApplication):
            raise RuntimeError("DigiTux requires a QApplication")
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor(0x181818))
        pal.setColor(QPalette.WindowText, QColor(0xdddddd))
        pal.setColor(QPalette.Base, QColor(0x1a1a1a))
        pal.setColor(QPalette.Text, QColor(0xdddddd))
        pal.setColor(QPalette.Button, QColor(0x222222))
        pal.setColor(QPalette.ButtonText, QColor(0xdddddd))
        pal.setColor(QPalette.Highlight, QColor(0xffb000))
        pal.setColor(QPalette.HighlightedText, QColor(0x111111))
        app.setPalette(pal)
        app.setStyle("Fusion")

    # ------------------------------------------------------------- device
    def _connect(self):
        try:
            self.dev.connect()
            self._session_open = True
            self.worker = Worker(self.dev)
            self.worker.notif.connect(self._on_notif)
            self.worker.snapshot.connect(self._on_snapshot)
            self.worker.failed.connect(self._on_sync_error)
            self.worker.disconnected.connect(self._on_disconnect)
            self.worker.start()
            self._connected = True
            self._refresh_names()
            self._reload()
            self._poll_timer.start()
        except Exception as e:
            self._connected = False
            self._poll_timer.stop()
            if hasattr(self, "worker"):
                self.worker.stop()
            if self._session_open:
                try:
                    self.dev.disconnect()
                except Exception:
                    log.exception("Error closing failed session")
                self._session_open = False
            self.status.showMessage(translate("Offline: {error}").format(error=e), 6000)
            self._load_library()

    def _refresh_names(self):
        self.user_names = self.dev.user_preset_names()
        self.factory_names = self.dev.factory_preset_names()
        self._on_tab(self.tabs.currentIndex())

    def _load_library(self):
        path = data_path("nexus_factory_presets.json")
        if path.exists():
            self.library_presets = json.loads(path.read_text())
        self._on_tab(2)

    def _on_tab(self, i):
        self.list.clear()
        if i == 0:
            names = getattr(self, "user_names", [])
            for n, name in enumerate(names):
                self.list.addItem(f"{n+1:2d}. {name or translate('— vacío —')}")
        elif i == 1:
            names = getattr(self, "factory_names", [])
            for n, name in enumerate(names):
                self.list.addItem(f"{n+1:2d}. {name or translate('— vacío —')}")
        else:
            for p in self.library_presets:
                name = p.get("name") or "—"
                art = p.get("artist") or ""
                self.list.addItem(f"{name}  ·  {art}" if art else name)

    def _on_select(self, item):
        i = self.list.row(item)
        tab = self.tabs.currentIndex()
        try:
            if tab == 0:
                self.dev.load_user_preset(i)
            elif tab == 1:
                self.dev.load_factory_preset(i)
            else:
                if 0 <= i < len(self.library_presets):
                    from ..model import Preset
                    p = Preset.from_json(self.library_presets[i]["data"])
                    self.dev.send_preset(p)
            self._reload()
        except Exception as e:
            self.status.showMessage(translate("Error: {error}").format(error=e), 5000)

    def _reload(self):
        try:
            if hasattr(self, "worker"):
                self.worker.invalidate()
            p = self.dev.get_active_preset()
            self._display_preset(p)
        except Exception as e:
            self.status.showMessage(translate("Error reload: {error}").format(error=e), 5000)

    def _display_preset(self, p):
        self.preset = p
        self.preset_name.setText(p.name)
        self._display_level(p.prs_levl)
        amp_slot = next((s for s in p.slots.values() if s.category == "amp"), None)
        self.amp_block.set_amp_slot(amp_slot)
        eq_slot = next((s for s in p.slots.values() if s.category == "eq"), None)
        self.amp_block.amp_view.eq_display.set_slot(eq_slot)
        self.pedalboard.rebuild(p.slots, self.db)
        self.control_panel.set_effect_slots(p.slots)
        lfo = p.ctrls.get("lfo1")
        if lfo is not None and lfo.speed is not None:
            blocked = self.control_panel.lfo_speed.blockSignals(True)
            self.control_panel.lfo_speed.setValue(lfo.speed)
            self.control_panel.lfo_speed.blockSignals(blocked)
        wah = next((s for s in p.slots.values() if s.category == "wah"), None)
        if wah:
            for name in ("WAH LEVL", "PEDAL"):
                if name in wah.params:
                    self._display_wah_param(name, wah.params[name])
        self.status.showMessage(translate("Preset: {name}").format(name=p.name))

    def _display_level(self, value):
        blocked = self.level_slider.blockSignals(True)
        self.level_slider.setValue(value)
        self.level_slider.blockSignals(blocked)
        self.level_value.setText(str(value))

    def _apply_slot_value(self, slot, name, value):
        s = self.preset.slots[slot]
        if name == "ENABLE":
            s.enable = None if value is None else bool(value)
            if s.category == "eq":
                self.amp_block.amp_view.eq_display.update()
            if s.category == "amp":
                self.amp_block.amp_view.update()
            elif slot in self.pedalboard.pedals:
                self.pedalboard.pedals[slot].update()
            return
        s.params[name] = value
        if s.category == "eq":
            self.amp_block.amp_view.eq_display.update()
        if s.category == "wah" and name in ("WAH LEVL", "PEDAL"):
            self._display_wah_param(name, value)
        if s.category == "amp":
            self.amp_block.update_param(name, value)
        else:
            pedal = self.pedalboard.pedals.get(slot)
            if pedal:
                pedal.update_param(name, value)

    def _display_wah_param(self, name, value):
        widget = (self.control_panel.wah_level_spin if name == "WAH LEVL"
                  else self.control_panel.pedal_spin)
        blocked = widget.blockSignals(True)
        widget.setValue(int(value))
        widget.blockSignals(blocked)

    def _set_wah_param(self, name, value):
        preset = getattr(self, "preset", None)
        if preset is not None:
            wah = next((s for s in preset.slots.values() if s.category == "wah"), None)
            if wah is not None:
                self._set_param(wah.slot, name, value)

    def _apply_snapshot(self, p):
        old = getattr(self, "preset", None)
        if (old is None or old.chain_order != p.chain_order
                or old.ctrls != p.ctrls or old.slots.keys() != p.slots.keys()
                or any(old.slots[i].model != s.model
                       or old.slots[i]._use_fx_subdict != s._use_fx_subdict
                       or old.slots[i].params.keys() != s.params.keys()
                       for i, s in p.slots.items())):
            self._display_preset(p)
            return
        self.preset_name.setText(p.name)
        old.name = p.name
        old.factmodify = p.factmodify
        old.prs_levl = p.prs_levl
        self._display_level(p.prs_levl)
        for i, slot in p.slots.items():
            if old.slots[i].enable != slot.enable:
                self._apply_slot_value(i, "ENABLE", slot.enable)
            for name, value in slot.params.items():
                if old.slots[i].params[name] != value:
                    self._apply_slot_value(i, name, value)

    def _request_sync(self):
        if not self._connected:
            return
        if self._sync_busy:
            self._sync_requested = True
            return
        self._sync_busy = True
        self._sync_requested = False
        self.worker.read_preset()

    def _on_snapshot(self, preset, revision):
        self._sync_busy = False
        if not self._connected:
            return
        watermark = None if preset is None else self.worker.merge_snapshot(preset, revision)
        if watermark is not None:
            self._apply_snapshot(preset)
            self._snapshot_watermark = watermark
        else:
            self._sync_requested = True
        if self._sync_requested:
            self._sync_timer.start()

    def _on_sync_error(self, error):
        self._sync_busy = False
        self._sync_requested = False
        if self._connected:
            self.status.showMessage(
                translate("Error sync: {error}").format(error=error), 5000)

    def _on_disconnect(self, error):
        self._connected = False
        self._poll_timer.stop()
        self._sync_timer.stop()
        self.status.showMessage(translate("Desconectado: {error}").format(error=error))

    def _filter(self, text):
        for i in range(self.list.count()):
            item = self.list.item(i)
            if item is None:
                log.warning("Missing preset list item at index %d", i)
                continue
            item.setHidden(text.lower() not in item.text().lower())

    def _preset_context_menu(self, pos):
        if self.tabs.currentIndex() != 0:
            return
        item = self.list.itemAt(pos)
        if item is None:
            return
        index = self.list.row(item)
        if index >= len(getattr(self, "user_names", [])) or not self.user_names[index]:
            return
        self.list.setCurrentItem(item)
        menu = QMenu(self)
        menu.addAction(translate("Copy"), lambda: self._copy_user_preset(index))
        menu.addAction(translate("Delete..."), lambda: self._delete_user_preset_at(index))
        viewport = self.list.viewport()
        if viewport is None:
            raise RuntimeError("Preset list viewport is unavailable")
        menu.exec_(viewport.mapToGlobal(pos))

    # ------------------------------------------------------------- actions
    def _build_menubar(self):
        mb = self.menuBar()
        if mb is None:
            raise RuntimeError("Main window menu bar is unavailable")
        mb.setStyleSheet("QMenuBar{background:#121212;color:#ddd;} QMenuBar::item:selected{background:#2a2a2a;}")
        f = mb.addMenu(translate("Archivo"))
        if f is None:
            raise RuntimeError("Could not create file menu")
        f.addAction(translate("Backup..."), self._backup)
        f.addAction(translate("Restore..."), self._restore)
        f.addSeparator()
        f.addAction(translate("Importar preset..."), self._import_preset)
        f.addAction(translate("Exportar preset..."), self._export_preset)
        p = mb.addMenu(translate("Preset"))
        if p is None:
            raise RuntimeError("Could not create preset menu")
        p.addAction(translate("Store New..."), self._store_new)
        p.addAction(translate("Quick Store"), self._quick_store)
        p.addAction(translate("Delete User Preset..."), self._delete_user_preset)
        p.addAction(translate("Copy"), self._copy)

    def _change_model(self, slot):
        from .effect_picker import EffectPicker
        s = self.preset.slots.get(slot)
        if not s:
            return
        cat_map = {"wah": "Wah", "cmpr": "Compressor", "dist": "Distortion", "amp": "Amplifier",
                   "gate": "Gate", "mod": "Mod", "dly": "Delay", "rvb": "Reverb",
                   "eq": "EQ", "vol": "Other"}
        title = translate("Selección de amplificador" if s.category == "amp"
                          else "Seleccionar efecto")
        picker = EffectPicker(self.db, current_category=cat_map.get(s.category), parent=self, title=title)
        if picker.exec_() and picker.result_effect:
            model = self.db.model_id(picker.result_effect["address"])
            if model:
                try:
                    self.dev.set_model(slot, model)
                    self._reload()
                except Exception as e:
                    self.status.showMessage(
                        translate("Error: {error}").format(error=e), 5000)

    # ------------------------------------------------------- controllers
    def _assign_stomp(self, ctrl, slot):
        try:
            if slot < 0:
                self.dev.clear_stomp(ctrl)
                self.status.showMessage(translate("{ctrl} unassigned").format(ctrl=ctrl))
            else:
                self.dev.assign_stomp(ctrl, slot)
                self.status.showMessage(
                    translate("{ctrl} → slot {slot}").format(ctrl=ctrl, slot=slot + 1))
            self._reload()
        except Exception as e:
            self.status.showMessage(
                translate("Error stomp: {error}").format(error=e), 5000)

    def _assign_expression(self, ctrl, slot, param, minv, maxv):
        try:
            s = self.preset.slots.get(slot)
            flat = s is not None and not getattr(s, "_use_fx_subdict", True)
            self.dev.assign_expression(ctrl, slot, param, minv, maxv, flat=flat)
            self.status.showMessage(
                translate("{ctrl} → slot {slot} {param}").format(
                    ctrl=ctrl, slot=slot + 1, param=param))
            self._reload()
        except Exception as e:
            self.status.showMessage(
                translate("Error expr: {error}").format(error=e), 5000)

    def _assign_lfo(self, slot, param, minv, maxv, speed, wave):
        try:
            beats = self.control_panel.tempo.lfo.currentData()
            if beats is not None:
                speed = lfo_speed(self.control_panel.tempo.bpm.value(), beats)
            s = self.preset.slots.get(slot)
            flat = s is not None and not getattr(s, "_use_fx_subdict", True)
            self.dev.assign_lfo(slot, param, minv, maxv, speed, wave, flat=flat)
            self.status.showMessage(
                translate("LFO → slot {slot} {param}").format(
                    slot=slot + 1, param=param))
            self._reload()
        except Exception as e:
            self.status.showMessage(
                translate("Error lfo: {error}").format(error=e), 5000)

    def _sync_tempo(self):
        tempo = self.control_panel.tempo
        preset = getattr(self, "preset", None)
        if tempo.delay.currentData() is None and tempo.lfo.currentData() is None:
            return
        if not self._connected or preset is None:
            self.status.showMessage(translate("Tempo: conecta el pedal y carga un preset"), 5000)
            return
        errors = []
        beats = tempo.delay.currentData()
        if beats is not None:
            delay = next((s for s in preset.slots.values() if s.category == "dly"), None)
            if delay is None or "TIME" not in delay.params:
                errors.append(translate("Delay sin parámetro TIME compatible"))
            else:
                value = delay_ms(tempo.bpm.value(), beats)
                try:
                    low, high = self.db.param_range(delay.model.split(".", 1)[-1], "TIME")
                    if not low <= value <= high:
                        errors.append(translate(
                            "Delay: {value} ms fuera del rango {low}–{high} ms"
                        ).format(value=value, low=low, high=high))
                    elif value != delay.params["TIME"]:
                        self._set_param(delay.slot, "TIME", value)
                except KeyError:
                    errors.append(translate("Rango de delay desconocido"))
        beats = tempo.lfo.currentData()
        if beats is not None:
            try:
                speed = lfo_speed(tempo.bpm.value(), beats)
            except ValueError as exc:
                errors.append(str(exc))
            else:
                ctrl = preset.ctrls.get("lfo1")
                if ctrl is None or not ctrl.lnk:
                    errors.append(translate("LFO sin asignar"))
                elif ctrl.speed != speed:
                    try:
                        if hasattr(self, "worker"):
                            self.worker.invalidate()
                        self.dev.set_ctrl_field("lfo1", "SPEED", speed)
                        if hasattr(self, "worker"):
                            self.worker.invalidate()
                        ctrl.speed = speed
                        blocked = self.control_panel.lfo_speed.blockSignals(True)
                        self.control_panel.lfo_speed.setValue(speed)
                        self.control_panel.lfo_speed.blockSignals(blocked)
                    except Exception as exc:
                        if hasattr(self, "worker"):
                            self.worker.invalidate()
                        log.exception("Could not synchronize LFO speed")
                        errors.append(translate("Error LFO: {error}").format(error=exc))
                        self._sync_timer.start()
        if errors:
            self.status.showMessage("; ".join(errors), 6000)

    # ------------------------------------------------------ file operations
    def _backup(self):
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, translate("Backup 99 presets"), "rp360_backup.json", "JSON (*.json)")
        if not path:
            return
        try:
            presets = self.dev.export_user_bank()
            data = {"user": [p.to_json() if p else None for p in presets]}
            import json as _json
            Path(path).write_text(_json.dumps(data, indent=2))
            self.status.showMessage(translate("Backup → {path}").format(path=path))
        except Exception as e:
            self.status.showMessage(
                translate("Error backup: {error}").format(error=e), 5000)

    def _restore(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        path, _ = QFileDialog.getOpenFileName(
            self, translate("Restaurar 99 presets"), "", "JSON (*.json)")
        if not path:
            return
        if QMessageBox.question(
                self, translate("Restore"),
                translate("Los presets del dispositivo serán sobrescritos. ¿Continuar?")) \
                != QMessageBox.Yes:
            return
        try:
            import json as _json
            from ..model import Preset
            data = _json.loads(Path(path).read_text())
            presets = [Preset.from_json(d) if d else None for d in data["user"]]
            n = self.dev.restore_user_bank(presets)
            self.status.showMessage(
                translate("Restaurados {count} presets").format(count=n))
        except Exception as e:
            self.status.showMessage(
                translate("Error restore: {error}").format(error=e), 5000)

    def _import_preset(self):
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, translate("Importar preset..."), "", "RP360 Preset (*.rp360p);;JSON (*.json)")
        if not path:
            return
        try:
            import json as _json
            from ..model import Preset
            d = _json.loads(Path(path).read_text())
            preset = Preset.from_json(d.get("preset", d))
            self.dev.send_preset(preset)
            self._reload()
            self.status.showMessage(
                translate("Importado: {name}").format(name=preset.name))
        except Exception as e:
            self.status.showMessage(
                translate("Error import: {error}").format(error=e), 5000)

    def _export_preset(self):
        from PyQt5.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, translate("Exportar preset..."), f"{self.preset.name}.rp360p",
            "RP360 Preset (*.rp360p)")
        if not path:
            return
        try:
            import json as _json
            Path(path).write_text(_json.dumps({"preset": self.preset.to_json()}, indent=2))
            self.status.showMessage(translate("Exported → {path}").format(path=path))
        except Exception as e:
            self.status.showMessage(
                translate("Error export: {error}").format(error=e), 5000)

    def _store_new(self):
        from PyQt5.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(
            self, translate("Store New"), translate("Nombre del preset:"),
            text=self.preset.name)
        if not ok:
            return
        idx, ok = QInputDialog.getInt(
            self, translate("Store New"), translate("Slot (1-99):"), 1, 1, 99)
        if not ok:
            return
        try:
            self.dev.save_and_rename(idx - 1, name)
            self._refresh_names()
            self.status.showMessage(
                translate("Guardado en User {slot}").format(slot=idx))
        except Exception as e:
            self.status.showMessage(
                translate("Error: {error}").format(error=e), 5000)

    def _quick_store(self):
        try:
            i = self.browser.list.currentRow()
            if self.tabs.currentIndex() != 0 or i < 0:
                self.status.showMessage(translate("Selecciona un slot de User"), 3000)
                return
            self.dev.save_to_user_slot(i)
            self.status.showMessage(
                translate("Quick store en User {slot}").format(slot=i + 1))
        except Exception as e:
            self.status.showMessage(
                translate("Error: {error}").format(error=e), 5000)

    def _delete_user_preset(self):
        from PyQt5.QtWidgets import QInputDialog

        default_slot = 1
        if self.tabs.currentIndex() == 0:
            selected = self.list.currentRow()
            if selected >= 0:
                default_slot = selected + 1

        slot, ok = QInputDialog.getInt(
            self, translate("Delete User Preset"), translate("Slot (1-99):"),
            default_slot, 1, 99
        )
        if not ok:
            return
        self._delete_user_preset_at(slot - 1)

    def _delete_user_preset_at(self, index):
        slot = index + 1
        name = ""
        if 0 <= index < len(getattr(self, "user_names", [])):
            name = self.user_names[index] or ""
        label = translate('User {slot} ("{name}")').format(slot=slot, name=name) \
            if name else translate("User {slot}").format(slot=slot)

        reply = QMessageBox.question(
            self,
            translate("Delete User Preset"),
            translate(
                "Reemplazar {label} por «Preset {slot}» con el amplificador y gabinete "
                "predeterminados, sin otros efectos? La posición no quedará vacía. "
                "El preset cargado en el editor no cambiará. Esta operación no se puede deshacer."
            ).format(label=label, slot=slot),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            replacement = self.db.build_reset_preset(f"Preset {slot}")
            self.dev.write_user_preset(index, replacement)
        except Exception as e:
            self.status.showMessage(
                translate("Error al eliminar: {error}").format(error=e), 5000)
            return

        try:
            saved = self.dev.get_user_preset(index)
            expected_amp = next(iter(replacement.slots.values()))
            if (len(saved.slots) != 1
                    or (amp := next(iter(saved.slots.values()))).model != expected_amp.model
                    or any(amp.params.get(k) != v for k, v in expected_amp.params.items())
                    or not amp.enable
                    or any(ctrl.lnk for ctrl in saved.ctrls.values())
                    or saved.name != replacement.name
                    or saved.prs_levl != replacement.prs_levl):
                raise ValueError(translate("el dispositivo no devolvió el preset predeterminado"))
        except Exception as e:
            self.status.showMessage(
                translate("Preset User {slot}: escritura enviada; error al verificar: {error}")
                .format(slot=slot, error=e), 8000)
            return

        try:
            names = list(getattr(self, "user_names", []))
            if index >= len(names):
                names.extend([None] * (index + 1 - len(names)))
            names[index] = saved.name
            self.user_names = names
            if self.tabs.currentIndex() == 0:
                item = self.list.item(index)
                if item is None:
                    self._on_tab(0)
                else:
                    item.setText(f"{index+1:2d}. {saved.name or translate('— vacío —')}")
                self._filter(self.search.text())
        except Exception as e:
            self.status.showMessage(
                translate("Preset User {slot} restablecido; error al actualizar: {error}")
                .format(slot=slot, error=e), 8000)
            return
        self.status.showMessage(
            translate("Preset User {slot} restablecido").format(slot=slot))

    def _copy_user_preset(self, index):
        try:
            preset = self.dev.get_user_preset(index)
            self._copy_preset(preset)
        except Exception as e:
            self.status.showMessage(
                translate("Error al copiar: {error}").format(error=e), 5000)

    def _copy_preset(self, preset):
        self._clipboard = json.dumps({"preset": preset.to_json()})
        self.status.showMessage(translate("Preset copiado al portapapeles interno"))

    def _copy(self):
        self._copy_preset(self.preset)

    def _store(self):
        i = self.list.currentRow()
        if self.tabs.currentIndex() == 0 and i >= 0:
            try:
                self.dev.save_and_rename(i, self.preset.name)
                self.status.showMessage(
                    translate("Guardado en User {slot}").format(slot=i + 1))
            except Exception as e:
                self.status.showMessage(
                    translate("Error: {error}").format(error=e), 5000)

    def _set_param(self, slot, param, value):
        try:
            flat = False
            s = self.preset.slots.get(slot)
            if s is not None and not getattr(s, "_use_fx_subdict", True):
                flat = True
            path = f"preset/fxc/{slot}/{param}" if flat else f"preset/fxc/{slot}/fx/{param}"
            if hasattr(self, "worker"):
                self.worker.record_change(path, value)
            self.dev.set_param(slot, param, value, flat=flat)
            if hasattr(self, "worker"):
                self.worker.record_change(path, value)
            if s is not None:
                self._apply_slot_value(slot, param, value)
        except Exception as e:
            if hasattr(self, "worker"):
                self.worker.invalidate()
            self.status.showMessage(
                translate("Error: {error}").format(error=e), 3000)
            self._sync_timer.start()

    def _set_enable(self, slot, enabled):
        try:
            path = f"preset/fxc/{slot}/ENABLE"
            self.worker.record_change(path, int(enabled))
            self.dev.set_enable(slot, enabled)
            self.worker.record_change(path, int(enabled))
            self._apply_slot_value(slot, "ENABLE", enabled)
        except Exception as e:
            self.worker.invalidate()
            self.status.showMessage(
                translate("Error: {error}").format(error=e), 3000)
            self._sync_timer.start()

    def _set_amp_bypass(self, slot, bypass):
        self._set_enable(slot, not bypass)

    def _set_preset_level(self, value):
        self.level_value.setText(str(value))
        try:
            if hasattr(self, "worker"):
                self.worker.record_change("preset/PRS LEVL", value)
            self.dev.set_preset_level(value)
            if hasattr(self, "worker"):
                self.worker.record_change("preset/PRS LEVL", value)
            if hasattr(self, "preset"):
                self.preset.prs_levl = value
        except Exception as e:
            if hasattr(self, "worker"):
                self.worker.invalidate()
            self.status.showMessage(
                translate("Error level: {error}").format(error=e), 3000)
            self._sync_timer.start()

    def _set_cabinet(self, slot, cab_idx):
        try:
            self.dev.set_param(slot, "CABINET", cab_idx)
            self._reload()
        except Exception as e:
            self.status.showMessage(
                translate("Error cabinet: {error}").format(error=e), 3000)

    def _delete_slot(self, slot):
        try:
            self.dev.delete_effect(slot)
            self._reload()
        except Exception as e:
            self.status.showMessage(
                translate("Error: {error}").format(error=e), 3000)

    def _reorder(self, src, target):
        """Reorder the chain: move the effect at slot `src` to position `target`."""
        try:
            occupied = reordered_slots(self.preset.slots, src, target)
            if occupied == sorted(self.preset.slots):
                return
            self.dev.reorder_chain(occupied)
            self._reload()
        except Exception as e:
            self.status.showMessage(
                translate("Error al reordenar: {error}").format(error=e), 5000)

    def _add_effect(self):
        from .effect_picker import EffectPicker
        from ..effects_db import SLOT_CATEGORY, natural_positions
        if not hasattr(self, "preset"):
            self.status.showMessage(translate("No hay preset cargado"), 5000)
            return
        # category already present -> cannot add another of that category
        prefix_to_cat = {"wah": "Wah", "cmpr": "Compressor", "dist": "Distortion",
                         "amp": "Amplifier", "eq": "EQ", "gate": "Gate",
                         "vol": "Other", "mod": "Mod", "dly": "Delay", "rvb": "Reverb"}
        used_categories = {prefix_to_cat.get(s.category, s.category)
                           for s in self.preset.slots.values()}
        allowed = [c for c in SLOT_CATEGORY.values() if c not in used_categories]
        if not allowed:
            self.status.showMessage(
                translate("Cadena completa: todas las categorías están en uso"), 5000)
            return
        picker = EffectPicker(self.db, parent=self, allowed_categories=allowed)
        if not (picker.exec_() and picker.result_effect):
            return
        effect = picker.result_effect
        # place at natural (or flexible) position that is still free
        target = None
        for idx in natural_positions(effect["category"]):
            if idx not in self.preset.slots:
                target = idx
                break
        if target is None:
            target = next((i for i in range(10) if i not in self.preset.slots), None)
        if target is None:
            self.status.showMessage(translate("No hay posición libre en la cadena"), 5000)
            return
        try:
            slot_data = self.db.build_slot_data(effect["address"])
            self.dev.add_effect(target, slot_data)
            self._reload()
        except Exception as e:
            self.status.showMessage(
                translate("Error: {error}").format(error=e), 5000)

    def _on_notif(self, msg, revision=None):
        if not self._connected or not msg:
            return
        if revision is not None and revision <= self._snapshot_watermark:
            return
        if msg[0] != "np":
            if msg[0] in ("cm", "ndc", "nsc", "nac"):
                self._sync_timer.start()
            return
        if len(msg) < 4 or not isinstance(msg[2], str):
            log.warning("Malformed property notification: %r", msg)
            self._sync_timer.start()
            return
        path, value = msg[2], msg[3]
        if not hasattr(self, "preset"):
            self._sync_timer.start()
            return
        if path == "preset/name" and isinstance(value, str):
            self.preset.name = value
            self.preset_name.setText(value)
        elif path == "preset/PRS LEVL" and isinstance(value, int):
            self.preset.prs_levl = value
            self._display_level(value)
        elif path.startswith("preset/fxc/"):
            parts = path.split("/")
            if len(parts) in (4, 5) and parts[2].isdigit():
                slot = self.preset.slots.get(int(parts[2]))
                if slot is not None:
                    name = parts[-1]
                    is_param = (len(parts) == 5 and parts[3] == "fx"
                                and slot._use_fx_subdict
                                or len(parts) == 4 and not slot._use_fx_subdict)
                    if (len(parts) == 4 and name == "ENABLE"
                            and isinstance(value, (int, bool))):
                        self._apply_slot_value(slot.slot, name, value)
                        return
                    if is_param and name in slot.params and isinstance(value, int):
                        self._apply_slot_value(slot.slot, name, value)
                        return
            self._sync_timer.start()
        elif path == "preset" or path.startswith("preset/") or path == "system/LAST PRES":
            self._sync_timer.start()

    def closeEvent(self, a0):
        self._connected = False
        self._poll_timer.stop()
        self._sync_timer.stop()
        if hasattr(self, "worker"):
            self.worker.stop()
        try:
            if self._session_open:
                self.dev.disconnect()
        except Exception:
            log.exception("Error disconnecting device")
        if a0 is not None:
            a0.accept()