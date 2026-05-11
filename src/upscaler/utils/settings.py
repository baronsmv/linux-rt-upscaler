from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication


def system_color_scheme() -> str:
    """Return 'dark' or 'light' based on the OS/desktop colour scheme."""
    # Qt 6.5+
    if hasattr(Qt, "ColorScheme"):
        scheme = QGuiApplication.styleHints().colorScheme()
        if scheme == Qt.ColorScheme.Dark:
            return "dark"
        return "light"

    # Fallback for older Qt 6 or Qt 5, try to read the XDG portal/GTK setting
    import subprocess, os

    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if "dark" in result.stdout.lower():
            return "dark"
    except Exception:
        pass

    # Fallback: check a common environment variable
    for var in ("GTK_THEME", "QT_STYLE_OVERRIDE", "DESKTOP_SESSION"):
        val = os.environ.get(var, "").lower()
        if "dark" in val:
            return "dark"

    return "light"
