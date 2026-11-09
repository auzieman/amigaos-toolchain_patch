from pathlib import Path
import json,shlex,subprocess
w=Path('/srv/data1/tabor-build/linux-live-001/work/native-vertex-contract-20261109-001')
src=r'''
#include "nir/ac_nir_native_vertex.h"
#include "compiler/glsl_types.h"
#include <stdio.h>
int main(void) {
 glsl_type_singleton_init_or_ref();
 static const nir_shader_compiler_options options={0};
 unsigned cases=0;
 for(unsigned bits=8;bits<=64;bits*=2)for(unsigned n=0;n<32;n++) {
  uint64_t expected=(UINT64_C(0x123456789abcdef1)*(n+1));
  if(bits<64)expected&=(UINT64_C(1)<<bits)-1;
  uint64_t raw=0;for(unsigned i=0;i<bits/8;i++)raw|=((expected>>(i*8))&255)<<(bits-8-i*8);
  nir_builder b=nir_builder_init_simple_shader(MESA_SHADER_COMPUTE,&options,"native-vertex-scalar");
  nir_def *value=ac_nir_native_vertex_scalar(&b,nir_imm_intN_t(&b,raw,bits));
  nir_store_ssbo(&b,value,nir_imm_int(&b,0),nir_imm_int(&b,0),.align_mul=bits/8);
  nir_intrinsic_instr *store=nir_instr_as_intrinsic(nir_block_last_instr(nir_start_block(b.impl)));
  while(nir_opt_constant_folding(b.shader)) {}
  const nir_const_value *constant=nir_src_as_const_value(store->src[0]);
  if(!constant || nir_const_value_as_uint(constant[0],bits)!=expected)return 2;
  ralloc_free(b.shader);cases++;
 }
 glsl_type_singleton_decref();printf("PASS actual NIR constant folding, %u scalar width cases\n",cases);return 0;
}
'''
(w/'check-native-vertex-nir.c').write_text(src)
commands=json.loads((w/'native/build/compile_commands.json').read_text())
row=next(x for x in commands if x['file'].endswith('ac_nir_prerast_utils.c'))
a=shlex.split(row['command']);filtered=[];i=0
while i<len(a):
 if a[i] in ['-o','-c','-MQ','-MF']:i+=2;continue
 if a[i] in ['-MD','-DNDEBUG']:i+=1;continue
 filtered.append(a[i]);i+=1
filtered+=['-UNDEBUG','-c','/work/check-native-vertex-nir.c','-o','/work/native-vertex-nir.o']
libs=['src/compiler/nir/libnir.a','src/compiler/libcompiler.a','src/util/libmesa_util.a','src/util/libmesa_util_sse41.a','src/util/blake3/libblake3.a']
link=['c++','/work/native-vertex-nir.o','-Wl,--gc-sections','-Wl,--start-group',*libs,'-Wl,--end-group','-lm','-lz','-ldl','-pthread','-o','/work/native-vertex-nir-test']
script='set -e\ncd /work/native/build\n'+shlex.join(filtered)+'\n'+shlex.join(link)+'\n/work/native-vertex-nir-test\n'
cmd=['docker','run','--rm','--cpus=2','--memory=4g','--network=none','-v',str(w)+':/work','-v',str(w/'mesa-source')+':/source:ro','--entrypoint','sh','sha256:92b850162c8dcc8aced3d4766e1da85d5b0a63cfcdb14c4732c0756c612d5eef','-c',script]
r=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
(w/'native-vertex-nir-check.json').write_text(json.dumps({'argv':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'limits':'Actual NIR builder and constant folder; memory load/store endpoints modeled; not GPU execution or full transform feedback pass'},indent=2)+'\n')
print(r.stdout[-1200:],r.stderr[-1800:]);r.check_returncode()
