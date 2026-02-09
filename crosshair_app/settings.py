"""
Settings panel GUI for CrosshairX.
Modern glassmorphism + wallpaper background, bilingual (RU/EN).

Window behavior:
  Close    (X)  = hide to tray, app keeps running
  Minimize (—)  = minimize to taskbar (native Qt)
  Выход button  = FULL QUIT — kills overlay + process
  Tray Quit     = FULL QUIT — kills overlay + process
"""

import os
import sys
import json
import ctypes

from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint, QTimer
from PyQt5.QtGui import (
    QColor, QFont, QPainter, QPen, QBrush,
    QLinearGradient, QPixmap, QImage, QPainterPath, QRegion
)
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox,
    QPushButton, QGroupBox, QCheckBox, QColorDialog, QSpinBox,
    QTabWidget, QGridLayout, QMessageBox, QInputDialog, QScrollArea,
    QDialog, QTextEdit, QApplication
)

from .i18n import t, set_language, get_language


def _resource_path(relative: str) -> str:
    """Absolute path to bundled resource (works in dev + PyInstaller)."""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


# ── Theme wallpaper paths ──
THEME_KEYS = ["midnight", "purple", "ocean", "sakura"]


def _enable_acrylic(hwnd, tint=0x14000000):
    """Enable Windows 10/11 acrylic blur behind the window (best-effort)."""
    if sys.platform != "win32":
        return
    try:
        class ACCENT_POLICY(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_uint),
                ("AccentFlags", ctypes.c_uint),
                ("GradientColor", ctypes.c_uint),
                ("AnimationId", ctypes.c_uint),
            ]
        class WINCOMPATTRDATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.POINTER(ACCENT_POLICY)),
                ("SizeOfData", ctypes.c_size_t),
            ]
        accent = ACCENT_POLICY()
        accent.AccentState = 4  # ACCENT_ENABLE_ACRYLICBLENDERBEHIND
        accent.AccentFlags = 2
        accent.GradientColor = tint  # ABGR
        data = WINCOMPATTRDATA()
        data.Attribute = 19  # WCA_ACCENT_POLICY
        data.Data = ctypes.pointer(accent)
        data.SizeOfData = ctypes.sizeof(accent)
        ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.byref(data))
    except Exception:
        pass
    # Windows 11: rounded corners
    try:
        pref = ctypes.c_int(2)  # DWMWCP_ROUND
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 33, ctypes.byref(pref), ctypes.sizeof(pref)
        )
    except Exception:
        pass


# ── Glass stylesheet ──
GLASS_STYLE = """
QWidget {
    color: #e8e8f0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 15px;
    background: transparent;
}
QTabWidget::pane {
    background: rgba(10, 10, 28, 130);
    border: 1px solid rgba(100, 120, 200, 20);
    border-radius: 10px;
}
QTabBar::tab {
    background: rgba(18, 18, 42, 140);
    color: #8888a8;
    padding: 10px 24px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 2px;
    font-weight: 600;
    font-size: 14px;
    min-width: 85px;
}
QTabBar::tab:selected {
    background: rgba(25, 25, 55, 180);
    color: #00d4ff;
    font-weight: 600;
}
QTabBar::tab:hover {
    background: rgba(30, 30, 65, 160);
    color: #c0c0d8;
}
QGroupBox {
    background-color: rgba(12, 12, 30, 120);
    border: 1px solid rgba(100, 120, 200, 25);
    border-radius: 12px;
    margin-top: 18px;
    padding: 22px 16px 16px 16px;
    font-weight: 700;
    font-size: 15px;
    color: #00d4ff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
    color: #00d4ff;
    font-size: 15px;
}
QPushButton {
    background-color: rgba(20, 20, 48, 200);
    border: 1px solid rgba(80, 100, 180, 40);
    border-radius: 8px;
    padding: 8px 18px;
    color: #d4d4e8;
    font-weight: 500;
    font-size: 15px;
}
QPushButton:hover {
    background-color: rgba(35, 35, 72, 220);
    border-color: rgba(0, 212, 255, 100);
    color: #ffffff;
}
QPushButton:pressed {
    background-color: rgba(55, 28, 110, 200);
}
QPushButton#colorBtn {
    border: 2px solid #00d4ff;
    border-radius: 14px;
    min-width: 28px;
    min-height: 28px;
}
QPushButton#accentBtn {
    background-color: rgba(0, 160, 210, 40);
    border: 1px solid rgba(0, 212, 255, 80);
    color: #00d4ff;
    font-weight: 700;
    font-size: 15px;
}
QPushButton#accentBtn:hover {
    background-color: rgba(0, 190, 245, 60);
    border-color: rgba(0, 212, 255, 160);
    color: #ffffff;
}
QPushButton#dangerBtn {
    background-color: rgba(55, 16, 26, 200);
    border: 1px solid rgba(200, 50, 80, 50);
    color: #ff5070;
    font-weight: 600;
}
QPushButton#dangerBtn:hover {
    background-color: rgba(80, 22, 38, 220);
    border-color: rgba(255, 60, 90, 120);
    color: #ff6888;
}
QPushButton#themeBtn {
    padding: 6px 10px;
    font-size: 13px;
    border-radius: 8px;
}
QPushButton#themeBtnActive {
    padding: 6px 10px;
    font-size: 13px;
    border-radius: 8px;
    border: 2px solid rgba(0, 212, 255, 200);
    background: rgba(0, 160, 220, 30);
    color: #00d4ff;
    font-weight: 700;
}
QSlider::groove:horizontal {
    height: 5px;
    background: rgba(28, 28, 55, 200);
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #00d4ff;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}
QSlider::sub-page:horizontal {
    background: rgba(0, 170, 230, 100);
    border-radius: 2px;
}
QComboBox {
    background-color: rgba(16, 16, 40, 200);
    border: 1px solid rgba(80, 100, 180, 40);
    border-radius: 8px;
    padding: 6px 12px;
    color: #d4d4e8;
    font-size: 15px;
    min-width: 120px;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: rgba(16, 16, 40, 245);
    color: #d4d4e8;
    selection-background-color: rgba(0, 170, 230, 60);
    border: 1px solid rgba(80, 100, 180, 40);
    border-radius: 6px;
    font-size: 15px;
}
QSpinBox {
    background-color: rgba(16, 16, 40, 200);
    border: 1px solid rgba(80, 100, 180, 40);
    border-radius: 6px;
    padding: 5px 10px;
    color: #d4d4e8;
    font-size: 15px;
    min-width: 70px;
}
QCheckBox {
    spacing: 10px;
    font-size: 15px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid rgba(80, 100, 180, 50);
    background: rgba(16, 16, 40, 200);
}
QCheckBox::indicator:checked {
    background: #00d4ff;
    border-color: #00d4ff;
}
QLabel {
    font-size: 15px;
}
QLabel#sectionHelper {
    color: #606880;
    font-size: 13px;
    padding: 2px 4px;
}
QLabel#valueLabel {
    color: #00d4ff;
    font-weight: 700;
    min-width: 40px;
    font-size: 15px;
}
QScrollArea {
    border: none;
    background: transparent;
}
"""


class CrosshairPreview(QWidget):
    """Live preview of the crosshair."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(170, 170)
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
        p.setBrush(QColor(8, 8, 22))
        p.setPen(QPen(QColor(50, 60, 100, 60), 1))
        p.drawRoundedRect(0, 0, 169, 169, 10, 10)
        pen = QPen(QColor(25, 25, 45), 1)
        p.setPen(pen)
        for i in range(0, 170, 20):
            p.drawLine(i, 0, i, 170)
            p.drawLine(0, i, 170, i)
        if self._renderer and self._config:
            self._renderer.draw(p, 85, 85, self._config)
        p.end()


class ImportCrosshairDialog(QDialog):
    """Dialog for importing crosshair configs generated by AI."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("prof.import_title"))
        self.setFixedSize(540, 480)
        self.result_config = None
        self.setStyleSheet(
            "QDialog { background: rgb(12, 12, 32); }"
            "QLabel { color: #e0e8f0; background: transparent; }"
            "QTextEdit { background: rgba(8,8,24,220); border: 1px solid rgba(80,100,180,40);"
            " border-radius: 8px; padding: 10px; color: #d4d4e8;"
            " font-family: Consolas, monospace; font-size: 13px; }"
            "QPushButton { background: rgba(20,20,48,220); border: 1px solid rgba(80,100,180,40);"
            " border-radius: 8px; padding: 8px 18px; color: #d4d4e8; font-size: 14px; }"
            "QPushButton:hover { background: rgba(35,35,72,230); color: #ffffff; }"
            "QPushButton#accent { background: rgba(0,160,210,50);"
            " border: 1px solid rgba(0,212,255,80); color: #00d4ff; font-weight: 700; }"
            "QPushButton#accent:hover { background: rgba(0,190,245,70); color: #fff; }"
        )
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        title = QLabel(t("prof.import_title"))
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #00d4ff;")
        lay.addWidget(title)

        desc = QLabel(t("prof.import_instruction"))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #a0a8c0; font-size: 13px;")
        lay.addWidget(desc)

        btn_copy = QPushButton(t("prof.import_copy_btn"))
        btn_copy.setObjectName("accent")
        btn_copy.setFixedWidth(220)
        btn_copy.clicked.connect(self._copy)
        lay.addWidget(btn_copy)

        lbl = QLabel(t("prof.import_paste_hint"))
        lbl.setStyleSheet("color: #6070a0; font-size: 12px;")
        lay.addWidget(lbl)

        self.text = QTextEdit()
        self.text.setPlaceholderText('{ "style": "cross", "size": 20, ... }')
        self.text.setMinimumHeight(120)
        lay.addWidget(self.text)

        row = QHBoxLayout()
        row.addStretch()
        ba = QPushButton(t("prof.import_apply_btn"))
        ba.setObjectName("accent")
        ba.clicked.connect(self._apply)
        row.addWidget(ba)
        bc = QPushButton(t("prof.import_cancel"))
        bc.clicked.connect(self.reject)
        row.addWidget(bc)
        lay.addLayout(row)

    def _copy(self):
        QApplication.clipboard().setText(t("prof.import_format"))
        btn = self.sender()
        if btn:
            btn.setText("OK!")
            QTimer.singleShot(1500, lambda: btn.setText(t("prof.import_copy_btn")))

    def _apply(self):
        raw = self.text.toPlainText().strip()
        if not raw:
            return
        try:
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object {...}")
            self.result_config = data
            self.accept()
        except Exception as e:
            QMessageBox.warning(
                self, t("prof.import_error_title"),
                f"{t('prof.import_error_msg')}\n\n{e}"
            )


class SettingsPanel(QWidget):
    """Glassmorphism settings panel with wallpaper backgrounds.

    Window behavior:
      Close (X)  = hide to tray, app keeps running
      Minimize   = minimize to taskbar (native)
      btn_quit   = FULL QUIT (os._exit)
    """

    config_changed = pyqtSignal()
    profile_changed = pyqtSignal(str)
    close_app = pyqtSignal()       # full quit signal
    hide_to_tray = pyqtSignal()    # hide-to-tray signal (X button)

    STYLE_KEYS = [
        "cross", "dot", "circle", "chevron", "diamond", "crossdot",
        "triangle", "crosshair_classic", "square", "plus_thin",
        "crosscircle", "arrows",
    ]
    ANIM_KEYS = [
        "none", "pulse", "rotate", "breathe", "rainbow",
        "recoil", "flash", "wave",
    ]

    def __init__(self, config, overlay, parent=None):
        super().__init__(parent)
        self.config = config
        self.overlay = overlay
        self._color = QColor(*config.get("crosshair.color", [0, 255, 0, 255]))
        self._outline_color = QColor(*config.get("crosshair.outline_color", [0, 0, 0, 180]))
        self._theme = config.get("general.theme", "midnight")
        self._bg_pixmap = None  # cached wallpaper pixmap

        lang = config.get("general.language", "ru")
        set_language(lang)

        self.setWindowTitle("CrosshairX")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(901, 631)
        self.setObjectName("settingsPanel")
        self.setStyleSheet(GLASS_STYLE)
        self._drag_pos = None
        self._acrylic_done = False

        self._load_wallpaper()

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(16, 8, 16, 12)
        self._main_layout.setSpacing(8)
        self._build_ui()
        self._load_from_config()

    # ── Wallpaper background ──

    def _load_wallpaper(self):
        """Load the current theme wallpaper image."""
        img_path = _resource_path(os.path.join("assets", "themes", f"{self._theme}.png"))
        if os.path.exists(img_path):
            self._bg_pixmap = QPixmap(img_path)
        else:
            self._bg_pixmap = None

    def paintEvent(self, event):
        """Draw wallpaper background with rounded corners + subtle overlay."""
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Rounded window clip
        path = QPainterPath()
        path.addRoundedRect(
            0.0, 0.0, float(self.width()), float(self.height()), 14.0, 14.0
        )
        p.setClipPath(path)

        if self._bg_pixmap and not self._bg_pixmap.isNull():
            scaled = self._bg_pixmap.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (scaled.width() - self.width()) // 2
            y = (scaled.height() - self.height()) // 2
            # Draw wallpaper at ~88% opacity for glass translucency
            p.setOpacity(0.88)
            p.drawPixmap(0, 0, scaled, x, y, self.width(), self.height())
            p.setOpacity(1.0)
            # Very subtle dark overlay (NOT heavy — wallpaper stays visible)
            p.fillRect(self.rect(), QColor(0, 0, 0, 30))
        else:
            grad = QLinearGradient(0, 0, self.width(), self.height())
            grad.setColorAt(0.0, QColor(8, 8, 28))
            grad.setColorAt(0.5, QColor(12, 12, 38))
            grad.setColorAt(1.0, QColor(8, 14, 30))
            p.fillRect(self.rect(), grad)

        p.end()

    # ── UI construction ──

    def _build_ui(self):
        """Build entire UI (called on init and language switch)."""
        while self._main_layout.count():
            item = self._main_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        lay = self._main_layout

        # ── Custom frameless title bar ──
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(12, 4, 4, 0)
        title_bar.setSpacing(8)

        hdr = QLabel("CrosshairX")
        hdr.setFont(QFont("Segoe UI", 14, QFont.Bold))
        hdr.setStyleSheet("color: #e0e8ff; background: transparent;")
        title_bar.addWidget(hdr)

        sub = QLabel(t("app.subtitle"))
        sub.setStyleSheet(
            "color: rgba(160,170,200,140); font-size: 12px; background: transparent;"
        )
        title_bar.addWidget(sub)
        title_bar.addStretch()

        self.combo_lang = QComboBox()
        self.combo_lang.addItem("RU", "ru")
        self.combo_lang.addItem("EN", "en")
        idx = self.combo_lang.findData(get_language())
        if idx >= 0:
            self.combo_lang.setCurrentIndex(idx)
        self.combo_lang.currentIndexChanged.connect(self._on_lang_changed)
        self.combo_lang.setFixedWidth(62)
        self.combo_lang.setFixedHeight(26)
        title_bar.addWidget(self.combo_lang)

        _btn_tb = (
            "QPushButton { background: transparent; border: none; color: #8090b0;"
            " font-size: 16px; font-weight: bold; border-radius: 6px; padding: 0 10px; }"
            "QPushButton:hover { background: rgba(255,255,255,15); color: #e0e8ff; }"
        )
        btn_min = QPushButton("-")
        btn_min.setFixedSize(32, 26)
        btn_min.setStyleSheet(_btn_tb)
        btn_min.clicked.connect(self.showMinimized)
        title_bar.addWidget(btn_min)

        btn_close = QPushButton("x")
        btn_close.setFixedSize(32, 26)
        btn_close.setStyleSheet(
            "QPushButton { background: transparent; border: none; color: #8090b0;"
            " font-size: 14px; font-weight: bold; border-radius: 6px; padding: 0 10px; }"
            "QPushButton:hover { background: rgba(255,60,60,60); color: #ff6080; }"
        )
        btn_close.clicked.connect(self.close)
        title_bar.addWidget(btn_close)

        title_bar_w = QWidget()
        title_bar_w.setFixedHeight(40)
        title_bar_w.setLayout(title_bar)
        lay.addWidget(title_bar_w)

        # ── Tabs ──
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_crosshair_tab(), t("tab.crosshair"))
        self.tabs.addTab(self._build_animation_tab(), t("tab.animation"))
        self.tabs.addTab(self._build_display_tab(), t("tab.display"))
        self.tabs.addTab(self._build_profiles_tab(), t("tab.profiles"))
        lay.addWidget(self.tabs)

        # ── Bottom buttons ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.btn_apply = QPushButton(t("btn.apply"))
        self.btn_apply.setObjectName("accentBtn")
        self.btn_apply.clicked.connect(self._apply_settings)
        btn_row.addWidget(self.btn_apply)

        self.btn_reset = QPushButton(t("btn.reset"))
        self.btn_reset.clicked.connect(self._reset_defaults)
        btn_row.addWidget(self.btn_reset)

        self.btn_hide = QPushButton(t("btn.show"))
        self.btn_hide.clicked.connect(self._toggle_overlay)
        btn_row.addWidget(self.btn_hide)

        self.btn_quit = QPushButton(t("btn.quit"))
        self.btn_quit.setObjectName("dangerBtn")
        self.btn_quit.clicked.connect(self._quit_app)
        btn_row.addWidget(self.btn_quit)

        btn_w = QWidget()
        btn_w.setLayout(btn_row)
        lay.addWidget(btn_w)

    # ── Tab builders ──

    def _build_crosshair_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(10)

        top = QHBoxLayout()

        # Preview
        pg = QGroupBox(t("xhair.preview"))
        pl = QVBoxLayout(pg)
        self.preview = CrosshairPreview()
        from .crosshair import CrosshairRenderer
        self._preview_renderer = CrosshairRenderer()
        self.preview.set_renderer(self._preview_renderer)
        pl.addWidget(self.preview, alignment=Qt.AlignCenter)
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
        g.setVerticalSpacing(10)

        g.addWidget(QLabel(t("xhair.size")), 0, 0)
        self.slider_size = QSlider(Qt.Horizontal)
        self.slider_size.setRange(4, 100)
        self.slider_size.valueChanged.connect(self._on_param_changed)
        g.addWidget(self.slider_size, 0, 1)
        self.lbl_size = QLabel("20")
        self.lbl_size.setObjectName("valueLabel")
        g.addWidget(self.lbl_size, 0, 2)

        g.addWidget(QLabel(t("xhair.thickness")), 1, 0)
        self.slider_thickness = QSlider(Qt.Horizontal)
        self.slider_thickness.setRange(1, 10)
        self.slider_thickness.valueChanged.connect(self._on_param_changed)
        g.addWidget(self.slider_thickness, 1, 1)
        self.lbl_thickness = QLabel("2")
        self.lbl_thickness.setObjectName("valueLabel")
        g.addWidget(self.lbl_thickness, 1, 2)

        g.addWidget(QLabel(t("xhair.gap")), 2, 0)
        self.slider_gap = QSlider(Qt.Horizontal)
        self.slider_gap.setRange(0, 30)
        self.slider_gap.valueChanged.connect(self._on_param_changed)
        g.addWidget(self.slider_gap, 2, 1)
        self.lbl_gap = QLabel("4")
        self.lbl_gap.setObjectName("valueLabel")
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
        lay.setSpacing(10)

        grp = QGroupBox(t("anim.settings"))
        g = QGridLayout(grp)
        g.setVerticalSpacing(10)

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
        self.lbl_anim_speed.setObjectName("valueLabel")
        g.addWidget(self.lbl_anim_speed, 2, 2)

        g.addWidget(QLabel(t("anim.intensity")), 3, 0)
        self.slider_anim_intensity = QSlider(Qt.Horizontal)
        self.slider_anim_intensity.setRange(0, 100)
        self.slider_anim_intensity.valueChanged.connect(self._on_param_changed)
        g.addWidget(self.slider_anim_intensity, 3, 1)
        self.lbl_anim_intensity = QLabel("30%")
        self.lbl_anim_intensity.setObjectName("valueLabel")
        g.addWidget(self.lbl_anim_intensity, 3, 2)

        lay.addWidget(grp)

        # Effect descriptions
        desc_grp = QGroupBox(t("anim.desc_title"))
        desc_lay = QVBoxLayout(desc_grp)
        for dk in ["pulse", "rotate", "breathe", "rainbow", "recoil", "flash", "wave"]:
            lbl = QLabel(t(f"anim.desc.{dk}"))
            lbl.setObjectName("sectionHelper")
            desc_lay.addWidget(lbl)
        lay.addWidget(desc_grp)

        lay.addStretch()
        return w

    def _build_display_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(10)

        # ── Theme / wallpaper selector ──
        theme_grp = QGroupBox(t("disp.theme"))
        theme_lay = QHBoxLayout(theme_grp)
        theme_lay.setSpacing(8)
        self.theme_buttons = {}
        _theme_colors = {
            "midnight": "#0a1432",
            "purple":   "#1c0828",
            "ocean":    "#061840",
            "sakura":   "#28081c",
        }
        for key in THEME_KEYS:
            btn = QPushButton(t(f"theme.{key}"))
            btn.setFixedHeight(38)
            active = key == self._theme
            btn.setObjectName("themeBtnActive" if active else "themeBtn")
            btn.setStyleSheet(
                f"QPushButton {{ background: {_theme_colors[key]}; }}"
                if not active else ""
            )
            btn.clicked.connect(lambda checked, k=key: self._set_theme(k))
            self.theme_buttons[key] = btn
            theme_lay.addWidget(btn)
        lay.addWidget(theme_grp)

        # ── Display settings ──
        grp = QGroupBox(t("disp.settings"))
        g = QGridLayout(grp)
        g.setVerticalSpacing(10)

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
        self.lbl_opacity.setObjectName("valueLabel")
        g.addWidget(self.lbl_opacity, 3, 2)

        g.addWidget(QLabel(t("disp.fps")), 4, 0)
        self.spin_fps = QSpinBox()
        self.spin_fps.setRange(10, 144)
        g.addWidget(self.spin_fps, 4, 1)

        lay.addWidget(grp)

        # ── Hotkeys ──
        hk_grp = QGroupBox(t("disp.hotkeys"))
        hk_lay = QVBoxLayout(hk_grp)
        hk_data = [
            ("F6",  t("hk.toggle")),
            ("F7",  t("hk.next")),
            ("F8",  t("hk.prev")),
            ("F9",  t("hk.anim")),
            ("F10", t("hk.settings")),
        ]
        for key, desc in hk_data:
            row = QHBoxLayout()
            kl = QLabel(key)
            kl.setStyleSheet(
                "background: rgba(0, 170, 230, 30); padding: 5px 14px; border-radius: 5px;"
                "font-weight: bold; color: #00d4ff; min-width: 42px; font-size: 15px;"
            )
            kl.setAlignment(Qt.AlignCenter)
            row.addWidget(kl)
            dl = QLabel(f"  {desc}")
            dl.setStyleSheet("color: #a0a8c0; font-size: 15px;")
            row.addWidget(dl)
            row.addStretch()
            hk_lay.addLayout(row)
        lay.addWidget(hk_grp)

        lay.addStretch()
        return w

    def _build_profiles_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(10)

        grp = QGroupBox(t("prof.title"))
        gl = QVBoxLayout(grp)

        sr = QHBoxLayout()
        sr.addWidget(QLabel(t("prof.profile")))
        self.combo_profile = QComboBox()
        self._refresh_profiles()
        sr.addWidget(self.combo_profile)
        gl.addLayout(sr)

        bg = QGridLayout()
        bg.setSpacing(8)
        bl = QPushButton(t("prof.load"))
        bl.clicked.connect(self._load_profile)
        bg.addWidget(bl, 0, 0)
        bs = QPushButton(t("prof.save"))
        bs.clicked.connect(self._save_profile)
        bg.addWidget(bs, 0, 1)
        bd = QPushButton(t("prof.delete"))
        bd.setObjectName("dangerBtn")
        bd.clicked.connect(self._delete_profile)
        bg.addWidget(bd, 1, 0)
        br = QPushButton(t("prof.refresh"))
        br.clicked.connect(self._refresh_profiles)
        bg.addWidget(br, 1, 1)
        gl.addLayout(bg)
        lay.addWidget(grp)

        # ── Import from AI ──
        ig = QGroupBox(t("prof.import_title"))
        il = QVBoxLayout(ig)
        import_hint = QLabel(t("prof.import_hint"))
        import_hint.setObjectName("sectionHelper")
        import_hint.setWordWrap(True)
        il.addWidget(import_hint)
        btn_import = QPushButton(t("prof.import_btn"))
        btn_import.setObjectName("accentBtn")
        btn_import.clicked.connect(self._open_import_dialog)
        il.addWidget(btn_import)
        lay.addWidget(ig)

        # Presets
        pg = QGroupBox(t("prof.presets"))
        pl = QVBoxLayout(pg)
        hint = QLabel(t("prof.presets_hint"))
        hint.setObjectName("sectionHelper")
        pl.addWidget(hint)
        from .config import PRESET_PROFILES
        for key, profile in PRESET_PROFILES.items():
            btn = QPushButton(profile['name'])
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

    def _update_theme_buttons(self):
        """Highlight active theme button."""
        _theme_colors = {
            "midnight": "#0a1432",
            "purple":   "#1c0828",
            "ocean":    "#061840",
            "sakura":   "#28081c",
        }
        for key, btn in self.theme_buttons.items():
            active = key == self._theme
            btn.setObjectName("themeBtnActive" if active else "themeBtn")
            if not active:
                btn.setStyleSheet(
                    f"QPushButton {{ background: {_theme_colors[key]};"
                    f"border: 1px solid rgba(80,100,180,40); border-radius: 8px;"
                    f"color: #a0a8c0; font-size: 13px; padding: 6px 10px; }}"
                    f"QPushButton:hover {{ border-color: #00d4ff; color: #d0d8f0; }}"
                )
            else:
                btn.setStyleSheet(
                    f"QPushButton {{ background: rgba(0,160,220,30);"
                    f"border: 2px solid rgba(0,212,255,200); border-radius: 8px;"
                    f"color: #00d4ff; font-weight: 700; font-size: 13px; padding: 6px 10px; }}"
                )

    def _set_theme(self, theme_key):
        """Change wallpaper theme."""
        self._theme = theme_key
        self.config.set("general.theme", theme_key)
        self.config.save()
        self._load_wallpaper()
        self._update_theme_buttons()
        self.update()

    # ── Event handlers ──

    def _on_lang_changed(self, _=None):
        lang = self.combo_lang.currentData()
        set_language(lang)
        self.config.set("general.language", lang)
        self.config.save()
        self._build_ui()
        self._load_from_config()

    def _on_param_changed(self, _=None):
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
            "color": [self._color.red(), self._color.green(),
                      self._color.blue(), self._color.alpha()],
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
            f"border: 2px solid #00d4ff; border-radius: 14px; "
            f"min-width: 28px; min-height: 28px; }}"
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
        """Full quit — kills overlay and process."""
        self.config.save()
        self.close_app.emit()
        os._exit(0)

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

        self._theme = c.get("general.theme", "midnight")
        self._load_wallpaper()
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
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.config.delete_profile(name)
                self._refresh_profiles()

    def _apply_preset(self, preset_name: str):
        if self.config.load_profile(preset_name):
            self._load_from_config()
            self.overlay.refresh_config()
            self.profile_changed.emit(preset_name)

    # ── Window events ──

    def showEvent(self, event):
        """Apply acrylic blur on first show."""
        super().showEvent(event)
        if sys.platform == "win32" and not self._acrylic_done:
            try:
                hwnd = int(self.winId())
                _enable_acrylic(hwnd)
                self._acrylic_done = True
            except Exception:
                pass

    def mousePressEvent(self, event):
        """Allow dragging from the title bar area (top 44px)."""
        if event.button() == Qt.LeftButton and event.pos().y() <= 44:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def closeEvent(self, event):
        """X button = hide to tray (app keeps running, crosshair stays)."""
        event.ignore()
        self.hide()
        self.hide_to_tray.emit()

    # ── Import crosshair from AI ──

    def _open_import_dialog(self):
        """Open the crosshair import dialog."""
        dlg = ImportCrosshairDialog(self)
        if dlg.exec_() == QDialog.Accepted and dlg.result_config:
            cfg = dlg.result_config
            valid_styles = self.STYLE_KEYS
            style = cfg.get("style", "cross")
            if style not in valid_styles:
                style = "cross"
            self.config.set("crosshair.style", style)
            self.config.set("crosshair.size", max(4, min(100, int(cfg.get("size", 20)))))
            self.config.set("crosshair.thickness", max(1, min(10, int(cfg.get("thickness", 2)))))
            self.config.set("crosshair.gap", max(0, min(30, int(cfg.get("gap", 4)))))
            color = cfg.get("color", [0, 255, 0, 255])
            if isinstance(color, list) and len(color) >= 3:
                color = [max(0, min(255, int(c))) for c in color[:4]]
                if len(color) == 3:
                    color.append(255)
                self.config.set("crosshair.color", color)
            self.config.set("crosshair.dot", bool(cfg.get("dot", True)))
            self.config.set("crosshair.dot_size", max(1, min(10, int(cfg.get("dot_size", 2)))))
            self.config.set("crosshair.outline", bool(cfg.get("outline", True)))
            self.config.set("crosshair.outline_thickness", max(1, min(5, int(cfg.get("outline_thickness", 1)))))
            self.config.set("crosshair.t_style", bool(cfg.get("t_style", False)))
            self.config.save()
            self._load_from_config()
            self.overlay.refresh_config()
            self.overlay.set_visible(True)
            self.btn_hide.setText(t("btn.hide"))
            QMessageBox.information(self, "CrosshairX", t("prof.import_success"))
