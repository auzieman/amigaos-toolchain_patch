from pathlib import Path
import subprocess,json
w=Path('/srv/data1/tabor-build/linux-live-001/work/native-vertex-contract-20261109-001')
h=(w/'mesa-source/src/amd/common/nir/ac_nir_native_vertex.h').read_text()
start=h.index('static inline nir_def *');helper=h[start:h.rindex('#endif')]
mock=r'''
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
typedef struct { unsigned bit_size,num_components;uint64_t v; } nir_def;
typedef int nir_builder;
static nir_def pool[256];static unsigned cursor;
static uint64_t mask(unsigned bits){return bits==64?UINT64_MAX:((UINT64_C(1)<<bits)-1);}
static nir_def *val(unsigned bits,uint64_t v){assert(cursor<256);nir_def *r=&pool[cursor++];*r=(nir_def){bits,1,v&mask(bits)};return r;}
static nir_def *nir_imm_intN_t(nir_builder*b,uint64_t v,unsigned bits){return val(bits,v);}
static nir_def *nir_ushr_imm(nir_builder*b,nir_def*v,unsigned n){return val(v->bit_size,v->v>>n);}
static nir_def *nir_iand_imm(nir_builder*b,nir_def*v,uint64_t m){return val(v->bit_size,v->v&m);}
static nir_def *nir_ishl_imm(nir_builder*b,nir_def*v,unsigned n){return val(v->bit_size,v->v<<n);}
static nir_def *nir_ior(nir_builder*b,nir_def*a,nir_def*c){return val(a->bit_size,a->v|c->v);}
'''
tests=r'''
static uint64_t state=0x1eaf23015678abcdULL;
static uint64_t next(void){state^=state<<13;state^=state>>7;state^=state<<17;return state;}
static uint64_t gpu_load(const unsigned char *p,unsigned bytes){uint64_t v=0;for(unsigned i=0;i<bytes;i++)v|=(uint64_t)p[i]<<(8*i);return v;}
int main(void){unsigned checks=0,old_mismatches=0;nir_builder b=0;
 for(unsigned bits=8;bits<=64;bits*=2)for(unsigned n=0;n<4096;n++){
  uint64_t expected=next()&mask(bits);unsigned bytes=bits/8;unsigned char native[8];
  /* Explicit BE scalar producer and LE GPU reader model, independent of host. */
  for(unsigned j=0;j<bytes;j++)native[j]=expected>>(8*(bytes-1-j));
  uint64_t raw=gpu_load(native,bytes);old_mismatches+=(raw!=expected);
  cursor=0;nir_def *got=ac_nir_native_vertex_scalar(&b,val(bits,raw));assert(got->v==expected);
  /* Same helper publishes native BE bytes through a little-endian store. */
  cursor=0;uint64_t encoded=ac_nir_native_vertex_scalar(&b,val(bits,expected))->v;
  for(unsigned j=0;j<bytes;j++)assert(((encoded>>(8*j))&255)==native[j]);
  checks++;
 }
 /* Actual dword-wise decode + half reorder used for double vertex fetch. */
 for(unsigned n=0;n<4096;n++){
  uint64_t expected=next();unsigned char p[8];for(unsigned j=0;j<8;j++)p[j]=expected>>(56-8*j);
  cursor=0;uint64_t hi=ac_nir_native_vertex_scalar(&b,val(32,gpu_load(p,4)))->v;
  cursor=0;uint64_t lo=ac_nir_native_vertex_scalar(&b,val(32,gpu_load(p+4,4)))->v;
  assert(((hi<<32)|lo)==expected);checks++;
 }
 assert(old_mismatches>12000);printf("PASS scalar/store cases=16384 double-pair cases=4096 old-BE-mismatches=%u total=%u\n",old_mismatches,checks);
}
'''
p=w/'native-vertex-scalars.c';p.write_text(mock+helper+tests)
b=Path('/srv/data1/tabor-build/linux-live-001');gcc=str(b/'tools/cxx-reference-002/bin/powerpc-linux-gnuspe-gcc')
commands={'x86':['gcc','-O2',str(p),'-o',str(w/'scalar-x86')], 'spe':[gcc,'--sysroot='+str(b/'sysroot'),'-mcpu=8548','-mabi=spe','-mspe','-mfloat-gprs=double','-mlong-double-128','-O2',str(p),'-o',str(w/'scalar-spe')]}
results={}
for arch,cmd in commands.items():
 r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr[-1000:]
 run=[str(w/'scalar-x86')] if arch=='x86' else ['qemu-ppc','-cpu','e500v2','-L','/home/owner/native-vertex-spe-20261109-001/root',str(w/'scalar-spe')]
 r=subprocess.run(run,capture_output=True,text=True,timeout=15);assert r.returncode==0,(arch,r.stdout,r.stderr)
 results[arch]={'argv':cmd,'output':r.stdout,'exit':r.returncode}
results['limits']='Actual scalar helper extracted; NIR builder integer operations interpreted by mock, not actual NIR optimizer or GPU. Load/store endpoints modeled. Packed formats checked as scalar containers, not full numeric normalization. Double input pairs modeled; lowered64 XFB ordering still unqualified.'
(w/'native-vertex-scalar-check.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
