"""R730 only: exact kernel emitters, actual native/SPE compilation, AMD field oracle."""
from pathlib import Path
import hashlib,json,subprocess
base=Path('/srv/data1/tabor-build/linux-live-001')
src=base/'work/e2e-usb-20261109-013/source/drivers/gpu/drm/amd/amdgpu'
w=Path('/home/owner/gfx8-contract-review-20261109-001');w.mkdir(exist_ok=True)
source=(src/'gfx_v8_0.c').read_text()
def extract(signature):
 start=source.index(signature);pos=source.index('{',start)+1;depth=1
 while depth:
  depth+=(source[pos]=='{')-(source[pos]=='}');pos+=1
 return source[start:pos]
functions='\n'.join(extract(s) for s in ('static void gfx_v8_0_ring_emit_ib_gfx(', 'static void gfx_v8_0_ring_emit_fence_gfx(', 'static void gfx_v8_0_ring_emit_pipeline_sync('))
prefix=r'''
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <assert.h>
#include <string.h>
#include "vid.h"
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define __BIG_ENDIAN 1
#else
#undef __BIG_ENDIAN
#endif
typedef uint32_t u32;typedef uint64_t u64;
#define lower_32_bits(x) ((uint32_t)(x))
#define upper_32_bits(x) ((uint32_t)((uint64_t)(x)>>32))
#define CACHE_FLUSH_AND_INV_TS_EVENT 0x14
#define AMDGPU_FENCE_FLAG_64BIT 1
#define AMDGPU_FENCE_FLAG_INT 2
#define AMDGPU_FENCE_FLAG_EXEC 8
#define AMDGPU_IB_FLAG_CE 1
#define AMDGPU_IB_FLAG_PREEMPT 4
#define AMDGPU_RING_TYPE_GFX 0
#define AMDGPU_JOB_GET_VMID(job) ((job)->vmid)
struct amdgpu_job {unsigned vmid;};
struct amdgpu_ib {unsigned flags,length_dw;u64 gpu_addr;bool is_le;};
struct funcs {unsigned type;};
struct amdgpu_ring {void *adev;struct funcs *funcs;struct {u32 sync_seq;u64 gpu_addr;} fence_drv;};
static uint32_t emitted[64];static unsigned count;
static bool amdgpu_sriov_vf(void *p){return false;}
static void gfx_v8_0_ring_emit_de_meta(struct amdgpu_ring *r){assert(0);}
static void amdgpu_ring_write(struct amdgpu_ring *r,uint32_t v){assert(count<64);emitted[count++]=v;}
/* Field oracle below uses AMD PAL historical PM4 ordinal positions,
 * independently of kernel macro definitions. Compare native numeric values
 * first, then explicitly check the serialized LE bytes from this host. */
static void word(unsigned i,uint32_t expected){assert(i<count);assert(emitted[i]==expected);
 uint32_t stored=emitted[i];
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
 stored=__builtin_bswap32(stored);
#endif
 unsigned char bytes[4];memcpy(bytes,&stored,4);for(unsigned b=0;b<4;b++)assert(bytes[b]==((expected>>(8*b))&255));}
'''
tests=r'''
int main(void){unsigned checks=0;struct funcs funcs={0};struct amdgpu_ring ring={.funcs=&funcs};
 const u64 addrs[]={0x10000ULL,0x12345678ULL,0x312345678ULL,0xffff12345678ULL};
 const unsigned sizes[]={1,8,1024,0xfffff};
 for(unsigned a=0;a<4;a++)for(unsigned s=0;s<4;s++)for(unsigned vm=0;vm<16;vm++)for(unsigned ce=0;ce<2;ce++){
 struct amdgpu_job job={vm};struct amdgpu_ib ib={ce,sizes[s],addrs[a],true};count=0;
 gfx_v8_0_ring_emit_ib_gfx(&ring,&job,&ib,0);assert(count==4);
 word(0,0xc0020000u|((ce?0x33u:0x3fu)<<8));word(1,(uint32_t)addrs[a]&~3u);word(2,(addrs[a]>>32)&0xffff);word(3,sizes[s]|(vm<<24));checks++;
 }
 for(unsigned a=0;a<4;a++)for(unsigned seq=1;seq<65;seq++)for(unsigned f=0;f<8;f++){
 u64 sequence=seq%4==0?0x100000000ULL:seq%4==1?0x12345678ffffffffULL:seq;
 unsigned flags=(f&1?1:0)|(f&2?2:0)|(f&4?8:0);count=0;
 gfx_v8_0_ring_emit_fence_gfx(&ring,addrs[a]&~7ULL,sequence,flags);assert(count==12);
 for(unsigned p=0;p<2;p++) {unsigned i=6*p;word(i,0xc0044700);word(i+1,0x00038514u|((p && (f&4))?0x10000000u:0));word(i+2,(uint32_t)addrs[a]&~7u);
 unsigned ds=p?((f&1)?2:1):1;unsigned intr=(p&&(f&2))?2:0;
 word(i+3,((addrs[a]>>32)&0xffff)|(ds<<29)|(intr<<24));word(i+4,(uint32_t)(sequence-1+p));word(i+5,(sequence-1+p)>>32);}
 checks++;
 }
 for(unsigned a=0;a<4;a++)for(unsigned seq=0;seq<64;seq++){ring.fence_drv.gpu_addr=addrs[a];ring.fence_drv.sync_seq=seq;count=0;gfx_v8_0_ring_emit_pipeline_sync(&ring);assert(count==7);
 word(0,0xc0053c00);word(1,0x113);word(2,(uint32_t)addrs[a]&~3u);word(3,addrs[a]>>32);word(4,seq);word(5,0xffffffff);word(6,4);checks++;}
 printf("PASS cases=%u: IB fields, EOP fields, pipeline wait fields and LE bytes\n",checks);return 0;}
'''
(w/'vid.h').write_bytes((src/'vid.h').read_bytes());(w/'check.c').write_text(prefix+functions+tests)
results={}
for arch in ('x86','spe'):
 gcc='gcc' if arch=='x86' else str(base/'tools/cxx-reference-002/bin/powerpc-linux-gnuspe-gcc')
 cmd=[gcc,'-O2',str(w/'check.c'),'-o',str(w/arch)]
 if arch=='spe':cmd[1:1]=['--sysroot='+str(base/'sysroot'),'-mcpu=8548','-mabi=spe','-mspe','-mfloat-gprs=double','-mlong-double-128']
 r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr[-2000:]
 run=[str(w/arch)] if arch=='x86' else ['qemu-ppc','-cpu','e500v2','-L','/home/owner/native-vertex-spe-20261109-001/root',str(w/arch)]
 r=subprocess.run(run,capture_output=True,text=True,timeout=20)
 results[arch]={'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr};assert not r.returncode,results[arch]
out={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'extracted_sha256':hashlib.sha256(functions.encode()).hexdigest(),'results':results,'limits':['actual three emitters, mocked numeric ring writer and non-SRIOV job','explicit byte serialization checker, not actual kernel ring helper','QEMU user execution on R730; no physical GPU, mappings, cache visibility, or initialization-state proof']}
(w/'result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
