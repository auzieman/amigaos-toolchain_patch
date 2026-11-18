/* #48: float->double (efdcfs) and float ops on +-Inf/NaN on e500v2, across the fenv calls
 * dEQP's interval arithmetic makes (fesetround to directed modes and back, fegetenv/fesetenv). */
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <fenv.h>
#include <sys/prctl.h>

static unsigned long long bd(double d) { unsigned long long u; memcpy(&u, &d, 8); return u; }
static unsigned bf(float f) { unsigned u; memcpy(&u, &f, 4); return u; }
__attribute__((noipa)) static double f2d(float f) { return f; }
__attribute__((noipa)) static float fmul(float a, float b) { return a * b; }
static unsigned spefscr(void) { unsigned v; __asm__ volatile("mfspr %0, 512" : "=r"(v)); return v; }

static void show(const char *tag)
{
   volatile float inf = __builtin_inff(), nan = __builtin_nanf("");
   unsigned fpexc = 0;
   prctl(PR_GET_FPEXC, &fpexc, 0, 0, 0);
   printf("%-26s spefscr=%08x fpexc=%08x | f2d(inf)=%016llx f2d(-inf)=%016llx f2d(nan)=%016llx | -1*inf=%08x\n",
          tag, spefscr(), fpexc, bd(f2d(inf)), bd(f2d(-inf)), bd(f2d(nan)), bf(fmul(-1.0f, inf)));
}

int main(void)
{
   fenv_t env;
   show("start");
   fesetround(FE_UPWARD);    show("fesetround(UPWARD)");
   fesetround(FE_DOWNWARD);  show("fesetround(DOWNWARD)");
   fesetround(FE_TONEAREST); show("fesetround(TONEAREST)");
   fegetenv(&env);           show("fegetenv");
   fesetenv(&env);           show("fesetenv(saved)");
   fesetenv(FE_DFL_ENV);     show("fesetenv(FE_DFL_ENV)");
   feholdexcept(&env);       show("feholdexcept");
   feupdateenv(&env);        show("feupdateenv");
   return 0;
}
