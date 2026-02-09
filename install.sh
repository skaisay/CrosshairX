#!/bin/bash
# CrosshairX — Install Script (Linux/macOS)
# Usage: chmod +x install.sh && ./install.sh

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║       CrosshairX — Custom Crosshair Overlay          ║"
echo "║       GPU-Accelerated • For Roblox & FPS             ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[!] Python3 не найден! Установите: sudo apt install python3 python3-pip"
    exit 1
fi

echo "[✓] Python3 найден: $(python3 --version)"
echo ""

# Install dependencies
echo "[*] Устанавливаю зависимости..."
pip3 install --upgrade pip
pip3 install -r requirements.txt
echo "[✓] Зависимости установлены"
echo ""

# Install the app
echo "[*] Устанавливаю CrosshairX..."
pip3 install -e .

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║            ✅ Установка завершена!                    ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "Запуск: crosshairx"
echo "Или:    python3 -m crosshair_app"
echo ""

read -p "Запустить CrosshairX сейчас? (y/n): " RUN
if [[ "$RUN" == "y" || "$RUN" == "Y" ]]; then
    echo "[*] Запускаю CrosshairX..."
    crosshairx &
fi
