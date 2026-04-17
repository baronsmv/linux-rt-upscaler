/**
 * @file capture.c
 * @brief Main XCB capture library – orchestrates damage, SHM, and tile cache.
 */

#include "capture.h"
#include "damage_tracking.h"
#include "shm_image.h"
#include "tile_cache.h"
#include "sync.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <xcb/xcb_aux.h>

/* -------------------------------------------------------------------------
 *  Clamping Utilities
 * ------------------------------------------------------------------------- */
static void clamp_rect(int *x, int *y, int *w, int *h, int max_w, int max_h) {
    if (*x < 0) { *w += *x; *x = 0; }
    if (*y < 0) { *h += *y; *y = 0; }
    if (*x + *w > max_w) *w = max_w - *x;
    if (*y + *h > max_h) *h = max_h - *y;
    if (*w < 0) *w = 0;
    if (*h < 0) *h = 0;
}

/* -------------------------------------------------------------------------
 *  Public API Implementation
 * ------------------------------------------------------------------------- */
CaptureContext *capture_create(xcb_connection_t *conn, xcb_window_t xid,
                               int crop_left, int crop_top, int width, int height) {
    if (!conn) return NULL;

    CaptureContext *ctx = calloc(1, sizeof(CaptureContext));
    if (!ctx) return NULL;

    ctx->conn = conn;
    ctx->xid = xid;
    ctx->x = crop_left;
    ctx->y = crop_top;
    ctx->width = width;
    ctx->height = height;

    /* Query window geometry to cache depth */
    xcb_get_geometry_cookie_t geom_cookie = xcb_get_geometry(conn, xid);
    xcb_get_geometry_reply_t *geom = xcb_get_geometry_reply(conn, geom_cookie, NULL);
    if (geom) {
        ctx->depth = geom->depth;
        free(geom);
    }

    /* Get the window's visual ID from attributes */
    xcb_get_window_attributes_cookie_t attr_cookie = xcb_get_window_attributes(conn, xid);
    xcb_get_window_attributes_reply_t *attr = xcb_get_window_attributes_reply(conn, attr_cookie, NULL);
    if (attr) {
        ctx->visual = attr->visual;
        free(attr);
    } else {
        // Fallback: use default visual of the screen
        const xcb_setup_t *setup = xcb_get_setup(conn);
        xcb_screen_iterator_t iter = xcb_setup_roots_iterator(setup);
        if (iter.rem > 0) {
            ctx->visual = iter.data->root_visual;
        } else {
            ctx->visual = 0;
        }
    }

    /* Obtain visual info (color masks, bits per pixel) using xcb-aux */
    if (ctx->visual != 0) {
        xcb_visualtype_t *visual_type = xcb_aux_get_visualtype(conn, 0, ctx->visual);  // 0 = default screen
        if (visual_type) {
            ctx->red_mask   = visual_type->red_mask;
            ctx->green_mask = visual_type->green_mask;
            ctx->blue_mask  = visual_type->blue_mask;
            ctx->bits_per_pixel = visual_type->bits_per_rgb_value;
        } else {
            ctx->red_mask   = 0xFF0000;
            ctx->green_mask = 0x00FF00;
            ctx->blue_mask  = 0x0000FF;
            ctx->bits_per_pixel = 32;
        }
    } else {
        ctx->red_mask   = 0xFF0000;
        ctx->green_mask = 0x00FF00;
        ctx->blue_mask  = 0x0000FF;
        ctx->bits_per_pixel = 32;
    }

    /* Initialize damage tracking */
    damage_init(ctx);

    /* Read configuration from environment */
    ctx->debug = (getenv("CAPTURE_DEBUG") != NULL);
    ctx->tile_size = DEFAULT_TILE_SIZE;
    const char *ts = getenv("CAPTURE_TILE_SIZE");
    if (ts) ctx->tile_size = atoi(ts);
    if (ctx->tile_size < MIN_TILE_SIZE) ctx->tile_size = MIN_TILE_SIZE;

    ctx->tile_threshold_percent = DEFAULT_THRESHOLD;
    const char *th = getenv("CAPTURE_TILE_THRESHOLD");
    if (th) ctx->tile_threshold_percent = atoi(th);
    if (ctx->tile_threshold_percent < 0) ctx->tile_threshold_percent = DEFAULT_THRESHOLD;
    if (ctx->tile_threshold_percent > 100) ctx->tile_threshold_percent = 100;

    if (!tile_cache_init(ctx)) {
        fprintf(stderr, "[capture] Failed to allocate tile cache\n");
    }

    if (ctx->debug) {
        fprintf(stderr,
                "[capture] Init %dx%d, damage=%d, tile_size=%d, tiles=%dx%d, threshold=%d%%\n",
                width, height, ctx->use_damage, ctx->tile_size,
                ctx->tiles_x, ctx->tiles_y, ctx->tile_threshold_percent);
    }

    return ctx;
}

int capture_grab_damage(CaptureContext *ctx, unsigned char *output_data,
                        OutputRect *rects, int max_rects) {
    if (!ctx || !ctx->conn) return -1;

    /* Clamp capture dimensions to current window size (optional) */
    xcb_get_geometry_cookie_t geom_cookie = xcb_get_geometry(ctx->conn, ctx->xid);
    xcb_get_geometry_reply_t *geom = xcb_get_geometry_reply(ctx->conn, geom_cookie, NULL);
    if (geom) {
        if (ctx->x + ctx->width > (int)geom->width)
            ctx->width = geom->width - ctx->x;
        if (ctx->y + ctx->height > (int)geom->height)
            ctx->height = geom->height - ctx->y;
        free(geom);
    }
    if (ctx->width <= 0 || ctx->height <= 0)
        return 0;

    /* Query damage region */
    int num_damage = 0;
    xcb_rectangle_t bounds = {0, 0, 0, 0};
    xcb_rectangle_t *damage_rects = NULL;
    damage_query(ctx, &num_damage, &bounds, &damage_rects);

    /* First frame: always capture full frame */
    if (!ctx->first_capture_done) {
        if (shm_capture_region(ctx, 0, 0, ctx->width, ctx->height, output_data) != 0)
            return -1;
        ctx->first_capture_done = 1;

        /* Initialize tile cache with first frame hashes */
        if (ctx->tile_cache) {
            int stride = ctx->width * 4;
            for (int ty = 0; ty < ctx->tiles_y; ++ty) {
                for (int tx = 0; tx < ctx->tiles_x; ++tx) {
                    int idx = ty * ctx->tiles_x + tx;
                    TileCacheEntry *t = &ctx->tile_cache[idx];
                    t->hash = tile_compute_hash(output_data, stride,
                                                t->x, t->y, t->width, t->height);
                }
            }
        }

        free(damage_rects);
        if (max_rects > 0) {
            rects[0].x = 0;
            rects[0].y = 0;
            rects[0].width = ctx->width;
            rects[0].height = ctx->height;
            rects[0].hash = 0;
            return 1;
        }
        return 1;
    }

    /* Determine capture region */
    int cap_x, cap_y, cap_w, cap_h;
    int use_full_frame = 0;
    if (num_damage > 0 && bounds.width > 0 && bounds.height > 0) {
        cap_x = bounds.x - ctx->x;
        cap_y = bounds.y - ctx->y;
        cap_w = bounds.width;
        cap_h = bounds.height;
        clamp_rect(&cap_x, &cap_y, &cap_w, &cap_h, ctx->width, ctx->height);
        if (cap_w <= 0 || cap_h <= 0) {
            free(damage_rects);
            return 0;
        }
    } else {
        cap_x = 0;
        cap_y = 0;
        cap_w = ctx->width;
        cap_h = ctx->height;
        use_full_frame = 1;
    }

    /* Perform capture */
    unsigned char *partial_buf = NULL;
    if (use_full_frame) {
        if (shm_capture_region(ctx, 0, 0, ctx->width, ctx->height, output_data) != 0) {
            free(damage_rects);
            return -1;
        }
    } else {
        partial_buf = malloc(cap_w * cap_h * 4);
        if (!partial_buf) {
            free(damage_rects);
            return -1;
        }
        if (shm_capture_region(ctx, cap_x, cap_y, cap_w, cap_h, partial_buf) != 0) {
            free(partial_buf);
            free(damage_rects);
            return -1;
        }
    }

    /* Detect changes using tile cache */
    int rect_count = 0;
    if (ctx->tile_cache) {
        rect_count = tile_cache_detect_changes(ctx, use_full_frame, output_data,
                                               partial_buf, cap_x, cap_y,
                                               cap_w, cap_h, rects, max_rects);
        if (rect_count == 1 && rects[0].width == ctx->width &&
            rects[0].height == ctx->height) {
            /* Threshold exceeded; full frame requested */
            if (!use_full_frame) {
                shm_capture_region(ctx, 0, 0, ctx->width, ctx->height, output_data);
            }
        } else if (!use_full_frame && rect_count > 0) {
            /* Copy changed tiles from partial buffer to full output */
            int stride_full = ctx->width * 4;
            int stride_part = cap_w * 4;
            for (int i = 0; i < rect_count; ++i) {
                OutputRect *r = &rects[i];
                int local_x = r->x - cap_x;
                int local_y = r->y - cap_y;
                unsigned char *src = partial_buf + local_y * stride_part + local_x * 4;
                unsigned char *dst = output_data + r->y * stride_full + r->x * 4;
                for (int row = 0; row < r->height; ++row) {
                    memcpy(dst + row * stride_full, src + row * stride_part,
                           r->width * 4);
                }
            }
        }
    } else {
        /* No tile cache – fallback to damage rectangles directly */
        if (num_damage > 0) {
            for (int i = 0; i < num_damage && rect_count < max_rects; ++i) {
                int rx = damage_rects[i].x - ctx->x;
                int ry = damage_rects[i].y - ctx->y;
                int rw = damage_rects[i].width;
                int rh = damage_rects[i].height;
                clamp_rect(&rx, &ry, &rw, &rh, ctx->width, ctx->height);
                if (rw <= 0 || rh <= 0) continue;
                rects[rect_count].x = rx;
                rects[rect_count].y = ry;
                rects[rect_count].width = rw;
                rects[rect_count].height = rh;
                rects[rect_count].hash = 0;
                ++rect_count;
            }
        } else if (use_full_frame) {
            if (max_rects > 0) {
                rects[0].x = 0;
                rects[0].y = 0;
                rects[0].width = ctx->width;
                rects[0].height = ctx->height;
                rects[0].hash = 0;
                rect_count = 1;
            }
        }
    }

    /* Final bounds validation */
    for (int i = 0; i < rect_count; ++i) {
        if (rects[i].x < 0 || rects[i].y < 0 ||
            rects[i].x + rects[i].width > ctx->width ||
            rects[i].y + rects[i].height > ctx->height) {
            clamp_rect(&rects[i].x, &rects[i].y, &rects[i].width, &rects[i].height,
                       ctx->width, ctx->height);
            if (rects[i].width <= 0 || rects[i].height <= 0) {
                rects[i] = rects[rect_count - 1];
                --rect_count;
                --i;
            }
        }
    }

    free(partial_buf);
    free(damage_rects);
    return rect_count;
}

int capture_grab(CaptureContext *ctx, unsigned char *output_data) {
    OutputRect dummy;
    int result = capture_grab_damage(ctx, output_data, &dummy, 0);
    return (result > 0) ? 0 : (result == 0) ? 1 : -1;
}

void capture_destroy(CaptureContext *ctx) {
    if (!ctx) return;
    shm_destroy_image(ctx);
    damage_destroy(ctx);
    tile_cache_free(ctx);
    free(ctx);
}