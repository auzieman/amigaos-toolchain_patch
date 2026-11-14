/* Minimal offscreen GLES2 check for the A1222 bring-up.
 * Surfaceless EGL, one 64x64 RGBA8 FBO. Stage 1: glClear to a known colour and
 * read back. Stage 2 ("draw"): a triangle with per-vertex colour from a VBO
 * (exercises vertex fetch), read back at fixed points.
 * Usage: gltest [clear|draw]   (default: clear then draw)
 * Exit: 0 pass, 1 pixel mismatch, 2 setup failure. */
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES2/gl2.h>
#include <GLES2/gl2ext.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define W 64
#define H 64
static int fail(const char *what) { fprintf(stderr, "SETUP FAIL: %s (egl 0x%x gl 0x%x)\n", what, eglGetError(), glGetError()); return 2; }

static int check(const char *stage, const unsigned char *px, int x, int y, const unsigned char want[4], int tol)
{
   const unsigned char *p = px + 4 * (y * W + x);
   int ok = 1;
   for (int c = 0; c < 4; c++)
      if (abs((int)p[c] - want[c]) > tol) ok = 0;
   printf("%s (%2d,%2d) got %02x%02x%02x%02x want %02x%02x%02x%02x %s\n", stage, x, y,
          p[0], p[1], p[2], p[3], want[0], want[1], want[2], want[3], ok ? "ok" : "MISMATCH");
   return ok;
}

static GLuint shader(GLenum type, const char *src)
{
   GLuint s = glCreateShader(type);
   glShaderSource(s, 1, &src, NULL);
   glCompileShader(s);
   GLint ok = 0; glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
   if (!ok) { char log[1024]; glGetShaderInfoLog(s, sizeof log, NULL, log); fprintf(stderr, "shader: %s\n", log); return 0; }
   return s;
}

int main(int argc, char **argv)
{
   setvbuf(stdout, NULL, _IOLBF, 0);
   int do_clear = argc < 2 || !strcmp(argv[1], "clear");
   int do_draw = argc < 2 || !strcmp(argv[1], "draw");

   PFNEGLGETPLATFORMDISPLAYEXTPROC gpd = (void *)eglGetProcAddress("eglGetPlatformDisplayEXT");
   if (!gpd) return fail("eglGetPlatformDisplayEXT");
   EGLDisplay dpy = gpd(EGL_PLATFORM_SURFACELESS_MESA, EGL_DEFAULT_DISPLAY, NULL);
   EGLint maj, min;
   if (!eglInitialize(dpy, &maj, &min)) return fail("eglInitialize");
   if (!eglBindAPI(EGL_OPENGL_ES_API)) return fail("eglBindAPI");
   static const EGLint cfg_attr[] = { EGL_RENDERABLE_TYPE, EGL_OPENGL_ES2_BIT, EGL_SURFACE_TYPE, 0, EGL_NONE };
   EGLConfig cfg; EGLint n = 0;
   if (!eglChooseConfig(dpy, cfg_attr, &cfg, 1, &n) || n < 1) return fail("eglChooseConfig");
   static const EGLint ctx_attr[] = { EGL_CONTEXT_CLIENT_VERSION, 2, EGL_NONE };
   EGLContext ctx = eglCreateContext(dpy, cfg, EGL_NO_CONTEXT, ctx_attr);
   if (ctx == EGL_NO_CONTEXT) return fail("eglCreateContext");
   if (!eglMakeCurrent(dpy, EGL_NO_SURFACE, EGL_NO_SURFACE, ctx)) return fail("eglMakeCurrent");
   printf("EGL %d.%d vendor=%s\n", maj, min, eglQueryString(dpy, EGL_VENDOR));
   printf("GL_RENDERER=%s\nGL_VERSION=%s\n", glGetString(GL_RENDERER), glGetString(GL_VERSION));

   GLuint fbo, rb;
   glGenFramebuffers(1, &fbo); glBindFramebuffer(GL_FRAMEBUFFER, fbo);
   glGenRenderbuffers(1, &rb); glBindRenderbuffer(GL_RENDERBUFFER, rb);
   glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA8_OES, W, H);
   glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, rb);
   if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) return fail("FBO incomplete");
   glViewport(0, 0, W, H);

   static unsigned char px[W * H * 4];
   int pass = 1;
   if (do_clear) {
      glClearColor(1.0f, 0.5f, 0.25f, 1.0f);   /* ff 80 40 ff: every channel distinct */
      glClear(GL_COLOR_BUFFER_BIT);
      memset(px, 0x5a, sizeof px);
      glReadPixels(0, 0, W, H, GL_RGBA, GL_UNSIGNED_BYTE, px);
      printf("CLEAR glGetError=0x%x\n", glGetError());
      static const unsigned char want[4] = { 0xff, 0x80, 0x40, 0xff };
      int bad = 0;
      for (int i = 0; i < W * H; i++)
         for (int c = 0; c < 4; c++)
            if (abs((int)px[4 * i + c] - want[c]) > 1) { bad++; break; }
      check("CLEAR", px, 0, 0, want, 1); check("CLEAR", px, W - 1, H - 1, want, 1);
      printf("CLEAR bad_pixels=%d/%d -> %s\n", bad, W * H, bad ? "FAIL" : "PASS");
      if (bad) pass = 0;
   }
   if (do_draw) {
      const char *vs = "attribute vec2 pos; attribute vec4 col; varying vec4 v;"
                       "void main(){ v = col; gl_Position = vec4(pos, 0.0, 1.0); }";
      const char *fs = "precision mediump float; varying vec4 v; void main(){ gl_FragColor = v; }";
      GLuint p = glCreateProgram(), a = shader(GL_VERTEX_SHADER, vs), b = shader(GL_FRAGMENT_SHADER, fs);
      if (!a || !b) return fail("shader compile");
      glAttachShader(p, a); glAttachShader(p, b);
      glBindAttribLocation(p, 0, "pos"); glBindAttribLocation(p, 1, "col");
      glLinkProgram(p);
      GLint ok = 0; glGetProgramiv(p, GL_LINK_STATUS, &ok); if (!ok) return fail("link");
      glUseProgram(p);
      /* A full-screen pair of triangles, all vertices the same colour, so every
       * pixel has a known value; float positions + float colours from a VBO. */
      static const float v[] = {
         -1, -1, 0.0f, 1.0f, 0.0f, 1.0f,   1, -1, 0.0f, 1.0f, 0.0f, 1.0f,   -1, 1, 0.0f, 1.0f, 0.0f, 1.0f,
          1, -1, 0.0f, 1.0f, 0.0f, 1.0f,   1,  1, 0.0f, 1.0f, 0.0f, 1.0f,   -1, 1, 0.0f, 1.0f, 0.0f, 1.0f,
      };
      GLuint vbo; glGenBuffers(1, &vbo); glBindBuffer(GL_ARRAY_BUFFER, vbo);
      glBufferData(GL_ARRAY_BUFFER, sizeof v, v, GL_STATIC_DRAW);
      glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void *)0);
      glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void *)(2 * sizeof(float)));
      glEnableVertexAttribArray(0); glEnableVertexAttribArray(1);
      glClearColor(0, 0, 0, 0); glClear(GL_COLOR_BUFFER_BIT);
      glDrawArrays(GL_TRIANGLES, 0, 6);
      memset(px, 0x5a, sizeof px);
      glReadPixels(0, 0, W, H, GL_RGBA, GL_UNSIGNED_BYTE, px);
      printf("DRAW glGetError=0x%x\n", glGetError());
      static const unsigned char green[4] = { 0x00, 0xff, 0x00, 0xff };
      int bad = 0;
      for (int i = 0; i < W * H; i++)
         for (int c = 0; c < 4; c++)
            if (abs((int)px[4 * i + c] - green[c]) > 1) { bad++; break; }
      check("DRAW", px, W / 2, H / 2, green, 1); check("DRAW", px, 1, 1, green, 1);
      printf("DRAW bad_pixels=%d/%d -> %s\n", bad, W * H, bad ? "FAIL" : "PASS");
      if (bad) pass = 0;
   }
   eglMakeCurrent(dpy, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);
   eglTerminate(dpy);
   printf("RESULT=%s\n", pass ? "PASS" : "FAIL");
   return pass ? 0 : 1;
}
