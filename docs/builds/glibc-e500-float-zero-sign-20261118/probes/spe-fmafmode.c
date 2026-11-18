/* glibc 0008: fmaf's exact-zero result in each rounding mode (IEEE: the sum of two zeros is -0
 * when both are -0, a cancellation is +0, and both are -0 under FE_DOWNWARD). Also ldexpf and
 * asinf of -0. Build natively and for the A1222; diff the output. 1 = -0. */
#include <stdio.h>
#include <math.h>
#include <fenv.h>
int main(void)
{
   static const int m[] = { FE_TONEAREST, FE_TOWARDZERO, FE_UPWARD, FE_DOWNWARD };
   static const char *mn[] = { "nearest", "zero", "up", "down" };
   volatile float v[][3] = { { -2, 1, 2 }, { 2, 1, -2 }, { -1, 0, -0.0f }, { 1, 0, -0.0f },
                             { -1, 0, 0 }, { 1, -0.0f, -0.0f }, { 0.5f, 4, -2 } };
   for (int i = 0; i < 4; i++) {
      fesetround(m[i]);
      printf("%-7s fmaf:", mn[i]);
      for (unsigned j = 0; j < sizeof v / sizeof v[0]; j++)
         printf(" %d", signbit(fmaf(v[j][0], v[j][1], v[j][2])) != 0);
      volatile float z = -0.0f;
      printf("  ldexpf(-0,3)=%d asinf(-0)=%d\n", signbit(ldexpf(z, 3)) != 0, signbit(asinf(z)) != 0);
   }
   return 0;
}
