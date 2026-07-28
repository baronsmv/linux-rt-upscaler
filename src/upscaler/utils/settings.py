import os
import subprocess

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication


def scheme_is_light() -> bool:
    """
    Return True if the OS/desktop color scheme is Light, False if Dark.
    """
    # Qt 6.5+ native API
    app = QGuiApplication.instance()
    if app is not None:
        if hasattr(app.styleHints(), "colorScheme"):
            scheme = app.styleHints().colorScheme()
            if scheme == Qt.ColorScheme.Dark:
                return False
            elif scheme == Qt.ColorScheme.Light:
                return True

    # GNOME/GTK
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if "dark" in result.stdout.lower():
            return False
        # If output is 'prefer-light' or 'default', treat as light
        if "light" in result.stdout.lower() or "default" in result.stdout.lower():
            return True
    except Exception:
        pass

    # 3. Environment variable heuristics (last resort)
    for var in ("GTK_THEME", "QT_STYLE_OVERRIDE"):
        val = os.environ.get(var, "").lower()
        if val.endswith("-dark") or "-dark-" in val or val == "dark":
            return False

    # 4. Final safe default: Assume Light
    return True
