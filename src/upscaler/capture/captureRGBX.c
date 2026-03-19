#include <X11/X.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <stdio.h>

// Macro to define a capture function with a given channel order and alpha
// setting. ORDER should be something like "output_data[ii+2] = red;
// output_data[ii+1] = green; output_data[ii+0] = blue;" ALPHA can be empty or
// "output_data[ii+3] = 0xff;"
#define DEFINE_CAPTURE(NAME, ORDER, ALPHA)                                     \
  int NAME(int xx, int yy, int W, int H, XID xid,                              \
           unsigned char *output_data) {                                       \
    Display *display = XOpenDisplay(NULL);                                     \
    if (!display)                                                              \
      return -1;                                                               \
    XImage *image = XGetImage(display, xid, xx, yy, W, H, AllPlanes, ZPixmap); \
    if (!image) {                                                              \
      XCloseDisplay(display);                                                  \
      return -1;                                                               \
    }                                                                          \
    unsigned long red_mask = image->red_mask;                                  \
    unsigned long green_mask = image->green_mask;                              \
    unsigned long blue_mask = image->blue_mask;                                \
    int ii = 0;                                                                \
    for (int y = 0; y < H; y++) {                                              \
      for (int x = 0; x < W; x++) {                                            \
        unsigned long pixel = XGetPixel(image, x, y);                          \
        unsigned char blue = (pixel & blue_mask);                              \
        unsigned char green = (pixel & green_mask) >> 8;                       \
        unsigned char red = (pixel & red_mask) >> 16;                          \
        ORDER;                                                                 \
        ALPHA;                                                                 \
        ii += 4;                                                               \
      }                                                                        \
    }                                                                          \
    XDestroyImage(image);                                                      \
    XCloseDisplay(display);                                                    \
    return 0;                                                                  \
  }

DEFINE_CAPTURE(captureRGBX, output_data[ii + 0] = red;
               output_data[ii + 1] = green; output_data[ii + 2] = blue;,
               /* no alpha */
)
DEFINE_CAPTURE(captureRGBA, output_data[ii + 0] = red;
               output_data[ii + 1] = green; output_data[ii + 2] = blue;
               , output_data[ii + 3] = 0xff;)
DEFINE_CAPTURE(captureBGRX, output_data[ii + 2] = red;
               output_data[ii + 1] = green; output_data[ii + 0] = blue;,
               /* no alpha */
)
DEFINE_CAPTURE(captureBGRA, output_data[ii + 2] = red;
               output_data[ii + 1] = green; output_data[ii + 0] = blue;
               , output_data[ii + 3] = 0xff;)