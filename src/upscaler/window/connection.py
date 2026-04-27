import logging
from typing import Optional

import xcffib

logger = logging.getLogger(__name__)


def open_xcb_connection() -> Optional[xcffib.Connection]:
    """Open an XCB connection to the default display."""
    try:
        conn = xcffib.connect()
        logger.debug("Opened XCB connection.")
        return conn
    except Exception as e:
        logger.error(f"Failed to open XCB connection: {e}", exc_info=True)
        return None


def close_xcb_connection(conn: Optional[xcffib.Connection]) -> None:
    """Safely close an XCB connection."""
    if conn is not None:
        try:
            conn.disconnect()
            logger.debug("Closed XCB connection.")
        except Exception as e:
            logger.warning(f"Error closing XCB connection: {e}")
