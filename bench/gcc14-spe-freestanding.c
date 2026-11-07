/* Selected compiler/ABI checks without libc or libgcc dependencies.
 * Not a full glibc, fenv, signal, threading or C++ qualification.
 */
#if !defined(__SPE__) || !defined(__NO_FPRS__)
#error This probe requires SPE with floating point in GPRs
#endif
#if __BYTE_ORDER__ != __ORDER_BIG_ENDIAN__ || __SIZEOF_LONG_DOUBLE__ != 16
#error Unexpected target data model
#endif

static volatile float single_a = 1.5f, single_b = 2.25f;
static volatile double double_a = 1.5, double_b = 2.25;
static volatile unsigned touched;
extern void probe_array(float *, const float *, const float *, unsigned);

__attribute__((noinline)) float probe_single(float a, float b) { return a + b; }
__attribute__((noinline)) double probe_double(double a, double b) { return a + b; }

__attribute__((noinline)) static double probe_varargs(int count, ...)
{
    __builtin_va_list args;
    __builtin_va_start(args, count);
    double result = 0;
    while (count--)
        result += __builtin_va_arg(args, double);
    __builtin_va_end(args);
    return result;
}

__attribute__((noinline)) static void clobber_callers(void)
{
    ++touched;
    __asm__ volatile("" ::: "r3", "r4", "r5", "r6", "r7", "r8",
                     "r9", "r10", "r11", "r12", "memory");
}

__attribute__((noinline)) static double probe_preserved(double value)
{
    double held = value * 2.0;
    clobber_callers();
    return held + 0.25;
}

static void write_result(const char *text, unsigned length)
{
    register unsigned nr __asm__("r0") = 4;
    register unsigned result __asm__("r3") = 1;
    register const char *buffer __asm__("r4") = text;
    register unsigned size __asm__("r5") = length;
    /* Linux PowerPC SC clobbers volatile syscall registers. In particular,
       a real kernel need not preserve r9 as QEMU user-mode happened to do.
       Match glibc2.41 sysdeps/unix/sysv/linux/powerpc/sysdep.h's SC contract. */
    __asm__ volatile("sc" : "+r"(nr), "+r"(result), "+r"(buffer), "+r"(size)
                     : : "r6", "r7", "r8", "r9", "r10", "r11", "r12",
                         "xer", "cr0", "ctr", "memory");
}

__attribute__((noreturn)) static void finish(unsigned status)
{
    static const char pass[] = "GCC14_SPE_FREESTANDING_PASS single double varargs preserved optimized-loop\n";
    static const char fail[] = "GCC14_SPE_FREESTANDING_FAIL\n";
    write_result(status ? fail : pass, status ? sizeof(fail) - 1 : sizeof(pass) - 1);
    register unsigned nr __asm__("r0") = 1;
    register unsigned code __asm__("r3") = status;
    __asm__ volatile("sc" : "+r"(nr), "+r"(code)
                     : : "r4", "r5", "r6", "r7", "r8", "r9", "r10",
                         "r11", "r12", "xer", "cr0", "ctr", "memory");
    for (;;) {}
}

__attribute__((noreturn)) void _start(void)
{
    union { float value; unsigned bits; } single;
    union { double value; unsigned words[2]; } wide;
    single.value = probe_single(single_a, single_b);
    if (single.bits != 0x40700000u) finish(1);
    wide.value = probe_double(double_a, double_b);
    if (wide.words[0] != 0x400e0000u || wide.words[1]) finish(2);
    wide.value = probe_varargs(2, double_a, double_b);
    if (wide.words[0] != 0x400e0000u || wide.words[1]) finish(3);
    wide.value = probe_preserved(double_a);
    if (wide.words[0] != 0x400a0000u || wide.words[1] || touched != 1) finish(4);
    float left[8], right[8], result[8];
    for (unsigned i = 0; i < 8; ++i) {
        left[i] = single_a;
        right[i] = single_b;
    }
    probe_array(result, left, right, 8);
    for (unsigned i = 0; i < 8; ++i) {
        single.value = result[i];
        if (single.bits != 0x40700000u) finish(5);
    }
    finish(0);
}
