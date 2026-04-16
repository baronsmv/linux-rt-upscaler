/**
 * @file vulkan_device.h
 * @brief Vulkan device abstraction – creation, queues, command pools, and
 * resource factories.
 */

#ifndef VULKAN_DEVICE_H
#define VULKAN_DEVICE_H

#include "vulkan_types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* -------------------------------------------------------------------------
   Public Python type object (defined in vulkan_device.c)
   ------------------------------------------------------------------------- */
extern PyTypeObject VkComp_Device_Type;

/* -------------------------------------------------------------------------
   Python object lifecycle (called by type)
   ------------------------------------------------------------------------- */
PyObject *VkComp_Device_New(PyTypeObject *type, PyObject *args, PyObject *kwds);
void VkComp_Device_Dealloc(VkComp_Device *self);

/* -------------------------------------------------------------------------
   Internal device methods
   ------------------------------------------------------------------------- */

/**
 * @brief Ensure the device is fully initialized (lazy creation of logical
 * device).
 */
VkComp_Device *VkComp_Device_GetActive(VkComp_Device *self);

/**
 * @brief Allocate a temporary command buffer from the device's command pool.
 */
VkResult VkComp_Device_AllocateCmd(VkComp_Device *device,
                                   VkCommandBuffer *pCmd);

/**
 * @brief Free a temporary command buffer.
 */
void VkComp_Device_FreeCmd(VkComp_Device *device, VkCommandBuffer cmd);

/**
 * @brief Submit a command buffer and wait for completion using a timeline
 * semaphore.
 */
VkResult VkComp_Device_SubmitAndWait(VkComp_Device *device, VkCommandBuffer cmd,
                                     VkFence fence);

/**
 * @brief Acquire a staging buffer from the device's pool or allocate a new one.
 */
VkResult VkComp_Device_AcquireStagingBuffer(VkComp_Device *device,
                                            VkDeviceSize size,
                                            VkBuffer *pBuffer,
                                            VkDeviceMemory *pMemory,
                                            VkBool32 *pFromPool);

/**
 * @brief Release a staging buffer (if not from pool, it is destroyed).
 */
void VkComp_Device_ReleaseStagingBuffer(VkComp_Device *device, VkBuffer buffer,
                                        VkDeviceMemory memory,
                                        VkBool32 fromPool);

/* -------------------------------------------------------------------------
   Python method declarations (exposed to Python)
   ------------------------------------------------------------------------- */
PyObject *VkComp_Device_CreateHeap(VkComp_Device *self, PyObject *args);
PyObject *VkComp_Device_CreateBuffer(VkComp_Device *self, PyObject *args);
PyObject *VkComp_Device_CreateTexture2D(VkComp_Device *self, PyObject *args);
PyObject *VkComp_Device_CreateSampler(VkComp_Device *self, PyObject *args);
PyObject *VkComp_Device_CreateCompute(VkComp_Device *self, PyObject *args,
                                      PyObject *kwds);
PyObject *VkComp_Device_CreateSwapchain(VkComp_Device *self, PyObject *args);
PyObject *VkComp_Device_GetDebugMessages(VkComp_Device *self, PyObject *args);
PyObject *VkComp_Device_SetBufferPoolSize(VkComp_Device *self, PyObject *args);
PyObject *VkComp_Device_WaitIdle(VkComp_Device *self, PyObject *args);

#ifdef __cplusplus
}
#endif

#endif /* VULKAN_DEVICE_H */