#include "compushady.h"
#include "vulkan_common.h"

/* ----------------------------------------------------------------------------
   Error objects (defined here)
   ------------------------------------------------------------------------- */
PyObject *Compushady_Texture2DError = NULL;
PyObject *Compushady_BufferError = NULL;
PyObject *Compushady_ComputeError = NULL;
PyObject *Compushady_SwapchainError = NULL;
PyObject *Compushady_HeapError = NULL;
PyObject *Compushady_SamplerError = NULL;
PyObject *Compushady_Texture1DError = NULL;
PyObject *Compushady_Texture3DError = NULL;

/* ----------------------------------------------------------------------------
   Device discovery
   ------------------------------------------------------------------------- */
PyObject *vulkan_get_discovered_devices(PyObject *self, PyObject *args) {
  if (!vulkan_instance_check())
    return NULL;

  uint32_t count = 0;
  vkEnumeratePhysicalDevices(vulkan_instance, &count, NULL);
  if (count == 0)
    return PyList_New(0);

  VkPhysicalDevice *devices =
      (VkPhysicalDevice *)PyMem_Malloc(count * sizeof(VkPhysicalDevice));
  vkEnumeratePhysicalDevices(vulkan_instance, &count, devices);

  PyObject *list = PyList_New(count);
  for (uint32_t i = 0; i < count; i++) {
    vulkan_Device *dev = PyObject_New(vulkan_Device, &vulkan_Device_Type);
    if (!dev) {
      Py_DECREF(list);
      PyMem_Free(devices);
      return PyErr_NoMemory();
    }
    // Zero all custom fields (skip PyObject header)
    memset((char *)dev + sizeof(PyObject), 0,
           sizeof(vulkan_Device) - sizeof(PyObject));
    dev->physical_device = devices[i];

    VkPhysicalDeviceProperties props;
    vkGetPhysicalDeviceProperties(devices[i], &props);
    dev->name = PyUnicode_FromString(props.deviceName);
    dev->is_discrete =
        (props.deviceType == VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU);
    dev->is_hardware = (props.deviceType != VK_PHYSICAL_DEVICE_TYPE_CPU &&
                        props.deviceType != VK_PHYSICAL_DEVICE_TYPE_OTHER);

    vkGetPhysicalDeviceMemoryProperties(devices[i], &dev->mem_props);
    for (uint32_t j = 0; j < dev->mem_props.memoryHeapCount; j++) {
      if (dev->mem_props.memoryHeaps[j].flags & VK_MEMORY_HEAP_DEVICE_LOCAL_BIT)
        dev->dedicated_video_memory += dev->mem_props.memoryHeaps[j].size;
      else
        dev->shared_system_memory += dev->mem_props.memoryHeaps[j].size;
    }
    dev->vendor_id = props.vendorID;
    dev->device_id = props.deviceID;

    PyList_SetItem(list, i, (PyObject *)dev);
  }
  PyMem_Free(devices);
  return list;
}

/* ----------------------------------------------------------------------------
   Module methods
   ------------------------------------------------------------------------- */
static PyMethodDef vulkan_module_methods[] = {
    {"get_discovered_devices", (PyCFunction)vulkan_get_discovered_devices,
     METH_NOARGS, "Returns the list of discovered GPU devices"},
    {"enable_debug", (PyCFunction)vulkan_enable_debug, METH_NOARGS,
     "Enable GPU debug mode"},
    {"get_shader_binary_type", (PyCFunction)vulkan_get_shader_binary_type,
     METH_NOARGS, "Returns the required shader binary type (SPIR-V = 1)"},
    {NULL, NULL, 0, NULL}};

/* ----------------------------------------------------------------------------
   Module definition
   ------------------------------------------------------------------------- */
static struct PyModuleDef vulkan_module = {PyModuleDef_HEAD_INIT, "vulkan",
                                           NULL, -1, vulkan_module_methods};

/* ----------------------------------------------------------------------------
   Module init
   ------------------------------------------------------------------------- */
PyMODINIT_FUNC PyInit_vulkan(void) {
  PyObject *m = PyModule_Create(&vulkan_module);
  if (!m)
    return NULL;

  // Create error objects
  Compushady_Texture2DError =
      PyErr_NewException("vulkan.Texture2DError", NULL, NULL);
  PyModule_AddObject(m, "Texture2DError", Compushady_Texture2DError);
  Compushady_BufferError = PyErr_NewException("vulkan.BufferError", NULL, NULL);
  PyModule_AddObject(m, "BufferError", Compushady_BufferError);
  Compushady_ComputeError =
      PyErr_NewException("vulkan.ComputeError", NULL, NULL);
  PyModule_AddObject(m, "ComputeError", Compushady_ComputeError);
  Compushady_SwapchainError =
      PyErr_NewException("vulkan.SwapchainError", NULL, NULL);
  PyModule_AddObject(m, "SwapchainError", Compushady_SwapchainError);
  Compushady_HeapError = PyErr_NewException("vulkan.HeapError", NULL, NULL);
  PyModule_AddObject(m, "HeapError", Compushady_HeapError);
  Compushady_SamplerError =
      PyErr_NewException("vulkan.SamplerError", NULL, NULL);
  PyModule_AddObject(m, "SamplerError", Compushady_SamplerError);
  Compushady_Texture1DError =
      PyErr_NewException("vulkan.Texture1DError", NULL, NULL);
  PyModule_AddObject(m, "Texture1DError", Compushady_Texture1DError);
  Compushady_Texture3DError =
      PyErr_NewException("vulkan.Texture3DError", NULL, NULL);
  PyModule_AddObject(m, "Texture3DError", Compushady_Texture3DError);

  // Assign methods to types
  extern PyMethodDef vulkan_Resource_methods[];
  extern PyMethodDef vulkan_Swapchain_methods[];
  extern PyMethodDef vulkan_Compute_methods[];

  vulkan_Resource_Type.tp_methods = vulkan_Resource_methods;
  vulkan_Swapchain_Type.tp_methods = vulkan_Swapchain_methods;
  vulkan_Compute_Type.tp_methods = vulkan_Compute_methods;

  // Register types
  if (PyType_Ready(&vulkan_Device_Type) < 0)
    return NULL;
  PyModule_AddObject(m, "Device", (PyObject *)&vulkan_Device_Type);

  if (PyType_Ready(&vulkan_Heap_Type) < 0)
    return NULL;
  PyModule_AddObject(m, "Heap", (PyObject *)&vulkan_Heap_Type);

  if (PyType_Ready(&vulkan_Resource_Type) < 0)
    return NULL;
  PyModule_AddObject(m, "Resource", (PyObject *)&vulkan_Resource_Type);

  if (PyType_Ready(&vulkan_Sampler_Type) < 0)
    return NULL;
  PyModule_AddObject(m, "Sampler", (PyObject *)&vulkan_Sampler_Type);

  if (PyType_Ready(&vulkan_Compute_Type) < 0)
    return NULL;
  PyModule_AddObject(m, "Compute", (PyObject *)&vulkan_Compute_Type);

  if (PyType_Ready(&vulkan_Swapchain_Type) < 0)
    return NULL;
  PyModule_AddObject(m, "Swapchain", (PyObject *)&vulkan_Swapchain_Type);

// Initialize format table
#define VK_FORMAT(x, size) vulkan_formats[x] = {VK_FORMAT_##x, size}
#define VK_FORMAT_FLOAT(x, size)                                               \
  vulkan_formats[x##_FLOAT] = {VK_FORMAT_##x##_SFLOAT, size}
#define VK_FORMAT_SRGB(x, size)                                                \
  vulkan_formats[x##_UNORM_SRGB] = {VK_FORMAT_##x##_SRGB, size}

  VK_FORMAT_FLOAT(R32G32B32A32, 4 * 4);
  VK_FORMAT(R32G32B32A32_UINT, 4 * 4);
  VK_FORMAT(R32G32B32A32_SINT, 4 * 4);
  VK_FORMAT_FLOAT(R32G32B32, 3 * 4);
  VK_FORMAT(R32G32B32_UINT, 3 * 4);
  VK_FORMAT(R32G32B32_SINT, 3 * 4);
  VK_FORMAT_FLOAT(R16G16B16A16, 4 * 2);
  VK_FORMAT(R16G16B16A16_UNORM, 4 * 2);
  VK_FORMAT(R16G16B16A16_UINT, 4 * 2);
  VK_FORMAT(R16G16B16A16_SNORM, 4 * 2);
  VK_FORMAT(R16G16B16A16_SINT, 4 * 2);
  VK_FORMAT_FLOAT(R32G32, 2 * 4);
  VK_FORMAT(R32G32_UINT, 2 * 4);
  VK_FORMAT(R32G32_SINT, 2 * 4);
  VK_FORMAT(R8G8B8A8_UNORM, 4);
  VK_FORMAT_SRGB(R8G8B8A8, 4);
  VK_FORMAT(R8G8B8A8_UINT, 4);
  VK_FORMAT(R8G8B8A8_SNORM, 4);
  VK_FORMAT(R8G8B8A8_SINT, 4);
  VK_FORMAT_FLOAT(R16G16, 2 * 2);
  VK_FORMAT(R16G16_UNORM, 2 * 2);
  VK_FORMAT(R16G16_UINT, 2 * 2);
  VK_FORMAT(R16G16_SNORM, 2 * 2);
  VK_FORMAT(R16G16_SINT, 2 * 2);
  VK_FORMAT_FLOAT(R32, 4);
  VK_FORMAT(R32_UINT, 4);
  VK_FORMAT(R32_SINT, 4);
  VK_FORMAT(R8G8_UNORM, 2);
  VK_FORMAT(R8G8_UINT, 2);
  VK_FORMAT(R8G8_SNORM, 2);
  VK_FORMAT(R8G8_SINT, 2);
  VK_FORMAT_FLOAT(R16, 2);
  VK_FORMAT(R16_UNORM, 2);
  VK_FORMAT(R16_UINT, 2);
  VK_FORMAT(R16_SNORM, 2);
  VK_FORMAT(R16_SINT, 2);
  VK_FORMAT(R8_UNORM, 1);
  VK_FORMAT(R8_UINT, 1);
  VK_FORMAT(R8_SNORM, 1);
  VK_FORMAT(R8_SINT, 1);
  VK_FORMAT(B8G8R8A8_UNORM, 4);
  VK_FORMAT_SRGB(B8G8R8A8, 4);

  vulkan_formats[R10G10B10A2_UNORM] = {VK_FORMAT_A2B10G10R10_UNORM_PACK32, 4};
  vulkan_formats[R10G10B10A2_UINT] = {VK_FORMAT_A2B10G10R10_UINT_PACK32, 4};

  return m;
}