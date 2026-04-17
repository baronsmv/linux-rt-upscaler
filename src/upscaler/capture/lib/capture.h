/**
 * @file capture.h
 * @brief Public API for the XCB capture library.
 */

#ifndef CAPTURE_H
#define CAPTURE_H

#include <xcb/xcb.h>
#include <xcb/shm.h>
#include <xcb/xfixes.h>
#include <xcb/damage.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Configuration constants */
#define DEFAULT_TILE_SIZE 64
#define MIN_TILE_SIZE 16
#define DEFAULT_THRESHOLD 30

/** Public output rectangle. */
typedef struct {
    int x, y, width, height;
    unsigned long long hash;
} OutputRect;

/** Internal tile cache entry. */
typedef struct TileCacheEntry {
    int x, y, width, height;
    unsigned long long hash;
} TileCacheEntry;

/**
 * Capture context – opaque structure.
 */
typedef struct CaptureContext {
    xcb_connection_t *conn;
    xcb_window_t xid;
    int x, y, width, height;

    /* SHM resources */
    xcb_shm_seg_t shm_seg;
    uint32_t shm_id;        /* OS shm id */
    void *shm_addr;         /* mapped address */
    int shm_attached;
    uint8_t depth;
    xcb_visualid_t visual;
    int use_fast_path;      /* 1 if visual is 32‑bit TrueColor */

    /* Pixel format info for BGRA conversion */
    uint32_t red_mask;
    uint32_t green_mask;
    uint32_t blue_mask;
    int bits_per_pixel;
    int had_shm_failure;    /* flag to avoid repeated SHM attempts */

    /* Damage extension */
    int use_damage;
    xcb_damage_damage_t damage;
    int first_capture_done;

    /* Tile cache */
    TileCacheEntry *tile_cache;
    int tiles_x, tiles_y;
    int tile_size;
    int tile_threshold_percent;
    int debug;
} CaptureContext;

/**
 * Create a capture context.
 * @param conn       XCB connection (must remain valid for lifetime of context).
 * @param xid        X11 window ID.
 * @param crop_left  Left crop offset.
 * @param crop_top   Top crop offset.
 * @param width      Width of region to capture.
 * @param height     Height of region to capture.
 * @return Opaque context pointer, or NULL on failure.
 */
CaptureContext *capture_create(xcb_connection_t *conn, xcb_window_t xid,
                               int crop_left, int crop_top, int width, int height);

/**
 * Capture a frame and return a list of changed rectangles.
 * @param ctx         Capture context.
 * @param output_data Pre‑allocated buffer (width*height*4 bytes) to hold BGRA data.
 * @param rects       Array to receive output rectangles.
 * @param max_rects   Maximum number of rectangles to return.
 * @return Number of rectangles written, -1 on error.
 */
int capture_grab_damage(CaptureContext *ctx, unsigned char *output_data,
                        OutputRect *rects, int max_rects);

/**
 * Simplified capture – returns 0 on success, 1 if no change, -1 on error.
 */
int capture_grab(CaptureContext *ctx, unsigned char *output_data);

/**
 * Destroy the capture context and free all resources.
 */
void capture_destroy(CaptureContext *ctx);

#ifdef __cplusplus
}
#endif

#endif /* CAPTURE_H */