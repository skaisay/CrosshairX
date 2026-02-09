"""
Transparent overlay window for CrosshairX.
Ultra-lightweight, click-through transparent overlay.
Optimized: smart repaint region, adaptive FPS, minimal CPU/GPU usage.
"""

import sys
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QWidget

from .crosshair import CrosshairRenderer
from .animations import AnimationEngine
from .config import Config


class OverlayWindow(QWidget):
    """
    Ultra-lightweight transparent overlay.
    Only repaints the small crosshair region, not the full screen.
    Adaptive FPS: high when animating, low when idle.
    """

    IDLE_FPS = 10      # FPS when static (no animation)
    ACTIVE_FPS = 60    # FPS when animating (smooth, low CPU)

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.renderer = CrosshairRenderer()
        self.animation = AnimationEngine()
        self._visible = True
        self._animation_enabled = config.get("animation.enabled", True)
        self._prev_margin = 60  # Track previous crosshair size for clearing

        self._setup_window()
        self._setup_timer()

    def _setup_window(self):
        """Configure click-through transparent overlay."""
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self._update_geometry()

    def _update_geometry(self):
        """Cover the selected monitor."""
        app = QApplication.instance()
        screens = app.screens()
        idx = self.config.get("display.monitor", 0)
        screen = screens[idx] if idx < len(screens) else app.primaryScreen()
        geo = screen.geometry()
        self.setGeometry(geo)
        self._center_x = geo.width() / 2 + self.config.get("display.offset_x", 0)
        self._center_y = geo.height() / 2 + self.config.get("display.offset_y", 0)

    def _setup_timer(self):
        """Smart adaptive timer."""
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._update_timer_interval()
        self._timer.start()

    def _update_timer_interval(self):
        """Set FPS based on animation state."""
        anim_type = self.config.get("animation.type", "none")
        if self._animation_enabled and anim_type != "none":
            fps = min(self.config.get("display.fps", 60), self.ACTIVE_FPS)
        else:
            fps = self.IDLE_FPS
        self._timer.setInterval(max(1, int(1000 / fps)))

    def _tick(self):
        """Only repaint a small region around the crosshair."""
        if not self._visible:
            return
        margin = self.config.get("crosshair.size", 20) + 40
        # Use the larger of current and previous margin to clear old remnants
        clear_margin = max(margin, self._prev_margin)
        self._prev_margin = margin
        x = int(self._center_x - clear_margin)
        y = int(self._center_y - clear_margin)
        self.update(x, y, clear_margin * 2, clear_margin * 2)

    def paintEvent(self, event):
        """Render the crosshair - minimal draw area."""
        if not self._visible:
            return

        painter = QPainter(self)
        # Clear the region first — erase any old crosshair pixels
        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.fillRect(event.rect(), Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.setRenderHint(QPainter.Antialiasing, True)

        anim_config = self.config.data.get("animation", {})
        if not self._animation_enabled:
            anim_config = dict(anim_config)
            anim_config["enabled"] = False

        anim_state = self.animation.get_state(anim_config)
        opacity = self.config.get("display.opacity", 1.0)
        anim_state["opacity"] = anim_state.get("opacity", 1.0) * opacity

        self.renderer.draw(
            painter, self._center_x, self._center_y,
            self.config.data.get("crosshair", {}), anim_state
        )
        painter.end()

    # ---- Public API ----

    def toggle_visibility(self):
        self._visible = not self._visible
        self.show() if self._visible else self.hide()
        return self._visible

    def toggle_animation(self):
        self._animation_enabled = not self._animation_enabled
        self.config.set("animation.enabled", self._animation_enabled)
        self._update_timer_interval()
        return self._animation_enabled

    def set_visible(self, visible: bool):
        self._visible = visible
        self.show() if visible else self.hide()

    def refresh_config(self):
        """Reload config and recalculate geometry + timer."""
        self._update_geometry()
        self._animation_enabled = self.config.get("animation.enabled", True)
        self._update_timer_interval()
        # Force full repaint so old crosshair is completely cleared
        self.repaint()

    def trigger_recoil(self):
        self.animation.trigger_recoil()
