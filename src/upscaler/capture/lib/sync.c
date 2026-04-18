/**
 * @file sync.c
 * @brief X11 thread safety and error handling.
 */

#include "sync.h"
#include <stdio.h>

pthread_mutex_t xlib_mutex = PTHREAD_MUTEX_INITIALIZER;

static int x11_error_handler(Display *dpy, XErrorEvent *ev) {
  (void)dpy;
  /* Suppress BadMatch during SHM attachment */
  if (ev->error_code == BadMatch && ev->request_code == 130)
    return 0;
  /* Other errors could be logged here if desired */
  return 0;
}

void x11_install_error_handler(void) { XSetErrorHandler(x11_error_handler); }

void x11_lock(void) { pthread_mutex_lock(&xlib_mutex); }

void x11_unlock(void) { pthread_mutex_unlock(&xlib_mutex); }