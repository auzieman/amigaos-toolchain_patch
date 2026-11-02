/* SPDX-License-Identifier: MIT. Isolate Evas drawing from E's compositor. */
#include <Ecore.h>
#include <Ecore_Evas.h>
#include <Ecore_X.h>
#include <Edje.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <stdio.h>
#include <string.h>
static Ecore_Evas *ee;
static int result=1, wallpaper, automatic;
static Eina_Bool check(void *data) {
 (void)data;if(!automatic)ecore_evas_manual_render(ee);ecore_x_sync();
 Display *d=XOpenDisplay(NULL);if(!d){ecore_main_loop_quit();return ECORE_CALLBACK_CANCEL;}
 Window w=ecore_evas_software_x11_window_get(ee);
 XImage *im=XGetImage(d,w,0,0,320,240,AllPlanes,ZPixmap);
 if(im){
  unsigned long colors[]={0xff0000,0x00ff00,0x0000ff,0xffffff};int failed=0;
  if(wallpaper){
   unsigned nonblack=0;for(int y=0;y<240;y++)for(int x=0;x<320;x++)nonblack+=!!(XGetPixel(im,x,y)&0xffffff);
   printf("EVAS_WALLPAPER nonblack=%u %s\n",nonblack,nonblack>100?"PASS":"FAIL");failed=nonblack<=100;
  }else for(int i=0;i<4;i++){
   unsigned long got=XGetPixel(im,(i%2)*160+40,(i/2)*120+40)&0xffffff;
   printf("EVAS_RECT quadrant=%d expected=%06lx got=%06lx %s\n",i,colors[i],got,got==colors[i]?"PASS":"FAIL");failed|=got!=colors[i];
  }
  XDestroyImage(im);result=failed?2:0;
 }
 XCloseDisplay(d);fflush(stdout);ecore_main_loop_quit();return ECORE_CALLBACK_CANCEL;
}
int main(int argc,char **argv){
 wallpaper=argc>1&&!strcmp(argv[1],"--wallpaper");
 automatic=argc>1&&!strcmp(argv[1],"--auto");
 int alpha=argc>1&&!strcmp(argv[1],"--alpha");
 if(!ecore_evas_init())return 3;if(!edje_init())return 4;
 ee=ecore_evas_software_x11_new(NULL,0,30,30,320,240);if(!ee)return 5;
 if(alpha)ecore_evas_alpha_set(ee,EINA_TRUE);
 Evas *e=ecore_evas_get(ee);
 if(wallpaper){
  Evas_Object *o=edje_object_add(e);
  if(!edje_object_file_set(o,"/usr/share/enlightenment/data/backgrounds/Molten-Steel-Wallpaper-Still-20261026.edj","e/desktop/background")){
   fprintf(stderr,"EDJE_LOAD_FAIL %s\n",edje_load_error_str(edje_object_load_error_get(o)));return 6;
  }
  evas_object_resize(o,320,240);evas_object_show(o);
 }else{
  int colors[4][3]={{255,0,0},{0,255,0},{0,0,255},{255,255,255}};
  for(int i=0;i<4;i++){Evas_Object *o=evas_object_rectangle_add(e);evas_object_move(o,(i%2)*160,(i/2)*120);evas_object_resize(o,160,120);evas_object_color_set(o,colors[i][0],colors[i][1],colors[i][2],255);evas_object_show(o);}
 }
 ecore_evas_title_set(ee,"SPE Evas primitive isolation probe");ecore_evas_show(ee);
 ecore_timer_add(wallpaper?6.0:3.0,check,NULL);ecore_main_loop_begin();
 ecore_evas_free(ee);edje_shutdown();ecore_evas_shutdown();return result;
}
