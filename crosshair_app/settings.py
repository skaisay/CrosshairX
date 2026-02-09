"""
Settings panel GUI for CrosshairX.
Modern glassmorphism + wallpaper background, bilingual (RU/EN).

Window behavior:
  Close    (X)  = hide to tray, app keeps running
  Minimize (-)  = minimize to taskbar (native Qt)
  Quit button   = FULL QUIT - kills overlay + process
  Tray Quit     = FULL QUIT - kills overlay + process
"""

import os
import sys
import json
import ctypes
import subprocess

from PyQt5.QtCore import (
    Qt, pyqtSignal, QRect, QPoint, QTimer,
    QPropertyAnimation, QEasingCurve,
)
from PyQt5.QtGui import (
    QColor, QFont, QPainter, QPen, QBrush,
    QLinearGradient, QPixmap, QImage, QPainterPath, QRegion,
)
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox,
    QPushButton, QGroupBox, QCheckBox, QColorDialog, QSpinBox,
    QTabWidget, QGridLayout, QMessageBox, QInputDialog, QScrollArea,
    QDialog, QTextEdit, QApplication, QProgressBar, QSizePolicy,
    QFrame,
)

from .i18n import t, set_language, get_language


def _resource_path(relative: str) -> str:
    """Absolute path to bundled resource (works in dev + PyInstaller)."""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


# -- Theme wallpaper paths --
THEME_KEYS = ["midnight", "purple", "ocean", "sakura"]

# -- Known game executables for monitoring --
KNOWN_GAMES = {
    "RobloxPlayerBeta.exe": "Roblox",
    "FortniteClient-Win64-Shipping.exe": "Fortnite",
    "csgo.exe": "CS:GO",
    "cs2.exe": "Counter-Strike 2",
    "valorant.exe": "Valorant",
    "VALORANT-Win64-Shipping.exe": "Valorant",
    "javaw.exe": "Minecraft (Java)",
    "Minecraft.Windows.exe": "Minecraft (Bedrock)",
    "GTA5.exe": "GTA V",
    "r5apex.exe": "Apex Legends",
    "overwatch.exe": "Overwatch 2",
    "dota2.exe": "Dota 2",
    "LeagueofLegends.exe": "League of Legends",
    "League of Legends.exe": "League of Legends",
    "PUBG-Win64-Shipping.exe": "PUBG",
    "TslGame.exe": "PUBG",
    "RocketLeague.exe": "Rocket League",
    "eldenring.exe": "Elden Ring",
    "Cyberpunk2077.exe": "Cyberpunk 2077",
    "cod.exe": "Call of Duty",
    "ModernWarfare.exe": "Call of Duty: MW",
    "destiny2.exe": "Destiny 2",
    "Warframe.x64.exe": "Warframe",
    "GenshinImpact.exe": "Genshin Impact",
    "ZenlessZoneZero.exe": "Zenless Zone Zero",
    "HonkaiStarRail.exe": "Honkai: Star Rail",
    "DeadByDaylight-Win64-Shipping.exe": "Dead By Daylight",
    "Terraria.exe": "Terraria",
    "left4dead2.exe": "Left 4 Dead 2",
    "hl2.exe": "Half-Life 2",
    "rust.exe": "Rust",
    "EscapeFromTarkov.exe": "Escape from Tarkov",
    "DayZGame_x64.exe": "DayZ",
    "bf2042.exe": "Battlefield 2042",
    "WorldOfTanks.exe": "World of Tanks",
    "WoT.exe": "World of Tanks",
    "WorldOfWarships.exe": "World of Warships",
    "Warthunder.exe": "War Thunder",
    "aces.exe": "War Thunder",
    "Overwatch.exe": "Overwatch 2",
    "amongus.exe": "Among Us",
    "FallGuys_client_game.exe": "Fall Guys",
    "PalWorld-Win64-Shipping.exe": "Palworld",
}


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


# -- Glass stylesheet (font-size 13px everywhere for proper fitting) --
GLASS_STYLE = """
QWidget {
    color: #e8e8f0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
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
    padding: 7px 14px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
    margin-right: 2px;
    font-weight: 600;
    font-size: 12px;
    min-width: 60px;
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
    margin-top: 14px;
    padding: 18px 10px 10px 10px;
    font-weight: 700;
    font-size: 13px;
    color: #00d4ff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
    color: #00d4ff;
    font-size: 13px;
}
QPushButton {
    background-color: rgba(20, 20, 48, 200);
    border: 1px solid rgba(80, 100, 180, 40);
    border-radius: 8px;
    padding: 6px 14px;
    color: #d4d4e8;
    font-weight: 500;
    font-size: 13px;
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
    font-size: 13px;
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
    padding: 5px 8px;
    font-size: 12px;
    border-radius: 8px;
}
QPushButton#themeBtnActive {
    padding: 5px 8px;
    font-size: 12px;
    border-radius: 8px;
    border: 2px solid rgba(0, 212, 255, 200);
    background: rgba(0, 160, 220, 30);
    color: #00d4ff;
    font-weight: 700;
}
QPushButton#descToggle {
    background: rgba(20, 20, 48, 160);
    border: 1px solid rgba(80, 100, 180, 30);
    border-radius: 6px;
    padding: 5px 12px;
    color: #8090b0;
    font-size: 12px;
    text-align: left;
}
QPushButton#descToggle:hover {
    background: rgba(30, 30, 60, 180);
    color: #a8b8d8;
}
QSlider::groove:horizontal {
    height: 5px;
    background: rgba(28, 28, 55, 200);
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #00d4ff;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: rgba(0, 170, 230, 100);
    border-radius: 2px;
}
QComboBox {
    background-color: rgba(16, 16, 40, 200);
    border: 1px solid rgba(80, 100, 180, 40);
    border-radius: 8px;
    padding: 5px 10px;
    color: #d4d4e8;
    font-size: 13px;
    min-width: 100px;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: rgba(16, 16, 40, 245);
    color: #d4d4e8;
    selection-background-color: rgba(0, 170, 230, 60);
    border: 1px solid rgba(80, 100, 180, 40);
    border-radius: 6px;
    font-size: 13px;
}
QSpinBox {
    background-color: rgba(16, 16, 40, 200);
    border: 1px solid rgba(80, 100, 180, 40);
    border-radius: 6px;
    padding: 4px 8px;
    color: #d4d4e8;
    font-size: 13px;
    min-width: 60px;
}
QCheckBox {
    spacing: 8px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid rgba(80, 100, 180, 50);
    background: rgba(16, 16, 40, 200);
}
QCheckBox::indicator:checked {
    background: #00d4ff;
    border-color: #00d4ff;
}
QLabel {
    font-size: 13px;
}
QLabel#sectionHelper {
    color: #606880;
    font-size: 12px;
    padding: 1px 4px;
}
QLabel#valueLabel {
    color: #00d4ff;
    font-weight: 700;
    min-width: 36px;
    font-size: 13px;
}
QScrollArea {
    border: none;
    background: transparent;
}
QProgressBar {
    background: rgba(16, 16, 40, 200);
    border: 1px solid rgba(80, 100, 180, 40);
    border-radius: 6px;
    height: 18px;
    text-align: center;
    color: #d4d4e8;
    font-size: 11px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 rgba(0,140,220,180), stop:1 rgba(0,212,255,140));
    border-radius: 5px;
}
"""


class CrosshairPreview(QWidget):
    """Live preview of the crosshair."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 150)
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
        p.drawRoundedRect(0, 0, 149, 149, 10, 10)
        pen = QPen(QColor(25, 25, 45), 1)
        p.setPen(pen)
        for i in range(0, 150, 20):
            p.drawLine(i, 0, i, 150)
            p.drawLine(0, i, 150, i)
        if self._renderer and self._config:
            self._renderer.draw(p, 75, 75, self._config)
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
            " border-radius: 8px; padding: 8px 18px; color: #d4d4e8; font-size: 13px; }"
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
        title.setFont(QFont("Segoe UI", 15, QFont.Bold))
        title.setStyleSheet("color: #00d4ff;")
        lay.addWidget(title)

        desc = QLabel(t("prof.import_instruction"))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #a0a8c0; font-size: 12px;")
        lay.addWidget(desc)

        btn_copy = QPushButton(t("prof.import_copy_btn"))
        btn_copy.setObjectName("accent")
        btn_copy.setFixedWidth(220)
        btn_copy.clicked.connect(self._copy)
        lay.addWidget(btn_copy)

        lbl = QLabel(t("prof.import_paste_hint"))
        lbl.setStyleSheet("color: #6070a0; font-size: 11px;")
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
    close_app = pyqtSignal()
    hide_to_tray = pyqtSignal()

    W, H = 901, 631

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
        self._bg_pixmap = None

        lang = config.get("general.language", "ru")
        set_language(lang)

        self.setWindowTitle("CrosshairX")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(self.W, self.H)
        self.setMinimumSize(self.W, self.H)
        self.setMaximumSize(self.W, self.H)
        self.setObjectName("settingsPanel")
        self.setStyleSheet(GLASS_STYLE)
        self._drag_pos = None
        self._acrylic_done = False

        self._load_wallpaper()

        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(14, 6, 14, 10)
        self._main_layout.setSpacing(4)
        self._build_ui()
        self._load_from_config()

        # Monitor auto-refresh timer
        self._mon_timer = QTimer(self)
        self._mon_timer.timeout.connect(self._refresh_monitor)
        self._mon_auto = False

    # -- Wallpaper --

    def _load_wallpaper(self):
        img_path = _resource_path(os.path.join("assets", "themes", f"{self._theme}.png"))
        if os.path.exists(img_path):
            self._bg_pixmap = QPixmap(img_path)
        else:
            self._bg_pixmap = None

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0.0, 0.0, float(self.width()), float(self.height()), 14.0, 14.0)
        p.setClipPath(path)

        if self._bg_pixmap and not self._bg_pixmap.isNull():
            scaled = self._bg_pixmap.scaled(
                self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            x = (scaled.width() - self.width()) // 2
            y = (scaled.height() - self.height()) // 2
            p.setOpacity(0.88)
            p.drawPixmap(0, 0, scaled, x, y, self.width(), self.height())
            p.setOpacity(1.0)
            p.fillRect(self.rect(), QColor(0, 0, 0, 30))
        else:
            grad = QLinearGradient(0, 0, self.width(), self.height())
            grad.setColorAt(0.0, QColor(8, 8, 28))
            grad.setColorAt(0.5, QColor(12, 12, 38))
            grad.setColorAt(1.0, QColor(8, 14, 30))
            p.fillRect(self.rect(), grad)
        p.end()

    # -- UI construction --

    def _build_ui(self):
        while self._main_layout.count():
            item = self._main_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        lay = self._main_layout

        # -- Custom frameless title bar --
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(10, 2, 4, 0)
        title_bar.setSpacing(6)

        hdr = QLabel("CrosshairX")
        hdr.setFont(QFont("Segoe UI", 13, QFont.Bold))
        hdr.setStyleSheet("color: #e0e8ff; background: transparent;")
        title_bar.addWidget(hdr)

        sub = QLabel(t("app.subtitle"))
        sub.setStyleSheet("color: rgba(160,170,200,140); font-size: 11px; background: transparent;")
        title_bar.addWidget(sub)
        title_bar.addStretch()

        self.combo_lang = QComboBox()
        self.combo_lang.addItem("RU", "ru")
        self.combo_lang.addItem("EN", "en")
        idx = self.combo_lang.findData(get_language())
        if idx >= 0:
            self.combo_lang.setCurrentIndex(idx)
        self.combo_lang.currentIndexChanged.connect(self._on_lang_changed)
        self.combo_lang.setFixedWidth(58)
        self.combo_lang.setFixedHeight(24)
        title_bar.addWidget(self.combo_lang)

        _btn_tb = (
            "QPushButton { background: transparent; border: none; color: #8090b0;"
            " font-size: 15px; font-weight: bold; border-radius: 6px; padding: 0 8px; }"
            "QPushButton:hover { background: rgba(255,255,255,15); color: #e0e8ff; }"
        )
        btn_min = QPushButton("\u2013")
        btn_min.setFixedSize(30, 24)
        btn_min.setStyleSheet(_btn_tb)
        btn_min.clicked.connect(self.showMinimized)
        title_bar.addWidget(btn_min)

        btn_close = QPushButton("\u2715")
        btn_close.setFixedSize(30, 24)
        btn_close.setStyleSheet(
            "QPushButton { background: transparent; border: none; color: #8090b0;"
            " font-size: 13px; font-weight: bold; border-radius: 6px; padding: 0 8px; }"
            "QPushButton:hover { background: rgba(255,60,60,60); color: #ff6080; }"
        )
        btn_close.clicked.connect(self.close)
        title_bar.addWidget(btn_close)

        title_bar_w = QWidget()
        title_bar_w.setFixedHeight(34)
        title_bar_w.setLayout(title_bar)
        lay.addWidget(title_bar_w)

        # -- Tabs --
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_crosshair_tab(), t("tab.crosshair"))
        self.tabs.addTab(self._build_animation_tab(), t("tab.animation"))
        self.tabs.addTab(self._build_display_tab(), t("tab.display"))
        self.tabs.addTab(self._build_monitor_tab(), t("tab.monitor"))
        self.tabs.addTab(self._build_profiles_tab(), t("tab.profiles"))
        lay.addWidget(self.tabs)

        # -- Bottom buttons --
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

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
        btn_w.setFixedHeight(36)
        btn_w.setLayout(btn_row)
        lay.addWidget(btn_w)

    # ================================================================
    #                       TAB BUILDERS
    # ================================================================

    def _make_scroll(self, inner_widget):
        """Wrap a widget in a transparent QScrollArea."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidget(inner_widget)
        return scroll

    # -- Crosshair Tab --

    def _build_crosshair_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(6)
        lay.setContentsMargins(6, 4, 6, 4)

        top = QHBoxLayout()
        top.setSpacing(8)

        # Preview
        pg = QGroupBox(t("xhair.preview"))
        pl = QVBoxLayout(pg)
        self.preview = CrosshairPreview()
        from .crosshair import CrosshairRenderer
        self._preview_renderer = CrosshairRenderer()
        self.preview.set_renderer(self._preview_renderer)
        pl.addWidget(self.preview, alignment=Qt.AlignCenter)
        pg.setFixedWidth(185)
        top.addWidget(pg)

        # Style + color
        sg = QGroupBox(t("xhair.style"))
        sl = QVBoxLayout(sg)
        sl.setSpacing(6)

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
        g.setVerticalSpacing(7)
        g.setHorizontalSpacing(8)
        g.setColumnMinimumWidth(0, 90)
        g.setColumnStretch(1, 1)
        g.setColumnMinimumWidth(2, 36)

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
        dr.addStretch()
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
        olr.addStretch()
        g.addLayout(olr, 4, 0, 1, 3)

        lay.addWidget(pg2)
        lay.addStretch()
        return self._make_scroll(w)

    # -- Animation Tab --

    def _build_animation_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(6)
        lay.setContentsMargins(6, 4, 6, 4)

        grp = QGroupBox(t("anim.settings"))
        g = QGridLayout(grp)
        g.setVerticalSpacing(7)
        g.setHorizontalSpacing(8)
        g.setColumnMinimumWidth(0, 100)
        g.setColumnStretch(1, 1)
        g.setColumnMinimumWidth(2, 36)

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

        # -- Collapsible effect descriptions (hidden by default) --
        self._desc_toggle = QPushButton(t("anim.show_desc"))
        self._desc_toggle.setObjectName("descToggle")
        self._desc_toggle.setCursor(Qt.PointingHandCursor)
        self._desc_toggle.clicked.connect(self._toggle_descriptions)
        lay.addWidget(self._desc_toggle)

        self._desc_container = QWidget()
        self._desc_container.setMaximumHeight(0)
        self._desc_container.setMinimumHeight(0)
        desc_lay = QVBoxLayout(self._desc_container)
        desc_lay.setContentsMargins(8, 4, 8, 4)
        desc_lay.setSpacing(2)
        for dk in ["pulse", "rotate", "breathe", "rainbow", "recoil", "flash", "wave"]:
            lbl = QLabel(t(f"anim.desc.{dk}"))
            lbl.setObjectName("sectionHelper")
            lbl.setWordWrap(True)
            desc_lay.addWidget(lbl)
        lay.addWidget(self._desc_container)

        self._desc_expanded = False

        lay.addStretch()
        return self._make_scroll(w)

    # -- Display Tab --

    def _build_display_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(6)
        lay.setContentsMargins(6, 4, 6, 4)

        # Theme selector
        theme_grp = QGroupBox(t("disp.theme"))
        theme_lay = QHBoxLayout(theme_grp)
        theme_lay.setSpacing(6)
        self.theme_buttons = {}
        _theme_colors = {
            "midnight": "#0a1432",
            "purple":   "#1c0828",
            "ocean":    "#061840",
            "sakura":   "#28081c",
        }
        for key in THEME_KEYS:
            btn = QPushButton(t(f"theme.{key}"))
            btn.setFixedHeight(32)
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

        # Display settings
        grp = QGroupBox(t("disp.settings"))
        g = QGridLayout(grp)
        g.setVerticalSpacing(7)
        g.setHorizontalSpacing(8)
        g.setColumnMinimumWidth(0, 110)
        g.setColumnStretch(1, 1)
        g.setColumnMinimumWidth(2, 36)

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

        # Hotkeys
        hk_grp = QGroupBox(t("disp.hotkeys"))
        hk_lay = QVBoxLayout(hk_grp)
        hk_lay.setSpacing(3)
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
                "background: rgba(0,170,230,30); padding: 3px 10px; border-radius: 5px;"
                "font-weight: bold; color: #00d4ff; min-width: 32px; font-size: 12px;"
            )
            kl.setAlignment(Qt.AlignCenter)
            kl.setFixedWidth(44)
            row.addWidget(kl)
            dl = QLabel(f"  {desc}")
            dl.setStyleSheet("color: #a0a8c0; font-size: 12px;")
            row.addWidget(dl)
            row.addStretch()
            hk_lay.addLayout(row)
        lay.addWidget(hk_grp)

        lay.addStretch()
        return self._make_scroll(w)

    # -- Monitor Tab (system resources + detected games) --

    def _build_monitor_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(6)
        lay.setContentsMargins(6, 4, 6, 4)

        # System Resources
        sys_grp = QGroupBox(t("mon.system"))
        sg = QGridLayout(sys_grp)
        sg.setVerticalSpacing(7)
        sg.setHorizontalSpacing(8)
        sg.setColumnMinimumWidth(0, 110)
        sg.setColumnStretch(1, 1)

        sg.addWidget(QLabel(t("mon.cpu")), 0, 0)
        self._cpu_bar = QProgressBar()
        self._cpu_bar.setRange(0, 100)
        self._cpu_bar.setValue(0)
        self._cpu_bar.setFormat("0%")
        sg.addWidget(self._cpu_bar, 0, 1)

        sg.addWidget(QLabel(t("mon.ram")), 1, 0)
        self._ram_bar = QProgressBar()
        self._ram_bar.setRange(0, 100)
        self._ram_bar.setValue(0)
        self._ram_bar.setFormat("0%")
        sg.addWidget(self._ram_bar, 1, 1)

        sg.addWidget(QLabel(t("mon.gpu")), 2, 0)
        self._gpu_bar = QProgressBar()
        self._gpu_bar.setRange(0, 100)
        self._gpu_bar.setValue(0)
        self._gpu_bar.setFormat("N/A")
        sg.addWidget(self._gpu_bar, 2, 1)

        lay.addWidget(sys_grp)

        # Detected Games
        game_grp = QGroupBox(t("mon.games"))
        gl = QVBoxLayout(game_grp)
        gl.setSpacing(3)
        self._games_label = QLabel(t("mon.no_games"))
        self._games_label.setWordWrap(True)
        self._games_label.setStyleSheet("color: #a0a8c0; font-size: 12px; padding: 4px;")
        gl.addWidget(self._games_label)
        lay.addWidget(game_grp)

        # Controls
        ctrl = QHBoxLayout()
        ctrl.setSpacing(8)
        btn_refresh = QPushButton(t("mon.refresh"))
        btn_refresh.setObjectName("accentBtn")
        btn_refresh.clicked.connect(self._refresh_monitor)
        ctrl.addWidget(btn_refresh)

        self._chk_auto_refresh = QCheckBox(t("mon.auto_refresh"))
        self._chk_auto_refresh.stateChanged.connect(self._toggle_monitor_auto)
        ctrl.addWidget(self._chk_auto_refresh)
        ctrl.addStretch()
        lay.addLayout(ctrl)

        lay.addStretch()
        return self._make_scroll(w)

    # -- Profiles Tab --

    def _build_profiles_tab(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(6)
        lay.setContentsMargins(6, 4, 6, 4)

        grp = QGroupBox(t("prof.title"))
        gl = QVBoxLayout(grp)
        gl.setSpacing(5)

        sr = QHBoxLayout()
        sr.addWidget(QLabel(t("prof.profile")))
        self.combo_profile = QComboBox()
        self._refresh_profiles()
        sr.addWidget(self.combo_profile, 1)
        gl.addLayout(sr)

        bg = QGridLayout()
        bg.setSpacing(5)
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

        # Import from AI
        ig = QGroupBox(t("prof.import_title"))
        il = QVBoxLayout(ig)
        il.setSpacing(4)
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
        pl.setSpacing(3)
        hint = QLabel(t("prof.presets_hint"))
        hint.setObjectName("sectionHelper")
        hint.setWordWrap(True)
        pl.addWidget(hint)
        from .config import PRESET_PROFILES
        for key, profile in PRESET_PROFILES.items():
            btn = QPushButton(profile['name'])
            btn.clicked.connect(lambda checked, k=key: self._apply_preset(k))
            pl.addWidget(btn)
        lay.addWidget(pg)
        lay.addStretch()
        return self._make_scroll(w)

    # ================================================================
    #                         HELPERS
    # ================================================================

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
                    f"color: #a0a8c0; font-size: 12px; padding: 5px 8px; }}"
                    f"QPushButton:hover {{ border-color: #00d4ff; color: #d0d8f0; }}"
                )
            else:
                btn.setStyleSheet(
                    f"QPushButton {{ background: rgba(0,160,220,30);"
                    f"border: 2px solid rgba(0,212,255,200); border-radius: 8px;"
                    f"color: #00d4ff; font-weight: 700; font-size: 12px; padding: 5px 8px; }}"
                )

    def _set_theme(self, theme_key):
        self._theme = theme_key
        self.config.set("general.theme", theme_key)
        self.config.save()
        self._load_wallpaper()
        self._update_theme_buttons()
        self.update()

    # ================================================================
    #                      EVENT HANDLERS
    # ================================================================

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

    def _toggle_descriptions(self):
        """Smooth collapsible toggle for effect descriptions."""
        if not self._desc_expanded:
            # Measure natural height
            self._desc_container.setMaximumHeight(16777215)
            target_h = self._desc_container.sizeHint().height()
            self._desc_container.setMaximumHeight(0)
            anim = QPropertyAnimation(self._desc_container, b"maximumHeight", self)
            anim.setDuration(300)
            anim.setEasingCurve(QEasingCurve.InOutCubic)
            anim.setStartValue(0)
            anim.setEndValue(target_h)
            anim.start(QPropertyAnimation.DeleteWhenStopped)
            self._desc_toggle.setText(t("anim.hide_desc"))
            self._desc_expanded = True
        else:
            anim = QPropertyAnimation(self._desc_container, b"maximumHeight", self)
            anim.setDuration(300)
            anim.setEasingCurve(QEasingCurve.InOutCubic)
            anim.setStartValue(self._desc_container.height())
            anim.setEndValue(0)
            anim.start(QPropertyAnimation.DeleteWhenStopped)
            self._desc_toggle.setText(t("anim.show_desc"))
            self._desc_expanded = False

    def _toggle_monitor_auto(self, state):
        if state == Qt.Checked:
            self._mon_auto = True
            self._mon_timer.start(3000)
            self._refresh_monitor()
        else:
            self._mon_auto = False
            self._mon_timer.stop()

    def _refresh_monitor(self):
        """Update system resource bars and detected games list."""
        try:
            import psutil

            cpu_pct = psutil.cpu_percent(interval=0)
            self._cpu_bar.setValue(int(cpu_pct))
            self._cpu_bar.setFormat(f"{cpu_pct:.0f}%")

            mem = psutil.virtual_memory()
            ram_pct = mem.percent
            used_gb = mem.used / (1024 ** 3)
            total_gb = mem.total / (1024 ** 3)
            self._ram_bar.setValue(int(ram_pct))
            self._ram_bar.setFormat(f"{ram_pct:.0f}%  ({used_gb:.1f}/{total_gb:.1f} GB)")

            game_list = []
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info['name']
                    if name in KNOWN_GAMES:
                        game_list.append(f"  {KNOWN_GAMES[name]}  ({name})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            if game_list:
                self._games_label.setText("\n".join(sorted(set(game_list))))
                self._games_label.setStyleSheet("color: #80e0a0; font-size: 12px; padding: 4px;")
            else:
                self._games_label.setText(t("mon.no_games"))
                self._games_label.setStyleSheet("color: #a0a8c0; font-size: 12px; padding: 4px;")
        except ImportError:
            self._cpu_bar.setFormat("N/A")
            self._ram_bar.setFormat("N/A")
            self._games_label.setText(t("mon.no_psutil"))

        # GPU via nvidia-smi
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=2,
                creationflags=0x08000000,  # CREATE_NO_WINDOW
            )
            if result.returncode == 0:
                gpu_pct = float(result.stdout.strip().split('\n')[0])
                self._gpu_bar.setValue(int(gpu_pct))
                self._gpu_bar.setFormat(f"{gpu_pct:.0f}%")
            else:
                self._gpu_bar.setValue(0)
                self._gpu_bar.setFormat("N/A")
        except Exception:
            self._gpu_bar.setValue(0)
            self._gpu_bar.setFormat("N/A")

    # ================================================================
    #                    APPLY / RESET / CONFIG
    # ================================================================

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

    # ================================================================
    #                      PROFILE MANAGEMENT
    # ================================================================

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

    # ================================================================
    #                       WINDOW EVENTS
    # ================================================================

    def showEvent(self, event):
        super().showEvent(event)
        if sys.platform == "win32":
            try:
                hwnd = int(self.winId())
                if not self._acrylic_done:
                    _enable_acrylic(hwnd)
                    self._acrylic_done = True
                # Remove WS_MAXIMIZEBOX to prevent Aero Snap maximize
                GWL_STYLE = -16
                WS_MAXIMIZEBOX = 0x00010000
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
                style &= ~WS_MAXIMIZEBOX
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
            except Exception:
                pass

    def changeEvent(self, event):
        """Prevent window from being maximized by Aero Snap (drag bug fix)."""
        super().changeEvent(event)
        from PyQt5.QtCore import QEvent
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMaximized:
                self.setWindowState(Qt.WindowNoState)
                QTimer.singleShot(0, lambda: self.setFixedSize(self.W, self.H))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.pos().y() <= 38:
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
        if self._drag_pos is not None:
            self._drag_pos = None
            # Re-enforce fixed size after drag (Aero Snap prevention)
            self.setFixedSize(self.W, self.H)
        super().mouseReleaseEvent(event)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.hide_to_tray.emit()

    # ================================================================
    #                   IMPORT CROSSHAIR FROM AI
    # ================================================================

    def _open_import_dialog(self):
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
