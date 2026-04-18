/**
 * @file damage_tracking.c
 * @brief XDamage implementation.
 */

#include "damage_tracking.h"
#include "capture.h"
#include "sync.h"
#include <stdio.h>
#include <stdlib.h>

int damage_init(CaptureContext *ctx) {
  int damage_event, damage_error;
  int xfixes_event, xfixes_error;
  if (!XDamageQueryExtension(ctx->dpy, &damage_event, &damage_error) ||
      !XFixesQueryExtension(ctx->dpy, &xfixes_event, &xfixes_error))
    return 0;

  ctx->damage = XDamageCreate(ctx->dpy, ctx->xid, XDamageReportRawRectangles);
  if (!ctx->damage)
    return 0;

  ctx->use_damage = 1;
  ctx->first_capture_done = 0;
  return 1;
}

void damage_destroy(CaptureContext *ctx) {
  if (ctx->damage) {
    x11_lock();
    XDamageDestroy(ctx->dpy, ctx->damage);
    x11_unlock();
    ctx->damage = 0;
  }
}

int damage_query(CaptureContext *ctx, int *num_rects, XRectangle *bounds,
                 XRectangle **rects) {
  if (!ctx->use_damage)
    return 0;

  x11_lock();
  XserverRegion region = XFixesCreateRegion(ctx->dpy, NULL, 0);
  XDamageSubtract(ctx->dpy, ctx->damage, None, region);
  *rects = XFixesFetchRegionAndBounds(ctx->dpy, region, num_rects, bounds);
  XFixesDestroyRegion(ctx->dpy, region);
  x11_unlock();

  return 1;
}

void damage_subtract(CaptureContext *ctx) {
  if (ctx->use_damage) {
    x11_lock();
    XDamageSubtract(ctx->dpy, ctx->damage, None, None);
    x11_unlock();
  }
}