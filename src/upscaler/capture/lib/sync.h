/**
 * @file sync.h
 * @brief Thread‑safety and error handling for X11 calls.
 */

#ifndef SYNC_H
#define SYNC_H

#include <X11/Xlib.h>
#include <pthread.h>

/** Global mutex protecting all Xlib calls. */
extern pthread_mutex_t xlib_mutex;

/** Install the custom X11 error handler. */
void x11_install_error_handler(void);

/** Lock the Xlib mutex. */
void x11_lock(void);

/** Unlock the Xlib mutex. */
void x11_unlock(void);

#endif /* SYNC_H */