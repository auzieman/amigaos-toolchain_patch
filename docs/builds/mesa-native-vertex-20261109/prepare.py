from pathlib import Path
import subprocess,difflib,json,hashlib
b=Path('/srv/data1/tabor-build/linux-live-001/work');old=b/'mesa-3d-contracts-20261109-001';w=b/'native-vertex-contract-20261109-001'
assert not w.exists();w.mkdir()
# Copy only source/build state. Dependency stage and SDK remain shared read-only.
for name in ['mesa-source','build','native','spe-cross.ini','3d-build.exit']:
 r=subprocess.run(['cp','-a',str(old/name),str(w/name)],capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stderr[-1000:])
(w/'stage').mkdir()

src=w/'mesa-source';changes=[]
def edit(name,fn):
 p=src/name;s=p.read_text();n=fn(s);assert n!=s,name;p.write_text(n)
 changes.append(''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/'+name,tofile='b/'+name)))
def replace(s,a,b):
 assert s.count(a)==1,(a[:70],s.count(a));return s.replace(a,b)
header='''/* SPDX-License-Identifier: MIT
 * Diagnostic GFX8 native CPU vertex/legacy-XFB payload contract.
 * Internal GPU descriptors, constants and command words have separate contracts.
 */
#ifndef AC_NIR_NATIVE_VERTEX_H
#define AC_NIR_NATIVE_VERTEX_H
#include "nir_builder.h"
#include "amd_family.h"
#include "util/u_debug.h"
#include "util/u_endian.h"

static inline bool
ac_nir_native_vertex_enabled(enum amd_gfx_level gfx_level)
{
#if UTIL_ARCH_BIG_ENDIAN
   return gfx_level == GFX8 && debug_get_bool_option("TABOR_NATIVE_VERTEX_DATA", false);
#else
   return false;
#endif
}

/* Operate on a scalar representation before numeric/format conversion.
 * Byte-sized channels are identity; larger scalars reverse their own bytes.
 */
static inline nir_def *
ac_nir_native_vertex_scalar(nir_builder *b, nir_def *value)
{
   unsigned bits = value->bit_size;
   assert(value->num_components == 1);
   assert(bits == 8 || bits == 16 || bits == 32 || bits == 64);
   if (bits == 8)
      return value;
   nir_def *result = nir_imm_intN_t(b, 0, bits);
   for (unsigned byte = 0; byte < bits / 8; byte++) {
      nir_def *part = nir_iand_imm(b, nir_ushr_imm(b, value, byte * 8), 0xff);
      result = nir_ior(b, result, nir_ishl_imm(b, part, bits - 8 - byte * 8));
   }
   return result;
}
#endif
'''
p=src/'src/amd/common/nir/ac_nir_native_vertex.h';p.write_text(header)
changes.append(''.join(difflib.unified_diff([],header.splitlines(True),fromfile='/dev/null',tofile='b/src/amd/common/nir/ac_nir_native_vertex.h')))
name='src/gallium/drivers/radeonsi/si_nir_lower_vs_inputs.c'
def inputs(s):
 s=replace(s,'#include "ac_nir.h"','#include "ac_nir.h"\n#include "ac_nir_native_vertex.h"')
 s=replace(s,'   int log_recombine = 0;','''   bool native_vertex = ac_nir_native_vertex_enabled(gfx_level);
   if (native_vertex) {
      /* Load scalar channels separately so byte arrays and packed formats keep
       * their format-defined ordering. Doubles are two dwords in memory.
       */
      load_log_size = MIN2(log_size, 2);
      load_num_channels = log_size == 3 ?
         (format == AC_FETCH_FORMAT_FLOAT ? 2 * num_channels : 1) : num_channels;
   }

   int log_recombine = 0;''')
 s=replace(s,'if ((gfx_level == GFX6 || gfx_level >= GFX10) && !known_aligned)', 'if (!native_vertex && (gfx_level == GFX6 || gfx_level >= GFX10) && !known_aligned)')
 s=replace(s,'} else if (load_num_channels == 2 || load_num_channels == 4) {','} else if (!native_vertex && (load_num_channels == 2 || load_num_channels == 4)) {')
 s=replace(s,'   if (log_recombine > 0) {','''   if (native_vertex) {
      for (unsigned i = 0; i < load_num_channels; i++)
         loads[i] = ac_nir_native_vertex_scalar(b, loads[i]);
      if (log_size == 3 && format == AC_FETCH_FORMAT_FLOAT) {
         for (unsigned i = 0; i < load_num_channels; i += 2) {
            nir_def *tmp = loads[i];
            loads[i] = loads[i + 1];
            loads[i + 1] = tmp;
         }
      }
   }

   if (log_recombine > 0) {''')
 return replace(s,'   if (opencode ||','   if (ac_nir_native_vertex_enabled(sel->screen->info.gfx_level) || opencode ||')
edit(name,inputs)
name='src/amd/common/nir/ac_nir_prerast_utils.c'
def streamout(s):
 s=replace(s,'#include "ac_nir.h"','#include "ac_nir.h"\n#include "ac_nir_native_vertex.h"')
 s=replace(s,'ac_nir_emit_legacy_streamout(nir_builder *b, unsigned stream, nir_xfb_info *info, ac_nir_prerast_out *out)','ac_nir_emit_legacy_streamout(nir_builder *b, unsigned stream, nir_xfb_info *info, ac_nir_prerast_out *out,\n                             enum amd_gfx_level gfx_level)')
 return replace(s,'         assert(out_comp >= output->component_offset);','''         if (ac_nir_native_vertex_enabled(gfx_level))
            data = ac_nir_native_vertex_scalar(b, data);

         assert(out_comp >= output->component_offset);''')
edit(name,streamout)
edit('src/amd/common/nir/ac_nir_helpers.h',lambda s:replace(s,'ac_nir_emit_legacy_streamout(nir_builder *b, unsigned stream, nir_xfb_info *info, ac_nir_prerast_out *out);','ac_nir_emit_legacy_streamout(nir_builder *b, unsigned stream, nir_xfb_info *info, ac_nir_prerast_out *out,\n                             enum amd_gfx_level gfx_level);'))
edit('src/amd/common/nir/ac_nir_lower_legacy_vs.c',lambda s:replace(s,'ac_nir_emit_legacy_streamout(&b, 0, ac_nir_get_sorted_xfb_info(nir), &out);','ac_nir_emit_legacy_streamout(&b, 0, ac_nir_get_sorted_xfb_info(nir), &out, gfx_level);'))
edit('src/amd/common/nir/ac_nir_create_gs_copy_shader.c',lambda s:replace(s,'ac_nir_emit_legacy_streamout(&b, stream, info, &out);','ac_nir_emit_legacy_streamout(&b, stream, info, &out, gfx_level);'))
(w/'0012-native-vertex-legacy-xfb-contract.patch').write_text(''.join(changes))
(w/'native-vertex-source.json').write_text(json.dumps({'parent':str(old),'default':'off','option':'TABOR_NATIVE_VERTEX_DATA=1','scope':'BE GFX8 native scalar vertex inputs and legacy streamout; SSBO-generated vertex data not qualified','source_sha256':{str(p.relative_to(src)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [src/'src/amd/common/nir/ac_nir_native_vertex.h',src/'src/gallium/drivers/radeonsi/si_nir_lower_vs_inputs.c',src/'src/amd/common/nir/ac_nir_prerast_utils.c']}},indent=2)+'\n')
print('Prepared isolated opt-in native vertex/legacy-XFB candidate')
