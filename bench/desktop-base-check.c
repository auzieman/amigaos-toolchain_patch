/* Source-built software desktop prerequisite check; no GPU/full-ABI claim. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <zlib.h>
#include <png.h>
#include <pixman.h>
int main(void) {
  const unsigned char original[]="Tabor SPE desktop prerequisite round trip";
  unsigned char compressed[256], restored[256];
  uLongf n=sizeof(compressed), m=sizeof(restored);
  if (compress2(compressed,&n,original,sizeof(original),9)!=Z_OK ||
      uncompress(restored,&m,compressed,n)!=Z_OK || m!=sizeof(original) ||
      memcmp(original,restored,m)) return 1;
  puts("DESKTOP_BASE_TEST zlib_roundtrip PASS");
  unsigned char pixels[16]={255,0,0,255, 0,255,0,255, 0,0,255,255, 255,255,255,128};
  unsigned char encoded[4096], decoded[16];
  png_image w; memset(&w,0,sizeof(w)); w.version=PNG_IMAGE_VERSION;
  w.width=2; w.height=2; w.format=PNG_FORMAT_RGBA;
  png_alloc_size_t bytes=sizeof(encoded);
  if (!png_image_write_to_memory(&w,encoded,&bytes,0,pixels,0,NULL)) return 2;
  png_image r; memset(&r,0,sizeof(r)); r.version=PNG_IMAGE_VERSION;
  if (!png_image_begin_read_from_memory(&r,encoded,bytes)) return 3;
  r.format=PNG_FORMAT_RGBA;
  if (r.width!=2 || r.height!=2 || !png_image_finish_read(&r,NULL,decoded,0,NULL) ||
      memcmp(pixels,decoded,sizeof(pixels))) return 4;
  png_image_free(&r); png_image_free(&w);
  puts("DESKTOP_BASE_TEST png_rgba_roundtrip PASS");
  uint32_t src[4]={0xffff0000,0xff00ff00,0xff0000ff,0xffffffff},dst[4]={0};
  pixman_image_t *s=pixman_image_create_bits(PIXMAN_a8r8g8b8,2,2,src,8);
  pixman_image_t *d=pixman_image_create_bits(PIXMAN_a8r8g8b8,2,2,dst,8);
  if (!s || !d) return 5;
  pixman_image_composite32(PIXMAN_OP_SRC,s,NULL,d,0,0,0,0,0,0,2,2);
  if (memcmp(src,dst,sizeof(src))) return 6;
  pixman_image_unref(s); pixman_image_unref(d);
  puts("DESKTOP_BASE_TEST pixman_argb_copy PASS");
  puts("DESKTOP_BASE_DONE no X11/E/GPU or full floating ABI acceptance");
  return 0;
}
