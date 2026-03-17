import ctypes
import logging

from PySide6.QtGui import QGuiApplication

logger = logging.getLogger(__name__)


def get_display() -> int:
    """
    Return the X11 Display pointer as an integer for compushady.
    This is needed to create a swapchain tied to an X11 window.
    """
    logger.debug("Opening X11 display for swapchain")
    try:
        xlib = ctypes.cdll.LoadLibrary("libX11.so")
    except OSError as e:
        logger.error(f"Failed to load libX11.so: {e}")
        raise RuntimeError("X11 library not found – is X11 installed?") from e

    display_ptr = xlib.XOpenDisplay(ctypes.c_int(0))
    if display_ptr == 0:
        logger.error("XOpenDisplay failed. Is X11 running?")
        raise RuntimeError("Cannot open X display – is XWayland running?")

    logger.debug(f"XOpenDisplay returned: {display_ptr}")
    return display_ptr


def get_display_new_method(allow_fallback: bool = True) -> int:
    """
    Return the X11 Display pointer used by Qt as an integer.
    If Qt's display cannot be obtained and allow_fallback is True,
    fall back to opening a new X11 connection via XOpenDisplay (with a warning).
    """
    display_ptr = 0
    methods_tried = []

    # ----- Method 1: Qt6 native interface (via application instance) -----
    try:
        app = QGuiApplication.instance()
        if app is not None:
            native = app.nativeInterface()
            if native is not None and hasattr(native, "display"):
                ptr = native.display()
                if ptr is not None and ptr != 0:
                    display_ptr = int(ptr)
                    logger.debug("Got X11 display via Qt6 native interface")
                    methods_tried.append("Qt6_native")
    except Exception as e:
        logger.debug(f"Qt6 native interface failed: {e}")

    # ----- Method 2: QX11Info (Qt5 compatibility) -----
    if display_ptr == 0:
        try:
            from PySide6.QtX11Extras import QX11Info

            ptr = QX11Info.display()
            if ptr != 0:
                display_ptr = int(ptr)
                logger.debug("Got X11 display via QX11Info")
                methods_tried.append("QX11Info")
        except ImportError:
            logger.debug("QX11Info not available (normal on Qt6)")
        except Exception as e:
            logger.debug(f"QX11Info failed: {e}")

    # ----- Method 3: Fallback to XOpenDisplay (if allowed) -----
    if display_ptr == 0 and allow_fallback:
        logger.warning(
            "Falling back to XOpenDisplay – this may cause issues with Vulkan swapchain"
        )
        try:
            import ctypes

            xlib = ctypes.cdll.LoadLibrary("libX11.so")
            xlib.XOpenDisplay.argtypes = [ctypes.c_char_p]
            xlib.XOpenDisplay.restype = ctypes.c_void_p
            ptr = xlib.XOpenDisplay(None)
            if ptr != 0:
                display_ptr = int(ptr)
                logger.debug(f"Opened X display via XOpenDisplay: {display_ptr}")
                methods_tried.append("XOpenDisplay")
            else:
                logger.error("XOpenDisplay returned NULL")
        except Exception as e:
            logger.error(f"XOpenDisplay failed: {e}")

    if display_ptr == 0:
        raise RuntimeError(
            f"Cannot obtain X11 display (tried: {', '.join(methods_tried) or 'none'}). "
            "Is X11 running and QT_QPA_PLATFORM=xcb set?"
        )

    return display_ptr
