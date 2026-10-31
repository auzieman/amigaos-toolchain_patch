/* Basic Linux/SPE C++ runtime checks; not full ABI certification. */
#include <atomic>
#include <cstdio>
#include <cstring>
#include <thread>
#include <unistd.h>

static int failures;
static thread_local int tls_value = 41;
static void check(const char *name, bool ok)
{
  std::printf("CXX_TEST %s %s\n", name, ok ? "PASS" : "FAIL");
  if (!ok) ++failures;
}
static int destroyed;
struct guard { ~guard() { ++destroyed; } };
struct payload { double value; };
__attribute__((noinline)) static void throws_value(double value)
{
  guard unwind;
  throw payload{value};
}
int main(int argc, char **argv)
{
  std::setvbuf(stdout, nullptr, _IONBF, 0);
  std::puts("TABOR_QEMU_INIT_OK: Linux/SPE C++ reference runtime checks");
  check("long_double_128", sizeof(long double) == 16);
  volatile double a = 1.5, b = 2.25;
  double sum = a + b;
  bool caught = false;
  try { throws_value(sum); }
  catch (const payload &value) { caught = value.value == 3.75 && sum == 3.75; }
  catch (...) { caught = false; }
  check("exception_unwind", caught && destroyed == 1);
  std::atomic<unsigned> counter{0};
  bool tls_ok = false;
  try {
    std::thread worker([&]() {
      bool initial = tls_value == 41;
      tls_value = 99;
      for (unsigned i = 0; i < 10000; ++i) counter.fetch_add(1);
      tls_ok = initial && tls_value == 99;
    });
    for (unsigned i = 0; i < 10000; ++i) counter.fetch_add(1);
    worker.join();
  } catch (...) { tls_ok = false; }
  check("thread_tls", tls_ok && tls_value == 41);
  check("atomic_u32", counter.load() == 20000);
  std::printf("CXX_SMOKE_DONE failures=%d\n", failures);
  if (argc == 2 && !std::strcmp(argv[1], "--cli")) return failures ? 1 : 0;
  for (;;) pause();
}
