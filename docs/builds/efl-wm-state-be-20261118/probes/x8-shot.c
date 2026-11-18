/* #8 test B: screenshot the X screen and measure each client window's interior.
 * Saves the root window as a binary PPM (argv[1]) and, for every client window (the window
 * manager's _NET_CLIENT_LIST, or the mapped top-level windows when there is none), prints its
 * name, geometry, the share of pure-black pixels inside it (2-pixel inset) and its mean colour,
 * all read from the same root image, i.e. what is on the screen. */
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <X11/Xutil.h>
#include <stdio.h>
#include <stdlib.h>

static void measure(Display *d, XImage *im, Window w, int W, int H)
{
   XWindowAttributes wa;
   if (!XGetWindowAttributes(d, w, &wa) || wa.map_state != IsViewable) return;
   int x, y; Window child;
   XTranslateCoordinates(d, w, DefaultRootWindow(d), 0, 0, &x, &y, &child);
   char *name = NULL; XFetchName(d, w, &name);
   long n = 0, black = 0, sr = 0, sg = 0, sb = 0;
   for (int j = y + 2; j < y + wa.height - 2; j++)
      for (int i = x + 2; i < x + wa.width - 2; i++) {
         if (i < 0 || j < 0 || i >= W || j >= H) continue;
         unsigned long p = XGetPixel(im, i, j);
         int r = (p >> 16) & 0xff, g = (p >> 8) & 0xff, b = p & 0xff;
         n++; black += !(r | g | b); sr += r; sg += g; sb += b;
      }
   if (n)
      printf("WINDOW 0x%lx \"%s\" %dx%d+%d+%d depth %d: black %.1f%% mean %ld/%ld/%ld\n", w, name ? name : "",
             wa.width, wa.height, x, y, wa.depth, 100.0 * black / n, sr / n, sg / n, sb / n);
   if (name) XFree(name);
}

int main(int argc, char **argv)
{
   Display *d = XOpenDisplay(NULL);
   if (!d || argc < 2) { printf("usage: x8-shot out.ppm (DISPLAY set)\n"); return 2; }
   Window root = DefaultRootWindow(d);
   int W = DisplayWidth(d, 0), H = DisplayHeight(d, 0);
   XImage *im = XGetImage(d, root, 0, 0, W, H, AllPlanes, ZPixmap);
   if (!im) { printf("XGetImage root failed\n"); return 2; }
   FILE *f = fopen(argv[1], "wb");
   fprintf(f, "P6\n%d %d\n255\n", W, H);
   for (int j = 0; j < H; j++)
      for (int i = 0; i < W; i++) {
         unsigned long p = XGetPixel(im, i, j);
         unsigned char c[3] = { (p >> 16) & 0xff, (p >> 8) & 0xff, p & 0xff };
         fwrite(c, 1, 3, f);
      }
   fclose(f);
   Atom list = XInternAtom(d, "_NET_CLIENT_LIST", True), type; int fmt; unsigned long cnt = 0, after;
   unsigned char *data = NULL;
   if (list != None && XGetWindowProperty(d, root, list, 0, 1024, False, XA_WINDOW, &type, &fmt, &cnt, &after, &data) == Success && cnt) {
      printf("clients (_NET_CLIENT_LIST): %lu\n", cnt);
      for (unsigned long k = 0; k < cnt; k++) measure(d, im, ((Window *)data)[k], W, H);
   } else {
      Window r, p, *kids; unsigned int nk;
      XQueryTree(d, root, &r, &p, &kids, &nk);
      printf("no window manager client list; top-level windows: %u\n", nk);
      for (unsigned int k = 0; k < nk; k++) measure(d, im, kids[k], W, H);
   }
   printf("saved %s %dx%d\n", argv[1], W, H);
   return 0;
}
