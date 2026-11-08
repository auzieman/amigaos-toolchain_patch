"""R730 standalone actual UVD encoder producers and simulated register endpoint."""
from pathlib import Path
import runpy,subprocess,json,hashlib,difflib
# Reuse extraction scaffolding and independently retained baseline checks.
b=runpy.run_path('/home/owner/standalone-gpu-codec-20261108/run.py')
S=b['S'];span=b['span'];u=b['u'];io=b['io'];functions=b['functions']
W=Path('/srv/data1/tabor-build/source-review/uvd-encoder-codec-20261108');W.mkdir(exist_ok=True)
ringpath='drivers/gpu/drm/amd/amdgpu/amdgpu_ring.c';old=(S/ringpath).read_text()
fixed=old.replace('ring->funcs->type == AMDGPU_RING_TYPE_COMPUTE);','ring->funcs->type == AMDGPU_RING_TYPE_COMPUTE ||\n\t\tring->funcs->type == AMDGPU_RING_TYPE_UVD_ENC);')
assert old!=fixed
patch=''.join(difflib.unified_diff(old.splitlines(True),fixed.splitlines(True),fromfile='a/'+ringpath,tofile='b/'+ringpath))
(W/'0023-polaris11-uvd-encoder-shared-le.patch').write_text(patch)
subprocess.run(['git','apply','--check',str(W/'0023-polaris11-uvd-encoder-shared-le.patch')],cwd=S,check=True)
pre=b['pre']
a=pre.index('struct amdgpu_device {');z=pre.index('#define unlikely') if '#define unlikely' in pre[a:] else -1
# Replace only simple scaffolding declarations, keeping freestanding helpers.
pre=pre.replace('struct funcs {u32 nop;int init_cond_exec;};','struct funcs {u32 nop;int init_cond_exec;unsigned type;};')
pre=pre.replace('struct amdgpu_device { unsigned usec_timeout; };','struct amdgpu_ring;struct inst {struct amdgpu_ring *ring_enc;};\nstruct amdgpu_device { unsigned usec_timeout;unsigned asic_type;struct {struct inst *inst;} uvd; };')
pre=pre.replace('static int software_le;\nstatic int amdgpu_ring_uses_sw_le(struct amdgpu_ring *r){(void)r;return software_le;}','')
pre+='''\nvoid *memset(void*p,int c,__SIZE_TYPE__ n){volatile unsigned char*b=p;for(__SIZE_TYPE__ i=0;i<n;i++)b[i]=c;return p;}
#define false 0
#define true 1
#define CHIP_POLARIS11 1
#define AMDGPU_RING_TYPE_GFX 0
#define AMDGPU_RING_TYPE_KIQ 1
#define AMDGPU_RING_TYPE_COMPUTE 2
#define AMDGPU_RING_TYPE_UVD 3
#define AMDGPU_RING_TYPE_UVD_ENC 4
#define AMDGPU_RING_TYPE_SDMA 5
#define upper_32_bits(x) ((u32)((u64)(x)>>32))
#define lower_32_bits(x) ((u32)(x))
#define AMDGPU_FENCE_FLAG_64BIT 1
#define AMDGPU_JOB_GET_VMID(job) ((job)->vmid)
struct amdgpu_job {unsigned vmid;};
struct amdgpu_ib {u64 gpu_addr;unsigned length_dw;u32 *ptr;};
#define ETIMEDOUT 110
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define __BIG_ENDIAN 4321
#endif
'''
vid=(S/'drivers/gpu/drm/amd/amdgpu/vid.h').read_text()
pre+='\n'.join(l for l in vid.splitlines() if l.startswith('#define HEVC_ENC_CMD_'))+'\n'
regs=(S/'drivers/gpu/drm/amd/include/asic_reg/uvd/uvd_6_0_d.h').read_text()
pre+='\n'.join(l for l in regs.splitlines() if any(l.startswith('#define '+n+' ') for n in ['mmUVD_RB_RPTR','mmUVD_RB_RPTR2','mmUVD_RB_WPTR','mmUVD_RB_WPTR2']))+'\n'
model=r'''
static u32 register_bytes[4],read_start;
static u32 le_device_load(u32 raw){return cpu_to_le32(raw);}
static u32 mock_read(unsigned reg) {unsigned i=reg==mmUVD_RB_RPTR?0:1;return le_device_load(register_bytes[i]);}
static void mock_write(unsigned reg,u32 value){unsigned i=reg==mmUVD_RB_WPTR?2:3;register_bytes[i]=cpu_to_le32(value);}
#define RREG32(reg) ((void)adev,mock_read(reg))
#define WREG32(reg,value) do {(void)adev;mock_write(reg,value);}while(0)
#define udelay(n) do {(void)(n);}while(0)
'''
get=span(u,'static uint64_t uvd_v6_0_enc_ring_get_rptr(').replace('uint64_t','u64')
setptr=span(u,'static void uvd_v6_0_enc_ring_set_wptr(')
model+=get+'\n'+setptr+r'''
static u32 amdgpu_ring_get_rptr(struct amdgpu_ring*r){return uvd_v6_0_enc_ring_get_rptr(r);}
static int amdgpu_ring_alloc(struct amdgpu_ring*r,int n){read_start=r->wptr;r->count_dw=n;return 0;}
static void amdgpu_ring_commit(struct amdgpu_ring*r) {
 u32 command=le_device_load(r->ring[read_start&r->buf_mask]);
 uvd_v6_0_enc_ring_set_wptr(r);
 if(command==HEVC_ENC_CMD_END) {
  unsigned i=r==&r->adev->uvd.inst->ring_enc[0]?0:1;
  register_bytes[i]=cpu_to_le32((u32)r->wptr);
 }
}
'''
producers='\n'.join(span(u,n) for n in ['static int uvd_v6_0_enc_ring_test_ring(','static void uvd_v6_0_enc_ring_insert_end(','static void uvd_v6_0_enc_ring_emit_fence(','static void uvd_v6_0_enc_ring_emit_ib('])
ringc=(S/ringpath).read_text();producers+='\n'+span(ringc,'void amdgpu_ring_insert_nop(')
main=r'''
int main(void) {
 u32 mem[2][64],shadow;struct funcs f={HEVC_ENC_CMD_NO_OP,1,AMDGPU_RING_TYPE_UVD_ENC};
 struct amdgpu_ring rings[2];struct inst inst={rings};struct amdgpu_device dev={4,CHIP_POLARIS11,{&inst}};
 for(unsigned ringid=0;ringid<2;ringid++) {
  struct amdgpu_ring*r=&rings[ringid];
  *r=(struct amdgpu_ring){.adev=&dev,.ring=mem[ringid],.cond_exe_cpu_addr=&shadow,.funcs=&f,.ptr_mask=0xffffffff,.buf_mask=63,.ring_size=256};
  for(unsigned start=0;start<64;start++) {
   r->wptr=start;register_bytes[ringid]=cpu_to_le32(start);
   amdgpu_ring_clear_ring(r);
   int result=uvd_v6_0_enc_ring_test_ring(r);
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
   int expected=FIXED?0:-ETIMEDOUT;
#else
   int expected=0;
#endif
   if(result!=expected)return 1;
   hex(ringid);hex(start);hex(result);hex(le_device_load(mem[ringid][start]));hex(amdgpu_ring_get_rptr(r));emit("\n",1);
  }
  if(FIXED || __BYTE_ORDER__ != __ORDER_BIG_ENDIAN__) {
   r->wptr=61;r->count_dw=32;
   struct amdgpu_job job={7};struct amdgpu_ib ib={0x000000ff12345678ULL,37,0};
   uvd_v6_0_enc_ring_emit_ib(r,&job,&ib,0);
   uvd_v6_0_enc_ring_emit_fence(r,0x000000ff87654320ULL,0x12345678,0);
   uvd_v6_0_enc_ring_insert_end(r);amdgpu_ring_insert_nop(r,3);
   u32 expected[]={HEVC_ENC_CMD_IB_VM,7,0x12345678,0xff,37,HEVC_ENC_CMD_FENCE,0x87654320,0xff,0x12345678,HEVC_ENC_CMD_TRAP,HEVC_ENC_CMD_END,0,0,0};
   for(unsigned i=0;i<14;i++)if(le_device_load(r->ring[(61+i)&63])!=expected[i])return 2;
  }
 }
 /* Predicate isolates this encoder: decoder/SDMA and other ASICs unchanged. */
 f.type=AMDGPU_RING_TYPE_UVD;if(amdgpu_ring_uses_sw_le(&rings[0]))return 3;
 f.type=AMDGPU_RING_TYPE_SDMA;if(amdgpu_ring_uses_sw_le(&rings[0]))return 4;
 f.type=AMDGPU_RING_TYPE_UVD_ENC;dev.asic_type=999;if(amdgpu_ring_uses_sw_le(&rings[0]))return 5;
 return failed?6:0;
}
'''
result={'gpu_accessed':False,'hardware_tested':False,'patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),'scenarios_per_version_arch':128,'ring_instances':2,'raw_packet_expected_dwords':14,'model_assumption':'Encoder firmware fetches LE words with no hardware swap. Not established on physical GPU.','results':{}}
for ver,text in [('old',old),('fixed',fixed)]:
 policy=span(text,'bool amdgpu_ring_uses_sw_le(').replace('bool amdgpu_ring_uses_sw_le','static bool amdgpu_ring_uses_sw_le')
 code=u[:u.index('#include')]+pre+policy+'\n'+'\n'.join(functions)+'\nint main(void);\n'+io+model+producers+'\n#define FIXED '+str(int(ver=='fixed'))+'\n'+main
 name=ver+'-encoder';(W/(name+'.c')).write_text(code)
 for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
  exe=W/(name+'-'+arch)
  cmd=[cc]+(['-mstackrealign'] if arch=='x86' else [])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static','-Wall','-Wextra','-Wno-unused-function','-Wno-unused-parameter',str(W/(name+'.c')),'-o',str(exe)]
  c=subprocess.run(cmd,capture_output=True,text=True);(W/(name+'-'+arch+'-compile.log')).write_text(c.stderr)
  if c.returncode:raise RuntimeError(c.stderr)
  c=subprocess.run(runner+[str(exe)],capture_output=True);(W/(name+'-'+arch+'.log')).write_bytes(c.stdout);c.check_returncode()
  result['results'][ver+'-'+arch]={'status':'PASS','sha256':hashlib.sha256(exe.read_bytes()).hexdigest()}
assert (W/'old-encoder-x86.log').read_bytes()==(W/'fixed-encoder-x86.log').read_bytes()==(W/'fixed-encoder-ppc.log').read_bytes()
assert (W/'old-encoder-ppc.log').read_bytes()!=(W/'old-encoder-x86.log').read_bytes()
result.update(status='PASS',fixed_ppc_matches_unchanged_x86=True)
(W/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
