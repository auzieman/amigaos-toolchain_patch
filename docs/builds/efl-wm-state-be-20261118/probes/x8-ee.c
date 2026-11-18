/* #8: the smallest Evas client. An ecore_evas software_x11 window (300x200) with a red background
 * rectangle and a blue rectangle over the top-left quarter. After 2 s it reads its own X window
 * back from the server (XGetImage) and prints the pixels in each quarter, so the result is what the
 * X server holds, not what Evas thinks it drew. ECORE_EVAS_ENGINE picks another engine name. */
#include <Ecore.h>
#include <Ecore_Evas.h>
#include <Ecore_X.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <stdio.h>
#include <stdlib.h>

static Ecore_Evas *ee;
static int bad;

static Eina_Bool check(void *data)
{
   (void)data;
   Display *d = XOpenDisplay(NULL);
   Window w = (Window)ecore_evas_window_get(ee);
   XImage *im = XGetImage(d, w, 0, 0, 300, 200, AllPlanes, ZPixmap);
   int xs[4] = { 75, 225, 75, 225 }, ys[4] = { 50, 50, 150, 150 };
   const char *n[4] = { "top-left (blue)", "top-right (red)", "bottom-left (red)", "bottom-right (red)" };
   unsigned long want[4] = { 0x0000ff, 0xff0000, 0xff0000, 0xff0000 };
   printf("engine %s window 0x%lx depth %d\n", ecore_evas_engine_name_get(ee), w, im ? im->depth : -1);
   for (int i = 0; im && i < 4; i++) {
      unsigned long p = XGetPixel(im, xs[i], ys[i]) & 0xffffff;
      bad += p != want[i];
      printf("  %-20s pixel=%06lx want=%06lx %s\n", n[i], p, want[i], p == want[i] ? "ok" : "MISMATCH");
   }
   printf("RESULT %s\n", bad ? "FAIL" : "PASS");
   ecore_main_loop_quit();
   return EINA_FALSE;
}

int main(void)
{
   if (!ecore_evas_init()) return 2;
   const char *eng = getenv("ECORE_EVAS_ENGINE");
   ee = ecore_evas_new(eng ? eng : "software_x11", 0, 0, 300, 200, NULL);
   if (!ee) { printf("ecore_evas_new failed\n"); return 2; }
   Evas *e = ecore_evas_get(ee);
   Evas_Object *bg = evas_object_rectangle_add(e);
   evas_object_color_set(bg, 255, 0, 0, 255); evas_object_resize(bg, 300, 200); evas_object_show(bg);
   Evas_Object *r = evas_object_rectangle_add(e);
   evas_object_color_set(r, 0, 0, 255, 255); evas_object_resize(r, 150, 100); evas_object_show(r);
   ecore_evas_show(ee);
   ecore_timer_add(2.0, check, NULL);
   ecore_main_loop_begin();
   ecore_evas_free(ee); ecore_evas_shutdown();
   return bad ? 1 : 0;
}
