/* Minimal native init: the smoke kernel need not enable script interpreters. */
#include <sys/mount.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <termios.h>
#include <unistd.h>
#include <string.h>

int
main(void)
{
  static const char ready[] =
    "\nA1222 experimental SPE bootstrap shell\nSHELL_READY\n";
  static const char failed[] = "Unable to execute bootstrap shell\n";
  char *const argv[] = { "/bin/sh", "-i", 0 };
  char *envp[] = { "PATH=/bin:/sbin:/usr/bin:/usr/sbin", "HOME=/root", "TERM=vt100", 0 };
  char console[64] = "/dev/console";

  mount("proc", "/proc", "proc", 0, 0);
  mount("sysfs", "/sys", "sysfs", 0, 0);
  mount("devtmpfs", "/dev", "devtmpfs", 0, 0);
  /* Follow the last explicit kernel console, rather than forcing serial on
   * a board whose operator has only USB keyboard and HDMI capture. */
  int cmdfd = open("/proc/cmdline", O_RDONLY);
  if (cmdfd >= 0) {
    char command[4096], *save = 0, *token;
    ssize_t count = read(cmdfd, command, sizeof command - 1);
    close(cmdfd);
    if (count > 0) {
      command[count] = 0;
      for (token = strtok_r(command, " \n", &save); token;
           token = strtok_r(0, " \n", &save)) {
        if (strncmp(token, "console=", 8)) continue;
        char *name = token + 8;
        size_t length = strcspn(name, ",");
        if (length < 4 || length >= sizeof console - 5) continue;
        if (strncmp(name, "tty", 3) && strncmp(name, "hvc", 3)) continue;
        size_t i;
        for (i = 0; i < length; ++i)
          if (!((name[i] >= '0' && name[i] <= '9') ||
                (name[i] >= 'A' && name[i] <= 'Z') ||
                (name[i] >= 'a' && name[i] <= 'z'))) break;
        if (i != length) continue;
        memcpy(console, "/dev/", 5);
        memcpy(console + 5, name, length);
        console[5 + length] = 0;
      }
    }
  }
  if (!strcmp(console, "/dev/tty0")) strcpy(console, "/dev/tty1");
  if (!strncmp(console, "/dev/tty", 8) && console[8] >= '0' && console[8] <= '9')
    envp[2] = "TERM=linux";
  /* Acquire the selected tty so shell signals and job control work. */
  setsid();
  int fd = open(console, O_RDWR);
  if (fd < 0) fd = open("/dev/console", O_RDWR);
  if (fd >= 0) {
    ioctl(fd, TIOCSCTTY, 1);
    dup2(fd, STDIN_FILENO);
    dup2(fd, STDOUT_FILENO);
    dup2(fd, STDERR_FILENO);
    if (fd > STDERR_FILENO) close(fd);
    tcsetpgrp(STDIN_FILENO, getpgrp());
  }
  write(STDOUT_FILENO, ready, sizeof ready - 1);
  /* A first physical boot may have no working GPU yet. Bring up the optional
   * lab network payload independently, without delaying the local shell. */
  if (access("/etc/start-network", X_OK) == 0 && fork() == 0) {
    int input = open("/dev/null", O_RDONLY);
    int output = open("/tmp/network-boot.log", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (input >= 0) { dup2(input, STDIN_FILENO); if (input > 2) close(input); }
    if (output >= 0) {
      dup2(output, STDOUT_FILENO); dup2(output, STDERR_FILENO);
      if (output > 2) close(output);
    }
    char *const network_argv[] = { "/bin/sh", "/etc/start-network", 0 };
    execve("/bin/sh", network_argv, envp);
    _exit(127);
  }
  execve(argv[0], argv, envp);
  write(STDERR_FILENO, failed, sizeof failed - 1);
  _exit(127);
}
