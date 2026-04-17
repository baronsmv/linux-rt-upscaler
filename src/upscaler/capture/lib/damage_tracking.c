/**
 * @file damage_tracking.c
 * @brief XDamage + XFixes integration using XCB.
 */

#include "capture.h"
#include <stdlib.h>
#include <string.h>
#include <xcb/xcb_aux.h>

/* -------------------------------------------------------------------------
 *  Helper: check extension presence
 * ------------------------------------------------------------------------- */
static int has_extension(xcb_connection_t *conn, const char *name) {
    xcb_query_extension_cookie_t cookie = xcb_query_extension(conn, strlen(name), name);
    xcb_query_extension_reply_t *reply = xcb_query_extension_reply(conn, cookie, NULL);
    int present = reply ? reply->present : 0;
    free(reply);
    return present;
}

/* -------------------------------------------------------------------------
 *  Public Functions
 * ------------------------------------------------------------------------- */
int damage_init(CaptureContext *ctx) {
    if (!ctx || !ctx->conn) return 0;

    if (!has_extension(ctx->conn, "DAMAGE") || !has_extension(ctx->conn, "XFIXES")) {
        ctx->use_damage = 0;
        return 0;
    }

    xcb_damage_damage_t damage = xcb_generate_id(ctx->conn);
    xcb_damage_create(ctx->conn, damage, ctx->xid,
                      XCB_DAMAGE_REPORT_LEVEL_RAW_RECTANGLES);

    ctx->damage = damage;
    ctx->use_damage = 1;
    ctx->first_capture_done = 0;
    xcb_flush(ctx->conn);
    return 1;
}

void damage_destroy(CaptureContext *ctx) {
    if (!ctx || !ctx->use_damage || !ctx->damage) return;

    xcb_damage_destroy(ctx->conn, ctx->damage);
    ctx->damage = 0;
    ctx->use_damage = 0;
    xcb_flush(ctx->conn);
}

int damage_query(CaptureContext *ctx, int *num_rects,
                 xcb_rectangle_t *bounds, xcb_rectangle_t **rects) {
    if (!ctx || !ctx->use_damage) {
        *num_rects = 0;
        bounds->x = bounds->y = bounds->width = bounds->height = 0;
        *rects = NULL;
        return 0;
    }

    xcb_xfixes_region_t region = xcb_generate_id(ctx->conn);
    xcb_xfixes_create_region(ctx->conn, region, 0, NULL);

    xcb_damage_subtract(ctx->conn, ctx->damage, XCB_NONE, region);

    xcb_xfixes_fetch_region_cookie_t cookie =
        xcb_xfixes_fetch_region_unchecked(ctx->conn, region);
    xcb_xfixes_fetch_region_reply_t *reply =
        xcb_xfixes_fetch_region_reply(ctx->conn, cookie, NULL);

    if (!reply) {
        xcb_xfixes_destroy_region(ctx->conn, region);
        *num_rects = 0;
        bounds->x = bounds->y = bounds->width = bounds->height = 0;
        *rects = NULL;
        return 0;
    }

    bounds->x = reply->extents.x;
    bounds->y = reply->extents.y;
    bounds->width = reply->extents.width;
    bounds->height = reply->extents.height;

    // Correct function names:
    int length = xcb_xfixes_fetch_region_rectangles_length(reply);
    *num_rects = length / sizeof(xcb_rectangle_t);

    if (*num_rects > 0) {
        *rects = malloc(length);
        if (*rects) {
            memcpy(*rects, xcb_xfixes_fetch_region_rectangles(reply), length);
        }
    } else {
        *rects = NULL;
    }

    free(reply);
    xcb_xfixes_destroy_region(ctx->conn, region);
    xcb_flush(ctx->conn);
    return 1;
}

void damage_subtract(CaptureContext *ctx) {
    if (!ctx || !ctx->use_damage) return;

    xcb_damage_subtract(ctx->conn, ctx->damage, XCB_NONE, XCB_NONE);
    xcb_flush(ctx->conn);
}