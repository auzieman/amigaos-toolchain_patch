/* fbfmt: framebuffer byte-order check for #35 (amdgpu ADDFB2 on big-endian), no GL.
 *
 * Fills a dumb buffer with four quadrants (red top-left, green top-right, white
 * bottom-right, blue bottom-left) and shows it for <secs> seconds per case:
 *   1. legacy ADDFB 32/24, pixels as host-order 0x00RRGGBB words
 *   2. ADDFB2 BGRX8888,     pixels as host-order 0x00RRGGBB words
 *   3. ADDFB2 XRGB8888,     pixels as little-endian bytes B,G,R,X
 * Every case must look the same on the monitor. Prints the result of each ioctl
 * and the format the kernel recorded (GETFB2). Exit 0 = all ioctls succeeded. */
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <drm_fourcc.h>
#include <xf86drm.h>
#include <xf86drmMode.h>

static int fd;

static void fill(uint8_t *m, uint32_t pitch, int w, int h, int le_bytes)
{
   static const uint32_t c[4] = { 0xff0000, 0x00ff00, 0xffffff, 0x0000ff }; /* TL TR BR BL */
   for (int y = 0; y < h; y++)
      for (int x = 0; x < w; x++) {
         int top = y < h / 2, left = x < w / 2;
         uint32_t v = c[top ? (left ? 0 : 1) : (left ? 3 : 2)];
         uint8_t *p = m + (size_t)y * pitch + 4 * x;
         if (le_bytes) { p[0] = v; p[1] = v >> 8; p[2] = v >> 16; p[3] = 0; }
         else *(uint32_t *)p = v;
      }
}

static void show(const char *name, int rc, uint32_t fb, uint32_t crtc, uint32_t conn, drmModeModeInfo *mode, int secs)
{
   if (rc) { printf("%-34s ioctl FAILED: %s\n", name, strerror(errno)); return; }
   drmModeFB2 *f = drmModeGetFB2(fd, fb);
   uint32_t fmt = f ? f->pixel_format : 0;
   printf("%-34s ok, kernel format %.4s (0x%08x)\n", name, (char *)&(uint32_t){ __builtin_bswap32(fmt) }, fmt);
   if (f) drmModeFreeFB2(f);
   if (drmModeSetCrtc(fd, crtc, fb, 0, 0, &conn, 1, mode)) printf("  SETCRTC FAILED: %s\n", strerror(errno));
   else sleep(secs);
}

int main(int argc, char **argv)
{
   setvbuf(stdout, NULL, _IOLBF, 0);
   int secs = argc > 1 ? atoi(argv[1]) : 8, bad = 0;
   fd = open("/dev/dri/card0", O_RDWR | O_CLOEXEC);
   if (fd < 0) { perror("open card0"); return 2; }
   drmModeRes *res = drmModeGetResources(fd);
   drmModeConnector *conn = NULL;
   for (int i = 0; res && i < res->count_connectors; i++) {
      conn = drmModeGetConnector(fd, res->connectors[i]);
      if (conn && conn->connection == DRM_MODE_CONNECTED && conn->count_modes) break;
      drmModeFreeConnector(conn); conn = NULL;
   }
   if (!conn) { fprintf(stderr, "no connected connector\n"); return 2; }
   drmModeModeInfo mode = conn->modes[0];
   for (int i = 0; i < conn->count_modes; i++)
      if (conn->modes[i].type & DRM_MODE_TYPE_PREFERRED) { mode = conn->modes[i]; break; }
   uint32_t crtc = 0;
   drmModeEncoder *enc = conn->encoder_id ? drmModeGetEncoder(fd, conn->encoder_id) : NULL;
   if (enc && enc->crtc_id) crtc = enc->crtc_id;
   for (int e = 0; !crtc && e < conn->count_encoders; e++) {
      drmModeEncoder *en = drmModeGetEncoder(fd, conn->encoders[e]);
      for (int c = 0; en && c < res->count_crtcs; c++)
         if (en->possible_crtcs & (1u << c)) { crtc = res->crtcs[c]; break; }
      drmModeFreeEncoder(en);
   }
   if (!crtc) { fprintf(stderr, "no crtc\n"); return 2; }
   drmModeCrtc *saved = drmModeGetCrtc(fd, crtc);
   int W = mode.hdisplay, H = mode.vdisplay;
   printf("connector %u crtc %u mode %dx%d@%d\n", conn->connector_id, crtc, W, H, mode.vrefresh);

   struct drm_mode_create_dumb cd = { .width = W, .height = H, .bpp = 32 };
   if (drmIoctl(fd, DRM_IOCTL_MODE_CREATE_DUMB, &cd)) { perror("CREATE_DUMB"); return 2; }
   struct drm_mode_map_dumb md = { .handle = cd.handle };
   if (drmIoctl(fd, DRM_IOCTL_MODE_MAP_DUMB, &md)) { perror("MAP_DUMB"); return 2; }
   uint8_t *m = mmap(NULL, cd.size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, md.offset);
   if (m == MAP_FAILED) { perror("mmap"); return 2; }

   uint32_t h[4] = { cd.handle }, p[4] = { cd.pitch }, o[4] = { 0 }, fb;
   int rc;

   fill(m, cd.pitch, W, H, 0);
   rc = drmModeAddFB(fd, W, H, 24, 32, cd.pitch, cd.handle, &fb); bad += !!rc;
   show("1 legacy ADDFB 32/24 host words", rc, fb, crtc, conn->connector_id, &mode, secs);
   if (!rc) drmModeRmFB(fd, fb);

   rc = drmModeAddFB2(fd, W, H, DRM_FORMAT_BGRX8888, h, p, o, &fb, 0); bad += !!rc;
   show("2 ADDFB2 BGRX8888 host words", rc, fb, crtc, conn->connector_id, &mode, secs);
   if (!rc) drmModeRmFB(fd, fb);

   fill(m, cd.pitch, W, H, 1);
   rc = drmModeAddFB2(fd, W, H, DRM_FORMAT_XRGB8888, h, p, o, &fb, 0); bad += !!rc;
   show("3 ADDFB2 XRGB8888 LE bytes", rc, fb, crtc, conn->connector_id, &mode, secs);
   if (!rc) drmModeRmFB(fd, fb);

   if (saved) drmModeSetCrtc(fd, saved->crtc_id, saved->buffer_id, saved->x, saved->y,
                             &conn->connector_id, 1, &saved->mode);
   printf("%s: %d ioctl failure(s); compare the three screens by eye\n", bad ? "FAIL" : "DONE", bad);
   return bad ? 1 : 0;
}
