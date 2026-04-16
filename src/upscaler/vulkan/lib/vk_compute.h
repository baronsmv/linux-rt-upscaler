#ifndef VK_COMPUTE_H
#define VK_COMPUTE_H

#include "vk_common.h"

/* ----------------------------------------------------------------------------
   Compute type definition
   ------------------------------------------------------------------------- */
extern PyTypeObject vk_Compute_Type;

/* ----------------------------------------------------------------------------
   Compute deallocator (internal)
   ------------------------------------------------------------------------- */
void vk_Compute_dealloc(vk_Compute *self);

/* ----------------------------------------------------------------------------
   Python method: dispatch
   ------------------------------------------------------------------------- */
/**
 * Execute a compute pipeline.
 *
 * Args:
 *     x (int): number of groups in X dimension.
 *     y (int): number of groups in Y dimension.
 *     z (int): number of groups in Z dimension.
 *     push_data (bytes, optional): push constant data (must be multiple of 4).
 */
PyObject *vk_Compute_dispatch(vk_Compute *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Python method: dispatch_indirect
   ------------------------------------------------------------------------- */
/**
 * Execute an indirect dispatch using arguments from a buffer.
 *
 * Args:
 *     buffer (vk.Resource): buffer containing {x, y, z} as three uint32_t.
 *     offset (int): byte offset into the buffer.
 *     push_data (bytes, optional): push constant data.
 */
PyObject *vk_Compute_dispatch_indirect(vk_Compute *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Python method: dispatch_indirect_batch
   ------------------------------------------------------------------------- */
/**
 * Execute multiple indirect dispatches from a buffer.
 *
 * Args:
 *     buffer (vk.Resource): buffer containing dispatch arguments.
 *     offset (int): starting byte offset.
 *     count (int): number of dispatches.
 *     stride (int): byte stride between argument blocks.
 *     push_data (bytes, optional): push constant data (same for all).
 */
PyObject *vk_Compute_dispatch_indirect_batch(vk_Compute *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Python method: dispatch_sequence
   ------------------------------------------------------------------------- */
/**
 * Execute a sequence of compute dispatches with optional pre‑copy and present.
 *
 * Args (keyword arguments):
 *     sequence (list): list of 5‑tuples (compute, x, y, z, push_data).
 *     copy_src (vk.Resource, optional): source buffer to copy to texture.
 *     copy_dst (vk.Resource, optional): destination texture.
 *     copy_slice (int, optional): texture array slice.
 *     present_image (vk.Resource, optional): texture to transition for present.
 *     timestamps (bool, optional): enable timestamp queries.
 *
 * Returns:
 *     If timestamps enabled, returns a tuple (None, timestamps_list).
 *     Otherwise returns None.
 */
PyObject *vk_Compute_dispatch_sequence(vk_Compute *self, PyObject *args, PyObject *kwds);

/* ----------------------------------------------------------------------------
   Python method: dispatch_tiles
   ------------------------------------------------------------------------- */
/**
 * Dispatch multiple tiles with per‑tile push constants.
 *
 * Args:
 *     tiles (list): list of 3‑tuples (tx, ty, push_data).
 *     tile_width (int): width of each tile in pixels.
 *     tile_height (int): height of each tile in pixels.
 */
PyObject *vk_Compute_dispatch_tiles(vk_Compute *self, PyObject *args);

/* ----------------------------------------------------------------------------
   Bindless binding methods (only valid when bindless > 0)
   ------------------------------------------------------------------------- */
PyObject *vk_Compute_bind_cbv(vk_Compute *self, PyObject *args);
PyObject *vk_Compute_bind_srv(vk_Compute *self, PyObject *args);
PyObject *vk_Compute_bind_uav(vk_Compute *self, PyObject *args);

#endif /* VK_COMPUTE_H */