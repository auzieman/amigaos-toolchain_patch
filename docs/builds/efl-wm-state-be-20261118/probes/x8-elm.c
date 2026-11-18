/* #8: what an Elementary window's Evas scene holds on this host. A standard window (theme
 * background) with a label and a button, 300x200. After 2 s: every Evas object, smart members
 * included, with type, geometry, visibility, colour and clipper; then the window read back from
 * the X server (black share and the centre pixel). Compare with the same program on another host. */
#include <Elementary.h>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <stdio.h>

static Evas_Object *win;
static int npre, npost;
static void cb_pre(void *d, Evas *e, void *ev) { (void)d; (void)e; (void)ev; npre++; }
static void cb_post(void *d, Evas *e, void *ev) { (void)d; (void)e; (void)ev; npost++; }

static double readback(Window *wout)
{
   Display *d = XOpenDisplay(NULL);
   Window w = (Window)elm_win_xwindow_get(win); *wout = w;
   XImage *im = XGetImage(d, w, 0, 0, 300, 200, AllPlanes, ZPixmap);
   long black = 0;
   for (int y = 0; im && y < 200; y++) for (int x = 0; x < 300; x++) black += !(XGetPixel(im, x, y) & 0xffffff);
   XCloseDisplay(d);
   return 100.0 * black / 60000;
}

static void dump(Evas_Object *o, int depth)
{
   Evas_Coord x, y, w, h; int r, g, b, a;
   evas_object_geometry_get(o, &x, &y, &w, &h);
   evas_object_color_get(o, &r, &g, &b, &a);
   Evas_Object *clip = evas_object_clip_get(o);
   Evas_Coord cx = 0, cy = 0, cw = -1, ch = -1; int ca = -1;
   if (clip) { evas_object_geometry_get(clip, &cx, &cy, &cw, &ch); evas_object_color_get(clip, NULL, NULL, NULL, &ca); }
   printf("%*s%s%s%s %d,%d %dx%d vis=%d rgba=%d,%d,%d,%d clip=%dx%d+%d+%d a%d\n", depth * 2, "",
          evas_object_type_get(o), evas_object_name_get(o) ? " " : "", evas_object_name_get(o) ? evas_object_name_get(o) : "",
          x, y, w, h, evas_object_visible_get(o), r, g, b, a, cw, ch, cx, cy, ca);
   if (evas_object_smart_smart_get(o)) {
      Eina_List *l = evas_object_smart_members_get(o), *it; Evas_Object *m;
      EINA_LIST_FOREACH(l, it, m) if (depth < 12) dump(m, depth + 1);
      eina_list_free(l);
   }
}

static Eina_Bool check(void *data)
{
   (void)data;
   Evas *e = evas_object_evas_get(win);
   Ecore_Evas *ee = ecore_evas_ecore_evas_get(e);
   Window w0; double b0 = readback(&w0);
   printf("== render: pre %d post %d manual_render %d visible %d withdrawn %d iconified %d black %.1f%%\n", npre, npost,
          ecore_evas_manual_render_get(ee), ecore_evas_visibility_get(ee), ecore_evas_withdrawn_get(ee),
          ecore_evas_iconified_get(ee), b0);
   ecore_evas_manual_render(ee);
   Window w1; double b1 = readback(&w1);
   printf("== after ecore_evas_manual_render: pre %d post %d black %.1f%%\n", npre, npost, b1);
   printf("== scene (top-level objects, top first)\n");
   for (Evas_Object *o = evas_object_top_get(e); o; o = evas_object_below_get(o)) dump(o, 0);
   Display *d = XOpenDisplay(NULL);
   Window w = (Window)elm_win_xwindow_get(win);
   XImage *im = XGetImage(d, w, 0, 0, 300, 200, AllPlanes, ZPixmap);
   long black = 0;
   for (int y = 0; im && y < 200; y++) for (int x = 0; x < 300; x++) black += !(XGetPixel(im, x, y) & 0xffffff);
   printf("== X readback: window 0x%lx black %.1f%% centre %06lx scale %.3f engine %s\n", w, 100.0 * black / 60000,
          im ? XGetPixel(im, 150, 100) & 0xffffff : 0, elm_config_scale_get(), elm_config_accel_preference_get() ?: "-");
   elm_exit();
   return EINA_FALSE;
}

EAPI_MAIN int elm_main(int argc, char **argv)
{
   (void)argc; (void)argv;
   win = elm_win_util_standard_add("x8", "x8");
   Evas_Object *box = elm_box_add(win);
   evas_object_size_hint_weight_set(box, EVAS_HINT_EXPAND, EVAS_HINT_EXPAND);
   elm_win_resize_object_add(win, box); evas_object_show(box);
   Evas_Object *lb = elm_label_add(win); elm_object_text_set(lb, "Hello A1222"); elm_box_pack_end(box, lb); evas_object_show(lb);
   Evas_Object *bt = elm_button_add(win); elm_object_text_set(bt, "Button"); elm_box_pack_end(box, bt); evas_object_show(bt);
   evas_object_resize(win, 300, 200); evas_object_show(win);
   evas_event_callback_add(evas_object_evas_get(win), EVAS_CALLBACK_RENDER_PRE, cb_pre, NULL);
   evas_event_callback_add(evas_object_evas_get(win), EVAS_CALLBACK_RENDER_POST, cb_post, NULL);
   ecore_timer_add(2.0, check, NULL);
   elm_run();
   return 0;
}
ELM_MAIN()
