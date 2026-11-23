/* glibc on e500v2: libm results against an IEEE host, bit for bit, for every libm function that
 * Mesa's constant folding calls (nir_constant_expressions.c, ir_constant_expression.cpp), over a
 * grid with signed zeros, infinities, NaN and denormals. Build natively and for the A1222, run
 * both, diff. Each line: function input-index result-bits (NaN printed as one value). */
#include <stdio.h>
#include <math.h>
#include <string.h>
#include <float.h>

static volatile float G[] = { -0.0f, 0.0f, 1.0f, -1.0f, 2.0f, -2.0f, 0.5f, -0.5f, 3.0f, -3.0f,
   1.5f, -1.5f, 0.25f, 1e-30f, -1e-30f, FLT_MIN, -FLT_MIN, 1.4e-45f, -1.4e-45f,
   FLT_MAX, -FLT_MAX, INFINITY, -INFINITY, NAN, 0.3f, -0.7f };
#define NG (sizeof(G) / sizeof(G[0]))
static volatile int E[] = { 0, 3, -3, 200, -200, 127, -126 };
#define NE (sizeof(E) / sizeof(E[0]))

static void f32(const char *n, unsigned i, float r)
{ unsigned u; memcpy(&u, &r, 4); printf("%s %u %08x\n", n, i, r != r ? 0x7fc00000u : u); }
static void f64(const char *n, unsigned i, double r)
{ unsigned long long u; memcpy(&u, &r, 8); printf("%s %u %016llx\n", n, i, r != r ? 0x7ff8000000000000ull : u); }

int main(void)
{
   for (unsigned a = 0; a < NG; a++) {
      float x = G[a]; double d = x;
      f32("acosf", a, acosf(x)); f32("asinf", a, asinf(x)); f32("atanf", a, atanf(x));
      f32("ceilf", a, ceilf(x)); f32("cosf", a, cosf(x)); f32("exp2f", a, exp2f(x));
      f32("expf", a, expf(x)); f32("floorf", a, floorf(x)); f32("log2f", a, log2f(x));
      f32("logf", a, logf(x)); f32("rintf", a, rintf(x)); f32("sinf", a, sinf(x));
      f32("sqrtf", a, sqrtf(x)); f32("truncf", a, truncf(x));
      if (x == x && fabsf(x) < 1e18f) {
         printf("lrintf %u %ld\n", a, lrintf(x)); printf("llrintf %u %lld\n", a, llrintf(x));
      }
      f64("ceil", a, ceil(d)); f64("cos", a, cos(d)); f64("floor", a, floor(d));
      f64("rint", a, rint(d)); f64("sin", a, sin(d)); f64("sqrt", a, sqrt(d));
      f64("trunc", a, trunc(d));
      int e; double m = frexp(d, &e); f64("frexp", a, m); if (isfinite(d)) printf("frexp-e %u %d\n", a, e);
      for (unsigned k = 0; k < NE; k++) {
         f32("ldexpf", a * NE + k, ldexpf(x, E[k]));
         f64("ldexp", a * NE + k, ldexp(d, E[k]));
      }
   }
   for (unsigned a = 0; a < NG; a++)
      for (unsigned b = 0; b < NG; b++) {
         unsigned i = a * NG + b;
         float x = G[a], y = G[b];
         f32("atan2f", i, atan2f(x, y)); f32("powf", i, powf(x, y));
         f64("pow", i, pow(x, y)); f64("fmax", i, fmax(x, y)); f64("fmin", i, fmin(x, y));
         for (unsigned c = 0; c < NG; c++) {
            f32("fmaf", i * NG + c, fmaf(x, y, G[c]));
            f64("fma", i * NG + c, fma(x, y, G[c]));
         }
      }
   return 0;
}
