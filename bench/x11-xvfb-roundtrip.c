#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <stdio.h>
#include <string.h>
int main(void) {
    Display *d = XOpenDisplay(NULL);
    if (!d) { puts("XOpenDisplay failed"); return 1; }
    int s = DefaultScreen(d);
    Window w = XCreateSimpleWindow(d, RootWindow(d, s), 0, 0, 64, 32, 0, 0, WhitePixel(d, s));
    Atom a = XInternAtom(d, "TABOR_SPE_TEST", False);
    XStoreName(d, w, "spe-gcc14");
    XMapWindow(d, w); XSync(d, False);
    char *name = NULL; XFetchName(d, w, &name);
    XImage *img = XGetImage(d, w, 0, 0, 8, 8, AllPlanes, ZPixmap);
    unsigned long px = img ? XGetPixel(img, 3, 3) : 0;
    printf("vendor=%s release=%d screen=%dx%d depth=%d atom=%s name=%s pixel=%06lx\n",
           ServerVendor(d), VendorRelease(d), DisplayWidth(d, s), DisplayHeight(d, s),
           DefaultDepth(d, s), XGetAtomName(d, a), name ? name : "?", px & 0xffffff);
    int ok = name && !strcmp(name, "spe-gcc14") && (px & 0xffffff) == (WhitePixel(d, s) & 0xffffff);
    XCloseDisplay(d);
    puts(ok ? "X11 roundtrip ok" : "X11 roundtrip MISMATCH");
    return !ok;
}
