"""R730-only actual-source fence, GART and Polaris interrupt byte contracts."""
from pathlib import Path
import subprocess,json,hashlib,os,resource
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
B=Path('/srv/data1/tabor-build/source-review');W=B/'interface-closure-20261108';W.mkdir(exist_ok=True)
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-004/source/drivers/gpu/drm/amd/amdgpu')
def function(file,name):
 t=(S/file).read_text();a=t.index(name);i=t.index('{',a)+1;depth=1
 while depth:depth+=(t[i]=='{')-(t[i]=='}');i+=1
 return t[a:i]
pre=(B/'shared-kernel-boundary-20261108/fixed-asic-clock.c').read_text().split('union get_clock_dividers')[0]
pre+=r'''
typedef unsigned long long uint64_t;typedef uint64_t u64;
#define __iomem
#define AMDGPU_IRQ_CLIENTID_LEGACY 0
struct amdgpu_device{int unused;};
struct amdgpu_fence_driver {u32*cpu_addr;u32 last_seq;};
struct amdgpu_ring{struct amdgpu_fence_driver fence_drv;};
#define atomic_read(p) (*(p))
/* Model Linux writeq's documented LE MMIO bytes, not native u64 assignment. */
static void writeq(u64 v,void*p){u8*b=p;for(unsigned i=0;i<8;i++)b[i]=v>>(i*8);}
struct amdgpu_ih_ring{u32 rptr;u32*ring;};
struct amdgpu_iv_entry{u32 client_id,src_id,src_data[4],ring_id,vmid,pasid;};
'''
names=[('amdgpu_fence.c','static void amdgpu_fence_write('),('amdgpu_fence.c','static u32 amdgpu_fence_read('),('amdgpu_gmc.c','int amdgpu_gmc_set_pte_pde('),('tonga_ih.c','static void tonga_ih_decode_iv(')]
code=pre+'\n'.join(function(*x)for x in names)+r'''
int main(void){
 u32 cell;struct amdgpu_ring ring={.fence_drv={&cell,0}};u8 table[128];u32 iv[64];struct amdgpu_ih_ring ih={0,iv};
 for(unsigned n=0;n<256;n++){
  u32 v=0x12345678u^(n*0x0103070bu);amdgpu_fence_write(&ring,v);
  for(unsigned i=0;i<4;i++)if(((u8*)&cell)[i]!=(u8)(v>>(8*i)))return 1;
  if(amdgpu_fence_read(&ring)!=v)return 2;emit((char*)&cell,4);
  ring.fence_drv.cpu_addr=0;ring.fence_drv.last_seq=v;if(amdgpu_fence_read(&ring)!=v)return 3;ring.fence_drv.cpu_addr=&cell;
  u64 addr=0x123456789abcULL+((u64)n<<24),flags=0x65;unsigned idx=n%16;
  for(unsigned i=0;i<128;i++)table[i]=0xa5;
  if(amdgpu_gmc_set_pte_pde(0,table,idx,addr,flags))return 4;
  u64 expected=(addr&0x0000FFFFFFFFF000ULL)|flags;
  for(unsigned i=0;i<128;i++)if(table[i]!=(i>=idx*8&&i<idx*8+8?(u8)(expected>>((i-idx*8)*8)):0xa5))return 5;
  emit((char*)table,128);
  unsigned start=(n%16)*4;u32 words[]={v,v^0xfedcba98,0x87654321^v,0x12345678};
  for(unsigned i=0;i<4;i++)put_unaligned_le32(words[i],iv+start+i);
  ih.rptr=start*4;struct amdgpu_iv_entry e={0};tonga_ih_decode_iv(0,&ih,&e);
  if(e.client_id!=AMDGPU_IRQ_CLIENTID_LEGACY||e.src_id!=(words[0]&255)||e.src_data[0]!=(words[1]&0xfffffff)||e.ring_id!=(words[2]&255)||e.vmid!=((words[2]>>8)&255)||e.pasid!=(words[2]>>16)||ih.rptr!=start*4+16)return 6;
  hex(e.src_id);hex(e.src_data[0]);hex(e.ring_id);hex(e.vmid);hex(e.pasid);hex(ih.rptr);
 }
 return 0;
}
'''
(W/'memory-contracts.c').write_text(code)
outputs={}
for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
 exe=W/('memory-'+arch);cmd=[cc]+(['-mstackrealign']if arch=='x86'else[])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static',str(W/'memory-contracts.c'),'-o',str(exe)]
 r=subprocess.run(cmd,capture_output=True);(W/(arch+'-compile.log')).write_bytes(r.stderr);r.check_returncode()
 r=subprocess.run(runner+[str(exe)],capture_output=True);r.check_returncode();outputs[arch]=r.stdout
assert outputs['x86']==outputs['ppc']
receipt=dict(status='PASS',actual_functions=[n for f,n in names],cases_per_architecture={'fence_memory':256,'fence_atomic_fallback':256,'pte_write_with_sentinels':256,'polaris_interrupt_decode':256},hardware_accessed=False,source_sha256=hashlib.sha256(code.encode()).hexdigest(),output_bytes=len(outputs['ppc']),output_sha256=hashlib.sha256(outputs['ppc']).hexdigest(),limitations=['Linux writeq is modeled using its LE contract, not executed against MMIO','No DMA, IRQ delivery, cache, PCIe or display execution','Does not test interrupt doorbell shadow pointer encoding'])
(W/'memory-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
