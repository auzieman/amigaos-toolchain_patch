/* SPDX-License-Identifier: MIT */
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/extensions/Xcomposite.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
int main(int argc,char **argv) {
 Display *d=XOpenDisplay(NULL);if(!d)return 1;
 int s=DefaultScreen(d);Window root=RootWindow(d,s);
 Window w=XCreateSimpleWindow(d,root,40,40,320,240,0,0,0);
 int major,minor;XCompositeQueryVersion(d,&major,&minor);printf("Composite version %d.%d selection_owner=%lu\n",major,minor,XGetSelectionOwner(d,XInternAtom(d,"_NET_WM_CM_S0",False)));
 if(getenv("REDIRECT_TEST"))XCompositeRedirectWindow(d,w,CompositeRedirectManual);
 XStoreName(d,w,"SPE X11 pixel diagnostic - RED GREEN / BLUE WHITE");
 XSelectInput(d,w,ExposureMask|StructureNotifyMask);XMapRaised(d,w);XSync(d,False);sleep(10);
 GC gc=XCreateGC(d,w,0,NULL);unsigned long colors[4]={0xff0000,0x00ff00,0x0000ff,0xffffff};
 for(int i=0;i<4;i++){XSetForeground(d,gc,colors[i]);XFillRectangle(d,w,gc,(i%2)*160,(i/2)*120,160,120);}
 XSync(d,False);sleep(2);
 int failed=0;XImage *im=XGetImage(d,w,0,0,320,240,AllPlanes,ZPixmap);if(!im)return 2;
 for(int i=0;i<4;i++){unsigned long p=XGetPixel(im,(i%2)*160+40,(i/2)*120+40)&0xffffff;printf("client quadrant %d expected=%06lx got=%06lx %s\n",i,colors[i],p,p==colors[i]?"PASS":"FAIL");failed|=p!=colors[i];}XDestroyImage(im);
 Pixmap p=XCompositeNameWindowPixmap(d,w);im=XGetImage(d,p,0,0,320,240,AllPlanes,ZPixmap);if(!im)return 3;
 for(int i=0;i<4;i++){unsigned long got=XGetPixel(im,(i%2)*160+40,(i/2)*120+40)&0xffffff;printf("redirected pixmap quadrant %d got=%06lx %s\n",i,got,got==colors[i]?"PASS":"FAIL");failed|=got!=colors[i];}XDestroyImage(im);XFreePixmap(d,p);fflush(stdout);
 if(argc>1)sleep((unsigned int)atoi(argv[1]));XFreeGC(d,gc);XDestroyWindow(d,w);XCloseDisplay(d);return failed?4:0;
}
