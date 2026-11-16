#include <ffi.h>
#include <stdio.h>
#include <string.h>
static double mix(int a, double b, long long c, float d, double e, int f, double g, double h, double i) {
    return a + b * 2 + (double)c / 3 + d * 4 + e - f + g * h + i;
}
static void handler(ffi_cif *cif, void *ret, void **args, void *ud) {
    (void)cif; (void)ud;
    *(double *)ret = *(double *)args[0] * 10 + *(int *)args[1] + *(long long *)args[2];
}
int main(void) {
    ffi_cif cif; ffi_type *t[9] = { &ffi_type_sint, &ffi_type_double, &ffi_type_sint64, &ffi_type_float, &ffi_type_double,
                                    &ffi_type_sint, &ffi_type_double, &ffi_type_double, &ffi_type_double };
    int a = 7, f = 2; double b = 1.5, e = -0.25, g = 3.0, h = 0.5, i = 1e-3; long long c = 9000000000LL; float d = 0.125f;
    void *v[9] = { &a, &b, &c, &d, &e, &f, &g, &h, &i };
    double r1, r2;
    if (ffi_prep_cif(&cif, FFI_DEFAULT_ABI, 9, &ffi_type_double, t) != FFI_OK) return 2;
    ffi_call(&cif, FFI_FN(mix), &r1, v);
    r2 = mix(a, b, c, d, e, f, g, h, i);
    ffi_cif c2; ffi_type *t2[3] = { &ffi_type_double, &ffi_type_sint, &ffi_type_sint64 }; void *code;
    ffi_closure *cl = ffi_closure_alloc(sizeof(ffi_closure), &code);
    if (ffi_prep_cif(&c2, FFI_DEFAULT_ABI, 3, &ffi_type_double, t2) != FFI_OK || ffi_prep_closure_loc(cl, &c2, handler, NULL, code) != FFI_OK) return 3;
    double r3 = ((double (*)(double, int, long long))code)(2.5, 4, 5000000000LL);
    printf("ffi_call %.17g direct %.17g closure %.17g\n", r1, r2, r3);
    return !(r1 == r2 && r3 == 5000000029.0);
}
