/* #39: PR_GET_FPEXC/PR_SET_FPEXC as an SPE program sees them (kernel or qemu-user), then
 * glibc's fegetenv/fesetenv round trip and sqrt() leaving SPEFSCR alone. */
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <math.h>
#include <fenv.h>
#include <pthread.h>
#include <sys/prctl.h>
static unsigned spefscr(void) { unsigned v; __asm__ volatile("mfspr %0, 512" : "=r"(v)); return v; }
static void get(const char *tag)
{
    unsigned v = 0xdeadbeef;
    int r = prctl(PR_GET_FPEXC, &v, 0, 0, 0);
    printf("%-34s rc=%d errno=%-2d val=%#x\n", tag, r, r ? errno : 0, v);
}
static void set(unsigned val)
{
    int r = prctl(PR_SET_FPEXC, val, 0, 0, 0);
    char tag[48]; snprintf(tag, sizeof tag, "PR_SET_FPEXC %#x", val);
    printf("%-34s rc=%d errno=%d\n", tag, r, r ? errno : 0);
}
static void *thr(void *a) { (void)a; get("thread: PR_GET_FPEXC"); return NULL; }
static volatile double two = 2.0, big = 1e308, ten = 10.0;
int main(void)
{
    get("start: PR_GET_FPEXC");
    set(0x80 | 0x20000);  get("after SW_ENABLE|OVF");
    pthread_t t; pthread_create(&t, NULL, thr, NULL); pthread_join(t, NULL);
    set(0x80 | 0xff0000); get("after SW_ENABLE|0xff0000 (masked)");
    set(2);               get("after classic 2");
    set(4);               get("after invalid 4");
    set(3);
    fenv_t e; memset(&e, 0x5a, sizeof e);
    int r = fegetenv(&e);
    unsigned w[2]; memcpy(w, &e, sizeof w);
    printf("fegetenv rc=%d env words %#x %#x spefscr=%#x\n", r, w[0], w[1], spefscr());
    unsigned s0 = spefscr();
    volatile double q = sqrt(two);
    printf("sqrt=%a spefscr before=%#x after=%#x big*ten=%g\n", (double)q, s0, spefscr(), big * ten);
    return 0;
}
