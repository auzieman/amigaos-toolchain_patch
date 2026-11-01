/* SPDX-License-Identifier: MIT
 * SPE-built GLX demo. Renderer identity is reported, never inferred from FPS.
 */
#include <GL/gl.h>
#include <GL/glx.h>
#include <X11/Xlib.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
static void cube(void) {
 static const GLfloat vertices[8][3]={{-1,-1,-1},{1,-1,-1},{1,1,-1},{-1,1,-1},{-1,-1,1},{1,-1,1},{1,1,1},{-1,1,1}};
 static const int faces[6][4]={{0,1,2,3},{4,7,6,5},{0,4,5,1},{3,2,6,7},{1,5,6,2},{0,3,7,4}};
 static const GLfloat colors[6][3]={{1,.2f,.2f},{.2f,1,.3f},{.2f,.5f,1},{1,.8f,.1f},{.7f,.2f,1},{.2f,1,1}};
 glBegin(GL_QUADS);
 for(int f=0;f<6;f++){glColor3fv(colors[f]);for(int j=0;j<4;j++)glVertex3fv(vertices[faces[f][j]]);}
 glEnd();
}
int main(int argc,char **argv) {
 int frames=120;const char *ppm=NULL;
 for(int i=1;i<argc;i++) {if(!strcmp(argv[i],"--frames")&&i+1<argc)frames=atoi(argv[++i]);else if(!strcmp(argv[i],"--ppm")&&i+1<argc)ppm=argv[++i];else return 1;}
 if(frames<1||frames>3600)return 1;
 Display *d=XOpenDisplay(NULL);if(!d){fputs("XOpenDisplay failed\n",stderr);return 2;}
 int attr[]={GLX_RGBA,GLX_DOUBLEBUFFER,GLX_DEPTH_SIZE,16,None};XVisualInfo *vi=glXChooseVisual(d,DefaultScreen(d),attr);if(!vi)return 3;
 Colormap cmap=XCreateColormap(d,RootWindow(d,vi->screen),vi->visual,AllocNone);
 XSetWindowAttributes wa={.colormap=cmap,.event_mask=ExposureMask|KeyPressMask|StructureNotifyMask};
 Window w=XCreateWindow(d,RootWindow(d,vi->screen),620,480,384,288,0,vi->depth,InputOutput,vi->visual,CWColormap|CWEventMask,&wa);
 XStoreName(d,w,"GL/SPE demo - renderer printed in terminal; no implied GPU pass");XMapWindow(d,w);
 GLXContext c=glXCreateContext(d,vi,NULL,True);if(!c||!glXMakeCurrent(d,w,c))return 4;
 printf("GL_VENDOR=%s\nGL_RENDERER=%s\nGL_VERSION=%s\n",glGetString(GL_VENDOR),glGetString(GL_RENDERER),glGetString(GL_VERSION));fflush(stdout);
 glViewport(0,0,384,288);glEnable(GL_DEPTH_TEST);glMatrixMode(GL_PROJECTION);glLoadIdentity();glFrustum(-1.333,1.333,-1,1,1,20);
 struct timespec start,end;clock_gettime(CLOCK_MONOTONIC,&start);int done=0;unsigned char *pixels=malloc(384u*288u*3u);if(!pixels)return 5;
 for(int frame=0;frame<frames;frame++) {
  while(XPending(d)){XEvent e;XNextEvent(d,&e);if(e.type==KeyPress||e.type==DestroyNotify)done=1;}if(done)break;
  glClearColor(.04f,.06f,.09f,1);glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT);
  glMatrixMode(GL_MODELVIEW);glLoadIdentity();glTranslatef(0,0,-5);glRotatef(25+frame*2,1,.7f,.3f);cube();
  glFinish();glPixelStorei(GL_PACK_ALIGNMENT,1);glReadPixels(0,0,384,288,GL_RGB,GL_UNSIGNED_BYTE,pixels);
  GLenum error=glGetError();if(error!=GL_NO_ERROR){fprintf(stderr,"GL_ERROR=0x%x\n",error);return 6;}
  glXSwapBuffers(d,w);usleep(16000);
 }
 clock_gettime(CLOCK_MONOTONIC,&end);unsigned colored=0;
 for(unsigned i=0;i<384u*288u;i++)if(pixels[i*3]>64||pixels[i*3+1]>64||pixels[i*3+2]>64)colored++;
 if(ppm){FILE *f=fopen(ppm,"wb");if(!f)return 7;fprintf(f,"P6\n384 288\n255\n");for(int y=287;y>=0;y--)if(fwrite(pixels+y*384*3,1,384*3,f)!=384*3)return 8;if(fclose(f))return 9;}
 printf("GL_PIXEL_CHECK=%s colored_pixels=%u elapsed_seconds=%.3f\n",colored>1000?"PASS":"FAIL",colored,(end.tv_sec-start.tv_sec)+(end.tv_nsec-start.tv_nsec)/1e9);
 puts("SPE-built CPU code with measured GL readback; not full ABI or hardware acceleration validation.");
 free(pixels);glXMakeCurrent(d,None,NULL);glXDestroyContext(d,c);XDestroyWindow(d,w);XFreeColormap(d,cmap);XFree(vi);XCloseDisplay(d);return colored>1000?0:10;
}
