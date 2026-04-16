#include "vk_common.h"
#include "vk_instance.h"
#include "vk_device.h"
#include "vk_heap.h"
#include "vk_resource.h"
#include "vk_sampler.h"
#include "vk_compute.h"
#include "vk_swapchain.h"

/* ----------------------------------------------------------------------------
   Error objects
   ------------------------------------------------------------------------- */
PyObject *vk_Texture2DError = nullptr;
PyObject *vk_BufferError = nullptr;
PyObject *vk_ComputeError = nullptr;
PyObject *vk_SwapchainError = nullptr;
PyObject *vk_HeapError = nullptr;
PyObject *vk_SamplerError = nullptr;
PyObject *vk_Texture1DError = nullptr;
PyObject *vk_Texture3DError = nullptr;

/* ----------------------------------------------------------------------------
   Module methods
   ------------------------------------------------------------------------- */
static PyMethodDef vulkan_module_methods[] = {
    {"get_discovered_devices", (PyCFunction)vk_get_discovered_devices, METH_NOARGS,
     "Return a list of all Vulkan devices in the system."},
    {"enable_debug", (PyCFunction)vk_enable_debug_mode, METH_NOARGS,
     "Enable Vulkan debug output."},
    {"get_shader_binary_type", (PyCFunction)vk_get_shader_binary_type, METH_NOARGS,
     "Return the required shader binary type (SPIR‑V = 1)."},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef vulkan_module = {
    PyModuleDef_HEAD_INIT,
    "vulkan",
    nullptr,
    -1,
    vulkan_module_methods
};

/* ----------------------------------------------------------------------------
   Module initialisation
   ------------------------------------------------------------------------- */
PyMODINIT_FUNC PyInit_vulkan(void) {
    PyObject *m = PyModule_Create(&vulkan_module);
    if (!m) return nullptr;

    // Create error objects
    #define MAKE_ERR(name) \
        vk_##name = PyErr_NewException("vulkan." #name, nullptr, nullptr); \
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

    // Register all types
    #define READY_TYPE(type) \
        if (PyType_Ready(&vk_##type##_Type) < 0) return nullptr; \
        PyModule_AddObject(m, #type, (PyObject *)&vk_##type##_Type);

    READY_TYPE(Device);
    READY_TYPE(Heap);
    READY_TYPE(Resource);
    READY_TYPE(Sampler);
    READY_TYPE(Compute);
    READY_TYPE(Swapchain);

    #undef READY_TYPE

    // Populate format map
    #define VK_FORMAT_MAP(fmt, size) vk_format_map[fmt] = { VK_FORMAT_##fmt, size }
    #define VK_FORMAT_MAP_FLOAT(fmt, size) vk_format_map[fmt##_FLOAT] = { VK_FORMAT_##fmt##_SFLOAT, size }
    #define VK_FORMAT_MAP_SRGB(fmt, size) vk_format_map[fmt##_UNORM_SRGB] = { VK_FORMAT_##fmt##_SRGB, size }

    VK_FORMAT_MAP_FLOAT(R32G32B32A32, 16);
    VK_FORMAT_MAP(R32G32B32A32_UINT, 16);
    VK_FORMAT_MAP(R32G32B32A32_SINT, 16);
    VK_FORMAT_MAP_FLOAT(R32G32B32, 12);
    VK_FORMAT_MAP(R32G32B32_UINT, 12);
    VK_FORMAT_MAP(R32G32B32_SINT, 12);
    VK_FORMAT_MAP_FLOAT(R16G16B16A16, 8);
    VK_FORMAT_MAP(R16G16B16A16_UNORM, 8);
    VK_FORMAT_MAP(R16G16B16A16_UINT, 8);
    VK_FORMAT_MAP(R16G16B16A16_SNORM, 8);
    VK_FORMAT_MAP(R16G16B16A16_SINT, 8);
    VK_FORMAT_MAP_FLOAT(R32G32, 8);
    VK_FORMAT_MAP(R32G32_UINT, 8);
    VK_FORMAT_MAP(R32G32_SINT, 8);
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
    VK_FORMAT_MAP(R8G8_UNORM, 2);
    VK_FORMAT_MAP(R8G8_UINT, 2);
    VK_FORMAT_MAP(R8G8_SNORM, 2);
    VK_FORMAT_MAP(R8G8_SINT, 2);
    VK_FORMAT_MAP_FLOAT(R16, 2);
    VK_FORMAT_MAP(R16_UNORM, 2);
    VK_FORMAT_MAP(R16_UINT, 2);
    VK_FORMAT_MAP(R16_SNORM, 2);
    VK_FORMAT_MAP(R16_SINT, 2);
    VK_FORMAT_MAP(R8_UNORM, 1);
    VK_FORMAT_MAP(R8_UINT, 1);
    VK_FORMAT_MAP(R8_SNORM, 1);
    VK_FORMAT_MAP(R8_SINT, 1);
    VK_FORMAT_MAP(B8G8R8A8_UNORM, 4);
    VK_FORMAT_MAP_SRGB(B8G8R8A8, 4);
    vk_format_map[R10G10B10A2_UNORM] = { VK_FORMAT_A2B10G10R10_UNORM_PACK32, 4 };
    vk_format_map[R10G10B10A2_UINT]  = { VK_FORMAT_A2B10G10R10_UINT_PACK32, 4 };

        // Shader binary type
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

    // Pixel formats (expose the same numeric constants to Python)
    PyModule_AddIntConstant(m, "R32G32B32A32_FLOAT", R32G32B32A32_FLOAT);
    PyModule_AddIntConstant(m, "R32G32B32A32_UINT", R32G32B32A32_UINT);
    PyModule_AddIntConstant(m, "R32G32B32A32_SINT", R32G32B32A32_SINT);
    PyModule_AddIntConstant(m, "R32G32B32_FLOAT", R32G32B32_FLOAT);
    PyModule_AddIntConstant(m, "R32G32B32_UINT", R32G32B32_UINT);
    PyModule_AddIntConstant(m, "R32G32B32_SINT", R32G32B32_SINT);
    PyModule_AddIntConstant(m, "R16G16B16A16_FLOAT", R16G16B16A16_FLOAT);
    PyModule_AddIntConstant(m, "R16G16B16A16_UNORM", R16G16B16A16_UNORM);
    PyModule_AddIntConstant(m, "R16G16B16A16_UINT", R16G16B16A16_UINT);
    PyModule_AddIntConstant(m, "R16G16B16A16_SNORM", R16G16B16A16_SNORM);
    PyModule_AddIntConstant(m, "R16G16B16A16_SINT", R16G16B16A16_SINT);
    PyModule_AddIntConstant(m, "R32G32_FLOAT", R32G32_FLOAT);
    PyModule_AddIntConstant(m, "R32G32_UINT", R32G32_UINT);
    PyModule_AddIntConstant(m, "R32G32_SINT", R32G32_SINT);
    PyModule_AddIntConstant(m, "R10G10B10A2_UNORM", R10G10B10A2_UNORM);
    PyModule_AddIntConstant(m, "R10G10B10A2_UINT", R10G10B10A2_UINT);
    PyModule_AddIntConstant(m, "R8G8B8A8_UNORM", R8G8B8A8_UNORM);
    PyModule_AddIntConstant(m, "R8G8B8A8_UNORM_SRGB", R8G8B8A8_UNORM_SRGB);
    PyModule_AddIntConstant(m, "R8G8B8A8_UINT", R8G8B8A8_UINT);
    PyModule_AddIntConstant(m, "R8G8B8A8_SNORM", R8G8B8A8_SNORM);
    PyModule_AddIntConstant(m, "R8G8B8A8_SINT", R8G8B8A8_SINT);
    PyModule_AddIntConstant(m, "R16G16_FLOAT", R16G16_FLOAT);
    PyModule_AddIntConstant(m, "R16G16_UNORM", R16G16_UNORM);
    PyModule_AddIntConstant(m, "R16G16_UINT", R16G16_UINT);
    PyModule_AddIntConstant(m, "R16G16_SNORM", R16G16_SNORM);
    PyModule_AddIntConstant(m, "R16G16_SINT", R16G16_SINT);
    PyModule_AddIntConstant(m, "R32_FLOAT", R32_FLOAT);
    PyModule_AddIntConstant(m, "R32_UINT", R32_UINT);
    PyModule_AddIntConstant(m, "R32_SINT", R32_SINT);
    PyModule_AddIntConstant(m, "R8G8_UNORM", R8G8_UNORM);
    PyModule_AddIntConstant(m, "R8G8_UINT", R8G8_UINT);
    PyModule_AddIntConstant(m, "R8G8_SNORM", R8G8_SNORM);
    PyModule_AddIntConstant(m, "R8G8_SINT", R8G8_SINT);
    PyModule_AddIntConstant(m, "R16_FLOAT", R16_FLOAT);
    PyModule_AddIntConstant(m, "R16_UNORM", R16_UNORM);
    PyModule_AddIntConstant(m, "R16_UINT", R16_UINT);
    PyModule_AddIntConstant(m, "R16_SNORM", R16_SNORM);
    PyModule_AddIntConstant(m, "R16_SINT", R16_SINT);
    PyModule_AddIntConstant(m, "R8_UNORM", R8_UNORM);
    PyModule_AddIntConstant(m, "R8_UINT", R8_UINT);
    PyModule_AddIntConstant(m, "R8_SNORM", R8_SNORM);
    PyModule_AddIntConstant(m, "R8_SINT", R8_SINT);
    PyModule_AddIntConstant(m, "B8G8R8A8_UNORM", B8G8R8A8_UNORM);
    PyModule_AddIntConstant(m, "B8G8R8A8_UNORM_SRGB", B8G8R8A8_UNORM_SRGB);

    return m;
}