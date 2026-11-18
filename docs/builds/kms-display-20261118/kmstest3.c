/* KMS + GBM + EGL/GLES2 display check for the A1222 bring-up.
 * Takes the first connected connector at its preferred mode, renders with radeonsi into a
 * GBM scanout surface (XRGB8888) and shows it with KMS, then restores the previous CRTC.
 *
 * Stage "bars" (always): four quadrants, top-left RED, top-right GREEN, bottom-left BLUE,
 * bottom-right WHITE, drawn with scissored clears only (no shaders). It prints the GL
 * readback and the scanout BO's raw memory bytes for one pixel of each quadrant, then holds
 * the frame for <bars_seconds> so the screen can be compared by eye.
 * Stage "cube": a rotating cube (six face colours, depth test) page-flipped for <frames>
 * frames, reporting frames/seconds/FPS and the flip count.
 *
 * Usage: kmstest [bars_seconds=10] [frames=600]   (frames=0 skips the cube)
 * kmstest3 (#35 display path) adds, through the environment:
 *   KMS_FORMAT=XR24|BX24|XB24|AR24|BA24  surface format, from the EGL configs with that visual
 *   KMS_MODE=WxH@R                       mode to set instead of the preferred one
 *   KMS_NORESTORE=1                      exit without restoring the previous CRTC
 * and prints the result of DRM_CLIENT_CAP_UNIVERSAL_PLANES and DRM_CLIENT_CAP_ATOMIC.
 * Exit: 0 done, 1 GL readback mismatch, 2 setup failure. */
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES2/gl2.h>
#include <errno.h>
#include <fcntl.h>
#include <gbm.h>
#include <math.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

static int fail(const char *what) { fprintf(stderr, "SETUP FAIL: %s (errno %d egl 0x%x)\n", what, errno, eglGetError()); return 2; }
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec * 1e-9; }

static int drm_fd;
static uint32_t fb_format;   /* 0: register the FB in the BO's own format */
static uint32_t crtc_id, conn_id;
static drmModeModeInfo mode;

struct fbinfo { uint32_t fb_id; };
static void fb_destroy(struct gbm_bo *bo, void *data)
{
   struct fbinfo *f = data;
   if (f->fb_id) drmModeRmFB(drm_fd, f->fb_id);
   free(f);
}
static uint32_t bo_fb(struct gbm_bo *bo)
{
   struct fbinfo *f = gbm_bo_get_user_data(bo);
   if (f) return f->fb_id;
   f = calloc(1, sizeof *f);
   uint32_t handles[4] = { gbm_bo_get_handle(bo).u32 }, pitches[4] = { gbm_bo_get_stride(bo) }, offs[4] = { 0 };
   if (drmModeAddFB2(drm_fd, gbm_bo_get_width(bo), gbm_bo_get_height(bo), fb_format ? fb_format : gbm_bo_get_format(bo),
                     handles, pitches, offs, &f->fb_id, 0)) {
      /* A big-endian kernel refuses ADDFB2 unless the driver sets
       * quirk_addfb_prefer_host_byte_order (drm_framebuffer.c, drm_mode_addfb2_ioctl);
       * legacy ADDFB 32/24 is the host-order XRGB8888 framebuffer. */
      int e = errno;
      static int said;
      /* Legacy ADDFB is host order on such a kernel, so it only fits a host-order
       * (BGRX8888 on big-endian) BO; a little-endian XRGB8888 BO would scan out
       * with its bytes swapped. */
      if (e == EOPNOTSUPP && gbm_bo_get_format(bo) != GBM_FORMAT_BGRX8888) {
         fprintf(stderr, "ADDFB2 refused and the BO is not host-order BGRX8888: legacy ADDFB would "
                 "show swapped colours (kernel without quirk_addfb_prefer_host_byte_order, #35)\n");
         free(f); return 0;
      }
      if (e != EOPNOTSUPP || drmModeAddFB(drm_fd, gbm_bo_get_width(bo), gbm_bo_get_height(bo), 24, 32,
                                          gbm_bo_get_stride(bo), handles[0], &f->fb_id)) {
         fprintf(stderr, "drmModeAddFB2 failed: %s; legacy AddFB: %s\n", strerror(e), strerror(errno));
         free(f); return 0;
      }
      if (!said++) printf("ADDFB2 refused (%s), using legacy ADDFB 32bpp/depth24\n", strerror(e));
   }
   gbm_bo_set_user_data(bo, f, fb_destroy);
   return f->fb_id;
}

static int flip_pending;
static void flip_handler(int fd, unsigned seq, unsigned s, unsigned us, void *data) { flip_pending = 0; }

static GLuint shader(GLenum type, const char *src)
{
   GLuint s = glCreateShader(type);
   glShaderSource(s, 1, &src, NULL); glCompileShader(s);
   GLint ok = 0; glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
   if (!ok) { char log[1024]; glGetShaderInfoLog(s, sizeof log, NULL, log); fprintf(stderr, "shader: %s\n", log); return 0; }
   return s;
}

static void mat_mul(float *r, const float *a, const float *b)
{
   float t[16];
   for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) {
      t[j * 4 + i] = 0;
      for (int k = 0; k < 4; k++) t[j * 4 + i] += a[k * 4 + i] * b[j * 4 + k];
   }
   memcpy(r, t, sizeof t);
}

int main(int argc, char **argv)
{
   setvbuf(stdout, NULL, _IOLBF, 0);
   int bars_s = argc > 1 ? atoi(argv[1]) : 10, frames = argc > 2 ? atoi(argv[2]) : 600;

   drm_fd = open("/dev/dri/card0", O_RDWR | O_CLOEXEC);
   if (drm_fd < 0) return fail("open card0");
   drmModeRes *res = drmModeGetResources(drm_fd);
   if (!res) return fail("drmModeGetResources");
   drmModeConnector *conn = NULL;
   for (int i = 0; i < res->count_connectors; i++) {
      conn = drmModeGetConnector(drm_fd, res->connectors[i]);
      if (conn && conn->connection == DRM_MODE_CONNECTED && conn->count_modes) break;
      drmModeFreeConnector(conn); conn = NULL;
   }
   if (!conn) return fail("no connected connector");
   printf("client cap universal planes: %s, atomic: %s\n",
          drmSetClientCap(drm_fd, DRM_CLIENT_CAP_UNIVERSAL_PLANES, 1) ? strerror(errno) : "ok",
          drmSetClientCap(drm_fd, DRM_CLIENT_CAP_ATOMIC, 1) ? strerror(errno) : "ok");
   conn_id = conn->connector_id;
   mode = conn->modes[0];
   for (int i = 0; i < conn->count_modes; i++)
      if (conn->modes[i].type & DRM_MODE_TYPE_PREFERRED) { mode = conn->modes[i]; break; }
   const char *want_mode = getenv("KMS_MODE");
   if (want_mode) {
      int w = 0, h = 0, r = 0, found = 0;
      sscanf(want_mode, "%dx%d@%d", &w, &h, &r);
      for (int i = 0; i < conn->count_modes && !found; i++)
         if (conn->modes[i].hdisplay == w && conn->modes[i].vdisplay == h && conn->modes[i].vrefresh == r) {
            mode = conn->modes[i]; found = 1;
         }
      if (!found) return fail("KMS_MODE not in the connector's mode list");
   }
   drmModeEncoder *enc = conn->encoder_id ? drmModeGetEncoder(drm_fd, conn->encoder_id) : NULL;
   if (enc && enc->crtc_id) crtc_id = enc->crtc_id;
   else {
      for (int e = 0; e < conn->count_encoders && !crtc_id; e++) {
         drmModeEncoder *en = drmModeGetEncoder(drm_fd, conn->encoders[e]);
         for (int c = 0; en && c < res->count_crtcs; c++)
            if (en->possible_crtcs & (1u << c)) { crtc_id = res->crtcs[c]; break; }
         drmModeFreeEncoder(en);
      }
   }
   if (!crtc_id) return fail("no crtc");
   drmModeCrtc *saved = drmModeGetCrtc(drm_fd, crtc_id);
   printf("connector %u crtc %u mode %s %dx%d@%d\n", conn_id, crtc_id, mode.name, mode.hdisplay, mode.vdisplay, mode.vrefresh);
   const int W = mode.hdisplay, H = mode.vdisplay;

   struct gbm_device *gbm = gbm_create_device(drm_fd);
   if (!gbm) return fail("gbm_create_device");
   printf("gbm backend %s\n", gbm_device_get_backend_name(gbm));

   PFNEGLGETPLATFORMDISPLAYEXTPROC gpd = (void *)eglGetProcAddress("eglGetPlatformDisplayEXT");
   EGLDisplay dpy = gpd(EGL_PLATFORM_GBM_KHR, gbm, NULL);
   EGLint maj, min;
   if (!eglInitialize(dpy, &maj, &min)) return fail("eglInitialize");
   eglBindAPI(EGL_OPENGL_ES_API);
   static const EGLint cattr[] = { EGL_SURFACE_TYPE, EGL_WINDOW_BIT, EGL_RED_SIZE, 8, EGL_GREEN_SIZE, 8, EGL_BLUE_SIZE, 8,
                                   EGL_ALPHA_SIZE, 0, EGL_DEPTH_SIZE, 16, EGL_RENDERABLE_TYPE, EGL_OPENGL_ES2_BIT, EGL_NONE };
   static EGLConfig cfgs[2048]; EGLConfig cfg = NULL; EGLint n = 0, all = 0, lastvid = 0;
   eglGetConfigs(dpy, NULL, 0, &all);
   printf("EGL configs reported: %d\n", all);
   eglGetConfigs(dpy, cfgs, 2048, &all);
   printf("EGL configs: %d total\n", all);
   for (int i = 0; i < all; i++) {
      EGLint vid, r, g, b, a, d, st, rt;
      eglGetConfigAttrib(dpy, cfgs[i], EGL_NATIVE_VISUAL_ID, &vid);
      eglGetConfigAttrib(dpy, cfgs[i], EGL_RED_SIZE, &r); eglGetConfigAttrib(dpy, cfgs[i], EGL_GREEN_SIZE, &g);
      eglGetConfigAttrib(dpy, cfgs[i], EGL_BLUE_SIZE, &b); eglGetConfigAttrib(dpy, cfgs[i], EGL_ALPHA_SIZE, &a);
      eglGetConfigAttrib(dpy, cfgs[i], EGL_DEPTH_SIZE, &d); eglGetConfigAttrib(dpy, cfgs[i], EGL_SURFACE_TYPE, &st);
      eglGetConfigAttrib(dpy, cfgs[i], EGL_RENDERABLE_TYPE, &rt);
      if (i == 0 || vid != lastvid) printf("  cfg %2d visual %.4s (0x%08x) rgba %d%d%d%d depth %d surface 0x%x renderable 0x%x\n",
                         i, (char *)&vid, vid, r, g, b, a, d, st, rt);
      lastvid = vid;
   }
   eglChooseConfig(dpy, cattr, cfgs, 2048, &n);
   printf("EGL configs matching rgb888/depth16/window/es2: %d\n", n);
   for (int i = 0; i < n; i++) {
      EGLint vid; eglGetConfigAttrib(dpy, cfgs[i], EGL_NATIVE_VISUAL_ID, &vid);
      EGLint r, a, d; eglGetConfigAttrib(dpy, cfgs[i], EGL_RED_SIZE, &r);
      eglGetConfigAttrib(dpy, cfgs[i], EGL_ALPHA_SIZE, &a); eglGetConfigAttrib(dpy, cfgs[i], EGL_DEPTH_SIZE, &d);
      if (i < 24) printf("  match %2d visual %c%c%c%c (0x%08x) r%d a%d depth %d\n", i,
                         vid & 0xff, (vid >> 8) & 0xff, (vid >> 16) & 0xff, (vid >> 24) & 0xff, vid, r, a, d);
      if (!cfg && vid == GBM_FORMAT_XRGB8888) cfg = cfgs[i];
   }
   uint32_t sfmt = GBM_FORMAT_XRGB8888;
   const char *want_fmt = getenv("KMS_FORMAT");
   if (want_fmt && strlen(want_fmt) == 4) {
      sfmt = (uint32_t)want_fmt[0] | (uint32_t)want_fmt[1] << 8 | (uint32_t)want_fmt[2] << 16 | (uint32_t)want_fmt[3] << 24;
      cfg = NULL;
      eglGetConfigs(dpy, cfgs, 2048, &all);   /* eglChooseConfig above reused cfgs */
      for (int i = 0; i < all && !cfg; i++) {   /* a window config with that visual and a depth buffer */
         EGLint vid, st, d; eglGetConfigAttrib(dpy, cfgs[i], EGL_NATIVE_VISUAL_ID, &vid);
         eglGetConfigAttrib(dpy, cfgs[i], EGL_SURFACE_TYPE, &st); eglGetConfigAttrib(dpy, cfgs[i], EGL_DEPTH_SIZE, &d);
         if ((uint32_t)vid == sfmt && (st & EGL_WINDOW_BIT) && d >= 16) cfg = cfgs[i];
      }
      if (!cfg) return fail("no EGL window config with the KMS_FORMAT visual");
   }
   for (int i = 0; !cfg && i < n; i++) {   /* fall back to the 8-bit format EGL does offer */
      EGLint vid; eglGetConfigAttrib(dpy, cfgs[i], EGL_NATIVE_VISUAL_ID, &vid);
      if (vid == GBM_FORMAT_XBGR8888) { cfg = cfgs[i]; sfmt = GBM_FORMAT_XBGR8888; }
   }
   for (int i = 0; !cfg && i < n; i++) {
      /* Big-endian Mesa reports its host-order XRGB config as BGRX8888 (memory X,R,G,B).
       * The FB is registered as BGRX8888 through ADDFB2, which works once the kernel sets
       * quirk_addfb_prefer_host_byte_order (#35). Older BE kernels refuse ADDFB2, and
       * bo_fb() falls back to legacy ADDFB 32/24, their host-order XRGB8888. */
      EGLint vid; eglGetConfigAttrib(dpy, cfgs[i], EGL_NATIVE_VISUAL_ID, &vid);
      if (vid == GBM_FORMAT_BGRX8888) { cfg = cfgs[i]; sfmt = GBM_FORMAT_BGRX8888; }
   }
   if (!cfg) return fail("no XRGB8888, XBGR8888 or BGRX8888 EGL config");
   printf("surface format %c%c%c%c%s\n", sfmt & 0xff, (sfmt >> 8) & 0xff, (sfmt >> 16) & 0xff, sfmt >> 24,
          sfmt == GBM_FORMAT_XRGB8888 || want_fmt ? "" : " (XRGB8888 not offered by EGL)");
   struct gbm_surface *gs = gbm_surface_create(gbm, W, H, sfmt, GBM_BO_USE_SCANOUT | GBM_BO_USE_RENDERING);
   if (!gs) return fail("gbm_surface_create");
   static const EGLint xattr[] = { EGL_CONTEXT_CLIENT_VERSION, 2, EGL_NONE };
   EGLContext ctx = eglCreateContext(dpy, cfg, EGL_NO_CONTEXT, xattr);
   EGLSurface surf = eglCreateWindowSurface(dpy, cfg, (EGLNativeWindowType)gs, NULL);
   if (ctx == EGL_NO_CONTEXT || surf == EGL_NO_SURFACE) return fail("context/surface");
   if (!eglMakeCurrent(dpy, surf, surf, ctx)) return fail("eglMakeCurrent");
   printf("EGL %d.%d GL_RENDERER=%s\n", maj, min, glGetString(GL_RENDERER));

   /* ---- stage bars ---- */
   glViewport(0, 0, W, H);
   glEnable(GL_SCISSOR_TEST);
   static const struct { const char *name; int x, y; float c[3]; unsigned char want[3]; } q[4] = {
      { "top-left RED",       0, 1, { 1, 0, 0 }, { 0xff, 0x00, 0x00 } },
      { "top-right GREEN",    1, 1, { 0, 1, 0 }, { 0x00, 0xff, 0x00 } },
      { "bottom-left BLUE",   0, 0, { 0, 0, 1 }, { 0x00, 0x00, 0xff } },
      { "bottom-right WHITE", 1, 0, { 1, 1, 1 }, { 0xff, 0xff, 0xff } },
   };
   for (int i = 0; i < 4; i++) {
      glScissor(q[i].x * W / 2, q[i].y * H / 2, W / 2, H / 2);
      glClearColor(q[i].c[0], q[i].c[1], q[i].c[2], 1); glClear(GL_COLOR_BUFFER_BIT);
   }
   glDisable(GL_SCISSOR_TEST);
   int bad = 0;
   for (int i = 0; i < 4; i++) {   /* GL origin is bottom-left */
      unsigned char px[4] = { 0x5a, 0x5a, 0x5a, 0x5a };
      glReadPixels(q[i].x * W / 2 + W / 4, q[i].y * H / 2 + H / 4, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, px);
      int ok = px[0] == q[i].want[0] && px[1] == q[i].want[1] && px[2] == q[i].want[2];
      bad += !ok;
      printf("BARS GL readback %-18s rgba=%02x%02x%02x%02x %s\n", q[i].name, px[0], px[1], px[2], px[3], ok ? "ok" : "MISMATCH");
   }
   eglSwapBuffers(dpy, surf);
   struct gbm_bo *bo = gbm_surface_lock_front_buffer(gs);
   uint32_t fb = bo_fb(bo);
   if (!fb) return fail("addfb bars");
   printf("BO stride %u format 0x%08x fb format 0x%08x modifier 0x%llx\n", gbm_bo_get_stride(bo), gbm_bo_get_format(bo),
          fb_format ? fb_format : gbm_bo_get_format(bo),
          (unsigned long long)gbm_bo_get_modifier(bo));
   /* Raw memory bytes of the scanout BO (memory order, byte 0 first). XRGB8888 is
    * little-endian by definition: a red pixel is 00 00 ff xx in memory (XBGR8888: ff 00 00 xx). */
   uint32_t mstride = 0; void *mdata = NULL;
   unsigned char *m = gbm_bo_map(bo, 0, 0, W, H, GBM_BO_TRANSFER_READ, &mstride, &mdata);
   for (int i = 0; m && i < 4; i++) {
      int x = q[i].x * W / 2 + W / 4, y = (1 - q[i].y) * H / 2 + H / 4;   /* BO origin is top-left */
      unsigned char *p = m + (size_t)y * mstride + 4 * x;
      printf("BARS BO bytes     %-18s %02x %02x %02x %02x\n", q[i].name, p[0], p[1], p[2], p[3]);
   }
   if (m) gbm_bo_unmap(bo, mdata); else printf("BARS BO map failed (%s)\n", strerror(errno));
   if (drmModeSetCrtc(drm_fd, crtc_id, fb, 0, 0, &conn_id, 1, &mode)) return fail("drmModeSetCrtc");
   printf("BARS on screen for %d s: expect top-left RED, top-right GREEN, bottom-left BLUE, bottom-right WHITE\n", bars_s);
   sleep(bars_s);

   /* ---- stage cube ---- */
   if (frames > 0) {
      const char *vs = "uniform mat4 mvp; attribute vec3 pos; attribute vec3 col; varying vec3 v;"
                       "void main(){ v = col; gl_Position = mvp * vec4(pos, 1.0); }";
      const char *fs = "precision mediump float; varying vec3 v; void main(){ gl_FragColor = vec4(v, 1.0); }";
      GLuint p = glCreateProgram(), a = shader(GL_VERTEX_SHADER, vs), b = shader(GL_FRAGMENT_SHADER, fs);
      if (!a || !b) return fail("shader compile");
      glAttachShader(p, a); glAttachShader(p, b);
      glBindAttribLocation(p, 0, "pos"); glBindAttribLocation(p, 1, "col");
      glLinkProgram(p); glUseProgram(p);
      GLint umvp = glGetUniformLocation(p, "mvp");
      static const float fc[6][3] = { {1,0,0}, {0,1,0}, {0,0,1}, {1,1,0}, {0,1,1}, {1,0,1} };
      static const signed char cv[6][4][3] = {
         {{-1,-1, 1},{ 1,-1, 1},{ 1, 1, 1},{-1, 1, 1}}, {{ 1,-1,-1},{-1,-1,-1},{-1, 1,-1},{ 1, 1,-1}},
         {{-1,-1,-1},{-1,-1, 1},{-1, 1, 1},{-1, 1,-1}}, {{ 1,-1, 1},{ 1,-1,-1},{ 1, 1,-1},{ 1, 1, 1}},
         {{-1, 1, 1},{ 1, 1, 1},{ 1, 1,-1},{-1, 1,-1}}, {{-1,-1,-1},{ 1,-1,-1},{ 1,-1, 1},{-1,-1, 1}} };
      static float vb[36 * 6]; int k = 0;
      static const int tri[6] = { 0, 1, 2, 0, 2, 3 };
      for (int f = 0; f < 6; f++) for (int t = 0; t < 6; t++) {
         for (int c = 0; c < 3; c++) vb[k++] = cv[f][tri[t]][c];
         for (int c = 0; c < 3; c++) vb[k++] = fc[f][c];
      }
      GLuint vbo; glGenBuffers(1, &vbo); glBindBuffer(GL_ARRAY_BUFFER, vbo);
      glBufferData(GL_ARRAY_BUFFER, sizeof vb, vb, GL_STATIC_DRAW);
      glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, (void *)0);
      glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, (void *)12);
      glEnableVertexAttribArray(0); glEnableVertexAttribArray(1);
      glEnable(GL_DEPTH_TEST);
      float asp = (float)W / H, fz = 1.0f / tanf(0.4f), zn = 1, zf = 20;
      float proj[16] = { fz / asp,0,0,0, 0,fz,0,0, 0,0,(zf+zn)/(zn-zf),-1, 0,0,2*zf*zn/(zn-zf),0 };
      drmEventContext ev = { .version = 2, .page_flip_handler = flip_handler };
      struct gbm_bo *prev = bo;
      int flips = 0, flip_err = 0;
      double t0 = now();
      for (int i = 0; i < frames; i++) {
         float t = i * 0.02f, ca = cosf(t), sa = sinf(t), cb = cosf(t * 0.7f), sb = sinf(t * 0.7f);
         float ry[16] = { ca,0,-sa,0, 0,1,0,0, sa,0,ca,0, 0,0,0,1 };
         float rx[16] = { 1,0,0,0, 0,cb,sb,0, 0,-sb,cb,0, 0,0,-6,1 };
         float mv[16], mvp[16]; mat_mul(mv, rx, ry); mat_mul(mvp, proj, mv);
         glUniformMatrix4fv(umvp, 1, GL_FALSE, mvp);
         glClearColor(0.1f, 0.1f, 0.1f, 1); glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
         glDrawArrays(GL_TRIANGLES, 0, 36);
         eglSwapBuffers(dpy, surf);
         struct gbm_bo *next = gbm_surface_lock_front_buffer(gs);
         uint32_t nfb = bo_fb(next);
         if (!nfb) { flip_err++; break; }
         flip_pending = 1;
         if (drmModePageFlip(drm_fd, crtc_id, nfb, DRM_MODE_PAGE_FLIP_EVENT, NULL)) {
            fprintf(stderr, "page flip failed: %s\n", strerror(errno)); flip_err++; flip_pending = 0;
         }
         while (flip_pending) {
            struct pollfd pf = { drm_fd, POLLIN, 0 };
            if (poll(&pf, 1, 1000) <= 0) { fprintf(stderr, "flip event timeout at frame %d\n", i); flip_err++; break; }
            drmHandleEvent(drm_fd, &ev);
         }
         if (!flip_err) flips++;
         gbm_surface_release_buffer(gs, prev);
         prev = next;
         if (flip_err) break;
      }
      double dt = now() - t0;
      printf("CUBE frames=%d seconds=%.3f fps=%.2f flips=%d flip_errors=%d\n", flips, dt, flips / dt, flips, flip_err);
   }

   if (saved && !getenv("KMS_NORESTORE"))
      drmModeSetCrtc(drm_fd, saved->crtc_id, saved->buffer_id, saved->x, saved->y, &conn_id, 1, &saved->mode);
   else printf("CRTC left as set (KMS_NORESTORE)\n");
   printf("RESULT %s (GL readback %s)\n", bad ? "FAIL" : "DONE", bad ? "mismatch" : "ok");
   return bad ? 1 : 0;
}
