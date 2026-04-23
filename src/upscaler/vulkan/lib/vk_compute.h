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
   Python method: dispatch_sequence
   ------------------------------------------------------------------------- */
/**
 * Execute a sequence of compute dispatches with optional pre-copy and
 * presentation.
 *
 * Args (keyword arguments):
 *     sequence (list): list of 5-tuples (compute, x, y, z, push_data).
 *     copy_src (vk.Resource, optional): source buffer to copy to texture.
 *     copy_dst (vk.Resource, optional): destination texture.
 *     copy_slice (int, optional): texture array slice.
 *     present_image (vk.Resource, optional): texture to transition for present.
 *     timestamps (bool, optional): enable timestamp queries.
 *
 * Returns:
 *     If timestamps enabled, returns (None, timestamps_list). Else None.
 */
PyObject *vk_Compute_dispatch_sequence(vk_Compute *self, PyObject *args,
                                       PyObject *kwds);

#endif /* VK_COMPUTE_H */