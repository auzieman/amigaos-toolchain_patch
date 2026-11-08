"""R730: actual display ATOM clock/timing buffer contracts on x86/PPC32 BE."""
from pathlib import Path
import subprocess,json,hashlib,os,resource
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
B=Path('/srv/data1/tabor-build/source-review');W=B/'console-selected-path-20261108';W.mkdir(exist_ok=True)
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-006/source');A=S/'drivers/gpu/drm/amd/amdgpu';t=(A/'atombios_crtc.c').read_text()
def span(key):
 a=t.index(key);i=t.index('{',a)+1;d=1
 while d:d+=(t[i]=='{')-(t[i]=='}');i+=1
 return t[a:i]
pre=(B/'shared-kernel-boundary-20261108/fixed-asic-clock.c').read_text().split('union get_clock_dividers')[0]
pre+=r'''
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define cpu_to_le16(v) __builtin_bswap16(v)
#else
#define cpu_to_le16(v) (v)
#endif
#define DRM_ERROR(...) do{}while(0)
#define ENCODER_MODE_IS_DP(mode) ((mode)==ATOM_ENCODER_MODE_DP)
struct atom_context{int unused;};struct amdgpu_device{struct{struct atom_context*atom_context;}mode_info;};
struct drm_device{struct amdgpu_device*adev;};struct drm_crtc{struct drm_device*dev;};
struct amdgpu_crtc{struct drm_crtc base;u32 h_border,v_border,crtc_id;};
#define to_amdgpu_crtc(c) ((struct amdgpu_crtc*)(c))
#define drm_to_adev(d) ((d)->adev)
struct drm_display_mode{u32 crtc_hdisplay,crtc_hblank_end,crtc_vdisplay,crtc_vblank_end,crtc_hsync_start,crtc_hsync_end,crtc_vsync_start,crtc_vsync_end,flags;};
struct amdgpu_atom_ss{u32 type;};
static u8 frev=1,crev=7;static bool header_valid=true;static unsigned calls;static int last_index,last_size;static u8 captured[512];
static bool amdgpu_atom_parse_cmd_header(struct atom_context*c,int i,u8*f,u8*r){(void)c;(void)i;*f=frev;*r=crev;return header_valid;}
static int amdgpu_atom_execute_table(struct atom_context*c,int i,u32*args,int size){(void)c;last_index=i;last_size=size;calls++;memcpy(captured,args,size);return 0;}
'''
flags=(S/'include/uapi/drm/drm_mode.h').read_text().splitlines()
for k in ['NVSYNC','NHSYNC','CSYNC','INTERLACE','DBLSCAN']:pre+=next(l for l in flags if l.startswith('#define DRM_MODE_FLAG_'+k+'\t')or l.startswith('#define DRM_MODE_FLAG_'+k+' '))+'\n'
code=pre+span('union set_pixel_clock {')+';\n'+span('union set_dce_clock {')+';\n'+span('static bool is_pixel_clock_source_from_pll(')+'\n'+span('void amdgpu_atombios_crtc_program_pll(')+'\n'+span('u32 amdgpu_atombios_crtc_set_dce_clock(')+'\n'+span('void amdgpu_atombios_crtc_set_dtd_timing(')
code+=r'''
int main(void){struct amdgpu_device a={0};struct drm_device d={&a};struct amdgpu_crtc c={{&d},0,0,1};struct amdgpu_atom_ss ss={0};unsigned cases=0;
 u8 revisions[]={1,2,3,5,6,7};u32 clocks[]={25175,74250,148500,297000};int bpcs[]={8,10,12,16};u32 encoders[]={ATOM_ENCODER_MODE_HDMI,ATOM_ENCODER_MODE_DVI,ATOM_ENCODER_MODE_DP};
 for(unsigned v=0;v<6;v++)for(unsigned b=0;b<4;b++)for(unsigned e=0;e<3;e++)for(unsigned f=0;f<4;f++){
  frev=1;crev=revisions[v];calls=0;amdgpu_atombios_crtc_program_pll(&c.base,1,0,encoders[e],3,clocks[f],2,123,5,4,bpcs[b],false,&ss);
  if(calls!=1||last_index!=GetIndexIntoMasterTable(COMMAND,SetPixelClock))return 1;
  union set_pixel_clock*p=(void*)captured;
  if(crev==7){if(get_unaligned_le32(&p->v7.ulPixelClock)!=clocks[f]*10||p->v7.ucCRTC!=1||p->v7.ucTransmitterID!=3||p->v7.ucEncoderMode!=encoders[e])return 2;}
  else if(crev==6){if(get_unaligned_le32(&p->v6.ulDispEngClkFreq)!=((1u<<24)|clocks[f]/10)||get_unaligned_le32(&p->v6.ulFbDivDecFrac)!=500000)return 3;}
  else {u16 raw=crev==5?p->v5.usPixelClock:crev==3?p->v3.usPixelClock:crev==2?p->v2.usPixelClock:p->v1.usPixelClock;if(le16_to_cpu(raw)!=clocks[f]/10)return 4;}
  emit((char*)captured,last_size);cases++;
 }
 frev=2;crev=1;for(unsigned i=0;i<4;i++)for(unsigned type=0;type<2;type++){
  calls=0;u32 ret=amdgpu_atombios_crtc_set_dce_clock(&a,clocks[i],type,1);union set_dce_clock*p=(void*)captured;
  if(calls!=1||get_unaligned_le32(&p->v2_1.asParam.ulDCEClkFreq)!=clocks[i]||p->v2_1.asParam.ucDCEClkType!=type||ret!=clocks[i]*10)return 5;
  emit((char*)captured,last_size);cases++;
 }
 for(unsigned border=0;border<3;border++)for(unsigned bits=0;bits<32;bits++){
  c.h_border=border;c.v_border=border;
  struct drm_display_mode m={1920,2200,1080,1125,2008,2052,1084,1089,0};
  u32 flags[]={DRM_MODE_FLAG_NVSYNC,DRM_MODE_FLAG_NHSYNC,DRM_MODE_FLAG_CSYNC,DRM_MODE_FLAG_INTERLACE,DRM_MODE_FLAG_DBLSCAN};for(unsigned i=0;i<5;i++)if(bits&(1u<<i))m.flags|=flags[i];
  calls=0;amdgpu_atombios_crtc_set_dtd_timing(&c.base,&m);SET_CRTC_USING_DTD_TIMING_PARAMETERS*p=(void*)captured;
  if(calls!=1||le16_to_cpu(p->usH_Size)!=1920-2*border||le16_to_cpu(p->usV_Size)!=1080-2*border||le16_to_cpu(p->usH_Blanking_Time)!=280+2*border||le16_to_cpu(p->usV_Blanking_Time)!=45+2*border||le16_to_cpu(p->usH_SyncOffset)!=88+border||le16_to_cpu(p->usH_SyncWidth)!=44||le16_to_cpu(p->usV_SyncOffset)!=4+border||le16_to_cpu(p->usV_SyncWidth)!=5||p->ucCRTC!=1)return 6;
  emit((char*)captured,last_size);cases++;
 }
 header_valid=false;calls=0;amdgpu_atombios_crtc_program_pll(&c.base,1,0,encoders[0],3,148500,0,0,0,0,8,false,&ss);if(calls)return 7;if(amdgpu_atombios_crtc_set_dce_clock(&a,60000,0,1)||calls)return 8;
 return cases==392?0:9;}
'''
(W/'atom-display.c').write_text(code);outputs={}
for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
 exe=W/('atom-display-'+arch);cmd=[cc]+(['-mstackrealign']if arch=='x86'else[])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static',str(W/'atom-display.c'),'-o',str(exe)]
 r=subprocess.run(cmd,capture_output=True);(W/('atom-'+arch+'-compile.log')).write_bytes(r.stderr)
 if r.returncode:print(r.stderr.decode()[-4000:]);r.check_returncode()
 r=subprocess.run(runner+[str(exe)],capture_output=True);r.check_returncode();outputs[arch]=r.stdout
assert outputs['x86']==outputs['ppc']
r=dict(status='PASS',actual_functions=4,scenarios_per_architecture=392,invalid_header_checks_per_architecture=2,source_sha256=hashlib.sha256(code.encode()).hexdigest(),output_sha256=hashlib.sha256(outputs['ppc']).hexdigest(),output_bytes=len(outputs['ppc']),hardware_accessed=False,limits=['ATOM endpoint records requests and echoes DCE clock field; no PLL programming performed','Firmware table revisions exercised synthetically; current raw VBIOS revision not captured','Only selected buffer fields independently decoded; all emitted request bytes compared','No EDID/link/scanout acceptance'])
(W/'atom-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
