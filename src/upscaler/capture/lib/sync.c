#include "sync.h"
#include <stdio.h>
#include <stdlib.h>
#include <xcb/xcb_aux.h>

/* -------------------------------------------------------------------------
 *  Public Functions
 * ------------------------------------------------------------------------- */
xcb_connection_t *xcb_connect_default(int debug) {
    int screen_num;
    xcb_connection_t *conn = xcb_connect(NULL, &screen_num);
    if (!conn || xcb_connection_has_error(conn)) {
        fprintf(stderr, "[xcb] Failed to connect to X server\n");
        return NULL;
    }
    if (debug) {
        fprintf(stderr, "[xcb] Connected to display :%d\n", screen_num);
    }
    return conn;
}

void xcb_sync(xcb_connection_t *conn) {
    if (!conn) return;
    xcb_aux_sync(conn);   /* Flushes and waits for events */
}

void xcb_disconnect(xcb_connection_t *conn) {
    if (conn) {
        xcb_disconnect(conn);
    }
}