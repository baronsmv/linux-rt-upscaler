/*
 * capture_x11.c – High‑performance X11 window capture with XShm, XDamage, and
 * XFixes.
 *
 * Compile:
 *   gcc -shared -fPIC -O3 -march=native capture_x11.c -o capture_x11.so \
 *       -lX11 -lXext -lXdamage -lXfixes
 */

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/extensions/XShm.h>
#include <X11/extensions/Xdamage.h>
#include <X11/extensions/Xfixes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/shm.h>

typedef struct CaptureContext {
  Display *dpy;
  XID xid;
  int x, y;
  int width, height;
  XShmSegmentInfo shminfo;
  XImage *img;
  unsigned long red_mask, green_mask, blue_mask;
  int use_fast_path;

  /* Damage tracking */
  int damage_event_base, damage_error_base;
  Damage damage;
  int xfixes_event_base, xfixes_error_base;
  int use_damage;         /* 1 if both XDamage and XFixes are usable */
  int needs_full_capture; /* force full capture after window resize, etc. */
} CaptureContext;

CaptureContext *capture_create(XID xid, int crop_left, int crop_top, int width,
                               int height) {
  CaptureContext *ctx = calloc(1, sizeof(CaptureContext));
  if (!ctx)
    return NULL;

  ctx->dpy = XOpenDisplay(NULL);
  if (!ctx->dpy)
    goto fail;

  /* Check SHM extension */
  int major, minor;
  Bool pixmaps;
  if (!XShmQueryExtension(ctx->dpy) ||
      !XShmQueryVersion(ctx->dpy, &major, &minor, &pixmaps)) {
    goto fail;
  }

  ctx->xid = xid;
  ctx->x = crop_left;
  ctx->y = crop_top;
  ctx->width = width;
  ctx->height = height;

  int scr = DefaultScreen(ctx->dpy);
  Visual *vis = DefaultVisual(ctx->dpy, scr);
  int depth = DefaultDepth(ctx->dpy, scr);

  ctx->img = XShmCreateImage(ctx->dpy, vis, depth, ZPixmap, NULL, &ctx->shminfo,
                             width, height);
  if (!ctx->img)
    goto fail;

  ctx->shminfo.shmid =
      shmget(IPC_PRIVATE, ctx->img->bytes_per_line * ctx->img->height,
             IPC_CREAT | 0777);
  if (ctx->shminfo.shmid == -1) {
    XDestroyImage(ctx->img);
    goto fail;
  }

  ctx->shminfo.shmaddr = ctx->img->data = shmat(ctx->shminfo.shmid, 0, 0);
  if (ctx->shminfo.shmaddr == (void *)-1) {
    shmctl(ctx->shminfo.shmid, IPC_RMID, 0);
    XDestroyImage(ctx->img);
    goto fail;
  }

  ctx->shminfo.readOnly = False;
  if (!XShmAttach(ctx->dpy, &ctx->shminfo)) {
    shmdt(ctx->shminfo.shmaddr);
    shmctl(ctx->shminfo.shmid, IPC_RMID, 0);
    XDestroyImage(ctx->img);
    goto fail;
  }

  ctx->red_mask = ctx->img->red_mask;
  ctx->green_mask = ctx->img->green_mask;
  ctx->blue_mask = ctx->img->blue_mask;
  ctx->use_fast_path =
      (ctx->img->bits_per_pixel == 32 && ctx->img->format == ZPixmap);

  /* Try to initialise XDamage and XFixes */
  ctx->use_damage = 0;
  if (XDamageQueryExtension(ctx->dpy, &ctx->damage_event_base,
                            &ctx->damage_error_base) &&
      XFixesQueryExtension(ctx->dpy, &ctx->xfixes_event_base,
                           &ctx->xfixes_error_base)) {
    ctx->damage = XDamageCreate(ctx->dpy, xid, XDamageReportNonEmpty);
    if (ctx->damage) {
      ctx->use_damage = 1;
      ctx->needs_full_capture = 1; /* first frame always captured */
    }
  }

  return ctx;

fail:
  if (ctx->dpy)
    XCloseDisplay(ctx->dpy);
  free(ctx);
  return NULL;
}

/*
 * capture_grab
 *
 * Returns:
 *   0  – success, frame data written to output_data
 *   1  – no damage (frame unchanged), output_data untouched
 *  -1  – error (window closed, etc.)
 */
int capture_grab(CaptureContext *ctx, unsigned char *output_data) {
  if (!ctx || !ctx->dpy || !ctx->img)
    return -1;

  /* Damage check using XFixes region emptiness */
  if (ctx->use_damage) {
    if (!ctx->needs_full_capture) {
      XserverRegion parts = XFixesCreateRegion(ctx->dpy, NULL, 0);
      /* Subtract nothing (repair = None), retrieve current damage in 'parts' */
      XDamageSubtract(ctx->dpy, ctx->damage, None, parts);

      int num_rects = 0;
      XFixesFetchRegion(ctx->dpy, parts, &num_rects);
      XFixesDestroyRegion(ctx->dpy, parts);

      if (num_rects == 0) {
        return 1; /* no damage – buffer unchanged */
      }
    }
    ctx->needs_full_capture = 0;
  }

  /* Perform the capture */
  if (!XShmGetImage(ctx->dpy, ctx->xid, ctx->img, ctx->x, ctx->y, AllPlanes))
    return -1;

  /* Convert pixels to BGRX (or as defined by the ORDER macro – we hardcode BGRX
   * here) */
  int ii = 0;
  if (ctx->use_fast_path) {
    unsigned char *src = (unsigned char *)ctx->img->data;
    int stride = ctx->img->bytes_per_line;
    unsigned long rm = ctx->red_mask;
    unsigned long gm = ctx->green_mask;
    unsigned long bm = ctx->blue_mask;

    for (int y = 0; y < ctx->height; y++) {
      uint32_t *row = (uint32_t *)(src + y * stride);
      for (int x = 0; x < ctx->width; x++) {
        uint32_t pixel = row[x];
        output_data[ii + 2] = (pixel & rm) >> 16; /* red */
        output_data[ii + 1] = (pixel & gm) >> 8;  /* green */
        output_data[ii + 0] = pixel & bm;         /* blue */
        ii += 4;
      }
    }
  } else {
    for (int y = 0; y < ctx->height; y++) {
      for (int x = 0; x < ctx->width; x++) {
        unsigned long pixel = XGetPixel(ctx->img, x, y);
        output_data[ii + 2] = (pixel & ctx->red_mask) >> 16;
        output_data[ii + 1] = (pixel & ctx->green_mask) >> 8;
        output_data[ii + 0] = pixel & ctx->blue_mask;
        ii += 4;
      }
    }
  }

  return 0;
}

void capture_destroy(CaptureContext *ctx) {
  if (!ctx)
    return;
  if (ctx->dpy && ctx->img) {
    XShmDetach(ctx->dpy, &ctx->shminfo);
    shmdt(ctx->shminfo.shmaddr);
    shmctl(ctx->shminfo.shmid, IPC_RMID, 0);
    XDestroyImage(ctx->img);
  }
  if (ctx->damage)
    XDamageDestroy(ctx->dpy, ctx->damage);
  if (ctx->dpy)
    XCloseDisplay(ctx->dpy);
  free(ctx);
}