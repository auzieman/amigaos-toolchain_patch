from pathlib import Path
import json,shlex,subprocess
w=Path('/srv/data1/tabor-build/linux-live-001/work/native-vertex-contract-20261109-001')
text=(w/'mesa-source/src/gallium/drivers/radeonsi/si_nir_lower_vs_inputs.c').read_text()
def extract(name,ret):
 pos=text.index('\n'+name+'(');start=text.rfind(ret,0,pos+1);brace=text.index('{',pos);depth=1;i=brace+1
 while depth:
  depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[start:i]+'\n'
head=(w/'mesa-source/src/gallium/drivers/radeonsi/si_shader.h').read_text()
start=head.index('union si_vs_fix_fetch {');end=head.index('\n};',start)+3
union=head[start:end]
uf=extract('ufN_to_float','static nir_def *')
fn=extract('opencoded_load_format','static void').replace('ac_nir_native_vertex_enabled(gfx_level)','test_native_contract').replace('nir_load_buffer_amd(', 'model_load(')
src=r'''#include "nir/ac_nir_native_vertex.h"
#include "ac_shader_util.h"
#include "compiler/glsl_types.h"
#include <stdio.h>
static bool test_native_contract;
static unsigned char payload[64];
static nir_def *model_load(nir_builder *b,unsigned channels,unsigned bits,nir_def *rsrc,nir_def *v,nir_def *offset,nir_def *index) {
 unsigned base=nir_const_value_as_uint(nir_src_as_const_value(nir_src_for_ssa(offset))[0],32);
 nir_def *values[4];
 for(unsigned c=0;c<channels;c++) {
  uint64_t value=0;for(unsigned i=0;i<bits/8;i++)value|=(uint64_t)payload[base+c*(bits/8)+i]<<(i*8);
  values[c]=nir_imm_intN_t(b,value,bits);
 }
 return nir_vec(b,values,channels);
}
'''+union+'\n'+uf+fn+r'''
static int evaluate(union si_vs_fix_fetch fix,bool native,unsigned width,uint32_t out_value[4]) {
 static const nir_shader_compiler_options options={0};
 test_native_contract=native;
 unsigned count=fix.u.num_channels_m1+1;
 if(fix.u.log_size==3 && fix.u.format!=AC_FETCH_FORMAT_FLOAT)count=1;
 memset(payload,0,sizeof(payload));
 for(unsigned c=0;c<count;c++) {
  uint64_t value=0x936ab51dULL+c*0x123;
  if(fix.u.format==AC_FETCH_FORMAT_FLOAT) {
   if(width==16)value=0x3c00+c*0x400;
   else if(width==32){float f=(float)c-1.0f;uint32_t u;memcpy(&u,&f,4);value=u;}
   else {double d=(double)c-1.;memcpy(&value,&d,8);}
  }
  for(unsigned i=0;i<width/8;i++)payload[c*(width/8)+i]=(value>>(8*(native?width/8-1-i:i)))&255;
 }
 nir_builder b=nir_builder_init_simple_shader(MESA_SHADER_VERTEX,&options,"native-format-input");
 nir_def *out[4];
 opencoded_load_format(&b,nir_imm_int(&b,0),nir_imm_int(&b,0),fix,true,GFX8,out);
 nir_store_ssbo(&b,nir_vec(&b,out,4),nir_imm_int(&b,0),nir_imm_int(&b,0),.align_mul=4);
 nir_intrinsic_instr *store=nir_instr_as_intrinsic(nir_block_last_instr(nir_start_block(b.impl)));
 while(nir_opt_constant_folding(b.shader)) {}
 const nir_const_value *values=nir_src_as_const_value(store->src[0]);
 if(!values)return 2;
 for(unsigned c=0;c<4;c++)out_value[c]=nir_const_value_as_uint(values[c],32);
 ralloc_free(b.shader);return 0;
}
int main(void) {
 glsl_type_singleton_init_or_ref();unsigned cases=0;
 for(unsigned format=0;format<AC_FETCH_FORMAT_NONE;format++)for(unsigned size=0;size<4;size++)for(unsigned channels=1;channels<=4;channels++)for(unsigned reverse=0;reverse<2;reverse++) {
  if(format==AC_FETCH_FORMAT_FLOAT && size==0)continue;
  if(format==AC_FETCH_FORMAT_FIXED && size<2)continue;
  if(size==3 && format!=AC_FETCH_FORMAT_FLOAT && channels!=(format==AC_FETCH_FORMAT_FIXED?3:4))continue;
  union si_vs_fix_fetch fix={0};fix.u.log_size=size;fix.u.num_channels_m1=channels-1;fix.u.format=format;fix.u.reverse=reverse;
  unsigned width=size==3 && format!=AC_FETCH_FORMAT_FLOAT?32:8u<<size;
  uint32_t a[4],b[4];
  if(evaluate(fix,false,width,a)||evaluate(fix,true,width,b))return 3;
  if(memcmp(a,b,sizeof(a))){fprintf(stderr,"mismatch format=%u size=%u channels=%u reverse=%u\n",format,size,channels,reverse);return 4;}
  cases++;
 }
 glsl_type_singleton_decref();printf("PASS actual vertex format lowering, %u LE/native scalar/packed/reversed cases\n",cases);return 0;
}
'''

(w/'check-native-vertex-formats.c').write_text(src)
commands=json.loads((w/'native/build/compile_commands.json').read_text())
row=next(x for x in commands if x['file'].endswith('ac_nir_prerast_utils.c'))
a=shlex.split(row['command']);filtered=[];i=0
while i<len(a):
 if a[i] in ['-o','-c','-MQ','-MF']:i+=2;continue
 if a[i] in ['-MD','-DNDEBUG']:i+=1;continue
 filtered.append(a[i]);i+=1
filtered+=['-UNDEBUG','-c','/work/check-native-vertex-formats.c','-o','/work/native-vertex-formats.o']
libs=['src/compiler/nir/libnir.a','src/compiler/libcompiler.a','src/util/libmesa_util.a','src/util/libmesa_util_sse41.a','src/util/blake3/libblake3.a']
link=['c++','/work/native-vertex-formats.o','-Wl,--gc-sections','-Wl,--start-group',*libs,'-Wl,--end-group','-lm','-lz','-ldl','-pthread','-o','/work/native-vertex-formats-test']
script='set -e\ncd /work/native/build\n'+shlex.join(filtered)+'\n'+shlex.join(link)+'\n/work/native-vertex-formats-test\n'
cmd=['docker','run','--rm','--cpus=2','--memory=4g','--network=none','-v',str(w)+':/work','-v',str(w/'mesa-source')+':/source:ro','--entrypoint','sh','sha256:92b850162c8dcc8aced3d4766e1da85d5b0a63cfcdb14c4732c0756c612d5eef','-c',script]
r=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
(w/'native-vertex-formats-check.json').write_text(json.dumps({'argv':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'limits':'Actual opencoded_load_format, ufN_to_float and si_vs_fix_fetch extracted from candidate; real NIR builder/constant folder. GPU scalar loads replaced by little-endian byte-reader model and native predicate controlled. No physical GPU execution.'},indent=2)+'\n')
print(r.stdout[-1200:],r.stderr[-1800:]);r.check_returncode()
