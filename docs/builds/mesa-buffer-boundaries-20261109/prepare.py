from pathlib import Path
import difflib,json,hashlib
w=Path('/srv/data1/tabor-build/linux-live-001/work/mesa-3d-contracts-20261109-001')
p=w/'mesa-source/src/amd/drm-shim/amdgpu_noop_drm_shim.c';s=p.read_text()
a='static const struct amdgpu_device *amdgpu_dev;'
n=s.replace(a,'#include <stdio.h>\n#include <unistd.h>\n#include "util/u_atomic.h"\n\n'+a)
a='''static int
amdgpu_ioctl_noop(int fd, unsigned long request, void *arg)'''
helper='''/* Offline no-op backend only. Record raw CPU-visible storage at submit;
 * no GPU emulation or interpretation. Prefixes are explicitly bounded.
 */
static int
amdgpu_capture_cs(int fd, unsigned long request, void *arg)
{
   const char *dir = getenv("TABOR_BO_CAPTURE_DIR");
   if (!dir)
      return 0;
   static unsigned serial;
   unsigned id = p_atomic_inc_return(&serial);
   struct shim_fd *shim_fd = drm_shim_fd_lookup(fd);
   mtx_lock(&shim_fd->handle_lock);
   hash_table_foreach(shim_fd->handles, entry) {
      struct shim_bo *bo = entry->data;
      unsigned handle = (uintptr_t)entry->key;
      unsigned count = MIN2(bo->size, 65536);
      unsigned char *data = calloc(1, count);
      if (!data)
         continue;
      ssize_t got = pread(shim_device.mem_fd, data, count, bo->mem_addr);
      if (got >= 0) {
         char path[1024];
         snprintf(path, sizeof(path), "%s/cs-%u-bo-%u-size-%u.bin", dir, id, handle, bo->size);
         FILE *f = fopen(path, "wb");
         if (f) {
            fwrite(data, 1, count, f);
            fclose(f);
         }
      }
      free(data);
   }
   mtx_unlock(&shim_fd->handle_lock);
   return 0;
}

'''
assert n.count(a)==1;n=n.replace(a,helper+a)
a='[DRM_AMDGPU_CS] = amdgpu_ioctl_noop,'
assert n.count(a)==1;n=n.replace(a,'[DRM_AMDGPU_CS] = amdgpu_capture_cs,')
p.write_text(n)
(w/'0011-offline-submit-buffer-capture.patch').write_text(''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/src/amd/drm-shim/amdgpu_noop_drm_shim.c',tofile='b/src/amd/drm-shim/amdgpu_noop_drm_shim.c')))
(w/'buffer-capture-source.json').write_text(json.dumps({'before':hashlib.sha256(s.encode()).hexdigest(),'after':hashlib.sha256(n.encode()).hexdigest(),'prefix_limit':65536,'gpu_execution':False},indent=2)+'\n')
