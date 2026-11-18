/* #8 sweep: does ecore_x read back a window's XDND protocol version? ecore_x_dnd_aware_set() writes
 * XdndAware = ECORE_X_DND_VERSION (5, format 32); ecore_x_dnd_version_get() must return 5. The raw
 * property is also read with XGetWindowProperty and printed as Xlib returns it (long). 0 means every
 * XDND-aware window looks unaware, so no drag can be dropped and no drop is accepted. */
#include <Ecore_X.h>
#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <stdio.h>

int main(void)
{
   if (!ecore_x_init(NULL)) { printf("ecore_x_init failed\n"); return 2; }
   Ecore_X_Window w = ecore_x_window_new(0, 0, 0, 64, 64);
   ecore_x_dnd_aware_set(w, EINA_TRUE);
   ecore_x_sync();
   Display *d = ecore_x_display_get();
   Atom type; int fmt; unsigned long n, after; unsigned char *p = NULL;
   XGetWindowProperty(d, w, XInternAtom(d, "XdndAware", False), 0, 8, False, XA_ATOM, &type, &fmt, &n, &after, &p);
   int v = ecore_x_dnd_version_get(w);
   printf("XdndAware raw: format %d items %lu value %ld | ecore_x_dnd_version_get %d (want %d) %s\n",
          fmt, n, p ? ((long *)p)[0] : -1L, v, ECORE_X_DND_VERSION,
          v == ECORE_X_DND_VERSION ? "ok" : "MISMATCH");
   if (p) XFree(p);
   ecore_x_window_free(w); ecore_x_shutdown();
   return v != ECORE_X_DND_VERSION;
}
