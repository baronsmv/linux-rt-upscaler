/**
 * @file vulkan_module.h
 * @brief Vulkan backend module initialization for Python.
 */

#ifndef VULKAN_MODULE_H
#define VULKAN_MODULE_H

#include <Python.h>

#ifdef __cplusplus
extern "C" {
#endif

/* -------------------------------------------------------------------------
   Module entry point
   ------------------------------------------------------------------------- */

/**
 * @brief Initialize the vulkan module.
 * @return The module object on success, NULL on failure.
 */
PyMODINIT_FUNC PyInit_vulkan(void);

#ifdef __cplusplus
}
#endif

#endif /* VULKAN_MODULE_H */