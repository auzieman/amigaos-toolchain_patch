/* Diagnostic-only bridge for the upstream no-op DRM shim's time32 hooks.
 * Obtain metadata through the actual ABI's headers; never reinterpret structs.
 */
#define _GNU_SOURCE 1
#define _LARGEFILE64_SOURCE 1
#include <sys/stat.h>
#include <stdint.h>
#include <string.h>
#include <dlfcn.h>
int tabor_probe_stat32(const char *path, int fd, uint64_t *device, uint32_t *mode)
{
   struct stat64 st;
   memset(&st, 0, sizeof(st));
   int r;
   if (path) {
      int (*call)(const char *, struct stat64 *) = dlsym(RTLD_NEXT, "stat64");
      r = call(path, &st);
   } else {
      int (*call)(int, struct stat64 *) = dlsym(RTLD_NEXT, "fstat64");
      r = call(fd, &st);
   }
   *device = st.st_rdev;
   *mode = st.st_mode;
   return r;
}

/* Trixie libdrm uses the time64 ioctl symbol. DRM requests in this offline
 * test carry no libc time_t fields; dispatch them through the existing shim.
 * Do not use this adapter for arbitrary time-bearing device ioctls.
 */
#include <stdarg.h>
int __ioctl_time64(int fd, unsigned long request, ...)
{
   va_list ap;
   va_start(ap, request);
   void *arg = va_arg(ap, void *);
   va_end(ap);
   int (*call)(int, unsigned long, ...) = dlsym(RTLD_NEXT, "ioctl");
   return call(fd, request, arg);
}

/* Keep duplicated fake DRM descriptors registered across libdrm's time64 ABI. */
int __fcntl_time64(int fd, int command, ...)
{
   va_list ap;
   va_start(ap, command);
   void *arg = va_arg(ap, void *);
   va_end(ap);
   int (*call)(int, int, ...) = dlsym(RTLD_NEXT, "fcntl");
   return call(fd, command, arg);
}
