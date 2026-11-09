from pathlib import Path
import json,shlex,subprocess
w=Path('/srv/data1/tabor-build/linux-live-001/work/native-vertex-contract-20261109-001')
text=(w/'mesa-source/src/amd/common/nir/ac_nir_prerast_utils.c').read_text()
def extract(name,ret):
 pos=text.index('\n'+name+'(');start=text.rfind(ret,0,pos+1);brace=text.index('{',pos);depth=1;i=brace+1
 while depth:
  depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[start:i]+'\n'
helper=extract('get_output_and_type','static nir_def **')
fn=extract('ac_nir_emit_legacy_streamout','\nvoid\n').replace('\nvoid\n','\nstatic void\n',1).replace('ac_nir_emit_legacy_streamout(', 'test_emit_streamout(').replace('ac_nir_native_vertex_enabled(gfx_level)','test_native_contract')
src=r'''#include "nir/ac_nir_native_vertex.h"
#include "nir/ac_nir_helpers.h"
#include "nir_xfb_info.h"
#include "compiler/glsl_types.h"
#include <stdio.h>
static bool test_native_contract;
'''+helper+fn+r'''
int main(void) {
 glsl_type_singleton_init_or_ref();
 static const nir_shader_compiler_options options={0};
 unsigned cases=0;
 for(unsigned mode=0;mode<2;mode++)for(unsigned components=1;components<=4;components++)for(unsigned gap=0;gap<2;gap++) {
  test_native_contract=mode;
  nir_builder b=nir_builder_init_simple_shader(MESA_SHADER_VERTEX,&options,"legacy-xfb-native");
  ac_nir_prerast_out out={0};
  unsigned count=gap?2:1;
  nir_xfb_info *info=rzalloc_size(b.shader,nir_xfb_info_size(count));
  info->output_count=count;info->buffers_written=1;info->buffers[0].stride=64;
  for(unsigned slot=0;slot<count;slot++) {
   info->outputs[slot].location=VARYING_SLOT_VAR0+slot;
   info->outputs[slot].component_mask=(1u<<components)-1;
   info->outputs[slot].offset=slot*32;
   for(unsigned c=0;c<components;c++)out.outputs[VARYING_SLOT_VAR0+slot][c]=nir_imm_int(&b,0x12345600+c);
  }
  test_emit_streamout(&b,0,info,&out,GFX8);
  while(nir_opt_constant_folding(b.shader)) {}
  unsigned stores=0;
  nir_foreach_block(block,b.impl) nir_foreach_instr(instr,block) {
   if(instr->type!=nir_instr_type_intrinsic)continue;
   nir_intrinsic_instr *in=nir_instr_as_intrinsic(instr);
   if(in->intrinsic!=nir_intrinsic_store_buffer_amd)continue;
   const nir_const_value *v=nir_src_as_const_value(in->src[0]);
   if(!v || nir_src_num_components(in->src[0])!=components)return 2;
   for(unsigned c=0;c<components;c++) {
    uint32_t expected=mode?__builtin_bswap32(0x12345600+c):0x12345600+c;
    if(nir_const_value_as_uint(v[c],32)!=expected)return 3;
   }
   stores++;
  }
  if(stores!=count)return 4;
  ralloc_free(b.shader);cases++;
 }
 glsl_type_singleton_decref();printf("PASS actual legacy streamout lowering, %u dense/gapped native/LE cases\n",cases);return 0;
}
'''

(w/'check-native-vertex-xfb.c').write_text(src)
commands=json.loads((w/'native/build/compile_commands.json').read_text())
row=next(x for x in commands if x['file'].endswith('ac_nir_prerast_utils.c'))
a=shlex.split(row['command']);filtered=[];i=0
while i<len(a):
 if a[i] in ['-o','-c','-MQ','-MF']:i+=2;continue
 if a[i] in ['-MD','-DNDEBUG']:i+=1;continue
 filtered.append(a[i]);i+=1
filtered+=['-UNDEBUG','-c','/work/check-native-vertex-xfb.c','-o','/work/native-vertex-xfb.o']
libs=['src/compiler/nir/libnir.a','src/compiler/libcompiler.a','src/util/libmesa_util.a','src/util/libmesa_util_sse41.a','src/util/blake3/libblake3.a']
link=['c++','/work/native-vertex-xfb.o','-Wl,--gc-sections','-Wl,--start-group',*libs,'-Wl,--end-group','-lm','-lz','-ldl','-pthread','-o','/work/native-vertex-xfb-test']
script='set -e\ncd /work/native/build\n'+shlex.join(filtered)+'\n'+shlex.join(link)+'\n/work/native-vertex-xfb-test\n'
cmd=['docker','run','--rm','--cpus=2','--memory=4g','--network=none','-v',str(w)+':/work','-v',str(w/'mesa-source')+':/source:ro','--entrypoint','sh','sha256:92b850162c8dcc8aced3d4766e1da85d5b0a63cfcdb14c4732c0756c612d5eef','-c',script]
r=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
(w/'native-vertex-xfb-check.json').write_text(json.dumps({'argv':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'limits':'Actual extracted legacy streamout function and get_output_and_type, NIR builder and constant folder; predicate controlled to exercise both modes on native host; 32-bit output components, dense and gapped stores; no GPU execution or lowered64 XFB acceptance'},indent=2)+'\n')
print(r.stdout[-1200:],r.stderr[-1800:]);r.check_returncode()
