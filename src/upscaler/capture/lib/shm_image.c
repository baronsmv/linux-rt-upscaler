/**
 * @file shm_image.c
 * @brief Universal SHM capture using Composite extension.
 */

#include "capture.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <xcb/shm.h>
#include <xcb/composite.h>
#include <xcb/xcb_aux.h>

/* -------------------------------------------------------------------------
 *  Fast BGRA conversion using precomputed shifts (Composite path only)
 * ------------------------------------------------------------------------- */
static void convert_32bit_to_bgra_fast(unsigned char *dest, const uint8_t *src,
                                       int w, int h, int src_stride,
                                       uint32_t red_mask, uint32_t green_mask, uint32_t blue_mask,
                                       int r_shift, int g_shift, int b_shift) {
    for (int y = 0; y < h; ++y) {
        const uint32_t *row = (const uint32_t *)(src + y * src_stride);
        unsigned char *d = dest + y * w * 4;
        for (int x = 0; x < w; ++x) {
            uint32_t pixel = row[x];
            d[x*4+2] = (pixel & red_mask)   >> r_shift;
            d[x*4+1] = (pixel & green_mask) >> g_shift;
            d[x*4+0] = (pixel & blue_mask)  >> b_shift;
            d[x*4+3] = 0xFF;
        }
    }
}

/* -------------------------------------------------------------------------
 *  Fallback using xcb_get_image (when Composite/SHM fails)
 * ------------------------------------------------------------------------- */
static int fallback_get_image(CaptureContext *ctx, int rx, int ry, int rw, int rh,
                              unsigned char *out) {
    xcb_get_image_cookie_t cookie = xcb_get_image(
        ctx->conn, XCB_IMAGE_FORMAT_Z_PIXMAP, ctx->xid,
        ctx->x + rx, ctx->y + ry, rw, rh, ~0);
    xcb_get_image_reply_t *reply = xcb_get_image_reply(ctx->conn, cookie, NULL);
    if (!reply) return -1;

    uint8_t *data = xcb_get_image_data(reply);
    int stride = xcb_get_image_data_length(reply) / rh;

    /* Use the fast conversion (assumes 32‑bit visual, which is typical) */
    convert_32bit_to_bgra_fast(out, data, rw, rh, stride,
                               ctx->red_mask, ctx->green_mask, ctx->blue_mask,
                               ctx->r_shift, ctx->g_shift, ctx->b_shift);

    free(reply);
    return 0;
}

/* -------------------------------------------------------------------------
 *  Composite Pixmap Management (cached across captures)
 * ------------------------------------------------------------------------- */
static int ensure_composite_pixmap(CaptureContext *ctx) {
    if (!ctx->use_composite) return 0;
    if (ctx->composite_pixmap) return 1;

    /* Create a pixmap that matches the window's current size and depth */
    xcb_get_geometry_cookie_t geom_cookie = xcb_get_geometry(ctx->conn, ctx->xid);
    xcb_get_geometry_reply_t *geom = xcb_get_geometry_reply(ctx->conn, geom_cookie, NULL);
    if (!geom) return 0;

    xcb_pixmap_t pixmap = xcb_generate_id(ctx->conn);
    xcb_create_pixmap(ctx->conn, geom->depth, pixmap, ctx->xid,
                      geom->width, geom->height);
    free(geom);

    /* Associate the pixmap with the window's off‑screen content */
    xcb_void_cookie_t name_cookie = xcb_composite_name_window_pixmap(ctx->conn, ctx->xid, pixmap);
    xcb_generic_error_t *error = xcb_request_check(ctx->conn, name_cookie);
    if (error) {
        if (ctx->debug) fprintf(stderr, "[shm] Composite naming error %d\n", error->error_code);
        free(error);
        xcb_free_pixmap(ctx->conn, pixmap);
        ctx->use_composite = 0;
        return 0;
    }

    ctx->composite_pixmap = pixmap;
    if (ctx->debug) fprintf(stderr, "[shm] Composite pixmap created\n");
    return 1;
}

/* -------------------------------------------------------------------------
 *  Public Functions
 * ------------------------------------------------------------------------- */
void shm_destroy_image(CaptureContext *ctx) {
    if (ctx->shm_addr) {
        if (ctx->shm_attached) xcb_shm_detach(ctx->conn, ctx->shm_seg);
        shmdt(ctx->shm_addr);
        shmctl(ctx->shm_id, IPC_RMID, 0);
        ctx->shm_addr = NULL;
        ctx->shm_id = 0;
        ctx->shm_seg = 0;
        ctx->shm_attached = 0;
    }
}

int shm_recreate_if_needed(CaptureContext *ctx) {
    /* If we already have a segment and the window size hasn't changed, reuse it */
    if (ctx->shm_addr && ctx->cached_width > 0 && ctx->cached_height > 0) {
        /* Quick check: query current geometry only if we suspect a resize */
        xcb_get_geometry_cookie_t geom_cookie = xcb_get_geometry(ctx->conn, ctx->xid);
        xcb_get_geometry_reply_t *geom = xcb_get_geometry_reply(ctx->conn, geom_cookie, NULL);
        if (geom) {
            if ((int)geom->width == ctx->cached_width && (int)geom->height == ctx->cached_height) {
                free(geom);
                return 1;  /* Size unchanged, reuse existing segment */
            }
            ctx->cached_width = geom->width;
            ctx->cached_height = geom->height;
            free(geom);
        }
        /* Size changed: destroy old segment and recreate */
        shm_destroy_image(ctx);
    }

    /* Determine drawable (prefer Composite pixmap for 32‑bit guarantee) */
    xcb_drawable_t drawable = ctx->xid;
    if (ensure_composite_pixmap(ctx)) {
        drawable = ctx->composite_pixmap;
    }

    xcb_get_geometry_cookie_t geom_cookie = xcb_get_geometry(ctx->conn, drawable);
    xcb_get_geometry_reply_t *geom = xcb_get_geometry_reply(ctx->conn, geom_cookie, NULL);
    if (!geom) return 0;

    int full_w = geom->width;
    int full_h = geom->height;
    ctx->cached_width = full_w;
    ctx->cached_height = full_h;
    free(geom);

    /* Composite pixmap is always 32‑bit; stride is width * 4 padded to 4 bytes */
    int stride = ((full_w * 4 + 3) / 4) * 4;
    size_t size = stride * full_h;
    if (size == 0) return 0;

    ctx->shm_id = shmget(IPC_PRIVATE, size, IPC_CREAT | 0777);
    if (ctx->shm_id == -1) { ctx->had_shm_failure = 1; return 0; }

    ctx->shm_addr = shmat(ctx->shm_id, NULL, 0);
    if (ctx->shm_addr == (void *)-1) {
        shmctl(ctx->shm_id, IPC_RMID, 0);
        ctx->shm_addr = NULL;
        ctx->had_shm_failure = 1;
        return 0;
    }

    ctx->shm_seg = xcb_generate_id(ctx->conn);
    xcb_void_cookie_t cookie = xcb_shm_attach_checked(ctx->conn, ctx->shm_seg, ctx->shm_id, 0);
    xcb_generic_error_t *err = xcb_request_check(ctx->conn, cookie);
    if (err) {
        free(err);
        shmdt(ctx->shm_addr);
        shmctl(ctx->shm_id, IPC_RMID, 0);
        ctx->shm_addr = NULL;
        ctx->had_shm_failure = 1;
        return 0;
    }
    ctx->shm_attached = 1;
    ctx->had_shm_failure = 0;
    return 1;
}

int shm_capture_region(CaptureContext *ctx, int rx, int ry, int rw, int rh,
                       unsigned char *out) {
    if (rw <= 0 || rh <= 0) return 0;

    if (ctx->had_shm_failure) {
        return fallback_get_image(ctx, rx, ry, rw, rh, out);
    }

    if (!shm_recreate_if_needed(ctx)) {
        ctx->had_shm_failure = 1;
        return fallback_get_image(ctx, rx, ry, rw, rh, out);
    }

    /* Prefer Composite pixmap for guaranteed 32‑bit format */
    xcb_drawable_t drawable = ctx->xid;
    if (ensure_composite_pixmap(ctx)) {
        drawable = ctx->composite_pixmap;
    }

    /* Use checked SHM request for error detection and fallback */
    xcb_shm_get_image_cookie_t cookie = xcb_shm_get_image(
        ctx->conn, drawable,
        ctx->x + rx, ctx->y + ry, rw, rh, ~0,
        XCB_IMAGE_FORMAT_Z_PIXMAP, ctx->shm_seg, 0);

    xcb_generic_error_t *error = NULL;
    xcb_shm_get_image_reply_t *reply = xcb_shm_get_image_reply(
        ctx->conn, cookie, &error);

    if (error) {
        if (ctx->debug) fprintf(stderr, "[shm] X11 error %d\n", error->error_code);
        free(error);
        ctx->had_shm_failure = 1;
        return fallback_get_image(ctx, rx, ry, rw, rh, out);
    }
    if (!reply || reply->length == 0) {
        if (ctx->debug) fprintf(stderr, "[shm] Empty reply\n");
        free(reply);
        ctx->had_shm_failure = 1;
        return fallback_get_image(ctx, rx, ry, rw, rh, out);
    }

    /* Wait for all pending requests (ensures SHM data is ready) */
    xcb_aux_sync(ctx->conn);

    /* Actual stride of the returned sub‑image */
    int sub_stride = reply->length / rh;

    if (ctx->debug) {
        fprintf(stderr, "[shm] success: %dx%d stride=%d via %s\n", rw, rh, sub_stride,
                (drawable == ctx->composite_pixmap) ? "Composite" : "window");
    }

    /* Fast conversion using precomputed shifts */
    convert_32bit_to_bgra_fast(out, (uint8_t*)ctx->shm_addr,
                               rw, rh, sub_stride,
                               ctx->red_mask, ctx->green_mask, ctx->blue_mask,
                               ctx->r_shift, ctx->g_shift, ctx->b_shift);

    free(reply);
    return 0;
}