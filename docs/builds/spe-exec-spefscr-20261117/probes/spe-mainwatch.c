/* #48: LD_PRELOAD shim. Reports SPEFSCR (after an SPE instruction, so the thread's own SPE
 * state is loaded) in a constructor, which runs after libc's initialisation and before the
 * program's own constructors and main, and again in a destructor at exit. */
#include <stdio.h>
#include <string.h>

static unsigned spefscr(void) { unsigned v; __asm__ volatile("mfspr %0, 512" : "=r"(v)); return v; }
__attribute__((noipa)) static double f2d(float f) { return f; }

static void report(const char *tag)
{
   volatile float inf = __builtin_inff();
   double d = f2d(inf);
   unsigned long long u; memcpy(&u, &d, 8);
   unsigned s = spefscr();
   fprintf(stderr, "[mainwatch] %s spefscr=%08x enables=%02x f2d(inf)=%016llx\n", tag, s, s & 0x7c, u);
}

__attribute__((constructor)) static void ctor(void) { report("ctor"); }
__attribute__((destructor)) static void dtor(void) { report("dtor"); }
