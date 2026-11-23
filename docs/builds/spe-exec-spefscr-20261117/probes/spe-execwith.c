/* #48: set SPEFSCR to argv[1] (hex) in this process, then exec argv[2..]. Shows whether the
 * exec'd program starts with the kernel's defined value or inherits the caller's register. */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
int main(int argc, char **argv)
{
   if (argc < 3) { fprintf(stderr, "usage: %s HEX prog [args]\n", argv[0]); return 2; }
   unsigned v = (unsigned)strtoul(argv[1], NULL, 16);
   volatile float x = 1.0f; x = x * 2.0f; /* make this thread's SPE state live */
   __asm__ volatile("mtspr 512, %0" : : "r"(v));
   execv(argv[2], argv + 2);
   perror("execv");
   return 1;
}
