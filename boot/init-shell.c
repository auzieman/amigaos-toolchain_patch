/* Minimal native init: the smoke kernel need not enable script interpreters. */
#include <sys/mount.h>
#include <unistd.h>

int
main(void)
{
  static const char ready[] =
    "\nA1222 experimental SPE bootstrap shell\nSHELL_READY\n";
  static const char failed[] = "Unable to execute bootstrap shell\n";
  char *const argv[] = { "/bin/sh", "-i", 0 };
  char *const envp[] = { "PATH=/bin", "HOME=/root", "TERM=vt100", 0 };

  mount("proc", "/proc", "proc", 0, 0);
  mount("sysfs", "/sys", "sysfs", 0, 0);
  mount("devtmpfs", "/dev", "devtmpfs", 0, 0);
  write(STDOUT_FILENO, ready, sizeof ready - 1);
  execve(argv[0], argv, envp);
  write(STDERR_FILENO, failed, sizeof failed - 1);
  _exit(127);
}
