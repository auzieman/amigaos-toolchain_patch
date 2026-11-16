#include <X11/Xlib.h>
#include <X11/extensions/Xrandr.h>
#include <X11/extensions/Xfixes.h>
#include <X11/extensions/Xrender.h>
#include <X11/extensions/XInput2.h>
#include <X11/extensions/Xcomposite.h>
#include <X11/extensions/Xdamage.h>
#include <X11/Xcursor/Xcursor.h>
#include <X11/xpm.h>
#include <stdio.h>
static char *xpm[] = { "4 2 2 1", "a c #FF0000", "b c #0000FF", "abab", "baba" };
int main(void) {
    Display *d = XOpenDisplay(NULL); if (!d) return 2;
    int ev, er, ma = 2, mi = 4, s = DefaultScreen(d);
    XRRQueryVersion(d, &ma, &mi); printf("randr %d.%d screens=%d\n", ma, mi, XRRGetScreenResources(d, RootWindow(d, s))->noutput >= 0);
    ma = 6; mi = 0; XFixesQueryVersion(d, &ma, &mi); printf("xfixes %d\n", ma);
    ma = 0; mi = 11; XRenderQueryVersion(d, &ma, &mi); printf("render %d.%d\n", ma, mi);
    int op; ma = 2; mi = 2; printf("xinput2 %d\n", XQueryExtension(d, "XInputExtension", &op, &ev, &er) && XIQueryVersion(d, &ma, &mi) == Success);
    printf("composite %d damage %d\n", XCompositeQueryExtension(d, &ev, &er), XDamageQueryExtension(d, &ev, &er));
    Pixmap pm = XCreatePixmap(d, RootWindow(d, s), 16, 16, 24);
    XRenderPictFormat *fmt = XRenderFindStandardFormat(d, PictStandardRGB24);
    Picture pic = XRenderCreatePicture(d, pm, fmt, 0, NULL);
    XRenderColor c = { 0x1234, 0x5678, 0x9abc, 0xffff }; XRenderFillRectangle(d, PictOpSrc, pic, &c, 0, 0, 16, 16);
    XImage *im = XGetImage(d, pm, 5, 5, 1, 1, AllPlanes, ZPixmap); printf("render fill pixel=%06lx\n", XGetPixel(im, 0, 0) & 0xffffff);
    Pixmap xp, xm; XpmAttributes at = { 0 }; int rc = XpmCreatePixmapFromData(d, RootWindow(d, s), xpm, &xp, &xm, &at);
    printf("xpm rc=%d %ux%u\n", rc, at.width, at.height);
    printf("cursor theme size=%d\n", XcursorGetDefaultSize(d) > 0);
    XCloseDisplay(d); return 0;
}
