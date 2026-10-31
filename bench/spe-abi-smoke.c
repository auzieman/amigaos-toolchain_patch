/* Basic restored Linux/SPE C ABI checks, not exhaustive ABI certification. */
#define _GNU_SOURCE
#include <fenv.h>
#include <errno.h>
#include <linux/futex.h>
#include <sys/syscall.h>
#include <pthread.h>
#include <setjmp.h>
#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <ucontext.h>
#include <unistd.h>

static int failures;
static __thread int tls_value = 41;
static volatile sig_atomic_t signal_ok;
static ucontext_t caller, child;
static char child_stack[32768] __attribute__((aligned(16)));
static volatile int context_ok;

static void check(const char *name, int ok)
{
  printf("ABI_TEST %s %s\n", name, ok ? "PASS" : "FAIL");
  if (!ok) failures++;
}

__attribute__((noinline)) static double add_args(int count, ...)
{
  va_list ap;
  double result = 0;
  va_start(ap, count);
  for (int i = 0; i < count; i++) result += va_arg(ap, double);
  va_end(ap);
  return result;
}

static void on_signal(int number, siginfo_t *info, void *context)
{
  volatile double a = 1.5, b = 2.25;
  signal_ok = number == SIGUSR1 && info && context && a + b == 3.75;
}

static void *thread_main(void *unused)
{
  (void)unused;
  if (tls_value != 41) return 0;
  tls_value = 99;
  volatile double a = 1.5, b = 2.25;
  return a + b == 3.75 && tls_value == 99 ? (void *)123 : 0;
}

static void context_main(void)
{
  volatile double a = 1.5, b = 2.25;
  context_ok = a + b == 3.75;
}

int main(int argc, char **argv)
{
  setvbuf(stdout, 0, _IONBF, 0);
  puts("TABOR_QEMU_INIT_OK: restored SPE libc C ABI checks");
  volatile float fa = 1.5f, fb = 2.25f;
  volatile double da = 1.5, db = 2.25;
  check("float32", fa + fb == 3.75f);
  check("float64", da + db == 3.75);
  check("varargs", add_args(2, da, db) == 3.75);
  char text[64];
  snprintf(text, sizeof text, "%.2f %.2Lf", 3.75, 3.75L);
  check("formatting", !strcmp(text, "3.75 3.75"));

  int saved_round = fegetround();
  volatile double one = 1.0, half_ulp = 0x1p-53;
  int env_ok = fesetround(FE_UPWARD) == 0;
  volatile double up = one + half_ulp;
  env_ok &= fegetround() == FE_UPWARD && up == 0x1.0000000000001p0;
  env_ok &= fesetround(FE_DOWNWARD) == 0;
  volatile double down = one + half_ulp;
  env_ok &= fegetround() == FE_DOWNWARD && down == 1.0;
  env_ok &= fesetround(saved_round) == 0;
  env_ok &= feclearexcept(FE_ALL_EXCEPT) == 0;
  env_ok &= feraiseexcept(FE_INVALID) == 0;
  env_ok &= (fetestexcept(FE_INVALID) & FE_INVALID) != 0;
  env_ok &= feclearexcept(FE_ALL_EXCEPT) == 0;
  printf("FENV_DETAIL up=%a down=%a saved_round=%d\n", up, down, saved_round);
  check("fenv", env_ok);

  jmp_buf jump;
  volatile double preserved = 3.75;
  int returned = setjmp(jump);
  if (!returned) longjmp(jump, 7);
  check("setjmp", returned == 7 && preserved == 3.75);

  struct sigaction action = { .sa_sigaction = on_signal, .sa_flags = SA_SIGINFO };
  sigemptyset(&action.sa_mask);
  int signal_result = sigaction(SIGUSR1, &action, 0);
  if (!signal_result) signal_result = raise(SIGUSR1);
  check("signal", signal_result == 0 && signal_ok && preserved == 3.75);

  int futex_word = 0;
  errno = 0;
  long futex_result = syscall(SYS_futex, &futex_word, FUTEX_WAKE, 1, 0, 0, 0);
  if (futex_result < 0 && errno == ENOSYS) {
    puts("ABI_TEST pthread_tls SKIP_KERNEL_FUTEX");
    failures++;
  } else {
    pthread_t thread;
    void *thread_result = 0;
    int thread_ok = pthread_create(&thread, 0, thread_main, 0) == 0;
    if (thread_ok) thread_ok = pthread_join(thread, &thread_result) == 0;
    check("pthread_tls", thread_ok && thread_result == (void *)123 && tls_value == 41);
  }

  int context_result = getcontext(&child);
  if (!context_result) {
    child.uc_stack.ss_sp = child_stack;
    child.uc_stack.ss_size = sizeof child_stack;
    child.uc_link = &caller;
    makecontext(&child, context_main, 0);
    context_result = swapcontext(&caller, &child);
  }
  check("ucontext", context_result == 0 && context_ok);
  printf("ABI_SMOKE_DONE failures=%d\n", failures);
  if (argc == 2 && strcmp(argv[1], "--cli") == 0) return failures ? 1 : 0;
  for (;;) pause(); /* PID1 must stay alive for the host's bounded test. */
}
