"""
Localization system for CrosshairX.
Supports Russian (ru) and English (en).
Plain text labels — no emojis, no Unicode symbols.
"""

_STRINGS = {
    # ---- App ----
    "app.title": {"ru": "CrosshairX", "en": "CrosshairX"},
    "app.subtitle": {"ru": "Кастомный прицел для игр", "en": "Custom Gaming Crosshair"},
    "app.tray_tooltip": {"ru": "CrosshairX — Прицел", "en": "CrosshairX — Crosshair"},

    # ---- Tray ----
    "tray.settings": {"ru": "Настройки", "en": "Settings"},
    "tray.toggle": {"ru": "Показать / скрыть", "en": "Show / Hide"},
    "tray.animation": {"ru": "Анимация", "en": "Animation"},
    "tray.profiles": {"ru": "Профили", "en": "Profiles"},
    "tray.quit": {"ru": "Выход", "en": "Quit"},
    "tray.overlay_on": {"ru": "Прицел включён", "en": "Crosshair ON"},
    "tray.overlay_off": {"ru": "Прицел выключен", "en": "Crosshair OFF"},
    "tray.anim_on": {"ru": "Анимация вкл", "en": "Animation ON"},
    "tray.anim_off": {"ru": "Анимация выкл", "en": "Animation OFF"},
    "tray.profile": {"ru": "Профиль", "en": "Profile"},

    # ---- Tabs ----
    "tab.crosshair": {"ru": "Прицел", "en": "Crosshair"},
    "tab.animation": {"ru": "Анимация", "en": "Animation"},
    "tab.display": {"ru": "Экран", "en": "Display"},
    "tab.monitor": {"ru": "Монитор", "en": "Monitor"},
    "tab.profiles": {"ru": "Профили", "en": "Profiles"},

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

    # ---- Styles (plain text) ----
    "style.cross":             {"ru": "Крест",          "en": "Cross"},
    "style.dot":               {"ru": "Точка",          "en": "Dot"},
    "style.circle":            {"ru": "Круг",           "en": "Circle"},
    "style.chevron":           {"ru": "Шеврон",         "en": "Chevron"},
    "style.diamond":           {"ru": "Ромб",           "en": "Diamond"},
    "style.crossdot":          {"ru": "Крест+Точка",    "en": "Cross+Dot"},
    "style.triangle":          {"ru": "Треугольник",    "en": "Triangle"},
    "style.crosshair_classic": {"ru": "Классический",   "en": "Classic"},
    "style.square":            {"ru": "Квадрат",        "en": "Square"},
    "style.plus_thin":         {"ru": "Тонкий крест",   "en": "Thin Plus"},
    "style.crosscircle":       {"ru": "Крест+Круг",     "en": "Cross+Circle"},
    "style.arrows":            {"ru": "Стрелки",        "en": "Arrows"},

    # ---- Animation tab ----
    "anim.settings": {"ru": "Настройки анимации", "en": "Animation Settings"},
    "anim.enable": {"ru": "Включить анимацию", "en": "Enable animation"},
    "anim.type": {"ru": "Тип:", "en": "Type:"},
    "anim.speed": {"ru": "Скорость:", "en": "Speed:"},
    "anim.intensity": {"ru": "Интенсивность:", "en": "Intensity:"},
    "anim.none":    {"ru": "Нет",         "en": "None"},
    "anim.pulse":   {"ru": "Пульсация",   "en": "Pulse"},
    "anim.rotate":  {"ru": "Вращение",    "en": "Rotate"},
    "anim.breathe": {"ru": "Дыхание",     "en": "Breathe"},
    "anim.rainbow": {"ru": "Радуга",      "en": "Rainbow"},
    "anim.recoil":  {"ru": "Отдача",      "en": "Recoil"},
    "anim.flash":   {"ru": "Вспышка",     "en": "Flash"},
    "anim.wave":    {"ru": "Волна",       "en": "Wave"},

    # ---- Animation descriptions ----
    "anim.desc_title": {"ru": "Описание эффектов", "en": "Effect descriptions"},
    "anim.show_desc": {"ru": "Показать описания эффектов", "en": "Show effect descriptions"},
    "anim.hide_desc": {"ru": "Скрыть описания", "en": "Hide descriptions"},
    "anim.desc.pulse":   {"ru": "Пульсация — плавное увеличение / уменьшение", "en": "Pulse — smooth grow / shrink"},
    "anim.desc.rotate":  {"ru": "Вращение — медленное вращение прицела", "en": "Rotate — slow rotation"},
    "anim.desc.breathe": {"ru": "Дыхание — появление / исчезание", "en": "Breathe — fade in / out"},
    "anim.desc.rainbow": {"ru": "Радуга — переливание цветов", "en": "Rainbow — color cycling"},
    "anim.desc.recoil":  {"ru": "Отдача — имитация отдачи оружия", "en": "Recoil — weapon recoil sim"},
    "anim.desc.flash":   {"ru": "Вспышка — периодические вспышки", "en": "Flash — periodic flash"},
    "anim.desc.wave":    {"ru": "Волна — волнообразное движение", "en": "Wave — wave movement"},

    # ---- Display tab ----
    "disp.settings": {"ru": "Настройки экрана", "en": "Display Settings"},
    "disp.theme": {"ru": "Тема оформления", "en": "App Theme"},
    "disp.monitor": {"ru": "Монитор:", "en": "Monitor:"},
    "disp.offset_x": {"ru": "Смещение X:", "en": "Offset X:"},
    "disp.offset_y": {"ru": "Смещение Y:", "en": "Offset Y:"},
    "disp.opacity": {"ru": "Прозрачность:", "en": "Opacity:"},
    "disp.fps": {"ru": "FPS:", "en": "FPS:"},
    "disp.hotkeys": {"ru": "Горячие клавиши", "en": "Hotkeys"},
    "disp.language": {"ru": "Язык / Language:", "en": "Language / Язык:"},

    # ---- Themes ----
    "theme.midnight": {"ru": "Полночь",  "en": "Midnight"},
    "theme.purple":   {"ru": "Фиолет",   "en": "Purple"},
    "theme.ocean":    {"ru": "Океан",     "en": "Ocean"},
    "theme.sakura":   {"ru": "Сакура",    "en": "Sakura"},

    # ---- Hotkey descriptions ----
    "hk.toggle":   {"ru": "Показать / скрыть прицел", "en": "Toggle crosshair"},
    "hk.next":     {"ru": "Следующий профиль",        "en": "Next profile"},
    "hk.prev":     {"ru": "Предыдущий профиль",       "en": "Previous profile"},
    "hk.anim":     {"ru": "Вкл / выкл анимацию",      "en": "Toggle animation"},
    "hk.settings": {"ru": "Открыть настройки",        "en": "Open settings"},

    # ---- Game Monitor tab ----
    "mon.system": {"ru": "Системные ресурсы", "en": "System Resources"},
    "mon.cpu": {"ru": "Процессор (CPU):", "en": "CPU:"},
    "mon.ram": {"ru": "Память (RAM):", "en": "RAM:"},
    "mon.gpu": {"ru": "Видеокарта (GPU):", "en": "GPU:"},
    "mon.gpu_temp": {"ru": "Темп. GPU:", "en": "GPU Temp:"},
    "mon.disk": {"ru": "Диск (C:):", "en": "Disk (C:):"},
    "mon.net_sent": {"ru": "Сеть (отправлено):", "en": "Net (sent):"},
    "mon.net_recv": {"ru": "Сеть (получено):", "en": "Net (received):"},
    "mon.uptime": {"ru": "Время работы:", "en": "Uptime:"},
    "mon.cpu_freq": {"ru": "Частота CPU:", "en": "CPU Freq:"},
    "mon.cpu_cores": {"ru": "Ядра / Потоки:", "en": "Cores / Threads:"},
    "mon.games": {"ru": "Обнаруженные игры", "en": "Detected Games"},
    "mon.no_games": {"ru": "Игры не обнаружены", "en": "No games detected"},
    "mon.refresh": {"ru": "Обновить", "en": "Refresh"},
    "mon.auto_refresh": {"ru": "Автообновление (3 сек)", "en": "Auto-refresh (3 sec)"},
    "mon.no_psutil": {"ru": "Установите psutil для мониторинга", "en": "Install psutil for monitoring"},
    "mon.process": {"ru": "Процесс", "en": "Process"},

    # ---- Profiles tab ----
    "prof.title": {"ru": "Профили прицелов", "en": "Crosshair Profiles"},
    "prof.profile": {"ru": "Профиль:", "en": "Profile:"},
    "prof.load":    {"ru": "Загрузить", "en": "Load"},
    "prof.save":    {"ru": "Сохранить", "en": "Save"},
    "prof.delete":  {"ru": "Удалить",   "en": "Delete"},
    "prof.refresh": {"ru": "Обновить",  "en": "Refresh"},
    "prof.presets": {"ru": "Готовые пресеты", "en": "Presets"},
    "prof.presets_hint": {"ru": "Выберите готовый пресет для быстрой настройки", "en": "Pick a preset for quick setup"},
    "prof.save_title":  {"ru": "Сохранить профиль", "en": "Save Profile"},
    "prof.save_prompt": {"ru": "Имя профиля:",      "en": "Profile name:"},
    "prof.del_title":   {"ru": "Удалить профиль",    "en": "Delete Profile"},
    "prof.del_confirm": {"ru": "Удалить профиль '{name}'?", "en": "Delete profile '{name}'?"},

    # ---- Buttons ----
    "btn.apply": {"ru": "Применить",       "en": "Apply"},
    "btn.reset": {"ru": "Сброс",           "en": "Reset"},
    "btn.hide":  {"ru": "Скрыть прицел",   "en": "Hide crosshair"},
    "btn.show":  {"ru": "Показать прицел",  "en": "Show crosshair"},
    "btn.quit":  {"ru": "Выход",            "en": "Quit"},

    # ---- Import crosshair from AI ----
    "prof.import_title": {"ru": "Импорт прицела", "en": "Import Crosshair"},
    "prof.import_hint": {
        "ru": "Создайте уникальный прицел с помощью ИИ и вставьте конфигурацию",
        "en": "Create a unique crosshair using AI and paste the config",
    },
    "prof.import_btn": {"ru": "Импорт из ИИ", "en": "Import from AI"},
    "prof.import_instruction": {
        "ru": "Скопируйте инструкцию ниже и отправьте любому ИИ-ассистенту "
              "(ChatGPT, Claude и др.). Затем вставьте полученный JSON сюда.",
        "en": "Copy the instruction below and send it to any AI assistant "
              "(ChatGPT, Claude, etc.). Then paste the returned JSON here.",
    },
    "prof.import_format": {
        "ru": ("Сгенерируй УНИКАЛЬНУЮ и КРЕАТИВНУЮ конфигурацию прицела для CrosshairX в формате JSON.\n"
               "ВАЖНО: придумай необычный и оригинальный прицел, которого НЕТ в стандартных пресетах.\n"
               "Используй нестандартные комбинации цветов, размеров и стилей.\n\n"
               "Поля:\n"
               '- "style": одно из ["cross","dot","circle","chevron","diamond",'
               '"crossdot","triangle","crosshair_classic","square","plus_thin",'
               '"crosscircle","arrows"]\n'
               '- "size": число 4-100\n'
               '- "thickness": число 1-10\n'
               '- "gap": число 0-30\n'
               '- "color": [R,G,B,A] (0-255) — используй яркие необычные цвета\n'
               '- "dot": true/false\n'
               '- "dot_size": число 1-10\n'
               '- "outline": true/false\n'
               '- "outline_thickness": число 1-5\n'
               '- "t_style": true/false\n\n'
               "Верни ТОЛЬКО JSON, без пояснений.\n"
               'Пример: {"style":"chevron","size":32,"thickness":3,"gap":8,'
               '"color":[255,100,50,230],"dot":true,"dot_size":3,'
               '"outline":true,"outline_thickness":2,"t_style":true}'),
        "en": ("Generate a UNIQUE and CREATIVE crosshair config for CrosshairX in JSON.\n"
               "IMPORTANT: create an original crosshair NOT found in standard presets.\n"
               "Use unusual color combos, sizes, and style combinations.\n\n"
               "Fields:\n"
               '- "style": one of ["cross","dot","circle","chevron","diamond",'
               '"crossdot","triangle","crosshair_classic","square","plus_thin",'
               '"crosscircle","arrows"]\n'
               '- "size": 4-100\n'
               '- "thickness": 1-10\n'
               '- "gap": 0-30\n'
               '- "color": [R,G,B,A] (0-255) — use bright unusual colors\n'
               '- "dot": true/false\n'
               '- "dot_size": 1-10\n'
               '- "outline": true/false\n'
               '- "outline_thickness": 1-5\n'
               '- "t_style": true/false\n\n'
               "Return ONLY JSON, no explanations.\n"
               'Example: {"style":"chevron","size":32,"thickness":3,"gap":8,'
               '"color":[255,100,50,230],"dot":true,"dot_size":3,'
               '"outline":true,"outline_thickness":2,"t_style":true}'),
    },
    "prof.import_copy_btn": {"ru": "Копировать инструкцию", "en": "Copy instruction"},
    "prof.import_paste_hint": {"ru": "Вставьте JSON конфигурацию:", "en": "Paste JSON config:"},
    "prof.import_apply_btn": {"ru": "Применить", "en": "Apply"},
    "prof.import_cancel": {"ru": "Отмена", "en": "Cancel"},
    "prof.import_success": {"ru": "Прицел успешно импортирован!", "en": "Crosshair imported!"},
    "prof.import_error_title": {"ru": "Ошибка импорта", "en": "Import Error"},
    "prof.import_error_msg": {"ru": "Не удалось прочитать JSON:", "en": "Failed to parse JSON:"},
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
