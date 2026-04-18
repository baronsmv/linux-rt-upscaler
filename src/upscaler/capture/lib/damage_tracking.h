/**
 * @file damage_tracking.h
 * @brief XDamage extension integration.
 */

#ifndef DAMAGE_TRACKING_H
#define DAMAGE_TRACKING_H

#include <X11/Xlib.h>
#include <X11/extensions/Xdamage.h>
#include <X11/extensions/Xfixes.h>

typedef struct CaptureContext CaptureContext;

/** Initialize the XDamage extension for the given window. */
int damage_init(CaptureContext *ctx);

/** Clean up damage resources. */
void damage_destroy(CaptureContext *ctx);

/**
 * Query the current damage region.
 * @param ctx           Capture context.
 * @param num_rects     Output: number of rectangles.
 * @param bounds        Output: bounding box.
 * @param rects         Output: array of XRectangle (must be freed with XFree).
 * @return 1 if damage is available, 0 otherwise.
 */
int damage_query(CaptureContext *ctx, int *num_rects, XRectangle *bounds,
                 XRectangle **rects);

/** Consume damage events (call after query). */
void damage_subtract(CaptureContext *ctx);

#endif /* DAMAGE_TRACKING_H */