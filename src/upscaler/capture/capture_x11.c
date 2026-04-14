/*
 * capture_x11.c – Fast, thread‑safe X11 capture with tile hashing.
 * Compile:
 *   gcc -shared -fPIC -O3 -march=native capture_x11.c -o capture_x11.so \
 *        -lX11 -lXext -lXdamage -lXfixes
 *
 * Environment variables:
 *   CAPTURE_DEBUG=1            – verbose logging
 *   CAPTURE_TILE_SIZE=64       – tile size (default 64)
 *   CAPTURE_TILE_THRESHOLD=30  – if >30% tiles changed, return full frame
 */

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/extensions/XShm.h>
#include <X11/extensions/Xdamage.h>
#include <X11/extensions/Xfixes.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <errno.h>

/* ------------------------- xxHash64 (embedded) ------------------------- */
#define XXH_PRIME64_1 11400714785074694791ULL
#define XXH_PRIME64_2 14029467366897019727ULL
#define XXH_PRIME64_3  1609587929392839161ULL
#define XXH_PRIME64_4  9650029242287828579ULL
#define XXH_PRIME64_5  2870177450012600261ULL

static inline unsigned long long XXH64_rotl(unsigned long long x, int r) {
    return (x << r) | (x >> (64 - r));
}

typedef struct {
    unsigned long long total_len;
    unsigned long long v1, v2, v3, v4;
    unsigned char mem[32];
    unsigned memsize;
} XXH64_state_t;

static void XXH64_reset(XXH64_state_t *state, unsigned long long seed) {
    state->v1 = seed + XXH_PRIME64_1 + XXH_PRIME64_2;
    state->v2 = seed + XXH_PRIME64_2;
    state->v3 = seed;
    state->v4 = seed - XXH_PRIME64_1;
    state->total_len = 0;
    state->memsize = 0;
}

static void XXH64_update(XXH64_state_t *state, const void *input, size_t len) {
    const unsigned char *p = (const unsigned char *)input;
    state->total_len += len;
    if (state->memsize + len < 32) {
        memcpy(state->mem + state->memsize, p, len);
        state->memsize += len;
        return;
    }
    if (state->memsize) {
        size_t fill = 32 - state->memsize;
        memcpy(state->mem + state->memsize, p, fill);
        p += fill; len -= fill;
        unsigned long long *m = (unsigned long long *)state->mem;
        state->v1 = XXH64_rotl(state->v1 + m[0] * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        state->v2 = XXH64_rotl(state->v2 + m[1] * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        state->v3 = XXH64_rotl(state->v3 + m[2] * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        state->v4 = XXH64_rotl(state->v4 + m[3] * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        state->memsize = 0;
    }
    while (len >= 32) {
        unsigned long long m0, m1, m2, m3;
        memcpy(&m0, p, 8); memcpy(&m1, p+8, 8); memcpy(&m2, p+16, 8); memcpy(&m3, p+24, 8);
        state->v1 = XXH64_rotl(state->v1 + m0 * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        state->v2 = XXH64_rotl(state->v2 + m1 * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        state->v3 = XXH64_rotl(state->v3 + m2 * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        state->v4 = XXH64_rotl(state->v4 + m3 * XXH_PRIME64_2, 31) * XXH_PRIME64_1;
        p += 32; len -= 32;
    }
    if (len) {
        memcpy(state->mem, p, len);
        state->memsize = len;
    }
}

static unsigned long long XXH64_digest(XXH64_state_t *state) {
    unsigned long long h64;
    if (state->total_len >= 32) {
        h64 = XXH64_rotl(state->v1, 1) + XXH64_rotl(state->v2, 7) + XXH64_rotl(state->v3, 12) + XXH64_rotl(state->v4, 18);
        h64 = (h64 ^ XXH64_rotl(state->v1 * XXH_PRIME64_2, 31) * XXH_PRIME64_1) * XXH_PRIME64_1 + XXH_PRIME64_4;
        h64 = (h64 ^ XXH64_rotl(state->v2 * XXH_PRIME64_2, 31) * XXH_PRIME64_1) * XXH_PRIME64_1 + XXH_PRIME64_4;
        h64 = (h64 ^ XXH64_rotl(state->v3 * XXH_PRIME64_2, 31) * XXH_PRIME64_1) * XXH_PRIME64_1 + XXH_PRIME64_4;
        h64 = (h64 ^ XXH64_rotl(state->v4 * XXH_PRIME64_2, 31) * XXH_PRIME64_1) * XXH_PRIME64_1 + XXH_PRIME64_4;
    } else {
        h64 = state->v3 + XXH_PRIME64_5;
    }
    h64 += state->total_len;
    unsigned char *p = state->mem;
    while (p + 8 <= state->mem + state->memsize) {
        unsigned long long k1; memcpy(&k1, p, 8);
        k1 *= XXH_PRIME64_2; k1 = XXH64_rotl(k1,31); k1 *= XXH_PRIME64_1;
        h64 ^= k1; h64 = XXH64_rotl(h64,27) * XXH_PRIME64_1 + XXH_PRIME64_4;
        p += 8;
    }
    if (p + 4 <= state->mem + state->memsize) {
        unsigned int k1; memcpy(&k1, p, 4);
        h64 ^= (unsigned long long)k1 * XXH_PRIME64_1;
        h64 = XXH64_rotl(h64, 23) * XXH_PRIME64_2 + XXH_PRIME64_3;
        p += 4;
    }
    while (p < state->mem + state->memsize) {
        h64 ^= (*p) * XXH_PRIME64_5; h64 = XXH64_rotl(h64, 11) * XXH_PRIME64_1; p++;
    }
    h64 ^= h64 >> 33; h64 *= XXH_PRIME64_2; h64 ^= h64 >> 29; h64 *= XXH_PRIME64_3; h64 ^= h64 >> 32;
    return h64;
}

/* ------------------------------------------------------------------------ */

#define MAX_DAMAGE_RECTS 1024

/* Public output rectangle (no hash) */
typedef struct {
    int x, y, width, height;
} OutputRect;

/* Internal tile cache entry (includes hash) */
typedef struct {
    int x, y, width, height;
    unsigned long long hash;
} TileCacheEntry;

typedef struct CaptureContext {
    Display *dpy;
    Window xid;
    int x, y, width, height;
    XShmSegmentInfo shminfo;
    XImage *img;
    unsigned long red_mask, green_mask, blue_mask;
    int use_fast_path;
    Visual *last_visual;
    int last_depth;

    int damage_event_base, damage_error_base;
    Damage damage;
    int xfixes_event_base, xfixes_error_base;
    int use_damage;
    int first_capture_done;

    int had_shm_failure;

    // Tile hashing
    TileCacheEntry *tile_cache;
    int tiles_x, tiles_y;
    int tile_size;
    int tile_threshold_percent;
    int debug;
} CaptureContext;

/* Global mutex for Xlib calls (thread safety) */
static pthread_mutex_t xlib_mutex = PTHREAD_MUTEX_INITIALIZER;

/* Forward declarations */
static unsigned long long compute_tile_hash(unsigned char *full_buf, int stride,
                                            int tx, int ty, int tw, int th);
static void convert_rect_to_bgra(unsigned char *dest, XImage *src,
                                 int src_x, int src_y, int w, int h,
                                 unsigned long rm, unsigned long gm, unsigned long bm,
                                 int fast_path);

/* ------------------------- X11 error handler --------------------------- */
static int x11_error_handler(Display *dpy, XErrorEvent *ev) {
    if (ev->error_code == BadMatch && ev->request_code == 130) return 0;
    return 0;
}

/* ------------------------- SHM helpers --------------------------------- */
static void destroy_shm_image(CaptureContext *ctx) {
    if (!ctx->img) return;
    pthread_mutex_lock(&xlib_mutex);
    XShmDetach(ctx->dpy, &ctx->shminfo);
    pthread_mutex_unlock(&xlib_mutex);
    shmdt(ctx->shminfo.shmaddr);
    shmctl(ctx->shminfo.shmid, IPC_RMID, 0);
    XDestroyImage(ctx->img);
    ctx->img = NULL;
    ctx->last_visual = NULL;
    ctx->last_depth = 0;
}

static int recreate_image_if_needed(CaptureContext *ctx) {
    XWindowAttributes attrs;
    pthread_mutex_lock(&xlib_mutex);
    if (!XGetWindowAttributes(ctx->dpy, ctx->xid, &attrs)) {
        pthread_mutex_unlock(&xlib_mutex);
        return 0;
    }
    pthread_mutex_unlock(&xlib_mutex);
    if (ctx->img && ctx->last_visual == attrs.visual && ctx->last_depth == attrs.depth)
        return 1;
    destroy_shm_image(ctx);

    ctx->img = XShmCreateImage(ctx->dpy, attrs.visual, attrs.depth, ZPixmap, NULL,
                               &ctx->shminfo, ctx->width, ctx->height);
    if (!ctx->img) { ctx->had_shm_failure = 1; return 0; }

    ctx->shminfo.shmid = shmget(IPC_PRIVATE, ctx->img->bytes_per_line * ctx->img->height,
                                IPC_CREAT | 0777);
    if (ctx->shminfo.shmid == -1) {
        XDestroyImage(ctx->img); ctx->img = NULL; ctx->had_shm_failure = 1; return 0;
    }
    ctx->shminfo.shmaddr = ctx->img->data = shmat(ctx->shminfo.shmid, 0, 0);
    if (ctx->shminfo.shmaddr == (void *)-1) {
        shmctl(ctx->shminfo.shmid, IPC_RMID, 0);
        XDestroyImage(ctx->img); ctx->img = NULL; ctx->had_shm_failure = 1; return 0;
    }
    ctx->shminfo.readOnly = False;
    pthread_mutex_lock(&xlib_mutex);
    if (!XShmAttach(ctx->dpy, &ctx->shminfo)) {
        pthread_mutex_unlock(&xlib_mutex);
        shmdt(ctx->shminfo.shmaddr);
        shmctl(ctx->shminfo.shmid, IPC_RMID, 0);
        XDestroyImage(ctx->img); ctx->img = NULL; ctx->had_shm_failure = 1; return 0;
    }
    pthread_mutex_unlock(&xlib_mutex);

    ctx->red_mask = ctx->img->red_mask;
    ctx->green_mask = ctx->img->green_mask;
    ctx->blue_mask = ctx->img->blue_mask;
    ctx->use_fast_path = (ctx->img->bits_per_pixel == 32 && ctx->img->format == ZPixmap);
    ctx->last_visual = attrs.visual;
    ctx->last_depth = attrs.depth;
    ctx->had_shm_failure = 0;
    return 1;
}

/* ------------------------- BGRA Conversion ----------------------------- */
static void convert_rect_to_bgra(unsigned char *dest, XImage *src,
                                 int src_x, int src_y, int w, int h,
                                 unsigned long rm, unsigned long gm, unsigned long bm,
                                 int fast_path) {
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

/* ------------------------- Core Capture Routine ------------------------ */
static int capture_region(CaptureContext *ctx, int rx, int ry, int rw, int rh,
                          unsigned char *out_buf) {
    if (rw <= 0 || rh <= 0) return 0;

    if (!recreate_image_if_needed(ctx)) {
        pthread_mutex_lock(&xlib_mutex);
        XImage *fb = XGetImage(ctx->dpy, ctx->xid, ctx->x + rx, ctx->y + ry, rw, rh,
                               AllPlanes, ZPixmap);
        pthread_mutex_unlock(&xlib_mutex);
        if (!fb) return -1;
        convert_rect_to_bgra(out_buf, fb, 0, 0, rw, rh,
                             fb->red_mask, fb->green_mask, fb->blue_mask,
                             (fb->bits_per_pixel == 32 && fb->format == ZPixmap));
        XDestroyImage(fb);
    } else {
        pthread_mutex_lock(&xlib_mutex);
        int ok = XShmGetImage(ctx->dpy, ctx->xid, ctx->img, ctx->x + rx, ctx->y + ry, AllPlanes);
        if (!ok) {
            pthread_mutex_unlock(&xlib_mutex);
            ctx->had_shm_failure = 1;
            pthread_mutex_lock(&xlib_mutex);
            XImage *fb = XGetImage(ctx->dpy, ctx->xid, ctx->x + rx, ctx->y + ry, rw, rh,
                                   AllPlanes, ZPixmap);
            pthread_mutex_unlock(&xlib_mutex);
            if (!fb) return -1;
            convert_rect_to_bgra(out_buf, fb, 0, 0, rw, rh,
                                 fb->red_mask, fb->green_mask, fb->blue_mask,
                                 (fb->bits_per_pixel == 32 && fb->format == ZPixmap));
            XDestroyImage(fb);
        } else {
            XSync(ctx->dpy, False);
            pthread_mutex_unlock(&xlib_mutex);
            convert_rect_to_bgra(out_buf, ctx->img, rx, ry, rw, rh,
                                 ctx->red_mask, ctx->green_mask, ctx->blue_mask,
                                 ctx->use_fast_path);
        }
    }
    return 0;
}

/* ------------------------- Tile Hash Computation ----------------------- */
static unsigned long long compute_tile_hash(unsigned char *full_buf, int stride,
                                            int tx, int ty, int tw, int th) {
    XXH64_state_t state;
    XXH64_reset(&state, 0);
    for (int row = 0; row < th; row++) {
        unsigned char *row_start = full_buf + (ty + row) * stride + tx * 4;
        XXH64_update(&state, row_start, tw * 4);
    }
    return XXH64_digest(&state);
}

/* ------------------------------------------------------------------------
   Public API
   ------------------------------------------------------------------------ */
CaptureContext *capture_create(XID xid, int crop_left, int crop_top, int width, int height) {
    CaptureContext *ctx = calloc(1, sizeof(CaptureContext));
    if (!ctx) return NULL;
    ctx->dpy = XOpenDisplay(NULL);
    if (!ctx->dpy) { free(ctx); return NULL; }
    XSetErrorHandler(x11_error_handler);

    int major, minor; Bool pixmaps;
    if (!XShmQueryExtension(ctx->dpy) || !XShmQueryVersion(ctx->dpy, &major, &minor, &pixmaps))
        ctx->had_shm_failure = 1;

    ctx->xid = xid;
    ctx->x = crop_left;
    ctx->y = crop_top;
    ctx->width = width;
    ctx->height = height;

    ctx->use_damage = 0;
    if (XDamageQueryExtension(ctx->dpy, &ctx->damage_event_base, &ctx->damage_error_base) &&
        XFixesQueryExtension(ctx->dpy, &ctx->xfixes_event_base, &ctx->xfixes_error_base)) {
        ctx->damage = XDamageCreate(ctx->dpy, xid, XDamageReportRawRectangles);
        if (ctx->damage) {
            ctx->use_damage = 1;
            ctx->first_capture_done = 0;
        }
    }

    ctx->debug = (getenv("CAPTURE_DEBUG") != NULL);
    ctx->tile_size = 64;
    const char *ts = getenv("CAPTURE_TILE_SIZE");
    if (ts) ctx->tile_size = atoi(ts);
    if (ctx->tile_size < 16) ctx->tile_size = 64;
    ctx->tile_threshold_percent = 30;
    const char *th = getenv("CAPTURE_TILE_THRESHOLD");
    if (th) ctx->tile_threshold_percent = atoi(th);
    if (ctx->tile_threshold_percent < 0) ctx->tile_threshold_percent = 30;
    if (ctx->tile_threshold_percent > 100) ctx->tile_threshold_percent = 100;

    ctx->tiles_x = (width + ctx->tile_size - 1) / ctx->tile_size;
    ctx->tiles_y = (height + ctx->tile_size - 1) / ctx->tile_size;
    ctx->tile_cache = calloc(ctx->tiles_x * ctx->tiles_y, sizeof(TileCacheEntry));
    if (ctx->tile_cache) {
        for (int ty = 0; ty < ctx->tiles_y; ty++) {
            for (int tx = 0; tx < ctx->tiles_x; tx++) {
                int idx = ty * ctx->tiles_x + tx;
                ctx->tile_cache[idx].x = tx * ctx->tile_size;
                ctx->tile_cache[idx].y = ty * ctx->tile_size;
                ctx->tile_cache[idx].width = ctx->tile_size;
                ctx->tile_cache[idx].height = ctx->tile_size;
                if (ctx->tile_cache[idx].x + ctx->tile_cache[idx].width > width)
                    ctx->tile_cache[idx].width = width - ctx->tile_cache[idx].x;
                if (ctx->tile_cache[idx].y + ctx->tile_cache[idx].height > height)
                    ctx->tile_cache[idx].height = height - ctx->tile_cache[idx].y;
            }
        }
    }

    if (ctx->debug) {
        fprintf(stderr, "[capture_x11] Init %dx%d, damage=%d, tile_size=%d, tiles=%dx%d, threshold=%d%%\n",
                width, height, ctx->use_damage, ctx->tile_size, ctx->tiles_x, ctx->tiles_y,
                ctx->tile_threshold_percent);
    }
    return ctx;
}

int capture_grab_damage(CaptureContext *ctx, unsigned char *output_data,
                        OutputRect *rects, int max_rects) {
    if (!ctx || !ctx->dpy) return -1;

    // Clamp dimensions
    XWindowAttributes attrs;
    pthread_mutex_lock(&xlib_mutex);
    if (XGetWindowAttributes(ctx->dpy, ctx->xid, &attrs)) {
        if (ctx->x + ctx->width > attrs.width) ctx->width = attrs.width - ctx->x;
        if (ctx->y + ctx->height > attrs.height) ctx->height = attrs.height - ctx->y;
    }
    pthread_mutex_unlock(&xlib_mutex);
    if (ctx->width <= 0 || ctx->height <= 0) return 0;

    // 1. Get damage region
    XserverRegion damage_region = None;
    int num_damage_rects = 0;
    XRectangle *damage_rects = NULL;
    XRectangle bounds = {0,0,0,0};
    if (ctx->use_damage) {
        pthread_mutex_lock(&xlib_mutex);
        damage_region = XFixesCreateRegion(ctx->dpy, NULL, 0);
        XDamageSubtract(ctx->dpy, ctx->damage, None, damage_region);
        damage_rects = XFixesFetchRegionAndBounds(ctx->dpy, damage_region, &num_damage_rects, &bounds);
        XFixesDestroyRegion(ctx->dpy, damage_region);
        pthread_mutex_unlock(&xlib_mutex);
    }

    // 2. First frame: capture full and init cache
    if (!ctx->first_capture_done) {
        if (capture_region(ctx, 0, 0, ctx->width, ctx->height, output_data) != 0)
            return -1;
        ctx->first_capture_done = 1;

        if (ctx->tile_cache) {
            int stride = ctx->width * 4;
            for (int ty = 0; ty < ctx->tiles_y; ty++) {
                for (int tx = 0; tx < ctx->tiles_x; tx++) {
                    int idx = ty * ctx->tiles_x + tx;
                    ctx->tile_cache[idx].hash = compute_tile_hash(output_data, stride,
                                                                  ctx->tile_cache[idx].x,
                                                                  ctx->tile_cache[idx].y,
                                                                  ctx->tile_cache[idx].width,
                                                                  ctx->tile_cache[idx].height);
                }
            }
        }

        if (damage_rects) XFree(damage_rects);
        if (max_rects > 0) {
            rects[0].x = 0; rects[0].y = 0; rects[0].width = ctx->width; rects[0].height = ctx->height;
            return 1;
        }
        return 1;
    }

    // 3. Determine capture region
    int cap_x, cap_y, cap_w, cap_h;
    int use_full_frame = 0;
    if (num_damage_rects > 0 && bounds.width > 0 && bounds.height > 0) {
        cap_x = bounds.x - ctx->x;
        cap_y = bounds.y - ctx->y;
        cap_w = bounds.width;
        cap_h = bounds.height;
        if (cap_x < 0) { cap_w += cap_x; cap_x = 0; }
        if (cap_y < 0) { cap_h += cap_y; cap_y = 0; }
        if (cap_x + cap_w > ctx->width) cap_w = ctx->width - cap_x;
        if (cap_y + cap_h > ctx->height) cap_h = ctx->height - cap_y;
        if (cap_w <= 0 || cap_h <= 0) {
            if (damage_rects) XFree(damage_rects);
            return 0;
        }
    } else {
        cap_x = 0; cap_y = 0; cap_w = ctx->width; cap_h = ctx->height;
        use_full_frame = 1;
    }

    // 4. Capture
    unsigned char *capture_buf = output_data;
    unsigned char *temp_buf = NULL;
    if (use_full_frame) {
        if (capture_region(ctx, 0, 0, ctx->width, ctx->height, output_data) != 0) {
            if (damage_rects) XFree(damage_rects);
            return -1;
        }
    } else {
        temp_buf = malloc(cap_w * cap_h * 4);
        if (!temp_buf) {
            if (damage_rects) XFree(damage_rects);
            return -1;
        }
        if (capture_region(ctx, cap_x, cap_y, cap_w, cap_h, temp_buf) != 0) {
            free(temp_buf);
            if (damage_rects) XFree(damage_rects);
            return -1;
        }
        capture_buf = temp_buf;
    }

    // 5. Tile hashing (single‑threaded)
    int rect_count = 0;
    int total_tiles = ctx->tiles_x * ctx->tiles_y;
    int changed_count = 0;

    if (ctx->tile_cache) {
        int stride_full = ctx->width * 4;
        int stride_cap = cap_w * 4;

        if (use_full_frame) {
            for (int ty = 0; ty < ctx->tiles_y; ty++) {
                for (int tx = 0; tx < ctx->tiles_x; tx++) {
                    int idx = ty * ctx->tiles_x + tx;
                    TileCacheEntry *tile = &ctx->tile_cache[idx];
                    unsigned long long cur_hash = compute_tile_hash(output_data, stride_full,
                                                                    tile->x, tile->y,
                                                                    tile->width, tile->height);
                    if (cur_hash != tile->hash) {
                        tile->hash = cur_hash;
                        changed_count++;
                        if (rect_count < max_rects) {
                            rects[rect_count].x = tile->x;
                            rects[rect_count].y = tile->y;
                            rects[rect_count].width = tile->width;
                            rects[rect_count].height = tile->height;
                            rect_count++;
                        }
                    }
                }
            }
        } else {
            int start_tx = cap_x / ctx->tile_size;
            int start_ty = cap_y / ctx->tile_size;
            int end_tx = (cap_x + cap_w + ctx->tile_size - 1) / ctx->tile_size;
            int end_ty = (cap_y + cap_h + ctx->tile_size - 1) / ctx->tile_size;
            if (end_tx > ctx->tiles_x) end_tx = ctx->tiles_x;
            if (end_ty > ctx->tiles_y) end_ty = ctx->tiles_y;

            for (int ty = start_ty; ty < end_ty; ty++) {
                for (int tx = start_tx; tx < end_tx; tx++) {
                    int idx = ty * ctx->tiles_x + tx;
                    TileCacheEntry *tile = &ctx->tile_cache[idx];
                    if (tile->x >= cap_x && tile->y >= cap_y &&
                        tile->x + tile->width <= cap_x + cap_w &&
                        tile->y + tile->height <= cap_y + cap_h) {
                        int local_x = tile->x - cap_x;
                        int local_y = tile->y - cap_y;
                        XXH64_state_t state;
                        XXH64_reset(&state, 0);
                        for (int row = 0; row < tile->height; row++) {
                            unsigned char *row_start = temp_buf + (local_y + row) * stride_cap + local_x * 4;
                            XXH64_update(&state, row_start, tile->width * 4);
                        }
                        unsigned long long cur_hash = XXH64_digest(&state);
                        if (cur_hash != tile->hash) {
                            tile->hash = cur_hash;
                            changed_count++;
                            if (rect_count < max_rects) {
                                rects[rect_count].x = tile->x;
                                rects[rect_count].y = tile->y;
                                rects[rect_count].width = tile->width;
                                rects[rect_count].height = tile->height;
                                rect_count++;
                            }
                        }
                    }
                }
            }
        }

        if (ctx->debug) {
            fprintf(stderr, "[capture_x11] tile hash: %d/%d tiles changed (%.1f%%)\n",
                    changed_count, total_tiles, 100.0 * changed_count / total_tiles);
        }

        int threshold_tiles = (total_tiles * ctx->tile_threshold_percent) / 100;
        if (changed_count > threshold_tiles) {
            if (ctx->debug) fprintf(stderr, "[capture_x11] threshold exceeded, full frame\n");
            if (!use_full_frame) {
                capture_region(ctx, 0, 0, ctx->width, ctx->height, output_data);
            }
            if (max_rects > 0) {
                rects[0].x = 0; rects[0].y = 0;
                rects[0].width = ctx->width; rects[0].height = ctx->height;
                rect_count = 1;
            }
        } else if (!use_full_frame && rect_count > 0) {
            for (int i = 0; i < rect_count; i++) {
                OutputRect *r = &rects[i];
                int local_x = r->x - cap_x;
                int local_y = r->y - cap_y;
                unsigned char *src = temp_buf + local_y * stride_cap + local_x * 4;
                unsigned char *dst = output_data + r->y * stride_full + r->x * 4;
                for (int row = 0; row < r->height; row++) {
                    memcpy(dst + row * stride_full, src + row * stride_cap, r->width * 4);
                }
            }
        }
    } else {
        // No tile cache: use damage rects directly
        if (num_damage_rects > 0) {
            for (int i = 0; i < num_damage_rects && rect_count < max_rects; i++) {
                int rx = damage_rects[i].x - ctx->x;
                int ry = damage_rects[i].y - ctx->y;
                int rw = damage_rects[i].width;
                int rh = damage_rects[i].height;
                if (rx < 0) { rw += rx; rx = 0; }
                if (ry < 0) { rh += ry; ry = 0; }
                if (rx + rw > ctx->width) rw = ctx->width - rx;
                if (ry + rh > ctx->height) rh = ctx->height - ry;
                if (rw <= 0 || rh <= 0) continue;
                rects[rect_count].x = rx;
                rects[rect_count].y = ry;
                rects[rect_count].width = rw;
                rects[rect_count].height = rh;
                rect_count++;
            }
        } else if (use_full_frame) {
            if (max_rects > 0) {
                rects[0].x = 0; rects[0].y = 0;
                rects[0].width = ctx->width; rects[0].height = ctx->height;
                rect_count = 1;
            }
        }
    }

    // Final bounds validation
    for (int i = 0; i < rect_count; i++) {
        if (rects[i].x < 0 || rects[i].y < 0 ||
            rects[i].x + rects[i].width > ctx->width ||
            rects[i].y + rects[i].height > ctx->height) {
            // Clamp or discard
            if (rects[i].x < 0) { rects[i].width += rects[i].x; rects[i].x = 0; }
            if (rects[i].y < 0) { rects[i].height += rects[i].y; rects[i].y = 0; }
            if (rects[i].x + rects[i].width > ctx->width) rects[i].width = ctx->width - rects[i].x;
            if (rects[i].y + rects[i].height > ctx->height) rects[i].height = ctx->height - rects[i].y;
            if (rects[i].width <= 0 || rects[i].height <= 0) {
                // Remove by swapping with last
                rects[i] = rects[rect_count-1];
                rect_count--;
                i--;
            }
        }
    }

    if (temp_buf) free(temp_buf);
    if (damage_rects) XFree(damage_rects);
    return rect_count;
}

int capture_grab(CaptureContext *ctx, unsigned char *output_data) {
    OutputRect dummy;
    int result = capture_grab_damage(ctx, output_data, &dummy, 0);
    return (result > 0) ? 0 : (result == 0) ? 1 : -1;
}

void capture_destroy(CaptureContext *ctx) {
    if (!ctx) return;
    destroy_shm_image(ctx);
    if (ctx->damage) {
        pthread_mutex_lock(&xlib_mutex);
        XDamageDestroy(ctx->dpy, ctx->damage);
        pthread_mutex_unlock(&xlib_mutex);
    }
    if (ctx->dpy) XCloseDisplay(ctx->dpy);
    free(ctx->tile_cache);
    free(ctx);
}