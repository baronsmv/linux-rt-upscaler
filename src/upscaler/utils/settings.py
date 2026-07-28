import configparser
import os
import subprocess

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication


def scheme_is_light() -> bool:
    """
    Return True if the Linux desktop color scheme is Light, False if Dark.
    Supports multiple fallbacks: Qt 6.5+, XDG Desktop Portal, KDE Plasma, XFCE,
    GNOME/GTK, and config files.
    """
    # Qt 6.5+ native API
    app = QGuiApplication.instance()
    if app is not None and hasattr(app.styleHints(), "colorScheme"):
        scheme = app.styleHints().colorScheme()
        if scheme == Qt.ColorScheme.Dark:
            return False
        if scheme == Qt.ColorScheme.Light:
            return True
        # If Unknown, fall through

    # XDG Desktop Portal (works on GNOME, KDE, sway, etc.)
    try:
        result = subprocess.run(
            [
                "dbus-send",
                "--session",
                "--print-reply",
                "--dest=org.freedesktop.portal.Desktop",
                "/org/freedesktop/portal/desktop",
                "org.freedesktop.portal.Settings.Read",
                "string:org.freedesktop.appearance",
                "string:color-scheme",
            ],
            capture_output=True,
            text=True,
            timeout=2,
        )
        # DBus returns: variant uint32 1 (Dark) or uint32 2 (Light)
        if "uint32 1" in result.stdout:
            return False
        if "uint32 2" in result.stdout:
            return True
    except Exception:
        pass

    # KDE Plasma (kreadconfig)
    for cmd in ("kreadconfig6", "kreadconfig5"):  # Try Plasma 6 first, then 5
        try:
            result = subprocess.run(
                [
                    cmd,
                    "--file",
                    "kdeglobals",
                    "--group",
                    "General",
                    "--key",
                    "ColorScheme",
                ],
                capture_output=True,
                text=True,
                timeout=1,
            )
            if "Dark" in result.stdout:
                return False
            if (
                "Light" in result.stdout
                or "Breeze" in result.stdout
                and "Dark" not in result.stdout
            ):
                return True
        except Exception:
            pass

    # KDE Plasma (Direct config file fallback)
    try:
        cp = configparser.ConfigParser()
        cp.read(os.path.expanduser("~/.config/kdeglobals"))
        if cp.has_option("General", "ColorScheme"):
            scheme = cp.get("General", "ColorScheme")
            if "Dark" in scheme:
                return False
            if "Light" in scheme or "Breeze" in scheme:
                return True
    except Exception:
        pass

    # XFCE (xfconf-query)
    try:
        result = subprocess.run(
            ["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if "dark" in result.stdout.lower():
            return False
    except Exception:
        pass

    # GTK (GNOME, Budgie, Cinnamon, etc.) via settings.ini
    for gtk_dir in ["gtk-4.0", "gtk-3.0"]:
        try:
            cp = configparser.ConfigParser()
            cp.read(os.path.expanduser(f"~/.config/{gtk_dir}/settings.ini"))
            if cp.has_option("Settings", "gtk-application-prefer-dark-theme"):
                if cp.getboolean("Settings", "gtk-application-prefer-dark-theme"):
                    return False
            if cp.has_option("Settings", "gtk-theme-name"):
                theme = cp.get("Settings", "gtk-theme-name").lower()
                if theme.endswith("-dark") or "-dark-" in theme or theme == "dark":
                    return False
        except Exception:
            pass

    # Legacy GNOME (gsettings)
    try:
        result = subprocess.run(
            ["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if "dark" in result.stdout.lower():
            return False
        if "light" in result.stdout.lower() or "default" in result.stdout.lower():
            return True
    except Exception:
        pass

    # Environment Variables (Last resort)
    for var in ("GTK_THEME", "QT_STYLE_OVERRIDE"):
        val = os.environ.get(var, "").lower()
        if val.endswith("-dark") or "-dark-" in val or val == "dark":
            return False

    # Safe Default
    return True  # Assume Light if everything fails
