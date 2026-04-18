/**
 * @file capture.h
 * @brief Public API for the X11 capture library.
 */

#ifndef CAPTURE_H
#define CAPTURE_H

#include <X11/Xlib.h>
#include <X11/extensions/XShm.h>
#include <X11/extensions/Xdamage.h>
#include <stdint.h>

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
 * Capture context – opaque structure holding all state.
 */
typedef struct CaptureContext {
  Display *dpy;
  Window xid;
  int x, y, width, height;

  /* SHM resources */
  XShmSegmentInfo shminfo;
  XImage *img;
  unsigned long red_mask, green_mask, blue_mask;
  int use_fast_path;
  Visual *last_visual;
  int last_depth;
  int had_shm_failure;

  /* Damage extension */
  int use_damage;
  Damage damage;
  int first_capture_done;

  /* Tile cache */
  TileCacheEntry *tile_cache;
  int tiles_x, tiles_y;
  int tile_size;
  int tile_threshold_percent;
  int debug;
} CaptureContext;

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Create a capture context.
 * @param xid        X11 window ID.
 * @param crop_left  Left crop offset.
 * @param crop_top   Top crop offset.
 * @param width      Width of region to capture.
 * @param height     Height of region to capture.
 * @return Opaque context pointer, or NULL on failure.
 */
CaptureContext *capture_create(XID xid, int crop_left, int crop_top, int width,
                               int height);

/**
 * Capture a frame and return a list of changed rectangles.
 * @param ctx         Capture context.
 * @param output_data Pre‑allocated buffer (width*height*4 bytes) to hold BGRA
 * data.
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

/**
 * Get the underlying XCB connection for use with Vulkan/XCB surfaces.
 * Returns NULL if no connection is available.
 * The returned pointer must be cast to xcb_connection_t* by the caller.
 */
void* capture_get_xcb_connection(CaptureContext *ctx);

#ifdef __cplusplus
}
#endif

#endif /* CAPTURE_H */