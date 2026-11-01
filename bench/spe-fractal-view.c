/* SPDX-License-Identifier: MIT. Displays only verified equal benchmark pixels. */
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
static int nibble(char c){return c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:-1;}
int main(int argc,char **argv) {
 if(argc<2)return 1;FILE *f=fopen(argv[1],"r");if(!f)return 2;
 char *line=malloc(26000);unsigned char image[2][128*96];int found[2]={0,0},pass=0;char timings[6][200];int nt=0;
 while(fgets(line,26000,f)) {
  if(!strncmp(line,"FRACTAL_TIME ",13)&&nt<6){snprintf(timings[nt++],200,"%.180s",line);}
  if(strstr(line,"FRACTAL_PASS identical"))pass=1;
  for(int m=0;m<2;m++){const char *prefix=m?"FRACTAL_PIXELS mode=SPE ":"FRACTAL_PIXELS mode=SOFT ";size_t n=strlen(prefix);if(strncmp(line,prefix,n))continue;if(strlen(line+n)<128*96*2)return 3;
   for(int i=0;i<128*96;i++){int hi=nibble(line[n+i*2]),lo=nibble(line[n+i*2+1]);if(hi<0||lo<0)return 4;image[m][i]=(unsigned char)(hi*16+lo);}found[m]=1;
  }
 }
 fclose(f);free(line);if(!pass||!found[0]||!found[1]||memcmp(image[0],image[1],sizeof image[0])||nt!=6)return 5;
 Display *d=XOpenDisplay(NULL);if(!d)return 6;int s=DefaultScreen(d);Window w=XCreateSimpleWindow(d,RootWindow(d,s),20,10,820,470,0,0,0x101820);XStoreName(d,w,"Verified fractal - SOFTWARE FP vs explicit SPE - QEMU timings only");XSelectInput(d,w,ExposureMask|KeyPressMask);XMapRaised(d,w);GC gc=XCreateGC(d,w,0,NULL);
 XImage *im=XCreateImage(d,DefaultVisual(d,s),DefaultDepth(d,s),ZPixmap,0,NULL,768,288,32,0);if(!im)return 7;im->data=calloc(im->bytes_per_line,im->height);if(!im->data)return 8;
 for(int m=0;m<2;m++)for(int y=0;y<288;y++)for(int x=0;x<384;x++){unsigned n=image[m][(y/3)*128+x/3];unsigned c=n==96?0:((n*13%256)<<16)|((n*7%256)<<8)|(n*19%256);XPutPixel(im,m*384+x,y,c);}
 printf("FRACTAL_VIEW_PASS equal_images=12288_pixels timings=6\n");fflush(stdout);
 for(;;){XEvent e;XNextEvent(d,&e);if(e.type==KeyPress)break;if(e.type!=Expose)continue;XPutImage(d,w,gc,im,0,0,20,45,768,288);XSetForeground(d,gc,0xffffff);const char *a="SOFTWARE FP",*b="EXPLICIT SPE",*note="Identical escape counts. Timings below are this guest run, not hardware performance.";
 XDrawString(d,w,gc,20,25,a,strlen(a));XDrawString(d,w,gc,404,25,b,strlen(b));XDrawString(d,w,gc,20,355,note,strlen(note));for(int i=0;i<nt;i++)XDrawString(d,w,gc,20,375+i*14,timings[i],strcspn(timings[i],"\n"));XFlush(d);}
 XDestroyImage(im);XFreeGC(d,gc);XDestroyWindow(d,w);XCloseDisplay(d);return 0;
}
