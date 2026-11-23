/* #48: does a new thread inherit SPEFSCR (exception enables) on e500v2 Linux? */
#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/syscall.h>
static unsigned spefscr(void) { unsigned v; __asm__ volatile("mfspr %0, 512" : "=r"(v)); return v; }
__attribute__((noipa)) static double f2d(float f) { return f; }
static void show(const char *tag)
{
   volatile float inf = __builtin_inff();
   double d = f2d(inf);
   unsigned long long u; memcpy(&u, &d, 8);
   printf("%-22s tid=%ld spefscr=%08x f2d(inf)=%016llx\n", tag, (long)syscall(SYS_gettid), spefscr(), u);
   fflush(stdout);
}
static void *child(void *a) { (void)a; show("child thread"); return NULL; }
static void *child2(void *a) { (void)a; show("child (parent idle)"); return NULL; }
int main(void)
{
   show("main");
   pthread_t t;
   pthread_create(&t, NULL, child, NULL); pthread_join(t, NULL);
   volatile float x = 1.0f; for (int i = 0; i < 1000; i++) x = x * 1.5f; /* SPE live in main */
   pthread_create(&t, NULL, child2, NULL); pthread_join(t, NULL);
   if (fork() == 0) { show("forked child"); _exit(0); }
   sleep(1);
   show("main end");
   return 0;
}
