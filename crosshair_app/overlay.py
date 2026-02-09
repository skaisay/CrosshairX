"""
Transparent overlay window for CrosshairX.
Ultra-lightweight, click-through transparent overlay.
Optimized: adaptive FPS, minimal CPU/GPU usage.
"""

import sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QApplication, QWidget

from .crosshair import CrosshairRenderer
from .animations import AnimationEngine
from .config import Config


class OverlayWindow(QWidget):
    """
    Ultra-lightweight transparent overlay.
    Uses hide()/show() for visibility — guarantees clean clearing.
    Adaptive FPS: high when animating, low when idle.
    """

    IDLE_FPS = 5
    ACTIVE_FPS = 60

    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.renderer = CrosshairRenderer()
        self.animation = AnimationEngine()
        self._visible = False  # Start hidden — no crosshair until user applies
        self._animation_enabled = config.get("animation.enabled", True)

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
        """Trigger repaint."""
        if not self._visible:
            return
        self.update()

    def paintEvent(self, event):
        """Render the crosshair."""
        if not self._visible:
            return

        painter = QPainter(self)
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

    def toggle_visibility(self) -> bool:
        """Toggle overlay on/off. Uses hide()/show() for clean clearing."""
        self._visible = not self._visible
        if self._visible:
            self.show()
            self.raise_()
        else:
            self.hide()
        return self._visible

    def toggle_animation(self) -> bool:
        self._animation_enabled = not self._animation_enabled
        self.config.set("animation.enabled", self._animation_enabled)
        self._update_timer_interval()
        return self._animation_enabled

    def set_visible(self, visible: bool):
        self._visible = visible
        if visible:
            self.show()
            self.raise_()
        else:
            self.hide()

    def shutdown(self):
        """Completely stop overlay — timer, visibility, widget. For app quit."""
        self._visible = False
        self._timer.stop()
        self.hide()
        self.close()
        self.deleteLater()

    def refresh_config(self):
        """Reload config and recalculate geometry + timer."""
        self._update_geometry()
        self._animation_enabled = self.config.get("animation.enabled", True)
        self._update_timer_interval()
        # Hide and re-show to force clean redraw (clears old pixels completely)
        if self._visible:
            self.hide()
            self.show()
            self.raise_()

    def trigger_recoil(self):
        self.animation.trigger_recoil()
