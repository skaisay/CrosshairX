"""
Configuration management for CrosshairX.
Handles loading, saving, and managing crosshair profiles.
"""

import json
import os
from pathlib import Path
from typing import Any


# Default directories
APP_DIR = Path(os.environ.get("APPDATA", Path.home())) / "CrosshairX"
CONFIG_FILE = APP_DIR / "config.json"
PROFILES_DIR = APP_DIR / "profiles"


# === Default Configuration ===
DEFAULT_CONFIG = {
    "crosshair": {
        "style": "cross",           # cross, dot, circle, chevron, diamond, crossdot, custom
        "size": 20,                  # Overall size in pixels
        "thickness": 2,              # Line thickness
        "gap": 4,                    # Center gap (for cross style)
        "color": [0, 255, 0, 255],  # RGBA - green by default
        "outline": True,             # Draw dark outline for visibility
        "outline_color": [0, 0, 0, 180],
        "outline_thickness": 1,
        "dot": True,                 # Show center dot
        "dot_size": 2,
        "t_style": False,            # T-style (no top line)
    },
    "animation": {
        "enabled": True,
        "type": "pulse",             # pulse, rotate, breathe, rainbow, recoil, none
        "speed": 1.0,                # Animation speed multiplier
        "intensity": 0.3,            # Animation intensity (0.0 - 1.0)
    },
    "display": {
        "monitor": 0,                # Primary monitor
        "offset_x": 0,               # Offset from center X
        "offset_y": 0,               # Offset from center Y
        "opacity": 1.0,              # Global opacity
        "fps": 60,                   # Overlay refresh rate (60 = smooth + low CPU)
    },
    "hotkeys": {
        "toggle_overlay": "F6",      # Show/hide overlay
        "next_profile": "F7",        # Switch to next profile
        "prev_profile": "F8",        # Switch to previous profile
        "toggle_animation": "F9",    # Enable/disable animation
        "open_settings": "F10",      # Open settings panel
    },
    "general": {
        "start_minimized": False,
        "start_with_windows": False,
        "current_profile": "default",
        "language": "ru",
        "gpu_acceleration": True,
    }
}

# === Preset Profiles ===
PRESET_PROFILES = {
    "default": {
        "name": "Default Green",
        "crosshair": {"style": "cross", "size": 20, "thickness": 2, "gap": 4,
                       "color": [0, 255, 0, 255], "dot": True, "dot_size": 2},
        "animation": {"type": "none", "speed": 1.0, "intensity": 0.3},
    },
    "roblox_fps": {
        "name": "Roblox FPS",
        "crosshair": {"style": "crossdot", "size": 16, "thickness": 2, "gap": 3,
                       "color": [255, 50, 50, 255], "dot": True, "dot_size": 3},
        "animation": {"type": "pulse", "speed": 0.8, "intensity": 0.2},
    },
    "sniper": {
        "name": "Sniper Dot",
        "crosshair": {"style": "dot", "size": 6, "thickness": 1, "gap": 0,
                       "color": [255, 0, 0, 255], "dot": True, "dot_size": 3},
        "animation": {"type": "breathe", "speed": 0.5, "intensity": 0.4},
    },
    "rainbow_circle": {
        "name": "Rainbow Circle",
        "crosshair": {"style": "circle", "size": 24, "thickness": 2, "gap": 0,
                       "color": [255, 255, 255, 255], "dot": True, "dot_size": 2},
        "animation": {"type": "rainbow", "speed": 1.5, "intensity": 1.0},
    },
    "competitive": {
        "name": "Competitive",
        "crosshair": {"style": "cross", "size": 12, "thickness": 1, "gap": 2,
                       "color": [0, 255, 255, 255], "dot": False, "dot_size": 0,
                       "t_style": True},
        "animation": {"type": "none", "speed": 1.0, "intensity": 0.0},
    },
    "diamond": {
        "name": "Diamond Pro",
        "crosshair": {"style": "diamond", "size": 18, "thickness": 2, "gap": 0,
                       "color": [255, 165, 0, 255], "dot": True, "dot_size": 2},
        "animation": {"type": "rotate", "speed": 0.3, "intensity": 0.5},
    },
    "chevron": {
        "name": "Chevron Tactical",
        "crosshair": {"style": "chevron", "size": 20, "thickness": 2, "gap": 3,
                       "color": [255, 220, 0, 255], "dot": True, "dot_size": 2},
        "animation": {"type": "recoil", "speed": 1.0, "intensity": 0.3},
    },
}


class Config:
    """Manages application configuration with profile support."""

    def __init__(self):
        self._config: dict = {}
        self._ensure_dirs()
        self.load()

    def _ensure_dirs(self):
        """Create config directories if they don't exist."""
        APP_DIR.mkdir(parents=True, exist_ok=True)
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    def load(self):
        """Load configuration from file, or create default."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
                # Merge with defaults for any missing keys
                self._config = self._deep_merge(DEFAULT_CONFIG, self._config)
            except (json.JSONDecodeError, IOError):
                self._config = DEFAULT_CONFIG.copy()
        else:
            self._config = DEFAULT_CONFIG.copy()
            self._install_preset_profiles()
            self.save()

    def save(self):
        """Save configuration to file."""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"[Config] Error saving config: {e}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a config value using dot notation. e.g. 'crosshair.color'"""
        keys = key_path.split(".")
        val = self._config
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def set(self, key_path: str, value: Any):
        """Set a config value using dot notation."""
        keys = key_path.split(".")
        d = self._config
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value

    @property
    def data(self) -> dict:
        return self._config

    # --- Profile Management ---

    def _install_preset_profiles(self):
        """Save all preset profiles to disk."""
        for name, profile in PRESET_PROFILES.items():
            path = PROFILES_DIR / f"{name}.json"
            if not path.exists():
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(profile, f, indent=2)

    def list_profiles(self) -> list[str]:
        """List available profile names."""
        profiles = []
        for p in PROFILES_DIR.glob("*.json"):
            profiles.append(p.stem)
        return sorted(profiles)

    def load_profile(self, name: str) -> bool:
        """Load and apply a profile."""
        path = PROFILES_DIR / f"{name}.json"
        if not path.exists():
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                profile = json.load(f)
            # Apply profile settings on top of current config
            if "crosshair" in profile:
                for k, v in profile["crosshair"].items():
                    self.set(f"crosshair.{k}", v)
            if "animation" in profile:
                for k, v in profile["animation"].items():
                    self.set(f"animation.{k}", v)
            self.set("general.current_profile", name)
            self.save()
            return True
        except (json.JSONDecodeError, IOError):
            return False

    def save_profile(self, name: str):
        """Save current crosshair+animation settings as a profile."""
        profile = {
            "name": name,
            "crosshair": self._config.get("crosshair", {}),
            "animation": self._config.get("animation", {}),
        }
        path = PROFILES_DIR / f"{name}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)

    def delete_profile(self, name: str) -> bool:
        """Delete a profile."""
        path = PROFILES_DIR / f"{name}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def next_profile(self) -> str:
        """Switch to the next profile and return its name."""
        profiles = self.list_profiles()
        if not profiles:
            return ""
        current = self.get("general.current_profile", "default")
        try:
            idx = profiles.index(current)
            idx = (idx + 1) % len(profiles)
        except ValueError:
            idx = 0
        self.load_profile(profiles[idx])
        return profiles[idx]

    def prev_profile(self) -> str:
        """Switch to the previous profile and return its name."""
        profiles = self.list_profiles()
        if not profiles:
            return ""
        current = self.get("general.current_profile", "default")
        try:
            idx = profiles.index(current)
            idx = (idx - 1) % len(profiles)
        except ValueError:
            idx = 0
        self.load_profile(profiles[idx])
        return profiles[idx]

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """Deep merge override into base, returning new dict."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Config._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
