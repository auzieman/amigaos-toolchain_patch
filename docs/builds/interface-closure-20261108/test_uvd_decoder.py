"""R730-only actual UVD decoder message producers and resume firmware transfers."""
from pathlib import Path
import subprocess,json,hashlib,os,resource
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
B=Path('/srv/data1/tabor-build/source-review');W=B/'interface-closure-20261108';W.mkdir(exist_ok=True)
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-004/source/drivers/gpu/drm/amd/amdgpu');t=(S/'amdgpu_uvd.c').read_text()
def span(name):
 a=t.index(name);i=t.index('{',a)+1;d=1
 while d:d+=(t[i]=='{')-(t[i]=='}');i+=1
 return t[a:i]
pre=(B/'shared-kernel-boundary-20261108/fixed-asic-clock.c').read_text().split('union get_clock_dividers')[0]
pre+=r'''
#define NULL ((void*)0)
#define AMDGPU_FW_LOAD_PSP 1
struct dma_fence{int unused;};struct amdgpu_bo{u8 bytes[4096];unsigned size;};
struct amdgpu_device;struct amdgpu_ring{struct amdgpu_device*adev;struct{bool initialized;}fence_drv;};
struct common_firmware_header{u32 ucode_array_offset_bytes,ucode_size_bytes;};
struct firmware{const u8*data;};
struct instance{struct amdgpu_bo*vcpu_bo;void*cpu_addr,*saved_bo;struct amdgpu_ring ring;};
struct amdgpu_device{struct{struct amdgpu_bo*ib_bo;unsigned num_uvd_inst,harvest_config;struct instance inst[2];struct firmware*fw;}uvd;struct{unsigned load_type;}firmware;};
static struct amdgpu_bo temp;static int alloc_fail,send_error,send_count,free_count,restore_free,force_count;static bool expect_destroy,expect_direct;static u32 expect_handle;
static void*amdgpu_bo_kptr(struct amdgpu_bo*b){return b->bytes;}
static int amdgpu_uvd_create_msg_bo_helper(struct amdgpu_device*a,unsigned size,struct amdgpu_bo**b){(void)a;if(alloc_fail)return -12;temp.size=size;*b=&temp;return 0;}
static void amdgpu_bo_free_kernel(struct amdgpu_bo**b,void*p,void**v){(void)p;*b=0;*v=0;free_count++;}
static int amdgpu_uvd_send_msg(struct amdgpu_ring*r,struct amdgpu_bo*b,bool direct,struct dma_fence**f){(void)r;(void)f;send_count++;if(direct!=expect_direct)return -22;
 for(unsigned i=0;i<1024;i++){
  u32 want=0;if(i==0)want=0xde4;if(i==1)want=expect_destroy?2:0;if(i==2)want=expect_handle;
  if(!expect_destroy){if(i==7)want=0x780;if(i==8)want=0x440;if(i==10)want=0x1b37000;}
  if(get_unaligned_le32(b->bytes+i*4)!=want)return -22;
 }
 emit((char*)b->bytes,4096);return send_error;
}
static unsigned amdgpu_bo_size(struct amdgpu_bo*b){return b->size;}
#define adev_to_drm(a) (a)
static bool drm_dev_enter(struct amdgpu_device*a,int*i){(void)a;*i=0;return true;}
static void drm_dev_exit(int i){(void)i;}
static void memcpy_toio(void*d,const void*s,unsigned n){u8*a=d;const u8*b=s;for(unsigned i=0;i<n;i++)a[i]=b[i];}
static void memset_io(void*d,int v,unsigned n){u8*a=d;for(unsigned i=0;i<n;i++)a[i]=v;}
static void kvfree(void*p){(void)p;restore_free++;}
static void amdgpu_fence_driver_force_completion(struct amdgpu_ring*r,void*p){(void)r;(void)p;force_count++;}
'''
code=pre+span('int amdgpu_uvd_get_create_msg(')+span('int amdgpu_uvd_get_destroy_msg(')+span('int amdgpu_uvd_resume(')+r'''
int main(void){
 struct amdgpu_bo bo={.size=4096};struct amdgpu_device dev={0};dev.uvd.ib_bo=&bo;struct amdgpu_ring ring={.adev=&dev};unsigned messages=0;
 for(unsigned op=0;op<3;op++)for(unsigned n=0;n<32;n++)for(unsigned fault=0;fault<3;fault++){
  expect_destroy=op!=0;expect_direct=op!=2;expect_handle=0x12345678^(n*0x0103070b);alloc_fail=fault==1;send_error=fault==2?-5:0;send_count=free_count=0;
  int ret=op?amdgpu_uvd_get_destroy_msg(&ring,expect_handle,expect_direct,0):amdgpu_uvd_get_create_msg(&ring,expect_handle,0);
  bool blocked=op==2&&alloc_fail;if(ret!=(blocked?-12:send_error)||send_count!=(blocked?0:1)||free_count!=(op==2&&!blocked?1:0))return 1;messages++;
 }
 u8 firmware_bytes[128],saved[128];for(unsigned i=0;i<128;i++){firmware_bytes[i]=(i*73+19)&255;saved[i]=(i*31+7)&255;}
 struct common_firmware_header*hdr=(void*)firmware_bytes;hdr->ucode_array_offset_bytes=cpu_to_le32(32);hdr->ucode_size_bytes=cpu_to_le32(64);struct firmware fw={firmware_bytes};dev.uvd.fw=&fw;dev.uvd.num_uvd_inst=1;dev.uvd.inst[0].vcpu_bo=&bo;dev.uvd.inst[0].cpu_addr=bo.bytes;bo.size=128;dev.uvd.inst[0].ring.fence_drv.initialized=true;
 for(unsigned mode=0;mode<3;mode++){
  for(unsigned i=0;i<128;i++)bo.bytes[i]=0xa5;restore_free=force_count=0;
  dev.uvd.inst[0].saved_bo=mode==1?saved:0;dev.firmware.load_type=mode==2?AMDGPU_FW_LOAD_PSP:0;
  if(amdgpu_uvd_resume(&dev))return 2;
  for(unsigned i=0;i<128;i++){u8 want=mode==1?saved[i]:mode==2?0:i<64?firmware_bytes[32+i]:0;if(bo.bytes[i]!=want)return 3;}
  if(restore_free!=(mode==1)||force_count!=(mode!=1)||dev.uvd.inst[0].saved_bo)return 4;
  emit((char*)bo.bytes,128);
 }
 dev.uvd.inst[0].vcpu_bo=0;if(amdgpu_uvd_resume(&dev)!=-EINVAL)return 5;
 dev.uvd.harvest_config=1;if(amdgpu_uvd_resume(&dev))return 6;
 return messages==288?0:7;
}
'''
(W/'uvd-decoder.c').write_text(code);outputs={}
for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
 exe=W/('uvd-decoder-'+arch);cmd=[cc]+(['-mstackrealign']if arch=='x86'else[])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static',str(W/'uvd-decoder.c'),'-o',str(exe)]
 r=subprocess.run(cmd,capture_output=True);(W/('decoder-'+arch+'-compile.log')).write_bytes(r.stderr);r.check_returncode();r=subprocess.run(runner+[str(exe)],capture_output=True);r.check_returncode();outputs[arch]=r.stdout
assert outputs['x86']==outputs['ppc']
r=dict(status='PASS',actual_functions=3,message_scenarios_per_architecture=288,firmware_resume_scenarios_per_architecture=5,output_bytes=len(outputs['ppc']),source_sha256=hashlib.sha256(code.encode()).hexdigest(),output_sha256=hashlib.sha256(outputs['ppc']).hexdigest(),hardware_accessed=False,limitations=['Allocation, submission, drm_dev_enter and IO copies mocked','Synthetic valid firmware header and payload; full upstream header validation not exercised','No hardware VCPU execution, IB decode, fence completion or video playback'])
(W/'uvd-decoder-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
