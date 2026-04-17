/**
 * @file tile_cache.h
 * @brief Tile‑based change detection using xxHash64.
 */

#ifndef TILE_CACHE_H
#define TILE_CACHE_H

#include "capture.h"
#include <stdint.h>

typedef struct CaptureContext CaptureContext;
typedef struct TileCacheEntry TileCacheEntry;

/** Compute the xxHash64 of a single tile. */
unsigned long long tile_compute_hash(const unsigned char *buf, int stride,
                                     int tx, int ty, int tw, int th);

/** Initialize the tile cache for the given dimensions and tile size. */
int tile_cache_init(CaptureContext *ctx);

/** Free the tile cache. */
void tile_cache_free(CaptureContext *ctx);

/**
 * Compare the current frame (full or partial) against the cache,
 * populate output rectangles, and return the number of changed tiles.
 *
 * @param ctx           Capture context.
 * @param full_frame    1 if output_data contains the complete frame.
 * @param output_data   Full‑frame buffer (used only if full_frame=1).
 * @param partial_buf   Partial capture buffer (used if full_frame=0).
 * @param cap_x,cap_y   Offset of partial capture within the full frame.
 * @param cap_w,cap_h   Dimensions of partial capture.
 * @param rects         Output array of rectangles.
 * @param max_rects     Maximum number of rectangles to return.
 * @return Number of rectangles written to rects.
 */
int tile_cache_detect_changes(CaptureContext *ctx, int full_frame,
                              unsigned char *output_data,
                              unsigned char *partial_buf,
                              int cap_x, int cap_y, int cap_w, int cap_h,
                              OutputRect *rects, int max_rects);

#endif /* TILE_CACHE_H */