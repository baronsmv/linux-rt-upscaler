/**
 * @file shm_image.h
 * @brief Management of XShm shared‑memory images.
 */

#ifndef SHM_IMAGE_H
#define SHM_IMAGE_H

#include <X11/Xlib.h>
#include <X11/extensions/XShm.h>

typedef struct CaptureContext CaptureContext;

/** Release all SHM resources. */
void shm_destroy_image(CaptureContext *ctx);

/**
 * Ensure a valid SHM image exists for the current window visual/depth.
 * @return 1 on success, 0 on failure.
 */
int shm_recreate_if_needed(CaptureContext *ctx);

/**
 * Capture a rectangular region into a pre‑allocated BGRA buffer.
 * Uses SHM if possible, falls back to XGetImage.
 * @param ctx   Capture context.
 * @param rx,ry Region offset within the cropped area.
 * @param rw,rh Region dimensions.
 * @param out   Output buffer (must hold rw*rh*4 bytes).
 * @return 0 on success, -1 on failure.
 */
int shm_capture_region(CaptureContext *ctx, int rx, int ry, int rw, int rh,
                       unsigned char *out);

#endif /* SHM_IMAGE_H */