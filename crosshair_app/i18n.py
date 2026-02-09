"""
Localization system for CrosshairX.
Supports Russian (ru) and English (en).
"""

_STRINGS = {
    # ---- App ----
    "app.title": {"ru": "⊕ CrosshairX", "en": "⊕ CrosshairX"},
    "app.subtitle": {"ru": "Кастомный прицел для игр", "en": "Custom Gaming Crosshair"},
    "app.tray_tooltip": {"ru": "CrosshairX — Прицел", "en": "CrosshairX — Crosshair"},

    # ---- Tray ----
    "tray.settings": {"ru": "Настройки", "en": "Settings"},
    "tray.toggle": {"ru": "Показать/скрыть", "en": "Show/Hide"},
    "tray.animation": {"ru": "Анимация", "en": "Animation"},
    "tray.profiles": {"ru": "Профили", "en": "Profiles"},
    "tray.quit": {"ru": "Выход", "en": "Quit"},
    "tray.overlay_on": {"ru": "Прицел включён ✅", "en": "Crosshair ON ✅"},
    "tray.overlay_off": {"ru": "Прицел выключен ❌", "en": "Crosshair OFF ❌"},
    "tray.anim_on": {"ru": "Анимация вкл ✨", "en": "Animation ON ✨"},
    "tray.anim_off": {"ru": "Анимация выкл", "en": "Animation OFF"},
    "tray.profile": {"ru": "Профиль", "en": "Profile"},

    # ---- Tabs ----
    "tab.crosshair": {"ru": "🎯 Прицел", "en": "🎯 Crosshair"},
    "tab.animation": {"ru": "✨ Анимация", "en": "✨ Animation"},
    "tab.display": {"ru": "🖥 Экран", "en": "🖥 Display"},
    "tab.profiles": {"ru": "📁 Профили", "en": "📁 Profiles"},

    # ---- Crosshair tab ----
    "xhair.preview": {"ru": "Превью", "en": "Preview"},
    "xhair.style": {"ru": "Стиль", "en": "Style"},
    "xhair.color": {"ru": "Цвет:", "en": "Color:"},
    "xhair.t_style": {"ru": "T-стиль", "en": "T-style"},
    "xhair.params": {"ru": "Параметры", "en": "Parameters"},
    "xhair.size": {"ru": "Размер:", "en": "Size:"},
    "xhair.thickness": {"ru": "Толщина:", "en": "Thickness:"},
    "xhair.gap": {"ru": "Промежуток:", "en": "Gap:"},
    "xhair.dot": {"ru": "Точка в центре", "en": "Center dot"},
    "xhair.dot_size": {"ru": "Размер:", "en": "Size:"},
    "xhair.outline": {"ru": "Обводка", "en": "Outline"},
    "xhair.outline_thick": {"ru": "Толщина:", "en": "Thickness:"},
    "xhair.pick_color": {"ru": "Выберите цвет прицела", "en": "Choose crosshair color"},

    # ---- Styles ----
    "style.cross": {"ru": "✚ Крест", "en": "✚ Cross"},
    "style.dot": {"ru": "● Точка", "en": "● Dot"},
    "style.circle": {"ru": "○ Круг", "en": "○ Circle"},
    "style.chevron": {"ru": "❱ Шеврон", "en": "❱ Chevron"},
    "style.diamond": {"ru": "◇ Ромб", "en": "◇ Diamond"},
    "style.crossdot": {"ru": "⊕ Крест+Точка", "en": "⊕ Cross+Dot"},
    "style.triangle": {"ru": "△ Треугольник", "en": "△ Triangle"},
    "style.crosshair_classic": {"ru": "⊕ Классический", "en": "⊕ Classic"},

    # ---- Animation tab ----
    "anim.settings": {"ru": "Анимация", "en": "Animation"},
    "anim.enable": {"ru": "Включить анимацию", "en": "Enable animation"},
    "anim.type": {"ru": "Тип:", "en": "Type:"},
    "anim.speed": {"ru": "Скорость:", "en": "Speed:"},
    "anim.intensity": {"ru": "Интенсивность:", "en": "Intensity:"},
    "anim.none": {"ru": "Нет", "en": "None"},
    "anim.pulse": {"ru": "💫 Пульсация", "en": "💫 Pulse"},
    "anim.rotate": {"ru": "🔄 Вращение", "en": "🔄 Rotate"},
    "anim.breathe": {"ru": "🌬 Дыхание", "en": "🌬 Breathe"},
    "anim.rainbow": {"ru": "🌈 Радуга", "en": "🌈 Rainbow"},
    "anim.recoil": {"ru": "💥 Отдача", "en": "💥 Recoil"},
    "anim.flash": {"ru": "⚡ Вспышка", "en": "⚡ Flash"},
    "anim.wave": {"ru": "🌊 Волна", "en": "🌊 Wave"},

    # ---- Animation descriptions ----
    "anim.desc.pulse": {"ru": "💫 Пульсация — плавное увеличение/уменьшение", "en": "💫 Pulse — smooth grow/shrink"},
    "anim.desc.rotate": {"ru": "🔄 Вращение — медленное вращение", "en": "🔄 Rotate — slow rotation"},
    "anim.desc.breathe": {"ru": "🌬 Дыхание — появление/исчезание", "en": "🌬 Breathe — fade in/out"},
    "anim.desc.rainbow": {"ru": "🌈 Радуга — переливание цветов", "en": "🌈 Rainbow — color cycling"},
    "anim.desc.recoil": {"ru": "💥 Отдача — имитация отдачи", "en": "💥 Recoil — weapon recoil sim"},
    "anim.desc.flash": {"ru": "⚡ Вспышка — периодические вспышки", "en": "⚡ Flash — periodic flash"},
    "anim.desc.wave": {"ru": "🌊 Волна — волнообразное движение", "en": "🌊 Wave — wave movement"},

    # ---- Display tab ----
    "disp.settings": {"ru": "Экран", "en": "Display"},
    "disp.monitor": {"ru": "Монитор:", "en": "Monitor:"},
    "disp.offset_x": {"ru": "Смещение X:", "en": "Offset X:"},
    "disp.offset_y": {"ru": "Смещение Y:", "en": "Offset Y:"},
    "disp.opacity": {"ru": "Прозрачность:", "en": "Opacity:"},
    "disp.fps": {"ru": "FPS:", "en": "FPS:"},
    "disp.hotkeys": {"ru": "Горячие клавиши", "en": "Hotkeys"},
    "disp.language": {"ru": "Язык / Language:", "en": "Language / Язык:"},

    # ---- Hotkey descriptions ----
    "hk.toggle": {"ru": "Показать / скрыть прицел", "en": "Toggle crosshair"},
    "hk.next": {"ru": "Следующий профиль", "en": "Next profile"},
    "hk.prev": {"ru": "Предыдущий профиль", "en": "Previous profile"},
    "hk.anim": {"ru": "Вкл / выкл анимацию", "en": "Toggle animation"},
    "hk.settings": {"ru": "Открыть настройки", "en": "Open settings"},

    # ---- Profiles tab ----
    "prof.title": {"ru": "Профили прицелов", "en": "Crosshair Profiles"},
    "prof.profile": {"ru": "Профиль:", "en": "Profile:"},
    "prof.load": {"ru": "📂 Загрузить", "en": "📂 Load"},
    "prof.save": {"ru": "💾 Сохранить", "en": "💾 Save"},
    "prof.delete": {"ru": "🗑 Удалить", "en": "🗑 Delete"},
    "prof.refresh": {"ru": "🔄 Обновить", "en": "🔄 Refresh"},
    "prof.presets": {"ru": "Готовые пресеты", "en": "Presets"},
    "prof.save_title": {"ru": "Сохранить профиль", "en": "Save Profile"},
    "prof.save_prompt": {"ru": "Имя профиля:", "en": "Profile name:"},
    "prof.del_title": {"ru": "Удалить профиль", "en": "Delete Profile"},
    "prof.del_confirm": {"ru": "Удалить профиль '{name}'?", "en": "Delete profile '{name}'?"},

    # ---- Buttons ----
    "btn.apply": {"ru": "✅ Применить", "en": "✅ Apply"},
    "btn.reset": {"ru": "🔄 Сброс", "en": "🔄 Reset"},
    "btn.hide": {"ru": "👁 Скрыть прицел", "en": "👁 Hide crosshair"},
    "btn.show": {"ru": "👁 Показать прицел", "en": "👁 Show crosshair"},
}

_current_lang = "ru"


def set_language(lang: str):
    """Set current language ('ru' or 'en')."""
    global _current_lang
    _current_lang = lang if lang in ("ru", "en") else "ru"


def get_language() -> str:
    return _current_lang


def t(key: str, **kwargs) -> str:
    """Get translated string by key. Supports {name} formatting."""
    entry = _STRINGS.get(key)
    if not entry:
        return key
    text = entry.get(_current_lang, entry.get("en", key))
    if kwargs:
        text = text.format(**kwargs)
    return text
