/* kernel 020 slowdown: the cost of one SPE exception fix-up. A loop of N double adds with an
 * Inf operand (traps with FINVE set) or a normal operand (no trap). Run plainly (0x3c) and with
 * spe-setfscr.so SPE_SETFSCR=0; per-op time from clock_gettime. */
#include <stdio.h>
#include <time.h>
#include <math.h>
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec * 1e-9; }
int main(void)
{
   volatile double inf = INFINITY, one = 1.0, acc = 0; const int n = 200000;
   unsigned f; __asm__ volatile("mfspr %0, 512" : "=r"(f));
   double t0 = now(); for (int i = 0; i < n; i++) acc = one + 1.0; double t1 = now();
   for (int i = 0; i < n; i++) acc = inf + 1.0; double t2 = now();
   volatile float fi = INFINITY, ff = 1.0f, fa = 0; double t3 = now();
   for (int i = 0; i < n; i++) fa = fi + 1.0f; double t4 = now();
   printf("spefscr=%08x  normal efdadd %.1f ns  Inf efdadd %.1f ns  Inf efsadd %.1f ns  (inf+1=%g)\n",
          f, (t1 - t0) / n * 1e9, (t2 - t1) / n * 1e9, (t4 - t3) / n * 1e9, (double)acc);
   (void)ff; (void)fa;
   return 0;
}
