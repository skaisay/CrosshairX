"""Entry point for CrosshairX."""
import sys
import os

# Support both: running as package (python -m crosshair_app) and as frozen EXE
if getattr(sys, 'frozen', False):
    # Running as PyInstaller EXE
    app_dir = os.path.dirname(sys.executable)
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)
    from crosshair_app.main import main
else:
    from .main import main

main()
