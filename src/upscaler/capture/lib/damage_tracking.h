/**
 * @file damage_tracking.h
 * @brief XDamage + XFixes integration using XCB.
 */

#ifndef DAMAGE_TRACKING_H
#define DAMAGE_TRACKING_H

#include <xcb/xcb.h>
#include <xcb/damage.h>
#include <xcb/xfixes.h>

typedef struct CaptureContext CaptureContext;

/** Initialize damage tracking for the window in the capture context.
 *  @return 1 on success, 0 if extensions are unavailable.
 */
int damage_init(CaptureContext *ctx);

/** Release all damage‑related resources. */
void damage_destroy(CaptureContext *ctx);

/**
 * Query the current accumulated damage region.
 * @param ctx        Capture context.
 * @param num_rects  Output: number of rectangles.
 * @param bounds     Output: bounding box of the region.
 * @param rects      Output: array of xcb_rectangle_t (must be freed with free()).
 * @return 1 if damage is supported and query succeeded, 0 otherwise.
 */
int damage_query(CaptureContext *ctx, int *num_rects,
                 xcb_rectangle_t *bounds, xcb_rectangle_t **rects);

/** Clear the damage region (call after processing). */
void damage_subtract(CaptureContext *ctx);

#endif /* DAMAGE_TRACKING_H */