/* #8 test A: does a redirected window's content come back right through Composite + XGetImage on a
 * big-endian SPE X server? This is the read E's software compositor does (e_pixmap_image_draw ->
 * ecore_x_image_get), with no EFL involved.
 *
 * A window at the default visual (and, if the server has one, a 32-bit ARGB window) is redirected
 * manually, filled with four quadrants by the core protocol (XFillRectangle: red, green, blue,
 * white) and with one quadrant by XPutImage, then read back three ways:
 *   1. XGetImage of the window;
 *   2. XGetImage of the pixmap from XCompositeNameWindowPixmap (the compositor's source);
 *   3. XShmGetImage of that pixmap, when MIT-SHM is available.
 * Each read prints the image byte order, bpp, depth and visual masks, and every quadrant's pixel
 * value, compared with what the visual's masks say it must be. Exit 0 if every read matches. */
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/extensions/Xcomposite.h>
#include <X11/extensions/XShm.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <unistd.h>

static int bad;
static const char *names[4] = { "red (fill)", "green (fill)", "blue (fill)", "white (PutImage)" };

static unsigned long pix(Visual *v, int r, int g, int b)
{
   unsigned long p = 0;
   for (int c = 0; c < 3; c++) {
      unsigned long m = c == 0 ? v->red_mask : c == 1 ? v->green_mask : v->blue_mask;
      int val = c == 0 ? r : c == 1 ? g : b, sh = 0;
      while (m && !(m & 1)) { m >>= 1; sh++; }
      p |= ((unsigned long)(val * (long)m / 255) & m) << sh;
   }
   return p;
}

static void check(const char *how, XImage *im, Visual *v, int w, int h, unsigned long want[4], unsigned long rgbmask)
{
   if (!im) { printf("  %-22s no image\n", how); bad++; return; }
   printf("  %-22s byte_order=%s bpp=%d depth=%d masks=%06lx/%06lx/%06lx\n", how,
          im->byte_order == MSBFirst ? "MSB" : "LSB", im->bits_per_pixel, im->depth, v->red_mask, v->green_mask, v->blue_mask);
   int xs[4] = { w / 4, 3 * w / 4, w / 4, 3 * w / 4 }, ys[4] = { h / 4, h / 4, 3 * h / 4, 3 * h / 4 };
   for (int i = 0; i < 4; i++) {
      unsigned long p = XGetPixel(im, xs[i], ys[i]);
      unsigned char *raw = (unsigned char *)im->data + ys[i] * im->bytes_per_line + xs[i] * im->bits_per_pixel / 8;
      int ok = (p & rgbmask) == (want[i] & rgbmask);
      bad += !ok;
      printf("    %-17s pixel=%08lx want=%08lx bytes=%02x %02x %02x %02x %s\n", names[i], p, want[i],
             raw[0], raw[1], raw[2], raw[3], ok ? "ok" : "MISMATCH");
   }
}

static void one(Display *d, Visual *v, int depth, Colormap cm, int shm_ok, const char *label)
{
   const int W = 256, H = 256;
   XSetWindowAttributes a = { 0 };
   a.colormap = cm; a.border_pixel = 0; a.background_pixel = 0;
   Window w = XCreateWindow(d, DefaultRootWindow(d), 10, 10, W, H, 0, depth, InputOutput, v,
                            CWColormap | CWBorderPixel | CWBackPixel, &a);
   XCompositeRedirectWindow(d, w, CompositeRedirectManual);
   XMapWindow(d, w); XSync(d, False);
   GC gc = XCreateGC(d, w, 0, NULL);
   unsigned long want[4] = { pix(v, 255, 0, 0), pix(v, 0, 255, 0), pix(v, 0, 0, 255), pix(v, 255, 255, 255) };
   if (depth == 32) for (int i = 0; i < 4; i++) want[i] |= 0xff000000UL;   /* opaque ARGB */
   int qx[4] = { 0, W / 2, 0, W / 2 }, qy[4] = { 0, 0, H / 2, H / 2 };
   for (int i = 0; i < 3; i++) {
      XSetForeground(d, gc, want[i]); XFillRectangle(d, w, gc, qx[i], qy[i], W / 2, H / 2);
   }
   XImage *put = XCreateImage(d, v, depth, ZPixmap, 0, malloc(W / 2 * H / 2 * 4), W / 2, H / 2, 32, 0);
   for (int y = 0; y < H / 2; y++) for (int x = 0; x < W / 2; x++) XPutPixel(put, x, y, want[3]);
   XPutImage(d, w, gc, put, 0, 0, qx[3], qy[3], W / 2, H / 2);
   XSync(d, False);
   unsigned long rgbmask = v->red_mask | v->green_mask | v->blue_mask | (depth == 32 ? 0xff000000UL : 0);
   printf("%s: visual 0x%lx depth %d\n", label, XVisualIDFromVisual(v), depth);
   check("XGetImage window", XGetImage(d, w, 0, 0, W, H, AllPlanes, ZPixmap), v, W, H, want, rgbmask);
   Pixmap p = XCompositeNameWindowPixmap(d, w);
   check("XGetImage pixmap", XGetImage(d, p, 0, 0, W, H, AllPlanes, ZPixmap), v, W, H, want, rgbmask);
   if (shm_ok) {
      XShmSegmentInfo si;
      XImage *im = XShmCreateImage(d, v, depth, ZPixmap, NULL, &si, W, H);
      si.shmid = shmget(IPC_PRIVATE, im->bytes_per_line * H, IPC_CREAT | 0600);
      si.shmaddr = im->data = shmat(si.shmid, NULL, 0); si.readOnly = False;
      XShmAttach(d, &si); XSync(d, False);
      if (XShmGetImage(d, p, im, 0, 0, AllPlanes)) check("XShmGetImage pixmap", im, v, W, H, want, rgbmask);
      else { printf("  XShmGetImage pixmap   failed\n"); bad++; }
      XShmDetach(d, &si); shmdt(si.shmaddr); shmctl(si.shmid, IPC_RMID, NULL);
   } else printf("  XShmGetImage pixmap   skipped (no MIT-SHM)\n");
   XFreePixmap(d, p); XDestroyWindow(d, w); XSync(d, False);
}

int main(void)
{
   Display *d = XOpenDisplay(NULL);
   if (!d) { printf("cannot open display\n"); return 2; }
   int ev, er, maj = 0, min = 4;
   if (!XCompositeQueryExtension(d, &ev, &er) || !XCompositeQueryVersion(d, &maj, &min)) { printf("no Composite\n"); return 2; }
   int shm_ok = XShmQueryExtension(d);
   printf("server %s %d, ImageByteOrder=%s BitmapBitOrder=%s, Composite %d.%d, MIT-SHM %s\n",
          ServerVendor(d), VendorRelease(d), ImageByteOrder(d) == MSBFirst ? "MSB" : "LSB",
          BitmapBitOrder(d) == MSBFirst ? "MSB" : "LSB", maj, min, shm_ok ? "yes" : "no");
   one(d, DefaultVisual(d, DefaultScreen(d)), DefaultDepth(d, DefaultScreen(d)), DefaultColormap(d, DefaultScreen(d)), shm_ok, "default visual");
   XVisualInfo vi;
   if (XMatchVisualInfo(d, DefaultScreen(d), 32, TrueColor, &vi)) {
      Colormap cm = XCreateColormap(d, DefaultRootWindow(d), vi.visual, AllocNone);
      one(d, vi.visual, 32, cm, shm_ok, "ARGB visual");
   } else printf("no 32-bit TrueColor visual\n");
   printf("RESULT %s (%d mismatches)\n", bad ? "FAIL" : "PASS", bad);
   XCloseDisplay(d);
   return bad ? 1 : 0;
}
