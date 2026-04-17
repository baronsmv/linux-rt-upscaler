#include "tile_cache.h"
#include "xxhash64.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* -------------------------------------------------------------------------
 *  Tile hash computation – inline for performance
 * ------------------------------------------------------------------------- */
static inline unsigned long long tile_compute_hash_inline(
    const unsigned char *buf, int stride,
    int tx, int ty, int tw, int th) {
    XXH64_state_t state;
    XXH64_reset(&state, 0);
    for (int row = 0; row < th; ++row) {
        const unsigned char *row_start = buf + (ty + row) * stride + tx * 4;
        XXH64_update(&state, row_start, tw * 4);
    }
    return XXH64_digest(&state);
}

unsigned long long tile_compute_hash(const unsigned char *buf, int stride,
                                     int tx, int ty, int tw, int th) {
    return tile_compute_hash_inline(buf, stride, tx, ty, tw, th);
}

/* -------------------------------------------------------------------------
 *  Public Functions
 * ------------------------------------------------------------------------- */
int tile_cache_init(CaptureContext *ctx) {
    ctx->tiles_x = (ctx->width + ctx->tile_size - 1) / ctx->tile_size;
    ctx->tiles_y = (ctx->height + ctx->tile_size - 1) / ctx->tile_size;
    size_t num_tiles = (size_t)ctx->tiles_x * ctx->tiles_y;

    ctx->tile_cache = calloc(num_tiles, sizeof(TileCacheEntry));
    if (!ctx->tile_cache) return 0;

    for (int ty = 0; ty < ctx->tiles_y; ++ty) {
        for (int tx = 0; tx < ctx->tiles_x; ++tx) {
            int idx = ty * ctx->tiles_x + tx;
            TileCacheEntry *t = &ctx->tile_cache[idx];
            t->x = tx * ctx->tile_size;
            t->y = ty * ctx->tile_size;
            t->width = ctx->tile_size;
            t->height = ctx->tile_size;
            if (t->x + t->width > ctx->width)
                t->width = ctx->width - t->x;
            if (t->y + t->height > ctx->height)
                t->height = ctx->height - t->y;
        }
    }
    return 1;
}

void tile_cache_free(CaptureContext *ctx) {
    free(ctx->tile_cache);
    ctx->tile_cache = NULL;
}

int tile_cache_detect_changes(CaptureContext *ctx, int full_frame,
                              unsigned char *output_data,
                              unsigned char *partial_buf,
                              int cap_x, int cap_y, int cap_w, int cap_h,
                              OutputRect *rects, int max_rects) {
    if (!ctx->tile_cache) return 0;

    int stride_full = ctx->width * 4;
    int stride_part = cap_w * 4;
    int rect_count = 0;
    int changed_count = 0;
    int total_tiles = ctx->tiles_x * ctx->tiles_y;

    if (full_frame) {
        /* Full frame: scan all tiles */
        for (int ty = 0; ty < ctx->tiles_y; ++ty) {
            for (int tx = 0; tx < ctx->tiles_x; ++tx) {
                int idx = ty * ctx->tiles_x + tx;
                TileCacheEntry *tile = &ctx->tile_cache[idx];
                unsigned long long cur_hash = tile_compute_hash_inline(
                    output_data, stride_full, tile->x, tile->y,
                    tile->width, tile->height);
                if (cur_hash != tile->hash) {
                    tile->hash = cur_hash;
                    ++changed_count;
                    if (rect_count < max_rects) {
                        rects[rect_count].x = tile->x;
                        rects[rect_count].y = tile->y;
                        rects[rect_count].width = tile->width;
                        rects[rect_count].height = tile->height;
                        rects[rect_count].hash = cur_hash;
                        ++rect_count;
                    }
                }
            }
        }
    } else {
        /* Partial capture: only scan tiles that intersect the captured region */
        int start_tx = cap_x / ctx->tile_size;
        int start_ty = cap_y / ctx->tile_size;
        int end_tx = (cap_x + cap_w + ctx->tile_size - 1) / ctx->tile_size;
        int end_ty = (cap_y + cap_h + ctx->tile_size - 1) / ctx->tile_size;
        if (end_tx > ctx->tiles_x) end_tx = ctx->tiles_x;
        if (end_ty > ctx->tiles_y) end_ty = ctx->tiles_y;

        for (int ty = start_ty; ty < end_ty; ++ty) {
            for (int tx = start_tx; tx < end_tx; ++tx) {
                int idx = ty * ctx->tiles_x + tx;
                TileCacheEntry *tile = &ctx->tile_cache[idx];
                /* Check if tile is fully inside captured region */
                if (tile->x >= cap_x && tile->y >= cap_y &&
                    tile->x + tile->width <= cap_x + cap_w &&
                    tile->y + tile->height <= cap_y + cap_h) {
                    int local_x = tile->x - cap_x;
                    int local_y = tile->y - cap_y;
                    unsigned long long cur_hash = tile_compute_hash_inline(
                        partial_buf, stride_part, local_x, local_y,
                        tile->width, tile->height);
                    if (cur_hash != tile->hash) {
                        tile->hash = cur_hash;
                        ++changed_count;
                        if (rect_count < max_rects) {
                            rects[rect_count].x = tile->x;
                            rects[rect_count].y = tile->y;
                            rects[rect_count].width = tile->width;
                            rects[rect_count].height = tile->height;
                            rects[rect_count].hash = cur_hash;
                            ++rect_count;
                        }
                    }
                }
            }
        }
    }

    if (ctx->debug) {
        fprintf(stderr, "[capture] tile hash: %d/%d tiles changed (%.1f%%)\n",
                changed_count, total_tiles,
                100.0 * changed_count / total_tiles);
    }

    /* If change exceeds threshold, signal full frame needed */
    int threshold_tiles = (total_tiles * ctx->tile_threshold_percent) / 100;
    if (changed_count > threshold_tiles) {
        if (ctx->debug)
            fprintf(stderr, "[capture] threshold exceeded, full frame\n");
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

    return rect_count;
}