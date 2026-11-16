#include <fenv.h>
#include <stdio.h>
__attribute__((noinline)) double d(double a, double b) { return a / b; }
int main(void) {
    fesetround(FE_UPWARD);
    double x = d(1.0, 3.0);
    int r = fegetround() == FE_UPWARD;
    fesetround(FE_TONEAREST);
    double y = d(1.0, 3.0);
    printf("%d %a %a\n", r, x, y);
    return !(r && x != y);
}
