"""R730: actual UVD encoder create/destroy IB producers and explicit fetch hypotheses."""
from pathlib import Path
import subprocess,json,hashlib,os,resource
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
B=Path('/srv/data1/tabor-build/source-review');W=B/'interface-closure-20261108';W.mkdir(exist_ok=True)
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-004/source/drivers/gpu/drm/amd/amdgpu');t=(S/'uvd_v6_0.c').read_text()
def span(name):
 a=t.index(name);i=t.index('{',a)+1;d=1
 while d:d+=(t[i]=='{')-(t[i]=='}');i+=1
 return t[a:i]
pre=(B/'shared-kernel-boundary-20261108/fixed-asic-clock.c').read_text().split('union get_clock_dividers')[0]
pre+=r'''
typedef unsigned long long uint64_t;typedef uint64_t u64;
#define NULL ((void*)0)
#define AMDGPU_IB_POOL_DIRECT 0
#define AMDGPU_KERNEL_JOB_ID_VCN_RING_TEST 0
#define upper_32_bits(x) ((u32)((u64)(x)>>32))
struct dma_fence {int refs;};struct amdgpu_device{int unused;};struct amdgpu_ring{struct amdgpu_device*adev;};
struct amdgpu_bo {u64 addr;};struct amdgpu_ib{u32*ptr;unsigned length_dw;};struct amdgpu_job{struct amdgpu_ib ibs[1];};
static struct amdgpu_job saved;static u32 storage[16];static struct dma_fence completion;static int alloc_fail,submit_fail,submitted,freed;static u32 expected_handle;static u64 expected_addr;static int operation;static unsigned matched_le,matched_swap;
static int amdgpu_job_alloc_with_ib(struct amdgpu_device*a,void*b,void*c,unsigned bytes,int pool,struct amdgpu_job**job,int id){(void)a;(void)b;(void)c;(void)pool;(void)id;if(alloc_fail)return -12;if(bytes!=64)return -22;for(unsigned i=0;i<16;i++)storage[i]=0xa5a5a5a5;saved.ibs[0]=(struct amdgpu_ib){storage,0};*job=&saved;return 0;}
static u64 amdgpu_bo_gpu_offset(struct amdgpu_bo*b){return b->addr;}
static struct dma_fence*dma_fence_get(struct dma_fence*f){f->refs++;return f;}
static void dma_fence_put(struct dma_fence*f){f->refs--;}
static void amdgpu_job_free(struct amdgpu_job*j){(void)j;freed++;}
static int amdgpu_job_submit_direct(struct amdgpu_job*j,struct amdgpu_ring*r,struct dma_fence**f){
 (void)r;submitted++;if(submit_fail)return -5;
 u32 words[]={0x18,1,expected_handle,0x10000,upper_32_bits(expected_addr),(u32)expected_addr,0x14,2,0x1c,1,0,8,(u32)operation,0,0,0};
 if(j->ibs[0].length_dw!=13)return -22;
 bool le=true,swap=true;
 for(unsigned i=0;i<16;i++){
  u8*b=(u8*)(storage+i);u32 l=(u32)b[0]|((u32)b[1]<<8)|((u32)b[2]<<16)|((u32)b[3]<<24);
  u32 s=(u32)b[3]|((u32)b[2]<<8)|((u32)b[1]<<16)|((u32)b[0]<<24);
  if(l!=words[i])le=false;if(s!=words[i])swap=false;
  /* Emit native semantics in normalized format; raw bytes are compared separately. */
  hex(storage[i]);
 }
 matched_le+=le;matched_swap+=swap;completion.refs=1;*f=&completion;return 0;
}
'''
code=pre+span('static int uvd_v6_0_enc_get_create_msg(')+span('static int uvd_v6_0_enc_get_destroy_msg(')+r'''
int main(void){
 struct amdgpu_device dev={0};struct amdgpu_ring ring={&dev};struct amdgpu_bo bo;unsigned cases=0;
 for(unsigned op=0;op<2;op++)for(unsigned n=0;n<64;n++)for(unsigned fault=0;fault<3;fault++)for(unsigned want=0;want<2;want++){
  alloc_fail=fault==1;submit_fail=fault==2;submitted=freed=0;expected_handle=0x12345678^(n*0x0103070b);expected_addr=0x123456789abcULL+((u64)n<<24);bo.addr=expected_addr;operation=0x08000001+op;
  struct dma_fence*out=0;int ret=op?uvd_v6_0_enc_get_destroy_msg(&ring,expected_handle,&bo,want?&out:0):uvd_v6_0_enc_get_create_msg(&ring,expected_handle,&bo,want?&out:0);
  if(ret!=(alloc_fail?-12:submit_fail?-5:0))return 1;
  if(submitted!=(alloc_fail?0:1)||freed!=(submit_fail?1:0))return 2;
  if(!fault){if(completion.refs!=(want?1:0)||!!out!=!!want)return 3;cases++;}
 }
 if(cases!=256)return 4;
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
 if(matched_le||matched_swap!=256)return 5;
#else
 if(matched_le!=256||matched_swap)return 6;
#endif
 return 0;
}
'''
(W/'uvd-ib-producers.c').write_text(code);outputs={}
for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
 exe=W/('uvd-ib-'+arch);cmd=[cc]+(['-mstackrealign']if arch=='x86'else[])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static',str(W/'uvd-ib-producers.c'),'-o',str(exe)]
 r=subprocess.run(cmd,capture_output=True);(W/('uvd-'+arch+'-compile.log')).write_bytes(r.stderr);r.check_returncode();r=subprocess.run(runner+[str(exe)],capture_output=True);r.check_returncode();outputs[arch]=r.stdout
assert outputs['x86']==outputs['ppc']
r=dict(status='PASS',actual_producer_functions=2,scenarios_per_architecture=768,successful_payloads_per_architecture=256,hardware_accessed=False,deployment_allowed=False,source_sha256=hashlib.sha256(code.encode()).hexdigest(),native_semantics_match=True,consumer_hypotheses={'x86':'LE fetch matches; byte-swapped fetch does not','PPC_BE':'byte-swapped fetch matches; LE fetch does not'},hardware_fetch_contract='UNRESOLVED for encoder IB; ring test does not prove this contract',limits=['Job/fence allocation and submission mocked','Actual encoder firmware fetch and LMI swap routing not observed','No payload conversion patch inferred from a mocked endpoint'])
(W/'uvd-payload-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
