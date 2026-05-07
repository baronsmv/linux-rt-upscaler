/**
 * @file sync.c
 * @brief X11 thread safety and error handling.
 */

#include "sync.h"
#include <stdio.h>

pthread_mutex_t xlib_mutex = PTHREAD_MUTEX_INITIALIZER;

static volatile int x11_error_shm_mismatch_flag = 0;

int x11_error_shm_mismatch_occurred(void) {
  int v = x11_error_shm_mismatch_flag;
  x11_error_shm_mismatch_flag = 0;
  return v;
}

static int x11_error_handler(Display *dpy, XErrorEvent *ev) {
  (void)dpy;

  /* Suppress BadMatch during SHM attachment (request 130) */
  if (ev->error_code == BadMatch && ev->request_code == 130)
    return 0;

  /* Treat BadMatch during SHM capture (request 73) as a recoverable visual
   * mismatch. The flag will trigger an immediate SHM rebuild + retry. */
  if (ev->error_code == BadMatch && ev->request_code == 73) {
    x11_error_shm_mismatch_flag = 1;
    return 0;
  }

  /* Other errors are silently ignored, we could log them here if needed. */
  return 0;
}

void x11_install_error_handler(void) { XSetErrorHandler(x11_error_handler); }

void x11_lock(void) { pthread_mutex_lock(&xlib_mutex); }

void x11_unlock(void) { pthread_mutex_unlock(&xlib_mutex); }