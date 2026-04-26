/**
 * @file vk_module.cpp
 * @brief Python module initialisation for the `vulkan` extension.
 *
 * This file is the entry point of the C extension. It defines:
 *   - The `vulkan` module object.
 *   - A table of top-level functions (get_discovered_devices, enable_debug,
 *     get_shader_binary_type).
 *   - The custom exception types used throughout the wrapper.
 *   - All supported Vulkan type objects (Device, Heap, Resource, ...).
 *   - The pixel-format constant -> (VkFormat, bytes per pixel) mapping.
 *   - Numeric constants for sampler filters, address modes, heap types, and
 *     all pixel format enums.
 */

#include "vk_common.h"
#include "vk_compute.h"
#include "vk_device.h"
#include "vk_heap.h"
#include "vk_instance.h"
#include "vk_resource.h"
#include "vk_sampler.h"
#include "vk_swapchain.h"

// =============================================================================
//  Global exception objects (prefixed with vk_)
// =============================================================================

PyObject *vk_Texture2DError = nullptr;
PyObject *vk_BufferError = nullptr;
PyObject *vk_ComputeError = nullptr;
PyObject *vk_SwapchainError = nullptr;
PyObject *vk_HeapError = nullptr;
PyObject *vk_SamplerError = nullptr;
PyObject *vk_Texture1DError = nullptr;
PyObject *vk_Texture3DError = nullptr;

// =============================================================================
//  Module method table (top-level functions)
// =============================================================================

static PyMethodDef vulkan_module_methods[] = {
    {"get_discovered_devices", (PyCFunction)vk_get_discovered_devices,
     METH_NOARGS,
     "Return a list of all Vulkan physical devices in the system."},
    {"enable_debug", (PyCFunction)vk_enable_debug_mode, METH_NOARGS,
     "Enable Vulkan debug output (validation layers and debug utils)."},
    {"get_shader_binary_type", (PyCFunction)vk_get_shader_binary_type,
     METH_NOARGS, "Return the required shader binary type (1 = SPIR-V)."},
    {nullptr, nullptr, 0, nullptr}};

static struct PyModuleDef vulkan_module = {
    PyModuleDef_HEAD_INIT, "vulkan",
    "Low-level Vulkan bindings with compute and presentation support.", -1,
    vulkan_module_methods};

// =============================================================================
//  Module initialisation
// =============================================================================

PyMODINIT_FUNC PyInit_vulkan(void) {
  PyObject *m = PyModule_Create(&vulkan_module);
  if (!m)
    return nullptr;

// -----------------------------------------------------------------
// 1. Create and register all exception types
// -----------------------------------------------------------------
#define MAKE_ERR(name)                                                         \
  vk_##name = PyErr_NewException("vulkan." #name, nullptr, nullptr);           \
  if (!vk_##name)                                                              \
    return nullptr;                                                            \
  PyModule_AddObject(m, #name, vk_##name);

  MAKE_ERR(Texture2DError);
  MAKE_ERR(BufferError);
  MAKE_ERR(ComputeError);
  MAKE_ERR(SwapchainError);
  MAKE_ERR(HeapError);
  MAKE_ERR(SamplerError);
  MAKE_ERR(Texture1DError);
  MAKE_ERR(Texture3DError);

#undef MAKE_ERR

// -----------------------------------------------------------------
// 2. Register all Python types
// -----------------------------------------------------------------
#define READY_TYPE(type)                                                       \
  if (PyType_Ready(&vk_##type##_Type) < 0)                                     \
    return nullptr;                                                            \
  PyModule_AddObject(m, #type, (PyObject *)&vk_##type##_Type);

  READY_TYPE(Device);
  READY_TYPE(Heap);
  READY_TYPE(Resource);
  READY_TYPE(Sampler);
  READY_TYPE(Compute);
  READY_TYPE(Swapchain);

#undef READY_TYPE

// -----------------------------------------------------------------
// 3. Populate the pixel-format map
// -----------------------------------------------------------------
#define VK_FORMAT_MAP(fmt, size) vk_format_map[fmt] = {VK_FORMAT_##fmt, size}
#define VK_FORMAT_MAP_FLOAT(fmt, size)                                         \
  vk_format_map[fmt##_FLOAT] = {VK_FORMAT_##fmt##_SFLOAT, size}
#define VK_FORMAT_MAP_SRGB(fmt, size)                                          \
  vk_format_map[fmt##_UNORM_SRGB] = {VK_FORMAT_##fmt##_SRGB, size}

  // 128-bit formats
  VK_FORMAT_MAP_FLOAT(R32G32B32A32, 16);
  VK_FORMAT_MAP(R32G32B32A32_UINT, 16);
  VK_FORMAT_MAP(R32G32B32A32_SINT, 16);
  VK_FORMAT_MAP_FLOAT(R32G32B32, 12);
  VK_FORMAT_MAP(R32G32B32_UINT, 12);
  VK_FORMAT_MAP(R32G32B32_SINT, 12);

  // 64-bit formats
  VK_FORMAT_MAP_FLOAT(R16G16B16A16, 8);
  VK_FORMAT_MAP(R16G16B16A16_UNORM, 8);
  VK_FORMAT_MAP(R16G16B16A16_UINT, 8);
  VK_FORMAT_MAP(R16G16B16A16_SNORM, 8);
  VK_FORMAT_MAP(R16G16B16A16_SINT, 8);
  VK_FORMAT_MAP_FLOAT(R32G32, 8);
  VK_FORMAT_MAP(R32G32_UINT, 8);
  VK_FORMAT_MAP(R32G32_SINT, 8);

  // 32-bit formats
  VK_FORMAT_MAP(R8G8B8A8_UNORM, 4);
  VK_FORMAT_MAP_SRGB(R8G8B8A8, 4);
  VK_FORMAT_MAP(R8G8B8A8_UINT, 4);
  VK_FORMAT_MAP(R8G8B8A8_SNORM, 4);
  VK_FORMAT_MAP(R8G8B8A8_SINT, 4);
  VK_FORMAT_MAP_FLOAT(R16G16, 4);
  VK_FORMAT_MAP(R16G16_UNORM, 4);
  VK_FORMAT_MAP(R16G16_UINT, 4);
  VK_FORMAT_MAP(R16G16_SNORM, 4);
  VK_FORMAT_MAP(R16G16_SINT, 4);
  VK_FORMAT_MAP_FLOAT(R32, 4);
  VK_FORMAT_MAP(R32_UINT, 4);
  VK_FORMAT_MAP(R32_SINT, 4);

  // 16-bit formats
  VK_FORMAT_MAP(R8G8_UNORM, 2);
  VK_FORMAT_MAP(R8G8_UINT, 2);
  VK_FORMAT_MAP(R8G8_SNORM, 2);
  VK_FORMAT_MAP(R8G8_SINT, 2);
  VK_FORMAT_MAP_FLOAT(R16, 2);
  VK_FORMAT_MAP(R16_UNORM, 2);
  VK_FORMAT_MAP(R16_UINT, 2);
  VK_FORMAT_MAP(R16_SNORM, 2);
  VK_FORMAT_MAP(R16_SINT, 2);

  // 8-bit formats
  VK_FORMAT_MAP(R8_UNORM, 1);
  VK_FORMAT_MAP(R8_UINT, 1);
  VK_FORMAT_MAP(R8_SNORM, 1);
  VK_FORMAT_MAP(R8_SINT, 1);

  // BGRA formats
  VK_FORMAT_MAP(B8G8R8A8_UNORM, 4);
  VK_FORMAT_MAP_SRGB(B8G8R8A8, 4);

  // Special 10-bit format mapping (R10G10B10A2 -> A2R10G10B10 on Vulkan)
  vk_format_map[R10G10B10A2_UNORM] = {VK_FORMAT_A2B10G10R10_UNORM_PACK32, 4};
  vk_format_map[R10G10B10A2_UINT] = {VK_FORMAT_A2B10G10R10_UINT_PACK32, 4};

#undef VK_FORMAT_MAP
#undef VK_FORMAT_MAP_FLOAT
#undef VK_FORMAT_MAP_SRGB

  // -----------------------------------------------------------------
  // 4. Expose module-level constants
  // -----------------------------------------------------------------
  PyModule_AddIntConstant(m, "SHADER_BINARY_TYPE_SPIRV", 1);

  // Sampler filters
  PyModule_AddIntConstant(m, "SAMPLER_FILTER_POINT", 0);
  PyModule_AddIntConstant(m, "SAMPLER_FILTER_LINEAR", 1);

  // Sampler address modes
  PyModule_AddIntConstant(m, "SAMPLER_ADDRESS_MODE_WRAP", 0);
  PyModule_AddIntConstant(m, "SAMPLER_ADDRESS_MODE_MIRROR", 1);
  PyModule_AddIntConstant(m, "SAMPLER_ADDRESS_MODE_CLAMP", 2);

  // Heap types
  PyModule_AddIntConstant(m, "HEAP_DEFAULT", 0);
  PyModule_AddIntConstant(m, "HEAP_UPLOAD", 1);
  PyModule_AddIntConstant(m, "HEAP_READBACK", 2);

// All pixel formats as module-level constants
#define ADD_CONST(name) PyModule_AddIntConstant(m, #name, name)

  ADD_CONST(R32G32B32A32_FLOAT);
  ADD_CONST(R32G32B32A32_UINT);
  ADD_CONST(R32G32B32A32_SINT);
  ADD_CONST(R32G32B32_FLOAT);
  ADD_CONST(R32G32B32_UINT);
  ADD_CONST(R32G32B32_SINT);
  ADD_CONST(R16G16B16A16_FLOAT);
  ADD_CONST(R16G16B16A16_UNORM);
  ADD_CONST(R16G16B16A16_UINT);
  ADD_CONST(R16G16B16A16_SNORM);
  ADD_CONST(R16G16B16A16_SINT);
  ADD_CONST(R32G32_FLOAT);
  ADD_CONST(R32G32_UINT);
  ADD_CONST(R32G32_SINT);
  ADD_CONST(R10G10B10A2_UNORM);
  ADD_CONST(R10G10B10A2_UINT);
  ADD_CONST(R8G8B8A8_UNORM);
  ADD_CONST(R8G8B8A8_UNORM_SRGB);
  ADD_CONST(R8G8B8A8_UINT);
  ADD_CONST(R8G8B8A8_SNORM);
  ADD_CONST(R8G8B8A8_SINT);
  ADD_CONST(R16G16_FLOAT);
  ADD_CONST(R16G16_UNORM);
  ADD_CONST(R16G16_UINT);
  ADD_CONST(R16G16_SNORM);
  ADD_CONST(R16G16_SINT);
  ADD_CONST(R32_FLOAT);
  ADD_CONST(R32_UINT);
  ADD_CONST(R32_SINT);
  ADD_CONST(R8G8_UNORM);
  ADD_CONST(R8G8_UINT);
  ADD_CONST(R8G8_SNORM);
  ADD_CONST(R8G8_SINT);
  ADD_CONST(R16_FLOAT);
  ADD_CONST(R16_UNORM);
  ADD_CONST(R16_UINT);
  ADD_CONST(R16_SNORM);
  ADD_CONST(R16_SINT);
  ADD_CONST(R8_UNORM);
  ADD_CONST(R8_UINT);
  ADD_CONST(R8_SNORM);
  ADD_CONST(R8_SINT);
  ADD_CONST(B8G8R8A8_UNORM);
  ADD_CONST(B8G8R8A8_UNORM_SRGB);

#undef ADD_CONST

  return m;
}