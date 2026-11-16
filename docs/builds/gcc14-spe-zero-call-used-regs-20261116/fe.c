#include <fenv.h>
#include <stdio.h>
__attribute__((noipa)) double d(double a, double b) { return a / b; }
static volatile double one = 1.0, three = 3.0;
int main(void) {
    fesetround(FE_UPWARD);
    double x = d(one, three);
    int r = fegetround() == FE_UPWARD;
    fesetround(FE_TONEAREST);
    double y = d(one, three);
    printf("%d %a %a\n", r, x, y);
    return !(r && x != y);
}
