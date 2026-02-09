"""
CrosshairX — Main Entry Point
GPU-Accelerated Custom Crosshair Overlay for Gaming.

Usage:
    python -m crosshair_app          — Launch the app
    python -m crosshair_app --help   — Show help
    python -m crosshair_app --tray   — Launch minimized to tray
"""

import sys
import os
import ctypes
import threading

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen

from .config import Config
from .overlay import OverlayWindow
from .settings import SettingsPanel
from .i18n import t, set_language


def create_app_icon() -> QIcon:
    """Create a simple crosshair icon programmatically (no external files needed)."""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw circle
    pen = QPen(QColor(0, 212, 255), 3)
    painter.setPen(pen)
    painter.drawEllipse(8, 8, 48, 48)

    # Draw cross
    pen = QPen(QColor(0, 255, 100), 2)
    painter.setPen(pen)
    painter.drawLine(32, 4, 32, 60)
    painter.drawLine(4, 32, 60, 32)

    # Center dot
    painter.setBrush(QBrush(QColor(255, 50, 50)))
    painter.setPen(QPen(QColor(255, 50, 50), 1))
    painter.drawEllipse(28, 28, 8, 8)

    painter.end()
    return QIcon(pixmap)


class CrosshairXApp:
    """Main application controller."""

    def __init__(self, start_minimized: bool = False):
        # Enable DPI awareness on Windows
        if sys.platform == "win32":
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass

        self.app = QApplication(sys.argv)
        self.app.setApplicationName("CrosshairX")
        self.app.setQuitOnLastWindowClosed(False)

        self.icon = create_app_icon()
        self.app.setWindowIcon(self.icon)

        # Load config
        self.config = Config()
        set_language(self.config.get("general.language", "ru"))

        # Create overlay
        self.overlay = OverlayWindow(self.config)

        # Create settings panel
        self.settings = SettingsPanel(self.config, self.overlay)
        self.settings.close_app.connect(self.quit)

        # Create system tray
        self._setup_tray()

        # Setup global hotkeys
        self._setup_hotkeys()

        # Show windows
        self.overlay.show()
        if not start_minimized:
            self.settings.show()

    def _setup_tray(self):
        """Setup system tray icon with context menu."""
        self.tray = QSystemTrayIcon(self.icon, self.app)

        menu = QMenu()

        action_settings = QAction(f"⚙️ {t('tray.settings')}", menu)
        action_settings.triggered.connect(self._show_settings)
        menu.addAction(action_settings)

        action_toggle = QAction(f"👁️ {t('tray.toggle')}", menu)
        action_toggle.triggered.connect(self._toggle_overlay)
        menu.addAction(action_toggle)

        action_anim = QAction(f"✨ {t('tray.animation')}", menu)
        action_anim.triggered.connect(self._toggle_animation)
        menu.addAction(action_anim)

        menu.addSeparator()

        profiles_menu = QMenu(f"📁 {t('tray.profiles')}", menu)
        for name in self.config.list_profiles():
            action = QAction(name, profiles_menu)
            action.triggered.connect(lambda checked, n=name: self._switch_profile(n))
            profiles_menu.addAction(action)
        menu.addMenu(profiles_menu)

        menu.addSeparator()

        action_quit = QAction(f"❌ {t('tray.quit')}", menu)
        action_quit.triggered.connect(self.quit)
        menu.addAction(action_quit)

        self.tray.setContextMenu(menu)
        self.tray.setToolTip(t('app.tray_tooltip'))
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _setup_hotkeys(self):
        """Setup global hotkeys using a background thread (Windows)."""
        if sys.platform != "win32":
            # Fallback: use a timer-based simple check
            return

        self._hotkey_timer = QTimer()
        self._hotkey_timer.timeout.connect(self._check_hotkeys)
        self._hotkey_timer.start(50)  # Check every 50ms

        self._key_states = {}

    def _check_hotkeys(self):
        """Poll for hotkey presses (Windows-compatible, no extra dependencies)."""
        if sys.platform != "win32":
            return

        try:
            GetAsyncKeyState = ctypes.windll.user32.GetAsyncKeyState

            hotkey_map = {
                0x75: self._toggle_overlay,     # F6
                0x76: self._next_profile,       # F7
                0x77: self._prev_profile,       # F8
                0x78: self._toggle_animation,   # F9
                0x79: self._show_settings,      # F10
            }

            for vk, handler in hotkey_map.items():
                state = GetAsyncKeyState(vk)
                was_pressed = self._key_states.get(vk, False)
                is_pressed = bool(state & 0x8000)

                if is_pressed and not was_pressed:
                    handler()

                self._key_states[vk] = is_pressed

        except Exception:
            pass

    # ===================== ACTIONS =====================

    def _show_settings(self):
        """Show settings panel."""
        self.settings.show()
        self.settings.raise_()
        self.settings.activateWindow()

    def _toggle_overlay(self):
        """Toggle overlay visibility."""
        visible = self.overlay.toggle_visibility()
        self.tray.showMessage(
            "CrosshairX",
            t('tray.overlay_on') if visible else t('tray.overlay_off'),
            QSystemTrayIcon.Information, 1000
        )

    def _toggle_animation(self):
        """Toggle animations."""
        enabled = self.overlay.toggle_animation()
        self.tray.showMessage(
            "CrosshairX",
            t('tray.anim_on') if enabled else t('tray.anim_off'),
            QSystemTrayIcon.Information, 1000
        )

    def _next_profile(self):
        name = self.config.next_profile()
        if name:
            self.overlay.refresh_config()
            self.settings._load_from_config()
            self.tray.showMessage("CrosshairX", f"{t('tray.profile')}: {name}", QSystemTrayIcon.Information, 1000)

    def _prev_profile(self):
        name = self.config.prev_profile()
        if name:
            self.overlay.refresh_config()
            self.settings._load_from_config()
            self.tray.showMessage("CrosshairX", f"{t('tray.profile')}: {name}", QSystemTrayIcon.Information, 1000)

    def _switch_profile(self, name: str):
        if self.config.load_profile(name):
            self.overlay.refresh_config()
            self.settings._load_from_config()
            self.tray.showMessage("CrosshairX", f"{t('tray.profile')}: {name}", QSystemTrayIcon.Information, 1000)

    def _on_tray_activated(self, reason):
        """Handle tray icon clicks."""
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_settings()

    def quit(self):
        """Quit the application."""
        self.config.save()
        self.tray.hide()
        self.app.quit()

    def run(self) -> int:
        """Start the application event loop."""
        return self.app.exec_()


def main():
    """CLI entry point."""
    start_minimized = "--tray" in sys.argv or "--minimized" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
╔══════════════════════════════════════════════════════╗
║         CrosshairX — Custom Crosshair Overlay        ║
║         GPU-Accelerated • For Roblox & FPS           ║
╚══════════════════════════════════════════════════════╝

Usage:
    crosshairx              Launch with settings panel
    crosshairx --tray       Launch minimized to system tray
    crosshairx --help       Show this help message

Hotkeys:
    F6   — Toggle overlay on/off
    F7   — Next profile
    F8   — Previous profile
    F9   — Toggle animation
    F10  — Open settings

Profiles are stored in: %APPDATA%/CrosshairX/profiles/
""")
        return

    app = CrosshairXApp(start_minimized=start_minimized)
    sys.exit(app.run())


if __name__ == "__main__":
    main()
