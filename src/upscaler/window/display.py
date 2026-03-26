import ctypes
import logging
from typing import Optional

from PySide6.QtGui import QGuiApplication
from Xlib.display import Display

logger = logging.getLogger(__name__)


def _x_error_handler(error, request) -> None:
    """
    Custom X error handler that logs at DEBUG level and suppresses stderr.
    """
    if hasattr(error, "get_text"):
        error_text = error.get_text()
    else:
        error_text = str(error)
    logger.debug(f"X error: {error_text} (request: {request})")


def open_x_display() -> Optional[Display]:
    """
    Open an X11 display and install a custom error handler.
    Returns a Display object, or None if opening fails.
    """
    try:
        disp = Display()
        disp.set_error_handler(_x_error_handler)
        logger.debug("Opened X display with custom error handler.")
        return disp
    except Exception as e:
        logger.error(f"Failed to open X display: {e}", exc_info=True)
        return None


def close_x_display(disp: Optional[Display]) -> None:
    """Safely close an X11 display."""
    if disp is not None:
        try:
            disp.close()
            logger.debug("Closed X display.")
        except Exception as e:
            logger.warning(f"Error closing X display: {e}")


def get_display(allow_fallback: bool = True) -> int:
    """
    Return the X11 Display pointer used by Qt as an integer.
    If Qt's display cannot be obtained and allow_fallback is True,
    fall back to opening a new X11 connection via XOpenDisplay (with a warning).
    """
    display_ptr = 0
    methods_tried = []

    # Method 1: Qt6 native interface (via application instance)
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

    # Method 2: QX11Info (Qt5 compatibility)
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

    # Method 3: Fallback to XOpenDisplay (if allowed)
    if display_ptr == 0 and allow_fallback:
        logger.warning(
            "Falling back to XOpenDisplay – this may cause issues with Vulkan swapchain"
        )
        try:

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
