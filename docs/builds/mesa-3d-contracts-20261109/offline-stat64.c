/* Diagnostic-only: preserve real libc time64 metadata, translating only the
 * no-op DRM shim's fabricated device/existence responses through typed fields.
 */
#define _GNU_SOURCE 1
#define _FILE_OFFSET_BITS 64
#define _TIME_BITS 64
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <stdint.h>
#include <string.h>
#include <dlfcn.h>
extern int tabor_probe_stat32(const char *, int, uint64_t *, uint32_t *);
static int fix_fake(struct stat64 *st, const char *path, int fd, int result)
{
   uint64_t device;
   uint32_t mode;
   if (tabor_probe_stat32(path, fd, &device, &mode) == 0 &&
       (result != 0 || (S_ISCHR(mode) && major(device) == 226))) {
      memset(st, 0, sizeof(*st));
      st->st_rdev = device;
      st->st_mode = mode;
      return 0;
   }
   return result;
}
int __stat64_time64(const char *path, struct stat64 *st)
{
   int (*call)(const char *, struct stat64 *) = dlsym(RTLD_NEXT, "__stat64_time64");
   return fix_fake(st, path, -1, call(path, st));
}
int __fstat64_time64(int fd, struct stat64 *st)
{
   int (*call)(int, struct stat64 *) = dlsym(RTLD_NEXT, "__fstat64_time64");
   return fix_fake(st, 0, fd, call(fd, st));
}
