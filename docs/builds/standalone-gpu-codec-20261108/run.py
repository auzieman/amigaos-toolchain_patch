"""R730-only standalone actual-driver extraction and simulated GPU consumer."""
from pathlib import Path
import subprocess,json,hashlib
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-002/source')
W=Path('/srv/data1/tabor-build/source-review/standalone-gpu-codec-20261108');W.mkdir(exist_ok=True)
I=Path('/home/owner/standalone-gpu-codec-20261108')
def span(s,start):
 a=s.index(start);i=s.index('{',a)+1;depth=1
 while depth:
  depth+=(s[i]=='{')-(s[i]=='}');i+=1
 return s[a:i]
h=(S/'drivers/gpu/drm/amd/amdgpu/amdgpu_ring.h').read_text()
u=(S/'drivers/gpu/drm/amd/amdgpu/uvd_v6_0.c').read_text()
template=(I/'ring-fixture-template.c').read_text()
# Keep scaffolding only; functions are extracted afresh from the candidate.
pre=template[:template.index('static inline u32 amdgpu_ring_encode_dw')]
pre=pre.replace('struct amdgpu_ring {','struct amdgpu_device { unsigned usec_timeout; };\nstruct amdgpu_ring {struct amdgpu_device *adev;')
pre=pre.replace('static int amdgpu_ring_uses_sw_le(struct amdgpu_ring *r){return 1;}','static int software_le;\nstatic int amdgpu_ring_uses_sw_le(struct amdgpu_ring *r){(void)r;return software_le;}')
pre=pre.replace('unsigned long n','__SIZE_TYPE__ n')
functions=[]
for name,signature in [('encode','static inline u32 amdgpu_ring_encode_dw('),('condition','static inline void amdgpu_ring_set_preempt_cond_exec('),('clear','static inline void amdgpu_ring_clear_ring('),('write','static inline void amdgpu_ring_write('),('bulk','static inline void amdgpu_ring_write_multiple('),('distance','static inline unsigned int amdgpu_ring_get_dw_distance('),('patch','static inline void amdgpu_ring_patch_cond_exec(')]:
 functions.append(span(h,signature))
uvdfunc=span(u,'static int uvd_v6_0_ring_test_ring(')
base=(Path('/srv/data1/tabor-build/source-review/shared-kernel-boundary-20261108/fixed-asic-clock.c')).read_text()
io=base[base.index('static void emit('):base.index('union get_clock_dividers')]
# Actual register and packet definitions, retaining their upstream values.
regs=(S/'drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_6_0_d.h').read_text()
reg=next(l for l in regs.splitlines() if l.startswith('#define mmUVD_CONTEXT_ID '))
sid=(S/'drivers/gpu/drm/amd/amdgpu/sid.h').read_text();a=sid.index('#define PACKET0(');b=sid.index('\n#define',a)
packet=sid[a:b]
model=r'''
#define ETIMEDOUT 110
#define PACKET_TYPE0 0
static u32 context,read_start;static int hardware_swap;
static u32 device_word(u32 raw) {
 u32 value=cpu_to_le32(raw); /* LE device load of native memory bytes */
 return hardware_swap?__builtin_bswap32(value):value;
}
#define WREG32(reg,value) do {(void)(reg);context=(value);}while(0)
#define RREG32(reg) ((void)(reg),context)
#define udelay(n) do {(void)(n);}while(0)
static int amdgpu_ring_alloc(struct amdgpu_ring*r,int n){r->count_dw=n;read_start=r->wptr;return 0;}
static void amdgpu_ring_commit(struct amdgpu_ring*r) {
 u32 header=device_word(r->ring[read_start&r->buf_mask]);
 if(header==PACKET0(mmUVD_CONTEXT_ID,0))
  context=device_word(r->ring[(read_start+1)&r->buf_mask]);
}
'''
main=r'''
int main(void) {
 u32 memory[8],shadow;struct funcs f={0x80000000,1};
 struct amdgpu_device dev={4};
 struct amdgpu_ring r={.adev=&dev,.ring=memory,.cond_exe_cpu_addr=&shadow,.funcs=&f,.ptr_mask=0xffffffff,.buf_mask=7,.ring_size=32};
 unsigned cases=0;
 for(unsigned mode=0;mode<4;mode++)for(unsigned start=0;start<8;start++) {
  software_le=(mode==1||mode==3);
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
  hardware_swap=(mode==0||mode==3);
  int expected=mode<2?0:-ETIMEDOUT;
#else
  hardware_swap=0;int expected=0;
#endif
  r.wptr=start;amdgpu_ring_clear_ring(&r);
  int result=uvd_v6_0_ring_test_ring(&r);
  hex(mode);hex(start);hex(result);hex(context);emit("\n",1);
  if(result!=expected)return 1;
  cases++;
 }
 /* Exercise actual bulk, wrap, conditional patch and shadow writers. */
 software_le=1;r.wptr=6;r.count_dw=32;
 amdgpu_ring_clear_ring(&r);
 u32 words[]={0xc0017900,0x40,0xdeadbeef};
 amdgpu_ring_write_multiple(&r,words,3);
 r.wptr=2;amdgpu_ring_write(&r,0);amdgpu_ring_write(&r,0x12345678);
 amdgpu_ring_patch_cond_exec(&r,2);amdgpu_ring_set_preempt_cond_exec(&r,1);
 if(cpu_to_le32(memory[6])!=words[0]||cpu_to_le32(memory[7])!=words[1]||cpu_to_le32(memory[0])!=words[2]||cpu_to_le32(memory[2])!=1||cpu_to_le32(shadow)!=1||failed)return 2;
 return cases==32?0:3;
}
'''
code=pre+'\n'.join(functions)+'\nint main(void);\n'+io+reg+'\n'+packet+'\n'+model+uvdfunc+main
(W/'standalone-codec.c').write_text(code)
r={'source':str(S),'gpu_accessed':False,'module_loaded':False,'mocked':['MMIO context register','ring allocation/commit','device fetch and hardware swap'],'actual_driver_functions':8,'cases_per_architecture':32,'additional_bulk_wrap_condition_checks':True,'source_sha256':hashlib.sha256(code.encode()).hexdigest(),'architectures':{}}
for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
 exe=W/('standalone-codec-'+arch)
 cmd=[cc]+(['-mstackrealign'] if arch=='x86' else [])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static','-Wall','-Wextra','-Wno-unused-parameter',str(W/'standalone-codec.c'),'-o',str(exe)]
 c=subprocess.run(cmd,capture_output=True,text=True);(W/('compile-'+arch+'.log')).write_text(c.stderr);c.check_returncode()
 c=subprocess.run(runner+[str(exe)],capture_output=True);(W/(arch+'.log')).write_bytes(c.stdout);c.check_returncode()
 r['architectures'][arch]={'status':'PASS','executable_sha256':hashlib.sha256(exe.read_bytes()).hexdigest()}
r['status']='PASS';r['limits']='Simulated consumer validates byte contracts, not actual GPU swap behavior, PCIe, DMA or timing.'
(W/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
