from pathlib import Path
import subprocess,json,hashlib,difflib
b=Path('/srv/data1/tabor-build/linux-live-001');old=b/'work/radeonsi-aco-20261109-002';w=b/'work/radeonsi-le-ib-20261109-001'
assert not w.exists();subprocess.run(['cp','-a','--reflink=auto',str(old),str(w)],check=True)
p=w/'mesa-source/src/gallium/winsys/amdgpu/drm/amdgpu_cs.cpp';s=p.read_text();n=s
anchor='/* FENCES */'
helper='''/* Opt-in diagnostic paired with kernel polaris11_le_user_ib=1.
 * Keep CPU construction and chain-size fixups native until publication.
 * This does not touch descriptors, shader binaries, or other engines.
 */
static bool tabor_explicit_le_gfx_ib(struct amdgpu_winsys *aws, enum amd_ip_type ip)
{
#if UTIL_ARCH_BIG_ENDIAN
   return ip == AMD_IP_GFX && aws->info.family == CHIP_POLARIS11 &&
          debug_get_bool_option("TABOR_POLARIS11_LE_IB", false);
#else
   return false;
#endif
}

static void tabor_serialize_gfx_ib(uint32_t *words, unsigned count)
{
   for (unsigned i = 0; i < count; i++)
      words[i] = util_cpu_to_le32(words[i]);
}

'''
assert n.count(anchor)==1;n=n.replace(anchor,helper+anchor)
n=n.replace('#include "util/os_time.h"','#include "util/os_time.h"\n#include "util/u_debug.h"\n#include "util/u_math.h"')
a='   ac_drm_bo_cpu_unmap(ctx->aws->dev, bo);';assert n.count(a)==1
n=n.replace(a,'''   if (tabor_explicit_le_gfx_ib(ctx->aws, AMD_IP_GFX))
      tabor_serialize_gfx_ib((uint32_t *)cpu, 1);

'''+a)
a='   amdgpu_pad_gfx_compute_ib(aws, cs->ip_type, map, &preamble_num_dw, 0);';assert n.count(a)==1
n=n.replace(a,a+'''
   if (tabor_explicit_le_gfx_ib(aws, cs->ip_type))
      tabor_serialize_gfx_ib(map, preamble_num_dw);''')
a='      /* Swap command streams. "cst" is going to be submitted. */';assert n.count(a)==1
n=n.replace(a,'''      /* Sizes, padding and optional noop replacement are now final. Serialize
       * each completed chunk once, including links patched by set_ib_size.
       * Kernel chunk metadata remains native; only GPU IB memory is LE.
       */
      if (tabor_explicit_le_gfx_ib(aws, cs->ip_type)) {
         for (unsigned i = 0; i < rcs->num_prev; i++)
            tabor_serialize_gfx_ib(rcs->prev[i].buf, rcs->prev[i].cdw);
         tabor_serialize_gfx_ib(rcs->current.buf, rcs->current.cdw);
      }

'''+a)
p.write_text(n)
patch=''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/src/gallium/winsys/amdgpu/drm/amdgpu_cs.cpp',tofile='b/src/gallium/winsys/amdgpu/drm/amdgpu_cs.cpp'))
(w/'0003-polaris-opt-in-explicit-le-gfx-ibs.patch').write_text(patch)
(w/'source-receipt.json').write_text(json.dumps({'parent':str(old),'old_source_sha256':hashlib.sha256(s.encode()).hexdigest(),'new_source_sha256':hashlib.sha256(n.encode()).hexdigest(),'patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),'default':'off','kernel_pair':'polaris11_le_user_ib=1','scope':'BE Polaris11 GFX complete native PM4 IBs only; main, chained, preamble, reset-nop','hardware_tested':False},indent=2)+'\n')
print(w)
