/* SPE client protocol proof against a separate native headless X server. */
#include <stdio.h>
#include <stdlib.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/extensions/Xrender.h>
#include <X11/extensions/Xrandr.h>
#include <X11/extensions/Xfixes.h>
#include <xcb/xcb.h>
int main(int argc,char **argv) {
 if(argc!=2 || !XInitThreads()) return 1;
 Display *d=XOpenDisplay(argv[1]); if(!d) {fputs("XOpenDisplay failed\n",stderr);return 2;}
 int screen=DefaultScreen(d); Window root=RootWindow(d,screen);
 Pixmap p=XCreatePixmap(d,root,4,4,DefaultDepth(d,screen));
 GC gc=XCreateGC(d,p,0,NULL); XSetForeground(d,gc,0x123456);
 XFillRectangle(d,p,gc,0,0,4,4); XSync(d,False);
 XImage *im=XGetImage(d,p,0,0,4,4,AllPlanes,ZPixmap);if(!im)return 3;
 for(int y=0;y<4;y++)for(int x=0;x<4;x++)if((XGetPixel(im,x,y)&0xffffff)!=0x123456)return 4;
 XDestroyImage(im);XFreeGC(d,gc);XFreePixmap(d,p);
 puts("X11_CLIENT_TEST xlib_pixel_roundtrip PASS");
 int a,b;
 if(!XRenderQueryVersion(d,&a,&b))return 5;
 if(!XRRQueryVersion(d,&a,&b))return 6;
 if(!XFixesQueryVersion(d,&a,&b))return 7;
 puts("X11_CLIENT_TEST render_randr_fixes_protocol PASS");
 XCloseDisplay(d);
 xcb_connection_t *c=xcb_connect(argv[1],NULL);if(xcb_connection_has_error(c))return 8;
 xcb_generic_error_t *e=NULL;
 xcb_get_input_focus_reply_t *reply=xcb_get_input_focus_reply(c,xcb_get_input_focus(c),&e);
 if(!reply||e)return 9;free(reply);xcb_disconnect(c);
 puts("X11_CLIENT_TEST xcb_request_reply PASS");
 puts("X11_CLIENT_DONE native headless server; no target Xorg/E/GPU acceptance");return 0;
}
