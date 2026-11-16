#include <stdio.h>
#include <string.h>
#include <math.h>
__attribute__((noinline)) long long mul(long long a, long long b) { return a * b + (a >> 3); }
__attribute__((noinline)) double dmix(double a, double b) { return sqrt(a * b) + a / b; }
__attribute__((noinline)) int sum(const int *v, int n) { int s = 0; for (int i = 0; i < n; i++) s += v[i] * (i + 1); return s; }
struct pair { long long q; double d; };
__attribute__((noinline)) struct pair both(long long x, double y) { struct pair p = { x * 3 - 1, y * 0.5 }; return p; }
int main(void) {
    int v[100]; for (int i = 0; i < 100; i++) v[i] = i * 7 - 50;
    struct pair p = both(1234567890123LL, 7.25);
    char buf[200];
    snprintf(buf, sizeof buf, "%lld %.17g %d %lld %.17g", mul(123456789LL, 987654321LL), dmix(2.0, 8.0), sum(v, 100), p.q, p.d);
    puts(buf);
    return strcmp(buf, "121932631128067367 4.25 2080600 3703703670368 3.625") != 0;
}
