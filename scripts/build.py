"""
Build script — creates a standalone .exe using PyInstaller.
No Python needed to run the result!
Run: python scripts/build.py
"""

import subprocess
import sys
import os


def build():
    print("=" * 50)
    print("  CrosshairX — Building Standalone EXE")
    print("=" * 50)
    print()

    # Install PyInstaller if needed
    try:
        import PyInstaller
    except ImportError:
        print("[*] Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "CrosshairX",
        "--add-data", f"crosshair_app{os.pathsep}crosshair_app",
        "--hidden-import", "PyQt5",
        "--hidden-import", "PyQt5.QtCore",
        "--hidden-import", "PyQt5.QtGui",
        "--hidden-import", "PyQt5.QtWidgets",
        # Optimize: strip debug, exclude heavy unused modules
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy",
        "--exclude-module", "scipy",
        "--exclude-module", "pandas",
        "--exclude-module", "tkinter",
        "--exclude-module", "unittest",
        "--exclude-module", "xmlrpc",
        "--exclude-module", "pydoc",
        "--noupx",
        "crosshair_app/__main__.py",
    ]

    print(f"[*] Building...")
    result = subprocess.run(cmd, cwd=root)

    if result.returncode == 0:
        exe_path = os.path.join(root, "dist", "CrosshairX.exe")
        size_mb = os.path.getsize(exe_path) / (1024 * 1024) if os.path.exists(exe_path) else 0
        print()
        print(f"[OK] Build complete!")
        print(f"[OK] File: dist/CrosshairX.exe ({size_mb:.1f} MB)")
        print(f"[OK] Send this .exe to anyone — no Python needed!")
        print()
        print("NOTE: Windows SmartScreen may warn about unsigned app.")
        print("Click 'More info' -> 'Run anyway' to launch.")
    else:
        print("[!] Build failed!")
        sys.exit(1)


if __name__ == "__main__":
    build()
