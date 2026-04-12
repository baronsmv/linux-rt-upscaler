/*
 * capture_x11.c – Fast X11 capture with damage rectangle support.
 *
 * Compile:
 *   gcc -shared -fPIC -O3 -mtune=generic capture_x11.c -o capture_x11.so \
 *        -lX11 -lXext -lXdamage -lXfixes
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
#include <errno.h>

#define MAX_DAMAGE_RECTS 256

typedef struct {
    int x, y, width, height;
} DamageRect;

typedef struct CaptureContext {
    Display *dpy;
    XID xid;
    int x, y;
    int width, height;
    XShmSegmentInfo shminfo;
    XImage *img;
    unsigned long red_mask, green_mask, blue_mask;
    int use_fast_path;
    Visual *last_visual;
    int last_depth;

    /* Damage */
    int damage_event_base, damage_error_base;
    Damage damage;
    int xfixes_event_base, xfixes_error_base;
    int use_damage;
    int first_capture_done;

    /* Error handling */
    int had_shm_failure;  /* track if SHM failed recently, fallback to XGetImage */
} CaptureContext;

/* ----------------------------------------------------------------------------
   X11 error handler – suppress expected BadMatch during visual changes
   ------------------------------------------------------------------------- */
static int x11_error_handler(Display *dpy, XErrorEvent *ev) {
    if (ev->error_code == BadMatch && ev->request_code == 130) { // ShmGetImage
        return 0;
    }
    char buffer[256];
    XGetErrorText(dpy, ev->error_code, buffer, sizeof(buffer));
    fprintf(stderr, "[capture_x11] X11 error: %s (code %d), request %d\n",
            buffer, ev->error_code, ev->request_code);
    return 0;
}

/* ----------------------------------------------------------------------------
   Destroy SHM image and associated resources
   ------------------------------------------------------------------------- */
static void destroy_shm_image(CaptureContext *ctx) {
    if (!ctx->img) return;
    XShmDetach(ctx->dpy, &ctx->shminfo);
    shmdt(ctx->shminfo.shmaddr);
    shmctl(ctx->shminfo.shmid, IPC_RMID, 0);
    XDestroyImage(ctx->img);
    ctx->img = NULL;
    ctx->last_visual = NULL;
    ctx->last_depth = 0;
    ctx->had_shm_failure = 0;
}

/* ----------------------------------------------------------------------------
   Recreate SHM image if window visual/depth changed or not yet created
   ------------------------------------------------------------------------- */
static int recreate_image_if_needed(CaptureContext *ctx) {
    XWindowAttributes attrs;
    if (!XGetWindowAttributes(ctx->dpy, ctx->xid, &attrs))
        return 0;

    /* If visual/depth unchanged and image exists, keep it */
    if (ctx->img && ctx->last_visual == attrs.visual && ctx->last_depth == attrs.depth)
        return 1;

    /* Destroy old image */
    destroy_shm_image(ctx);

    /* Create new SHM image */
    ctx->img = XShmCreateImage(ctx->dpy, attrs.visual, attrs.depth, ZPixmap, NULL,
                               &ctx->shminfo, ctx->width, ctx->height);
    if (!ctx->img) {
        ctx->had_shm_failure = 1;
        return 0;
    }

    ctx->shminfo.shmid = shmget(IPC_PRIVATE,
                                ctx->img->bytes_per_line * ctx->img->height,
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
    if (!XShmAttach(ctx->dpy, &ctx->shminfo)) {
        shmdt(ctx->shminfo.shmaddr);
        shmctl(ctx->shminfo.shmid, IPC_RMID, 0);
        XDestroyImage(ctx->img);
        ctx->img = NULL;
        ctx->had_shm_failure = 1;
        return 0;
    }

    ctx->red_mask = ctx->img->red_mask;
    ctx->green_mask = ctx->img->green_mask;
    ctx->blue_mask = ctx->img->blue_mask;
    ctx->use_fast_path = (ctx->img->bits_per_pixel == 32 && ctx->img->format == ZPixmap);
    ctx->last_visual = attrs.visual;
    ctx->last_depth = attrs.depth;
    ctx->had_shm_failure = 0;

    return 1;
}

/* ----------------------------------------------------------------------------
   capture_create
   ------------------------------------------------------------------------- */
CaptureContext *capture_create(XID xid, int crop_left, int crop_top, int width, int height) {
    CaptureContext *ctx = calloc(1, sizeof(CaptureContext));
    if (!ctx) return NULL;

    ctx->dpy = XOpenDisplay(NULL);
    if (!ctx->dpy) goto fail;

    XSetErrorHandler(x11_error_handler);

    int major, minor;
    Bool pixmaps;
    if (!XShmQueryExtension(ctx->dpy) ||
        !XShmQueryVersion(ctx->dpy, &major, &minor, &pixmaps)) {
        /* SHM not available, will use fallback path later */
        ctx->had_shm_failure = 1;
    }

    ctx->xid = xid;
    ctx->x = crop_left;
    ctx->y = crop_top;
    ctx->width = width;
    ctx->height = height;

    /* Try to initialize XDamage and XFixes */
    ctx->use_damage = 0;
    if (XDamageQueryExtension(ctx->dpy, &ctx->damage_event_base, &ctx->damage_error_base) &&
        XFixesQueryExtension(ctx->dpy, &ctx->xfixes_event_base, &ctx->xfixes_error_base)) {
        ctx->damage = XDamageCreate(ctx->dpy, xid, XDamageReportNonEmpty);
        if (ctx->damage) {
            ctx->use_damage = 1;
            ctx->first_capture_done = 0;
        }
    }

    return ctx;

fail:
    if (ctx->dpy) XCloseDisplay(ctx->dpy);
    free(ctx);
    return NULL;
}

/* ----------------------------------------------------------------------------
   convert_full_frame – swizzle XImage to BGRA output (fast path when possible)
   ------------------------------------------------------------------------- */
static void convert_full_frame(CaptureContext *ctx, unsigned char *output_data) {
    int ii = 0;
    if (ctx->use_fast_path) {
        unsigned char *src = (unsigned char *)ctx->img->data;
        int stride = ctx->img->bytes_per_line;
        unsigned long rm = ctx->red_mask, gm = ctx->green_mask, bm = ctx->blue_mask;

        for (int y = 0; y < ctx->height; y++) {
            uint32_t *row = (uint32_t *)(src + y * stride);
            for (int x = 0; x < ctx->width; x++) {
                uint32_t pixel = row[x];
                output_data[ii + 2] = (pixel & rm) >> 16;
                output_data[ii + 1] = (pixel & gm) >> 8;
                output_data[ii + 0] = pixel & bm;
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
}

/* ----------------------------------------------------------------------------
   fallback_capture – use XGetImage when SHM fails
   ------------------------------------------------------------------------- */
static int fallback_capture(CaptureContext *ctx, unsigned char *output_data) {
    XWindowAttributes attrs;
    if (!XGetWindowAttributes(ctx->dpy, ctx->xid, &attrs))
        return -1;

    XImage *fb_img = XGetImage(ctx->dpy, ctx->xid, ctx->x, ctx->y, ctx->width, ctx->height,
                               AllPlanes, ZPixmap);
    if (!fb_img)
        return -1;

    int ii = 0;
    for (int y = 0; y < ctx->height; y++) {
        for (int x = 0; x < ctx->width; x++) {
            unsigned long pixel = XGetPixel(fb_img, x, y);
            output_data[ii + 2] = (pixel & fb_img->red_mask) >> 16;
            output_data[ii + 1] = (pixel & fb_img->green_mask) >> 8;
            output_data[ii + 0] = pixel & fb_img->blue_mask;
            ii += 4;
        }
    }
    XDestroyImage(fb_img);
    return 0;
}

/* ----------------------------------------------------------------------------
   capture_grab_damage
   ------------------------------------------------------------------------- */
int capture_grab_damage(CaptureContext *ctx, unsigned char *output_data,
                        DamageRect *rects, int max_rects) {
    if (!ctx || !ctx->dpy) return -1;

    /* Clamp capture region to current window dimensions */
    XWindowAttributes attrs;
    if (XGetWindowAttributes(ctx->dpy, ctx->xid, &attrs)) {
        if (ctx->x + ctx->width > attrs.width)
            ctx->width = attrs.width - ctx->x;
        if (ctx->y + ctx->height > attrs.height)
            ctx->height = attrs.height - ctx->y;
        if (ctx->width <= 0 || ctx->height <= 0)
            return 0;  /* window too small, no capture */
    }

    /* Use fallback if SHM is known broken */
    int use_shm = !ctx->had_shm_failure && ctx->img != NULL;
    if (!use_shm) {
        /* Attempt to recreate SHM if possible */
        if (!ctx->had_shm_failure && !ctx->img) {
            recreate_image_if_needed(ctx);
            use_shm = (ctx->img != NULL);
        }
    }

    /* Full capture logic */
    if (!ctx->use_damage) {
        /* No damage extension: always full capture */
        if (use_shm) {
            if (!XShmGetImage(ctx->dpy, ctx->xid, ctx->img, ctx->x, ctx->y, AllPlanes)) {
                ctx->had_shm_failure = 1;
                if (fallback_capture(ctx, output_data) != 0)
                    return -1;
            } else {
                XSync(ctx->dpy, False);  /* Ensure transfer is complete */
                convert_full_frame(ctx, output_data);
            }
        } else {
            if (fallback_capture(ctx, output_data) != 0)
                return -1;
        }
        if (max_rects > 0) {
            rects[0].x = 0;
            rects[0].y = 0;
            rects[0].width = ctx->width;
            rects[0].height = ctx->height;
            return 1;
        }
        return 1;
    }

    /* Damage extension available */
    if (!ctx->first_capture_done) {
        if (use_shm) {
            if (!XShmGetImage(ctx->dpy, ctx->xid, ctx->img, ctx->x, ctx->y, AllPlanes)) {
                ctx->had_shm_failure = 1;
                if (fallback_capture(ctx, output_data) != 0)
                    return -1;
            } else {
                XSync(ctx->dpy, False);
                convert_full_frame(ctx, output_data);
            }
        } else {
            if (fallback_capture(ctx, output_data) != 0)
                return -1;
        }
        ctx->first_capture_done = 1;
        XDamageSubtract(ctx->dpy, ctx->damage, None, None);
        if (max_rects > 0) {
            rects[0].x = 0;
            rects[0].y = 0;
            rects[0].width = ctx->width;
            rects[0].height = ctx->height;
            return 1;
        }
        return 1;
    }

    /* Check for damage */
    XserverRegion parts = XFixesCreateRegion(ctx->dpy, NULL, 0);
    XDamageSubtract(ctx->dpy, ctx->damage, None, parts);

    int num_rects = 0;
    XRectangle bounds = {0, 0, 0, 0};
    XRectangle *xrects = XFixesFetchRegionAndBounds(ctx->dpy, parts, &num_rects, &bounds);
    XFixesDestroyRegion(ctx->dpy, parts);

    if (num_rects == 0 || bounds.width == 0 || bounds.height == 0) {
        if (xrects) XFree(xrects);
        return 0;  /* No damage, nothing captured */
    }

    /* Damage present: capture full frame */
    if (use_shm) {
        if (!XShmGetImage(ctx->dpy, ctx->xid, ctx->img, ctx->x, ctx->y, AllPlanes)) {
            ctx->had_shm_failure = 1;
            if (fallback_capture(ctx, output_data) != 0) {
                if (xrects) XFree(xrects);
                return -1;
            }
        } else {
            XSync(ctx->dpy, False);
            convert_full_frame(ctx, output_data);
        }
    } else {
        if (fallback_capture(ctx, output_data) != 0) {
            if (xrects) XFree(xrects);
            return -1;
        }
    }

    /* Clamp damage rectangles to capture region and output them */
    int count = 0;
    if (xrects) {
        for (int i = 0; i < num_rects && count < max_rects; i++) {
            /* Adjust rectangle to be relative to capture subregion */
            int rx = xrects[i].x - ctx->x;
            int ry = xrects[i].y - ctx->y;
            int rw = xrects[i].width;
            int rh = xrects[i].height;

            /* Clamp to valid capture area */
            if (rx < 0) { rw += rx; rx = 0; }
            if (ry < 0) { rh += ry; ry = 0; }
            if (rx + rw > ctx->width) rw = ctx->width - rx;
            if (ry + rh > ctx->height) rh = ctx->height - ry;
            if (rw <= 0 || rh <= 0) continue;

            rects[count].x = rx;
            rects[count].y = ry;
            rects[count].width = rw;
            rects[count].height = rh;
            count++;
        }
        XFree(xrects);
    } else {
        if (max_rects > 0) {
            int rx = bounds.x - ctx->x;
            int ry = bounds.y - ctx->y;
            int rw = bounds.width;
            int rh = bounds.height;
            if (rx < 0) { rw += rx; rx = 0; }
            if (ry < 0) { rh += ry; ry = 0; }
            if (rx + rw > ctx->width) rw = ctx->width - rx;
            if (ry + rh > ctx->height) rh = ctx->height - ry;
            if (rw > 0 && rh > 0) {
                rects[0].x = rx;
                rects[0].y = ry;
                rects[0].width = rw;
                rects[0].height = rh;
                count = 1;
            }
        }
    }
    return count;
}

int capture_grab(CaptureContext *ctx, unsigned char *output_data) {
    DamageRect dummy;
    int result = capture_grab_damage(ctx, output_data, &dummy, 0);
    return (result > 0) ? 0 : (result == 0) ? 1 : -1;
}

void capture_destroy(CaptureContext *ctx) {
    if (!ctx) return;
    destroy_shm_image(ctx);
    if (ctx->damage) XDamageDestroy(ctx->dpy, ctx->damage);
    if (ctx->dpy) XCloseDisplay(ctx->dpy);
    free(ctx);
}