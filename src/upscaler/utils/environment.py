import os


def setup_environment() -> None:
    """Force X11 session and configure Vulkan drivers for X11 WSI."""

    os.environ["QT_QPA_PLATFORM"] = "xcb"  # Qt → X11
    os.environ["XDG_SESSION_TYPE"] = "x11"  # Tell toolkits we're in X11
    os.environ.pop("WAYLAND_DISPLAY", None)  # Remove Wayland socket reference

    # Vulkan driver‑specific overrides
    os.environ["MESA_VK_WSI"] = "x11"  # Mesa drivers (RADV/ANV)
    os.environ["RADV_DEBUG"] = "no_wayland_wsi"  # Fallback for older Mesa
    os.environ["__GLX_VENDOR_LIBRARY_NAME"] = "nvidia"  # NVIDIA proprietary driver
