@echo off
chcp 65001 >nul 2>&1
title CrosshairX — Installer
echo.
echo ===================================================
echo   CrosshairX — Custom Crosshair Overlay Installer
echo ===================================================
echo.

REM ── Check if standalone EXE exists ──
if exist "dist\CrosshairX.exe" (
    echo [OK] Found CrosshairX.exe — launching directly!
    echo      No Python needed.
    echo.
    start "" "dist\CrosshairX.exe"
    goto :end
)

REM ── Check Python ──
echo [*] Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python found.
    goto :install_deps
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python found (py launcher).
    goto :install_deps_py
)

REM ── Python not found — try to install via winget ──
echo [!] Python not found on this system.
echo.
echo Options:
echo   1. Install Python automatically (requires winget)
echo   2. Exit and install Python manually
echo.
choice /C 12 /M "Choose option (1 or 2)"
if %errorlevel% equ 1 (
    echo.
    echo [*] Installing Python 3.11 via winget...
    winget install Python.Python.3.11 --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo [!] Auto-install failed. Please download Python from:
        echo     https://www.python.org/downloads/
        echo     Make sure to check "Add Python to PATH"!
        pause
        goto :end
    )
    echo [OK] Python installed! Refreshing PATH...
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python311\;%LOCALAPPDATA%\Programs\Python\Python311\Scripts\"
    goto :install_deps
) else (
    echo.
    echo Please download Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during install!
    echo Then run this script again.
    pause
    goto :end
)

:install_deps
echo.
echo [*] Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [!] Failed to install dependencies.
    pause
    goto :end
)
echo [OK] Dependencies installed.
echo.
echo [*] Launching CrosshairX...
echo.
echo    Hotkeys: F6=Toggle  F7/F8=Profiles  F9=Animation  F10=Settings
echo.
python -m crosshair_app
goto :end

:install_deps_py
echo.
echo [*] Installing dependencies...
py -m pip install --upgrade pip >nul 2>&1
py -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [!] Failed to install dependencies.
    pause
    goto :end
)
echo [OK] Dependencies installed.
echo.
echo [*] Launching CrosshairX...
py -m crosshair_app
goto :end

:end
echo.
echo ===================================================
echo   NOTE: If Windows SmartScreen blocks the app,
echo   click "More info" then "Run anyway".
echo ===================================================
pause
