#include <ft2build.h>
#include FT_FREETYPE_H
#include <fontconfig/fontconfig.h>
#include <stdio.h>
#include <stdint.h>
int main(int argc, char **argv) {
    FT_Library lib; FT_Face face; uint64_t h = 1469598103934665603ULL; long ink = 0;
    if (FT_Init_FreeType(&lib) || FT_New_Face(lib, argv[1], 0, &face)) return 2;
    const unsigned cps[] = { 'T', 'a', 'b', 'o', 'r', ' ', 'S', 'P', 'E', 0xC4, 0x3A9, 0x416, '@', '8' };
    for (int px = 9; px <= 41; px += 8) {
        FT_Set_Pixel_Sizes(face, 0, px);
        for (unsigned i = 0; i < sizeof cps / sizeof *cps; i++) {
            if (FT_Load_Char(face, cps[i], FT_LOAD_RENDER | FT_LOAD_TARGET_NORMAL)) return 3;
            FT_Bitmap *b = &face->glyph->bitmap;
            for (unsigned y = 0; y < b->rows; y++) for (unsigned x = 0; x < b->width; x++) {
                unsigned char v = b->buffer[y * b->pitch + x]; ink += v; h = (h ^ v) * 1099511628211ULL; }
            h = (h ^ (uint64_t)face->glyph->advance.x) * 1099511628211ULL;
        }
    }
    FcInit(); FcPattern *p = FcNameParse((const FcChar8 *)"DejaVu Sans:bold"); FcConfigSubstitute(NULL, p, FcMatchPattern); FcDefaultSubstitute(p);
    FcResult r; FcPattern *m = FcFontMatch(NULL, p, &r); FcChar8 *fam = NULL, *sty = NULL; FcPatternGetString(m, FC_FAMILY, 0, &fam); FcPatternGetString(m, FC_STYLE, 0, &sty);
    printf("glyphs hash=%016llx ink=%ld advance24=%ld fc-match=%s/%s\n", (unsigned long long)h, ink, (long)face->glyph->advance.x, fam, sty);
    return 0;
}
