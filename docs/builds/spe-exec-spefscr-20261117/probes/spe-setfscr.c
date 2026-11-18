/* kernel 020 slowdown: LD_PRELOAD shim that writes SPEFSCR from $SPE_SETFSCR (hex) in a
 * constructor, after exec, so kernel 020's start value (0x3c) can be replaced inside the process.
 * Threads created later inherit it. Prints the value before and after to stderr. */
#include <stdio.h>
#include <stdlib.h>
static unsigned rd(void) { unsigned v; __asm__ volatile("mfspr %0, 512" : "=r"(v)); return v; }
__attribute__((constructor)) static void set(void)
{
   const char *s = getenv("SPE_SETFSCR");
   if (!s) return;
   unsigned before = rd(), v = (unsigned)strtoul(s, NULL, 16);
   __asm__ volatile("mtspr 512, %0" :: "r"(v));
   fprintf(stderr, "spe-setfscr: %08x -> %08x\n", before, rd());
}
