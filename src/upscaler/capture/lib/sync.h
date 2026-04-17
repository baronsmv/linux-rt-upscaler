/**
 * @file sync.h
 * @brief XCB connection utilities and error handling.
 */

#ifndef SYNC_H
#define SYNC_H

#include <xcb/xcb.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Open an XCB connection to the default display.
 * @param debug   If non‑zero, enable verbose logging of XCB errors.
 * @return Connection pointer, or NULL on failure.
 */
xcb_connection_t *xcb_connect_default(int debug);

/**
 * Flush the connection and wait for all pending requests to be processed.
 * This ensures that SHM operations are visible to the CPU.
 * @param conn   XCB connection.
 */
void xcb_sync(xcb_connection_t *conn);

/**
 * Close the XCB connection.
 * @param conn   Connection to close.
 */
void xcb_disconnect(xcb_connection_t *conn);

#ifdef __cplusplus
}
#endif

#endif /* SYNC_H */