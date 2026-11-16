#include <stdio.h>
#include <math.h>
#include <fenv.h>
static volatile double two = 2.0, big = 1e308, ten = 10.0, one = 1.0, three = 3.0;
static unsigned spefscr(void) { unsigned v; __asm__ volatile("mfspefscr %0" : "=r"(v)); return v; }
int main(void) {
    printf("before: round=%d spefscr=%#x mul=%g third=%a\n", fegetround(), spefscr(), big * ten, one / three);
    volatile double r = sqrt(two);
    printf("sqrt=%a\n", r);
    printf("after:  round=%d spefscr=%#x mul=%g third=%a\n", fegetround(), spefscr(), big * ten, one / three);
    fesetround(FE_TONEAREST);
    printf("reset:  round=%d spefscr=%#x mul=%g\n", fegetround(), spefscr(), big * ten);
    return 0;
}
