#include "shm_image.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <xcb/shm.h>
#include <xcb/xcb_aux.h>

/* -------------------------------------------------------------------------
 *  Fast BGRA conversion for 32‑bit TrueColor (the common case)
 * ------------------------------------------------------------------------- */
static void convert_32bit_to_bgra(unsigned char * RESTRICT dest,
                                  const uint8_t * RESTRICT src,
                                  int src_x, int src_y,
                                  int w, int h, int src_stride,
                                  uint32_t red_mask, uint32_t green_mask,
                                  uint32_t blue_mask) {
    /* Pre‑compute shift amounts for the masks (assuming contiguous masks) */
    int r_shift = __builtin_ctz(red_mask);
    int g_shift = __builtin_ctz(green_mask);
    int b_shift = __builtin_ctz(blue_mask);

    for (int y = 0; y < h; ++y) {
        const uint32_t *row = (const uint32_t *)(src + (src_y + y) * src_stride);
        unsigned char *d = dest + y * w * 4;
        for (int x = 0; x < w; ++x) {
            uint32_t pixel = row[src_x + x];
            d[x * 4 + 2] = (pixel & red_mask)   >> r_shift;   /* R */
            d[x * 4 + 1] = (pixel & green_mask) >> g_shift;   /* G */
            d[x * 4 + 0] = (pixel & blue_mask)  >> b_shift;   /* B */
            /* Alpha is unused; leave as 0 */
        }
    }
}

/* -------------------------------------------------------------------------
 *  Generic conversion for non‑32‑bit visuals (rare, slower)
 * ------------------------------------------------------------------------- */
static void convert_generic_to_bgra(unsigned char * RESTRICT dest,
                                    const uint8_t * RESTRICT src,
                                    int src_x, int src_y,
                                    int w, int h, int src_stride,
                                    int bits_per_pixel,
                                    uint32_t red_mask, uint32_t green_mask,
                                    uint32_t blue_mask) {
    int bytes_per_pixel = (bits_per_pixel + 7) / 8;
    int r_shift = __builtin_ctz(red_mask);
    int g_shift = __builtin_ctz(green_mask);
    int b_shift = __builtin_ctz(blue_mask);

    for (int y = 0; y < h; ++y) {
        const uint8_t *row = src + (src_y + y) * src_stride;
        unsigned char *d = dest + y * w * 4;
        for (int x = 0; x < w; ++x) {
            const uint8_t *pixel_ptr = row + (src_x + x) * bytes_per_pixel;
            uint32_t pixel = 0;
            memcpy(&pixel, pixel_ptr, bytes_per_pixel);
            d[x * 4 + 2] = (pixel & red_mask)   >> r_shift;
            d[x * 4 + 1] = (pixel & green_mask) >> g_shift;
            d[x * 4 + 0] = (pixel & blue_mask)  >> b_shift;
        }
    }
}

/* -------------------------------------------------------------------------
 *  Fallback capture using xcb_get_image
 * ------------------------------------------------------------------------- */
static int fallback_get_image(CaptureContext *ctx, int rx, int ry,
                              int rw, int rh, unsigned char *out) {
    xcb_get_image_cookie_t cookie = xcb_get_image(
        ctx->conn, XCB_IMAGE_FORMAT_Z_PIXMAP, ctx->xid,
        ctx->x + rx, ctx->y + ry, rw, rh, ~0);
    xcb_get_image_reply_t *reply = xcb_get_image_reply(ctx->conn, cookie, NULL);
    if (!reply) return -1;

    uint8_t *data = xcb_get_image_data(reply);
    int data_len = xcb_get_image_data_length(reply);
    if (data_len < rw * rh * 4) {
        free(reply);
        return -1;  /* unexpected format */
    }

    /* Visual info for conversion */
    xcb_get_visual_info_cookie_t vi_cookie =
        xcb_get_visual_info(ctx->conn, ctx->visual);
    xcb_get_visual_info_reply_t *vi =
        xcb_get_visual_info_reply(ctx->conn, vi_cookie, NULL);
    uint32_t rm = vi ? vi->red_mask   : 0xFF0000;
    uint32_t gm = vi ? vi->green_mask : 0x00FF00;
    uint32_t bm = vi ? vi->blue_mask  : 0x0000FF;
    int bpp = vi ? vi->bits_per_rgb_value : 32;
    free(vi);

    int stride = data_len / rh;  /* bytes per line */

    if (bpp == 32 && reply->depth == 24) {
        convert_32bit_to_bgra(out, data, 0, 0, rw, rh, stride, rm, gm, bm);
    } else {
        convert_generic_to_bgra(out, data, 0, 0, rw, rh, stride, bpp, rm, gm, bm);
    }

    free(reply);
    return 0;
}

/* -------------------------------------------------------------------------
 *  Public Functions
 * ------------------------------------------------------------------------- */
void shm_destroy_image(CaptureContext *ctx) {
    if (!ctx->shm_addr) return;

    if (ctx->shm_attached) {
        xcb_shm_detach(ctx->conn, ctx->shm_seg);
        ctx->shm_attached = 0;
    }
    shmdt(ctx->shm_addr);
    shmctl(ctx->shm_id, IPC_RMID, 0);
    ctx->shm_addr = NULL;
    ctx->shm_id = 0;
    ctx->shm_seg = 0;
}

int shm_recreate_if_needed(CaptureContext *ctx) {
    /* Check if we already have a valid SHM segment for current size */
    if (ctx->shm_addr) {
        return 1;   /* already created; assume size hasn't changed */
    }

    int stride = ctx->width * 4;
    size_t size = stride * ctx->height;
    if (size == 0) return 0;

    /* Create System V shared memory segment */
    ctx->shm_id = shmget(IPC_PRIVATE, size, IPC_CREAT | 0777);
    if (ctx->shm_id == -1) {
        ctx->had_shm_failure = 1;
        return 0;
    }

    ctx->shm_addr = shmat(ctx->shm_id, NULL, 0);
    if (ctx->shm_addr == (void *)-1) {
        shmctl(ctx->shm_id, IPC_RMID, 0);
        ctx->shm_addr = NULL;
        ctx->had_shm_failure = 1;
        return 0;
    }

    /* Register with X server */
    xcb_void_cookie_t cookie;
    ctx->shm_seg = xcb_generate_id(ctx->conn);
    cookie = xcb_shm_attach_checked(ctx->conn, ctx->shm_seg, ctx->shm_id, 0);
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

    /* Query visual info once to store masks/bpp for fast conversion */
    xcb_get_visual_info_cookie_t vi_cookie =
        xcb_get_visual_info(ctx->conn, ctx->visual);
    xcb_get_visual_info_reply_t *vi =
        xcb_get_visual_info_reply(ctx->conn, vi_cookie, NULL);
    if (vi) {
        ctx->red_mask   = vi->red_mask;
        ctx->green_mask = vi->green_mask;
        ctx->blue_mask  = vi->blue_mask;
        ctx->bits_per_pixel = vi->bits_per_rgb_value;
        free(vi);
    } else {
        /* fallback defaults */
        ctx->red_mask   = 0xFF0000;
        ctx->green_mask = 0x00FF00;
        ctx->blue_mask  = 0x0000FF;
        ctx->bits_per_pixel = 32;
    }

    ctx->use_fast_path = (ctx->bits_per_pixel == 32);
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

    /* SHM capture */
    xcb_shm_get_image_cookie_t cookie = xcb_shm_get_image_unchecked(
        ctx->conn, ctx->xid, ctx->x + rx, ctx->y + ry, rw, rh, ~0,
        XCB_IMAGE_FORMAT_Z_PIXMAP, ctx->shm_seg, 0);
    xcb_shm_get_image_reply_t *reply =
        xcb_shm_get_image_reply(ctx->conn, cookie, NULL);

    if (!reply) {
        ctx->had_shm_failure = 1;
        return fallback_get_image(ctx, rx, ry, rw, rh, out);
    }

    /* Wait for X server to finish writing to SHM */
    xcb_aux_sync(ctx->conn);

    int stride = ctx->width * 4;   /* full frame stride */

    if (ctx->use_fast_path) {
        convert_32bit_to_bgra(out, (uint8_t *)ctx->shm_addr,
                              rx, ry, rw, rh, stride,
                              ctx->red_mask, ctx->green_mask, ctx->blue_mask);
    } else {
        convert_generic_to_bgra(out, (uint8_t *)ctx->shm_addr,
                                rx, ry, rw, rh, stride,
                                ctx->bits_per_pixel,
                                ctx->red_mask, ctx->green_mask, ctx->blue_mask);
    }

    free(reply);
    return 0;
}