#ifndef VK_RESOURCE_H
#define VK_RESOURCE_H

#include "vk_common.h"

/* ----------------------------------------------------------------------------
   Resource type definition
   ------------------------------------------------------------------------- */
extern PyTypeObject vk_Resource_Type;

/* ----------------------------------------------------------------------------
   Resource deallocator (internal)
   ------------------------------------------------------------------------- */
void vk_Resource_dealloc(vk_Resource *self);

/* ----------------------------------------------------------------------------
   Python method: upload
   ------------------------------------------------------------------------- */
/**
 * Upload data from a Python bytes-like object into a buffer resource.
 *
 * Args:
 *     data (bytes): data to upload.
 *     offset (int, optional): destination offset in bytes (default 0).
 */
PyObject *vk_Resource_upload(vk_Resource *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Python method: upload2d
   ------------------------------------------------------------------------- */
/**
 * Upload data into a buffer resource with 2D pitch.
 *
 * Args:
 *     data (bytes): source data.
 *     pitch (int): destination row pitch in bytes.
 *     width (int): width of the rectangle in pixels.
 *     height (int): height of the rectangle in pixels.
 *     bpp (int): bytes per pixel.
 */
PyObject *vk_Resource_upload2d(vk_Resource *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Python method: upload_subresource
   ------------------------------------------------------------------------- */
/**
 * Upload a rectangular region into a texture resource.
 *
 * Args:
 *     data (bytes): source data.
 *     x (int): destination X offset.
 *     y (int): destination Y offset.
 *     width (int): width in pixels.
 *     height (int): height in pixels.
 */
PyObject *vk_Resource_upload_subresource(vk_Resource *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Python method: upload_subresources
   ------------------------------------------------------------------------- */
/**
 * Batch upload of multiple rectangular regions into a texture resource.
 *
 * Args:
 *     rects (list): list of 5‑tuples (data, x, y, width, height).
 */
PyObject *vk_Resource_upload_subresources(vk_Resource *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Python method: readback
   ------------------------------------------------------------------------- */
/**
 * Read back data from a buffer resource.
 *
 * Args:
 *     size (int, optional): number of bytes to read (default = remaining).
 *     offset (int, optional): source offset in bytes (default 0).
 *
 * Returns:
 *     bytes: the data.
 */
PyObject *vk_Resource_readback(vk_Resource *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Python method: download
   ------------------------------------------------------------------------- */
/**
 * Download the entire texture resource into a bytes object.
 * (Only valid for textures.)
 *
 * Returns:
 *     bytes: raw pixel data (row‑major, RGBA).
 */
PyObject *vk_Resource_download(vk_Resource *self, PyObject *ignored);

/* ----------------------------------------------------------------------------
   Python method: download_regions
   ------------------------------------------------------------------------- */
/**
 * Download multiple rectangular regions from a texture resource.
 *
 * Args:
 *     regions (list): list of 4‑tuples (x, y, width, height).
 *
 * Returns:
 *     list[bytes]: one bytes object per region.
 */
PyObject *vk_Resource_download_regions(vk_Resource *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Python method: copy_to
   ------------------------------------------------------------------------- */
/**
 * Copy data from this resource to another resource.
 * Supports buffer‑to‑buffer, buffer‑to‑texture, texture‑to‑buffer,
 * and texture‑to‑texture.
 *
 * Args:
 *     dst (vk.Resource): destination resource.
 *     size (int, optional): number of bytes to copy (buffer‑to‑buffer only).
 *     src_offset (int, optional): source offset (buffer only).
 *     dst_offset (int, optional): destination offset (buffer only).
 *     width (int, optional): copy width (texture only, default full).
 *     height (int, optional): copy height (texture only, default full).
 *     depth (int, optional): copy depth (texture only, default 1).
 *     src_x, src_y, src_z (int, optional): source offsets.
 *     dst_x, dst_y, dst_z (int, optional): destination offsets.
 *     src_slice (int, optional): source array layer.
 *     dst_slice (int, optional): destination array layer.
 */
PyObject *vk_Resource_copy_to(vk_Resource *self, PyObject *args);

#endif /* VK_RESOURCE_H */