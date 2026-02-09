"""
Animation engine for CrosshairX.
Provides smooth animations: pulse, rotate, breathe, rainbow, recoil, etc.
"""

import time
import math
import colorsys


class AnimationEngine:
    """Produces per-frame animation state for the crosshair renderer."""

    def __init__(self):
        self._start_time = time.time()
        self._recoil_active = False
        self._recoil_start = 0.0

    def reset(self):
        """Reset animation timer."""
        self._start_time = time.time()

    def trigger_recoil(self):
        """Trigger a recoil animation (call on simulated shot)."""
        self._recoil_active = True
        self._recoil_start = time.time()

    def get_state(self, anim_config: dict) -> dict:
        """
        Calculate the current animation state.

        Args:
            anim_config: Animation config dict with keys: enabled, type, speed, intensity

        Returns:
            Dict with keys: size_mult, rotation, gap_offset, opacity, color_override
        """
        state = {
            "size_mult": 1.0,
            "rotation": 0.0,
            "gap_offset": 0.0,
            "opacity": 1.0,
            "color_override": None,
        }

        if not anim_config.get("enabled", True):
            return state

        anim_type = anim_config.get("type", "none")
        speed = anim_config.get("speed", 1.0)
        intensity = anim_config.get("intensity", 0.3)

        if anim_type == "none":
            return state

        t = (time.time() - self._start_time) * speed

        handler = getattr(self, f"_anim_{anim_type}", None)
        if handler:
            handler(t, intensity, state)

        return state

    # ===================== ANIMATION TYPES =====================

    def _anim_pulse(self, t: float, intensity: float, state: dict):
        """
        Pulsating size animation.
        The crosshair gently grows and shrinks.
        """
        pulse = math.sin(t * 3.0) * intensity
        state["size_mult"] = 1.0 + pulse * 0.3
        state["gap_offset"] = pulse * 2.0

    def _anim_rotate(self, t: float, intensity: float, state: dict):
        """
        Slow rotation animation.
        The crosshair rotates continuously.
        """
        state["rotation"] = (t * 45.0 * intensity) % 360.0

    def _anim_breathe(self, t: float, intensity: float, state: dict):
        """
        Breathing opacity animation.
        The crosshair fades in and out smoothly.
        """
        breath = (math.sin(t * 2.0) + 1.0) / 2.0  # 0.0 to 1.0
        min_opacity = max(0.3, 1.0 - intensity)
        state["opacity"] = min_opacity + breath * (1.0 - min_opacity)

    def _anim_rainbow(self, t: float, intensity: float, state: dict):
        """
        Rainbow color cycling animation.
        The crosshair cycles through all hue values.
        """
        hue = (t * 0.3 * intensity) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        state["color_override"] = [int(r * 255), int(g * 255), int(b * 255), 255]

    def _anim_recoil(self, t: float, intensity: float, state: dict):
        """
        Recoil simulation animation.
        The crosshair expands briefly then contracts, simulating weapon recoil.
        Also has a subtle idle sway.
        """
        # Idle sway
        sway = math.sin(t * 1.5) * intensity * 0.5
        state["gap_offset"] = sway

        # Active recoil
        if self._recoil_active:
            elapsed = time.time() - self._recoil_start
            if elapsed < 0.5:
                # Sharp expand then contract
                recoil_curve = math.exp(-elapsed * 8.0) * intensity * 15.0
                state["gap_offset"] += recoil_curve
                state["size_mult"] = 1.0 + math.exp(-elapsed * 6.0) * intensity * 0.5
            else:
                self._recoil_active = False

    def _anim_flash(self, t: float, intensity: float, state: dict):
        """
        Flash/blink animation.
        The crosshair briefly flashes brighter.
        """
        flash_period = 2.0
        flash_duration = 0.1
        phase = t % flash_period
        if phase < flash_duration:
            state["opacity"] = 1.0
            state["size_mult"] = 1.0 + intensity * 0.2
        else:
            state["opacity"] = max(0.6, 1.0 - intensity * 0.3)

    def _anim_wave(self, t: float, intensity: float, state: dict):
        """
        Wave animation.
        Creates a wavy movement effect on the gap.
        """
        wave = math.sin(t * 4.0) * math.cos(t * 2.5) * intensity
        state["gap_offset"] = wave * 4.0
        state["size_mult"] = 1.0 + math.sin(t * 2.0) * intensity * 0.1
