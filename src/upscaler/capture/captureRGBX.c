#include <stdio.h>
#include <X11/X.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
// For python ctypes, capture a window(xid) with XLIB, saves to provided buffer in RGBX RGBA BGRX BGRA formats
// gcc -shared -O3 -lX11 -fPIC -Wl,-soname,prtscn -o captureRGBX.so captureRGBX.c
// gcc -shared -O3 -lX11 -fPIC -o captureRGBX.so captureRGBX.c
// -03 = SIMD support
// REF https://stackoverflow.com/questions/69645/take-a-screenshot-via-a-python-script-on-linux/16141058#16141058

void captureRGBX(const int, const int, const int, const int, const XID, unsigned char *);
void captureRGBX(const int xx,const int yy,const int W, const int H, const XID xid, unsigned char * output_data) 
{
   Display *display = XOpenDisplay(NULL);
   //Window root = DefaultRootWindow(display);
   //XImage *image = XGetImage(display,root, xx,yy, W,H, AllPlanes, ZPixmap);
   XImage *image = XGetImage(display, xid, 0, 0, W, H, AllPlanes, ZPixmap);
   // if (!image) printf("XGetImage failed xid=%d\n", xid); // xlib aborts with its own error msg, this line does not run

   unsigned long red_mask   = image->red_mask;
   unsigned long green_mask = image->green_mask;
   unsigned long blue_mask  = image->blue_mask;
   int x, y;
   int ii = 0;
   for (y = 0; y < H; y++) {
       for (x = 0; x < W; x++) {
         unsigned long pixel = XGetPixel(image,x,y);
         unsigned char blue  = (pixel & blue_mask);
         unsigned char green = (pixel & green_mask) >> 8;
         unsigned char red   = (pixel & red_mask) >> 16;
         // output_data[ii + 3] = 0;		 
         output_data[ii + 2] = blue;
         output_data[ii + 1] = green;
         output_data[ii + 0] = red;
         ii += 4;
      }
   }
   XDestroyImage(image);
   //XDestroyWindow(display, root);
   XCloseDisplay(display);
}

void captureRGBA(const int, const int, const int, const int, const XID, unsigned char *);
void captureRGBA(const int xx,const int yy,const int W, const int H, const XID xid, unsigned char * output_data) 
{
   Display *display = XOpenDisplay(NULL);
   //Window root = DefaultRootWindow(display);
   //XImage *image = XGetImage(display,root, xx,yy, W,H, AllPlanes, ZPixmap);
   XImage *image = XGetImage(display, xid, 0, 0, W, H, AllPlanes, ZPixmap);
   // if (!image) printf("XGetImage failed xid=%d\n", xid); // xlib aborts with its own error msg, this line does not run

   unsigned long red_mask   = image->red_mask;
   unsigned long green_mask = image->green_mask;
   unsigned long blue_mask  = image->blue_mask;
   int x, y;
   int ii = 0;
   for (y = 0; y < H; y++) {
       for (x = 0; x < W; x++) {
         unsigned long pixel = XGetPixel(image,x,y);
         unsigned char blue  = (pixel & blue_mask);
         unsigned char green = (pixel & green_mask) >> 8;
         unsigned char red   = (pixel & red_mask) >> 16;
         output_data[ii + 3] = 0xff;		 
         output_data[ii + 2] = blue;
         output_data[ii + 1] = green;
         output_data[ii + 0] = red;
         ii += 4;
      }
   }
   XDestroyImage(image);
   //XDestroyWindow(display, root);
   XCloseDisplay(display);
}

void captureBGRX(const int, const int, const int, const int, const XID, unsigned char *);
void captureBGRX(const int xx,const int yy,const int W, const int H, const XID xid, unsigned char * output_data) 
{
   Display *display = XOpenDisplay(NULL);
   //Window root = DefaultRootWindow(display);
   //XImage *image = XGetImage(display,root, xx,yy, W,H, AllPlanes, ZPixmap);
   XImage *image = XGetImage(display, xid, 0, 0, W, H, AllPlanes, ZPixmap);
   // if (!image) printf("XGetImage failed xid=%d\n", xid); // xlib aborts with its own error msg, this line does not run

   unsigned long red_mask   = image->red_mask;
   unsigned long green_mask = image->green_mask;
   unsigned long blue_mask  = image->blue_mask;
   int x, y;
   int ii = 0;
   for (y = 0; y < H; y++) {
       for (x = 0; x < W; x++) {
         unsigned long pixel = XGetPixel(image,x,y);
         unsigned char blue  = (pixel & blue_mask);
         unsigned char green = (pixel & green_mask) >> 8;
         unsigned char red   = (pixel & red_mask) >> 16;
         // output_data[ii + 3] = 0;		 
         output_data[ii + 2] = red; // blue;
         output_data[ii + 1] = green;
         output_data[ii + 0] = blue; // red;
         ii += 4;
      }
   }
   XDestroyImage(image);
   //XDestroyWindow(display, root);
   XCloseDisplay(display);
}

void captureBGRA(const int, const int, const int, const int, const XID, unsigned char *);
void captureBGRA(const int xx,const int yy,const int W, const int H, const XID xid, unsigned char * output_data) 
{
   Display *display = XOpenDisplay(NULL);
   //Window root = DefaultRootWindow(display);
   //XImage *image = XGetImage(display,root, xx,yy, W,H, AllPlanes, ZPixmap);
   XImage *image = XGetImage(display, xid, 0, 0, W, H, AllPlanes, ZPixmap);
   // if (!image) printf("XGetImage failed xid=%d\n", xid); // xlib aborts with its own error msg, this line does not run

   unsigned long red_mask   = image->red_mask;
   unsigned long green_mask = image->green_mask;
   unsigned long blue_mask  = image->blue_mask;
   int x, y;
   int ii = 0;
   for (y = 0; y < H; y++) {
       for (x = 0; x < W; x++) {
         unsigned long pixel = XGetPixel(image,x,y);
         unsigned char blue  = (pixel & blue_mask);
         unsigned char green = (pixel & green_mask) >> 8;
         unsigned char red   = (pixel & red_mask) >> 16;
         output_data[ii + 3] = 0xff;		 
         output_data[ii + 2] = red; // blue;
         output_data[ii + 1] = green;
         output_data[ii + 0] = blue; // red;
         ii += 4;
      }
   }
   XDestroyImage(image);
   //XDestroyWindow(display, root);
   XCloseDisplay(display);
}