"""
Settings panel GUI for CrosshairX.
Minimalist, dark-themed, bilingual (RU/EN) settings window.
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QBrush
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox,
    QPushButton, QGroupBox, QCheckBox, QColorDialog, QSpinBox,
    QTabWidget, QGridLayout, QMessageBox, QInputDialog
)

from .i18n import t, set_language, get_language

# ── Compact dark stylesheet ──
DARK_STYLE = """
QWidget {
    background-color: #111120;
    color: #d0d0d0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
}
QGroupBox {
    border: 1px solid #1e1e3a;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 14px;
    font-weight: bold;
    color: #00c8ff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
QPushButton {
    background-color: #1a1a35;
    border: 1px solid #2a2a50;
    border-radius: 5px;
    padding: 5px 12px;
    color: #d0d0d0;
}
QPushButton:hover {
    background-color: #25254a;
    border-color: #00c8ff;
}
QPushButton:pressed {
    background-color: #3a1a6a;
}
QPushButton#colorBtn {
    border: 2px solid #00c8ff;
    border-radius: 12px;
    min-width: 24px; min-height: 24px;
}
QSlider::groove:horizontal {
    height: 4px;
    background: #1a1a35;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #00c8ff;
    width: 14px; height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: #1a3a60;
    border-radius: 2px;
}
QComboBox {
    background-color: #1a1a35;
    border: 1px solid #2a2a50;
    border-radius: 5px;
    padding: 3px 6px;
    color: #d0d0d0;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: #1a1a35;
    color: #d0d0d0;
    selection-background-color: #25254a;
}
QSpinBox {
    background-color: #1a1a35;
    border: 1px solid #2a2a50;
    border-radius: 4px;
    padding: 2px 4px;
    color: #d0d0d0;
}
QCheckBox::indicator {
    width: 14px; height: 14px;
    border-radius: 3px;
    border: 1px solid #2a2a50;
    background: #1a1a35;
}
QCheckBox::indicator:checked {
    background: #00c8ff;
    border-color: #00c8ff;
}
QTabWidget::pane {
    border: 1px solid #1e1e3a;
    border-radius: 6px;
    background: #111120;
}
QTabBar::tab {
    background: #1a1a35;
    color: #d0d0d0;
    padding: 6px 14px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    margin-right: 1px;
}
QTabBar::tab:selected {
    background: #25254a;
    color: #00c8ff;
}
QTabBar::tab:hover {
    background: #25254a;
}
"""


class CrosshairPreview(QWidget):
    """Compact live preview of the crosshair."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 160)
        self._config = {}
        self._renderer = None

    def set_renderer(self, renderer):
        self._renderer = renderer

    def set_config(self, config: dict):
        self._config = config
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(20, 20, 35))
        # Subtle grid
        pen = QPen(QColor(35, 35, 55), 1)
        p.setPen(pen)
        for i in range(0, 160, 20):
            p.drawLine(i, 0, i, 160)
            p.drawLine(0, i, 160, i)
        if self._renderer and self._config:
            self._renderer.draw(p, 80, 80, self._config)
        p.end()


class SettingsPanel(QWidget):
    """Minimalist settings panel with RU/EN language support."""

    config_changed = pyqtSignal()
    profile_changed = pyqtSignal(str)
    close_app = pyqtSignal()

    # Style keys (display names come from i18n)
    STYLE_KEYS = ["cross", "dot", "circle", "chevron", "diamond", "crossdot",
                  "triangle", "crosshair_classic", "square", "plus_thin", "crosscircle", "arrows"]
    ANIM_KEYS = ["none", "pulse", "rotate", "breathe", "rainbow", "recoil", "flash", "wave"]

    def __init__(self, config, overlay, parent=None):
        super().__init__(parent)
        self.config = config
        self.overlay = overlay
        self._color = QColor(*config.get("crosshair.color", [0, 255, 0, 255]))
        self._outline_color = QColor(*config.get("crosshair.outline_color", [0, 0, 0, 180]))

        # Set language from config
        lang = config.get("general.language", "ru")
        set_language(lang)

        self.setWindowTitle(t("app.title"))
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.setFixedSize(480, 600)
        self.setStyleSheet(DARK_STYLE)

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(10, 10, 10, 10)
        self._main_layout.setSpacing(6)
        self._build_ui()
        self._load_from_config()

    def _build_ui(self):
        """Build entire UI (called on init and on language switch)."""
        # Clear existing widgets
        while self._main_layout.count():
            item = self._main_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        lay = self._main_layout

        # ── Header row: title + language switch ──
        header_row = QHBoxLayout()
        hdr = QLabel(t("app.title"))
        hdr.setFont(QFont("Segoe UI", 16, QFont.Bold))
        hdr.setStyleSheet("color: #00c8ff;")
        header_row.addWidget(hdr)
        header_row.addStretch()

        self.combo_lang = QComboBox()
        self.combo_lang.addItem("Русский", "ru")
        self.combo_lang.addItem("English", "en")
        idx = self.combo_lang.findData(get_language())
        if idx >= 0:
            self.combo_lang.setCurrentIndex(idx)
        self.combo_lang.currentIndexChanged.connect(self._on_lang_changed)
        self.combo_lang.setFixedWidth(90)
        header_row.addWidget(self.combo_lang)

        header_w = QWidget()
        header_w.setLayout(header_row)
        lay.addWidget(header_w)

        sub = QLabel(t("app.subtitle"))
        sub.setStyleSheet("color: #666; font-size: 10px;")
        sub.setAlignment(Qt.AlignCenter)
        lay.addWidget(sub)

        # ── Tabs ──
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_crosshair_tab(), t("tab.crosshair"))
        self.tabs.addTab(self._build_animation_tab(), t("tab.animation"))
        self.tabs.addTab(self._build_display_tab(), t("tab.display"))
        self.tabs.addTab(self._build_profiles_tab(), t("tab.profiles"))
        lay.addWidget(self.tabs)

        # ── Bottom buttons ──
        btn_row = QHBoxLayout()
        self.btn_apply = QPushButton(t("btn.apply"))
        self.btn_apply.clicked.connect(self._apply_settings)
        btn_row.addWidget(self.btn_apply)

        self.btn_reset = QPushButton(t("btn.reset"))
        self.btn_reset.clicked.connect(self._reset_defaults)
        btn_row.addWidget(self.btn_reset)

        self.btn_hide = QPushButton(t("btn.show"))  # Starts as Show since overlay is hidden
        self.btn_hide.clicked.connect(self._toggle_overlay)
        btn_row.addWidget(self.btn_hide)

        self.btn_quit = QPushButton(t("btn.quit"))
        self.btn_quit.setStyleSheet(
            "QPushButton { background-color: #3a1020; border-color: #802040; color: #ff4060; }"
            "QPushButton:hover { background-color: #501030; border-color: #ff4060; }"
        )
        self.btn_quit.clicked.connect(self._quit_app)
        btn_row.addWidget(self.btn_quit)

        btn_w = QWidget()
        btn_w.setLayout(btn_row)
        lay.addWidget(btn_w)

    # ── Tab builders ──

    def _build_crosshair_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(6)

        top = QHBoxLayout()

        # Preview
        pg = QGroupBox(t("xhair.preview"))
        pl = QVBoxLayout(pg)
        self.preview = CrosshairPreview()
        from .crosshair import CrosshairRenderer
        self._preview_renderer = CrosshairRenderer()
        self.preview.set_renderer(self._preview_renderer)
        pl.addWidget(self.preview)
        top.addWidget(pg)

        # Style + color
        sg = QGroupBox(t("xhair.style"))
        sl = QVBoxLayout(sg)

        self.combo_style = QComboBox()
        for key in self.STYLE_KEYS:
            self.combo_style.addItem(t(f"style.{key}"), key)
        self.combo_style.currentIndexChanged.connect(self._on_param_changed)
        sl.addWidget(self.combo_style)

        cr = QHBoxLayout()
        cr.addWidget(QLabel(t("xhair.color")))
        self.btn_color = QPushButton()
        self.btn_color.setObjectName("colorBtn")
        self.btn_color.setFixedSize(28, 28)
        self.btn_color.clicked.connect(self._pick_color)
        self._update_color_button()
        cr.addWidget(self.btn_color)
        cr.addStretch()
        sl.addLayout(cr)

        self.chk_t_style = QCheckBox(t("xhair.t_style"))
        self.chk_t_style.stateChanged.connect(self._on_param_changed)
        sl.addWidget(self.chk_t_style)
        sl.addStretch()
        top.addWidget(sg)

        lay.addLayout(top)

        # Parameters
        pg2 = QGroupBox(t("xhair.params"))
        g = QGridLayout(pg2)

        g.addWidget(QLabel(t("xhair.size")), 0, 0)
        self.slider_size = QSlider(Qt.Horizontal)
        self.slider_size.setRange(4, 100)
        self.slider_size.valueChanged.connect(self._on_param_changed)
        g.addWidget(self.slider_size, 0, 1)
        self.lbl_size = QLabel("20")
        self.lbl_size.setMinimumWidth(26)
        g.addWidget(self.lbl_size, 0, 2)

        g.addWidget(QLabel(t("xhair.thickness")), 1, 0)
        self.slider_thickness = QSlider(Qt.Horizontal)
        self.slider_thickness.setRange(1, 10)
        self.slider_thickness.valueChanged.connect(self._on_param_changed)
        g.addWidget(self.slider_thickness, 1, 1)
        self.lbl_thickness = QLabel("2")
        self.lbl_thickness.setMinimumWidth(26)
        g.addWidget(self.lbl_thickness, 1, 2)

        g.addWidget(QLabel(t("xhair.gap")), 2, 0)
        self.slider_gap = QSlider(Qt.Horizontal)
        self.slider_gap.setRange(0, 30)
        self.slider_gap.valueChanged.connect(self._on_param_changed)
        g.addWidget(self.slider_gap, 2, 1)
        self.lbl_gap = QLabel("4")
        self.lbl_gap.setMinimumWidth(26)
        g.addWidget(self.lbl_gap, 2, 2)

        dr = QHBoxLayout()
        self.chk_dot = QCheckBox(t("xhair.dot"))
        self.chk_dot.stateChanged.connect(self._on_param_changed)
        dr.addWidget(self.chk_dot)
        dr.addWidget(QLabel(t("xhair.dot_size")))
        self.spin_dot_size = QSpinBox()
        self.spin_dot_size.setRange(1, 10)
        self.spin_dot_size.valueChanged.connect(self._on_param_changed)
        dr.addWidget(self.spin_dot_size)
        g.addLayout(dr, 3, 0, 1, 3)

        olr = QHBoxLayout()
        self.chk_outline = QCheckBox(t("xhair.outline"))
        self.chk_outline.stateChanged.connect(self._on_param_changed)
        olr.addWidget(self.chk_outline)
        olr.addWidget(QLabel(t("xhair.outline_thick")))
        self.spin_outline = QSpinBox()
        self.spin_outline.setRange(1, 5)
        self.spin_outline.valueChanged.connect(self._on_param_changed)
        olr.addWidget(self.spin_outline)
        g.addLayout(olr, 4, 0, 1, 3)

        lay.addWidget(pg2)
        return w

    def _build_animation_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)

        grp = QGroupBox(t("anim.settings"))
        g = QGridLayout(grp)

        self.chk_anim = QCheckBox(t("anim.enable"))
        self.chk_anim.stateChanged.connect(self._on_param_changed)
        g.addWidget(self.chk_anim, 0, 0, 1, 3)

        g.addWidget(QLabel(t("anim.type")), 1, 0)
        self.combo_anim = QComboBox()
        for key in self.ANIM_KEYS:
            self.combo_anim.addItem(t(f"anim.{key}"), key)
        self.combo_anim.currentIndexChanged.connect(self._on_param_changed)
        g.addWidget(self.combo_anim, 1, 1, 1, 2)

        g.addWidget(QLabel(t("anim.speed")), 2, 0)
        self.slider_anim_speed = QSlider(Qt.Horizontal)
        self.slider_anim_speed.setRange(1, 50)
        self.slider_anim_speed.valueChanged.connect(self._on_param_changed)
        g.addWidget(self.slider_anim_speed, 2, 1)
        self.lbl_anim_speed = QLabel("1.0")
        g.addWidget(self.lbl_anim_speed, 2, 2)

        g.addWidget(QLabel(t("anim.intensity")), 3, 0)
        self.slider_anim_intensity = QSlider(Qt.Horizontal)
        self.slider_anim_intensity.setRange(0, 100)
        self.slider_anim_intensity.valueChanged.connect(self._on_param_changed)
        g.addWidget(self.slider_anim_intensity, 3, 1)
        self.lbl_anim_intensity = QLabel("30%")
        g.addWidget(self.lbl_anim_intensity, 3, 2)

        lay.addWidget(grp)

        # Descriptions
        desc_keys = ["pulse", "rotate", "breathe", "rainbow", "recoil", "flash", "wave"]
        for dk in desc_keys:
            lbl = QLabel(t(f"anim.desc.{dk}"))
            lbl.setStyleSheet("color: #888; font-size: 10px; padding: 0 8px;")
            lay.addWidget(lbl)

        lay.addStretch()
        return w

    def _build_display_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)

        grp = QGroupBox(t("disp.settings"))
        g = QGridLayout(grp)

        g.addWidget(QLabel(t("disp.monitor")), 0, 0)
        self.spin_monitor = QSpinBox()
        self.spin_monitor.setRange(0, 10)
        g.addWidget(self.spin_monitor, 0, 1)

        g.addWidget(QLabel(t("disp.offset_x")), 1, 0)
        self.spin_offset_x = QSpinBox()
        self.spin_offset_x.setRange(-500, 500)
        g.addWidget(self.spin_offset_x, 1, 1)

        g.addWidget(QLabel(t("disp.offset_y")), 2, 0)
        self.spin_offset_y = QSpinBox()
        self.spin_offset_y.setRange(-500, 500)
        g.addWidget(self.spin_offset_y, 2, 1)

        g.addWidget(QLabel(t("disp.opacity")), 3, 0)
        self.slider_opacity = QSlider(Qt.Horizontal)
        self.slider_opacity.setRange(10, 100)
        self.slider_opacity.valueChanged.connect(self._on_param_changed)
        g.addWidget(self.slider_opacity, 3, 1)
        self.lbl_opacity = QLabel("100%")
        g.addWidget(self.lbl_opacity, 3, 2)

        g.addWidget(QLabel(t("disp.fps")), 4, 0)
        self.spin_fps = QSpinBox()
        self.spin_fps.setRange(10, 144)
        g.addWidget(self.spin_fps, 4, 1)

        lay.addWidget(grp)

        # Hotkeys
        hk_grp = QGroupBox(t("disp.hotkeys"))
        hk_lay = QVBoxLayout(hk_grp)
        hk_data = [
            ("F6", t("hk.toggle")),
            ("F7", t("hk.next")),
            ("F8", t("hk.prev")),
            ("F9", t("hk.anim")),
            ("F10", t("hk.settings")),
        ]
        for key, desc in hk_data:
            row = QHBoxLayout()
            kl = QLabel(key)
            kl.setStyleSheet(
                "background: #1a3a60; padding: 3px 8px; border-radius: 3px;"
                "font-weight: bold; color: #00c8ff; min-width: 36px;"
            )
            kl.setAlignment(Qt.AlignCenter)
            row.addWidget(kl)
            row.addWidget(QLabel(f" — {desc}"))
            row.addStretch()
            hk_lay.addLayout(row)
        lay.addWidget(hk_grp)

        lay.addStretch()
        return w

    def _build_profiles_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)

        grp = QGroupBox(t("prof.title"))
        gl = QVBoxLayout(grp)

        sr = QHBoxLayout()
        sr.addWidget(QLabel(t("prof.profile")))
        self.combo_profile = QComboBox()
        self._refresh_profiles()
        sr.addWidget(self.combo_profile)
        gl.addLayout(sr)

        bg = QGridLayout()
        bl = QPushButton(t("prof.load"))
        bl.clicked.connect(self._load_profile)
        bg.addWidget(bl, 0, 0)
        bs = QPushButton(t("prof.save"))
        bs.clicked.connect(self._save_profile)
        bg.addWidget(bs, 0, 1)
        bd = QPushButton(t("prof.delete"))
        bd.clicked.connect(self._delete_profile)
        bg.addWidget(bd, 1, 0)
        br = QPushButton(t("prof.refresh"))
        br.clicked.connect(self._refresh_profiles)
        bg.addWidget(br, 1, 1)
        gl.addLayout(bg)
        lay.addWidget(grp)

        # Presets
        pg = QGroupBox(t("prof.presets"))
        pl = QVBoxLayout(pg)
        from .config import PRESET_PROFILES
        for key, profile in PRESET_PROFILES.items():
            btn = QPushButton(f"🎯 {profile['name']}")
            btn.clicked.connect(lambda checked, k=key: self._apply_preset(k))
            pl.addWidget(btn)
        lay.addWidget(pg)

        lay.addStretch()
        return w

    # ── Helpers ──

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            elif item.layout():
                SettingsPanel._clear_layout(item.layout())

    # ── Event handlers ──

    def _on_lang_changed(self, _=None):
        """Switch language and rebuild UI."""
        lang = self.combo_lang.currentData()
        set_language(lang)
        self.config.set("general.language", lang)
        self.config.save()
        self._build_ui()
        self._load_from_config()

    def _on_param_changed(self, _=None):
        """Update labels and preview on any parameter change."""
        self.lbl_size.setText(str(self.slider_size.value()))
        self.lbl_thickness.setText(str(self.slider_thickness.value()))
        self.lbl_gap.setText(str(self.slider_gap.value()))
        self.lbl_anim_speed.setText(f"{self.slider_anim_speed.value() / 10:.1f}")
        self.lbl_anim_intensity.setText(f"{self.slider_anim_intensity.value()}%")
        self.lbl_opacity.setText(f"{self.slider_opacity.value()}%")

        preview_config = {
            "style": self.combo_style.currentData(),
            "size": self.slider_size.value(),
            "thickness": self.slider_thickness.value(),
            "gap": self.slider_gap.value(),
            "color": [self._color.red(), self._color.green(), self._color.blue(), self._color.alpha()],
            "outline": self.chk_outline.isChecked(),
            "outline_color": [self._outline_color.red(), self._outline_color.green(),
                              self._outline_color.blue(), self._outline_color.alpha()],
            "outline_thickness": self.spin_outline.value(),
            "dot": self.chk_dot.isChecked(),
            "dot_size": self.spin_dot_size.value(),
            "t_style": self.chk_t_style.isChecked(),
        }
        self.preview.set_config(preview_config)

    def _pick_color(self):
        color = QColorDialog.getColor(
            self._color, self, t("xhair.pick_color"), QColorDialog.ShowAlphaChannel
        )
        if color.isValid():
            self._color = color
            self._update_color_button()
            self._on_param_changed()

    def _update_color_button(self):
        self.btn_color.setStyleSheet(
            f"QPushButton#colorBtn {{ background-color: {self._color.name()}; "
            f"border: 2px solid #00c8ff; border-radius: 12px; "
            f"min-width: 24px; min-height: 24px; }}"
        )

    def _apply_settings(self):
        c = self.config
        c.set("crosshair.style", self.combo_style.currentData())
        c.set("crosshair.size", self.slider_size.value())
        c.set("crosshair.thickness", self.slider_thickness.value())
        c.set("crosshair.gap", self.slider_gap.value())
        c.set("crosshair.color", [self._color.red(), self._color.green(),
                                    self._color.blue(), self._color.alpha()])
        c.set("crosshair.outline", self.chk_outline.isChecked())
        c.set("crosshair.outline_thickness", self.spin_outline.value())
        c.set("crosshair.dot", self.chk_dot.isChecked())
        c.set("crosshair.dot_size", self.spin_dot_size.value())
        c.set("crosshair.t_style", self.chk_t_style.isChecked())
        c.set("animation.enabled", self.chk_anim.isChecked())
        c.set("animation.type", self.combo_anim.currentData())
        c.set("animation.speed", self.slider_anim_speed.value() / 10.0)
        c.set("animation.intensity", self.slider_anim_intensity.value() / 100.0)
        c.set("display.monitor", self.spin_monitor.value())
        c.set("display.offset_x", self.spin_offset_x.value())
        c.set("display.offset_y", self.spin_offset_y.value())
        c.set("display.opacity", self.slider_opacity.value() / 100.0)
        c.set("display.fps", self.spin_fps.value())
        c.save()

        # Show the overlay with new settings (hide first to fully clear old pixels)
        self.overlay.set_visible(False)
        self.overlay.refresh_config()
        self.overlay.set_visible(True)
        self.btn_hide.setText(t("btn.hide"))
        self.config_changed.emit()

    def _reset_defaults(self):
        from .config import DEFAULT_CONFIG
        for key, section in DEFAULT_CONFIG.items():
            if isinstance(section, dict):
                for k, v in section.items():
                    self.config.set(f"{key}.{k}", v)
        self.config.save()
        self._load_from_config()
        self.overlay.refresh_config()

    def _toggle_overlay(self):
        visible = self.overlay.toggle_visibility()
        self.btn_hide.setText(t("btn.hide") if visible else t("btn.show"))

    def _quit_app(self):
        """Fully quit the application — releases file locks so EXE can be deleted."""
        self.close_app.emit()

    def _load_from_config(self):
        c = self.config

        style = c.get("crosshair.style", "cross")
        idx = self.combo_style.findData(style)
        if idx >= 0:
            self.combo_style.setCurrentIndex(idx)

        self.slider_size.setValue(c.get("crosshair.size", 20))
        self.slider_thickness.setValue(c.get("crosshair.thickness", 2))
        self.slider_gap.setValue(c.get("crosshair.gap", 4))

        color = c.get("crosshair.color", [0, 255, 0, 255])
        self._color = QColor(color[0], color[1], color[2], color[3])
        self._update_color_button()

        self.chk_outline.setChecked(c.get("crosshair.outline", True))
        self.spin_outline.setValue(c.get("crosshair.outline_thickness", 1))
        self.chk_dot.setChecked(c.get("crosshair.dot", True))
        self.spin_dot_size.setValue(c.get("crosshair.dot_size", 2))
        self.chk_t_style.setChecked(c.get("crosshair.t_style", False))

        self.chk_anim.setChecked(c.get("animation.enabled", True))
        anim_type = c.get("animation.type", "none")
        idx = self.combo_anim.findData(anim_type)
        if idx >= 0:
            self.combo_anim.setCurrentIndex(idx)
        self.slider_anim_speed.setValue(int(c.get("animation.speed", 1.0) * 10))
        self.slider_anim_intensity.setValue(int(c.get("animation.intensity", 0.3) * 100))

        self.spin_monitor.setValue(c.get("display.monitor", 0))
        self.spin_offset_x.setValue(c.get("display.offset_x", 0))
        self.spin_offset_y.setValue(c.get("display.offset_y", 0))
        self.slider_opacity.setValue(int(c.get("display.opacity", 1.0) * 100))
        self.spin_fps.setValue(c.get("display.fps", 60))

        self._on_param_changed()

    # ── Profile management ──

    def _refresh_profiles(self):
        self.combo_profile.clear()
        for name in self.config.list_profiles():
            self.combo_profile.addItem(name)
        current = self.config.get("general.current_profile", "default")
        idx = self.combo_profile.findText(current)
        if idx >= 0:
            self.combo_profile.setCurrentIndex(idx)

    def _load_profile(self):
        name = self.combo_profile.currentText()
        if name and self.config.load_profile(name):
            self._load_from_config()
            self.overlay.refresh_config()
            self.profile_changed.emit(name)

    def _save_profile(self):
        name, ok = QInputDialog.getText(self, t("prof.save_title"), t("prof.save_prompt"))
        if ok and name:
            self._apply_settings()
            self.config.save_profile(name)
            self._refresh_profiles()

    def _delete_profile(self):
        name = self.combo_profile.currentText()
        if name:
            reply = QMessageBox.question(
                self, t("prof.del_title"),
                t("prof.del_confirm", name=name),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.config.delete_profile(name)
                self._refresh_profiles()

    def _apply_preset(self, preset_name: str):
        if self.config.load_profile(preset_name):
            self._load_from_config()
            self.overlay.refresh_config()
            self.profile_changed.emit(preset_name)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
