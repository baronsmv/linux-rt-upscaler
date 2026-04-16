#include "compushady.h"
#include <Python.h>

size_t compushady_get_size_by_pitch(const size_t pitch, const size_t width,
                                    const size_t height, const size_t depth,
                                    const size_t bytes_per_pixel) {
  const size_t rows = height * depth;
  if (rows > 1) {
    return (pitch * (rows - 1)) + (bytes_per_pixel * width);
  }
  return pitch;
}

bool compushady_check_copy_to(
    const bool src_is_buffer, const bool dst_is_buffer, const uint64_t size,
    const uint64_t src_offset, const uint64_t dst_offset,
    const uint64_t src_size, const uint64_t dst_size, const uint32_t src_x,
    const uint32_t src_y, const uint32_t src_z, const uint32_t src_slice,
    const uint32_t src_slices, const uint32_t dst_slice,
    const uint32_t dst_slices, const uint32_t src_width,
    const uint32_t src_height, const uint32_t src_depth,
    const uint32_t dst_width, const uint32_t dst_height,
    const uint32_t dst_depth, uint32_t *dst_x, uint32_t *dst_y, uint32_t *dst_z,
    uint32_t *width, uint32_t *height, uint32_t *depth) {
  // buffer to buffer
  if (src_is_buffer && dst_is_buffer) {
    if (src_offset + size > src_size || dst_offset + size > dst_size) {
      PyErr_Format(PyExc_ValueError,
                   "Resource requested size to copy (%llu) is out of bounds "
                   "(src_size: %llu, src_offset: %llu, dst_size: %llu, "
                   "dst_offset: %llu)",
                   size, src_size, src_offset, dst_size, dst_offset);
      return false;
    }
  }
  // buffer to texture
  else if (src_is_buffer && !dst_is_buffer) {
    *dst_x = 0;
    *dst_y = 0;
    *dst_z = 0;
    if (src_offset + size > src_size || size < dst_size ||
        dst_slice >= dst_slices) {
      PyErr_Format(
          PyExc_ValueError,
          "Resource requested size to copy (%llu) is out of bounds "
          "(src_size: %llu, src_offset: %llu, dst_size: %llu, dst_width: %u, "
          "dst_height: %u, dst_depth: %u dst_slices: %u)",
          size, size, src_offset, dst_size, dst_width, dst_height, dst_depth,
          dst_slices);
      return false;
    }
  }
  // texture to buffer
  else if (!src_is_buffer && dst_is_buffer) {
    *dst_x = 0;
    *dst_y = 0;
    *dst_z = 0;
    if (dst_offset + size > dst_size || size < src_size ||
        src_slice > src_slices) {
      PyErr_Format(
          PyExc_ValueError,
          "Resource requested size to copy (%llu) is out of bounds "
          "(dst_size: %llu, dst_offset: %llu, src_size: %llu, src_width: %u, "
          "src_height: %u, src_depth: %u src_slices: %u)",
          size, dst_size, src_offset, dst_size, src_width, src_height,
          src_depth, src_slices);
      return false;
    }
  }
  // texture to texture
  else {
    if (*width == 0) {
      *width = src_width;
    }

    if (*height == 0) {
      *height = src_height;
    }

    if (*depth == 0) {
      *depth = src_depth;
    }

    if (src_x + *width > src_width || src_y + *height > src_height ||
        src_z + *depth > src_depth || *dst_x + *width > dst_width ||
        *dst_y + *height > dst_height || *dst_z + *depth > dst_depth ||
        src_slice >= src_slices || dst_slice >= dst_slices) {
      PyErr_Format(
          PyExc_ValueError,
          "Resource requested size to copy (width: %u, height: %u, depth: %u) "
          "is out of bounds "
          "(src_width: %u, src_height: %u, src_depth: %u src_slices: %u, "
          "dst_width: %u, dst_height: %u, dst_depth: %u, dst_slices: %u)",
          *width, *height, *depth, src_width, src_height, src_depth, src_slices,
          dst_width, dst_height, dst_depth, dst_slices);
      return false;
    }
  }

  return true;
}