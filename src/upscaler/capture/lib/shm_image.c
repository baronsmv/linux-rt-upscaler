/**
 * @file shm_image.c
 * @brief SHM image operations.
 */

#include "shm_image.h"
#include "capture.h"
#include "x11_sync.h"
#include <X11/Xutil.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/shm.h>

/* -------------------------------------------------------------------------
 *  BGRA Conversion Helper
 * ------------------------------------------------------------------------- */
static void convert_to_bgra(unsigned char *dest, XImage *src, int src_x,
                            int src_y, int w, int h, unsigned long rm,
                            unsigned long gm, unsigned long bm, int fast_path) {
  int ii = 0;
  if (fast_path) {
    unsigned char *data = (unsigned char *)src->data;
    int stride = src->bytes_per_line;
    for (int y = 0; y < h; y++) {
      uint32_t *row = (uint32_t *)(data + (src_y + y) * stride + src_x * 4);
      for (int x = 0; x < w; x++) {
        uint32_t pixel = row[x];
        dest[ii + 2] = (pixel & rm) >> 16;
        dest[ii + 1] = (pixel & gm) >> 8;
        dest[ii + 0] = pixel & bm;
        ii += 4;
      }
    }
  } else {
    for (int y = 0; y < h; y++) {
      for (int x = 0; x < w; x++) {
        unsigned long pixel = XGetPixel(src, src_x + x, src_y + y);
        dest[ii + 2] = (pixel & rm) >> 16;
        dest[ii + 1] = (pixel & gm) >> 8;
        dest[ii + 0] = pixel & bm;
        ii += 4;
      }
    }
  }
}

/* -------------------------------------------------------------------------
 *  Public Functions
 * ------------------------------------------------------------------------- */
void shm_destroy_image(CaptureContext *ctx) {
  if (!ctx->img)
    return;
  x11_lock();
  XShmDetach(ctx->dpy, &ctx->shminfo);
  x11_unlock();
  shmdt(ctx->shminfo.shmaddr);
  shmctl(ctx->shminfo.shmid, IPC_RMID, 0);
  XDestroyImage(ctx->img);
  ctx->img = NULL;
  ctx->last_visual = NULL;
  ctx->last_depth = 0;
}

int shm_recreate_if_needed(CaptureContext *ctx) {
  XWindowAttributes attrs;
  x11_lock();
  if (!XGetWindowAttributes(ctx->dpy, ctx->xid, &attrs)) {
    x11_unlock();
    return 0;
  }
  x11_unlock();

  if (ctx->img && ctx->last_visual == attrs.visual &&
      ctx->last_depth == attrs.depth)
    return 1;

  shm_destroy_image(ctx);

  ctx->img = XShmCreateImage(ctx->dpy, attrs.visual, attrs.depth, ZPixmap, NULL,
                             &ctx->shminfo, ctx->width, ctx->height);
  if (!ctx->img) {
    ctx->had_shm_failure = 1;
    return 0;
  }

  ctx->shminfo.shmid =
      shmget(IPC_PRIVATE, ctx->img->bytes_per_line * ctx->img->height,
             IPC_CREAT | 0777);
  if (ctx->shminfo.shmid == -1) {
    XDestroyImage(ctx->img);
    ctx->img = NULL;
    ctx->had_shm_failure = 1;
    return 0;
  }

  ctx->shminfo.shmaddr = ctx->img->data = shmat(ctx->shminfo.shmid, 0, 0);
  if (ctx->shminfo.shmaddr == (void *)-1) {
    shmctl(ctx->shminfo.shmid, IPC_RMID, 0);
    XDestroyImage(ctx->img);
    ctx->img = NULL;
    ctx->had_shm_failure = 1;
    return 0;
  }

  ctx->shminfo.readOnly = False;
  x11_lock();
  if (!XShmAttach(ctx->dpy, &ctx->shminfo)) {
    x11_unlock();
    shmdt(ctx->shminfo.shmaddr);
    shmctl(ctx->shminfo.shmid, IPC_RMID, 0);
    XDestroyImage(ctx->img);
    ctx->img = NULL;
    ctx->had_shm_failure = 1;
    return 0;
  }
  x11_unlock();

  ctx->red_mask = ctx->img->red_mask;
  ctx->green_mask = ctx->img->green_mask;
  ctx->blue_mask = ctx->img->blue_mask;
  ctx->use_fast_path =
      (ctx->img->bits_per_pixel == 32 && ctx->img->format == ZPixmap);
  ctx->last_visual = attrs.visual;
  ctx->last_depth = attrs.depth;
  ctx->had_shm_failure = 0;
  return 1;
}

int shm_capture_region(CaptureContext *ctx, int rx, int ry, int rw, int rh,
                       unsigned char *out) {
  if (rw <= 0 || rh <= 0)
    return 0;

  if (!shm_recreate_if_needed(ctx)) {
    /* SHM unavailable – use XGetImage */
    x11_lock();
    XImage *fb = XGetImage(ctx->dpy, ctx->xid, ctx->x + rx, ctx->y + ry, rw, rh,
                           AllPlanes, ZPixmap);
    x11_unlock();
    if (!fb)
      return -1;
    convert_to_bgra(out, fb, 0, 0, rw, rh, fb->red_mask, fb->green_mask,
                    fb->blue_mask,
                    (fb->bits_per_pixel == 32 && fb->format == ZPixmap));
    XDestroyImage(fb);
    return 0;
  }

  /* SHM path */
  x11_lock();
  int ok = XShmGetImage(ctx->dpy, ctx->xid, ctx->img, ctx->x + rx, ctx->y + ry,
                        AllPlanes);
  if (!ok) {
    x11_unlock();
    ctx->had_shm_failure = 1;
    x11_lock();
    XImage *fb = XGetImage(ctx->dpy, ctx->xid, ctx->x + rx, ctx->y + ry, rw, rh,
                           AllPlanes, ZPixmap);
    x11_unlock();
    if (!fb)
      return -1;
    convert_to_bgra(out, fb, 0, 0, rw, rh, fb->red_mask, fb->green_mask,
                    fb->blue_mask,
                    (fb->bits_per_pixel == 32 && fb->format == ZPixmap));
    XDestroyImage(fb);
  } else {
    XSync(ctx->dpy, False);
    x11_unlock();
    convert_to_bgra(out, ctx->img, rx, ry, rw, rh, ctx->red_mask,
                    ctx->green_mask, ctx->blue_mask, ctx->use_fast_path);
  }
  return 0;
}