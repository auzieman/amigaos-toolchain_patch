"""R730: actual selected DCE11 mode-set caller and surface function, including errors."""
from pathlib import Path
import subprocess,json,difflib,hashlib,os,resource
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
B=Path('/srv/data1/tabor-build/source-review');W=B/'console-selected-path-20261108';S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-006/source');rel='drivers/gpu/drm/amd/amdgpu/dce_v11_0.c';t=(S/rel).read_text()
def span(key):
 a=t.index(key);i=t.index('{',a)+1;d=1
 while d:d+=(t[i]=='{')-(t[i]=='}');i+=1
 return t[a:i]
old=span('static int dce_v11_0_crtc_mode_set(')
new=old.replace('\tstruct amdgpu_device *adev = drm_to_adev(dev);','\tstruct amdgpu_device *adev = drm_to_adev(dev);\n\tint ret;').replace('\tdce_v11_0_crtc_do_set_base(crtc, old_fb, x, y, 0);','\tret = dce_v11_0_crtc_do_set_base(crtc, old_fb, x, y, 0);\n\tif (ret)\n\t\treturn ret;')
assert old!=new
fixed=t.replace(old,new);patch=''.join(difflib.unified_diff(t.splitlines(True),fixed.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel));(W/'0027-dce11-propagate-surface-programming-failure.patch').write_text(patch);subprocess.run(['git','apply','--check',str(W/'0027-dce11-propagate-surface-programming-failure.patch')],cwd=S,check=True)
pre=(W/'console-path.c').read_text().split('static int dce_v11_0_crtc_do_set_base(')[0]
pre=pre.replace('struct amdgpu_device {int unused;};','struct amdgpu_device {int unused;u32 asic_type;};')
pre=pre.replace('struct drm_crtc{','struct drm_display_mode{unsigned hdisplay,vdisplay,clock;};\nstruct amdgpu_encoder{unsigned encoder_id;};\nstruct amdgpu_atom_ss{u32 type;};\nstruct drm_crtc{').replace('struct{unsigned hdisplay,vdisplay;}mode;','struct drm_display_mode mode;')
pre=pre.replace('struct amdgpu_crtc{struct drm_crtc base;unsigned crtc_offset;};','struct amdgpu_crtc{struct drm_crtc base;unsigned crtc_offset,adjusted_clock,crtc_id,pll_id,bpc;bool ss_enabled;struct amdgpu_atom_ss ss;struct amdgpu_encoder*encoder;struct drm_display_mode hw_mode;};')
pre+=r'''
#define CHIP_POLARIS10 10
#define CHIP_POLARIS11 11
#define CHIP_POLARIS12 12
#define CHIP_VEGAM 13
#define to_amdgpu_encoder(p) (p)
static unsigned pll,timing,post;
static int amdgpu_atombios_encoder_get_encoder_mode(struct amdgpu_encoder*e){(void)e;return 0;}
static void amdgpu_atombios_crtc_program_pll(struct drm_crtc*c,...){(void)c;pll++;}
static void amdgpu_atombios_crtc_set_pll(struct drm_crtc*c,struct drm_display_mode*m){(void)c;(void)m;pll++;}
static void amdgpu_atombios_crtc_set_dtd_timing(struct drm_crtc*c,struct drm_display_mode*m){(void)c;(void)m;timing++;}
static void amdgpu_atombios_crtc_overscan_setup(struct drm_crtc*c,struct drm_display_mode*m,struct drm_display_mode*a){(void)c;(void)m;(void)a;post++;}
static void amdgpu_atombios_crtc_scaler_setup(struct drm_crtc*c){(void)c;post++;}
static void dce_v11_0_cursor_reset(struct drm_crtc*c){(void)c;post++;}
'''
main=r'''
int main(void){unsigned cases=0;for(unsigned chip=10;chip<15;chip++)for(unsigned clock=0;clock<2;clock++)for(unsigned fault=0;fault<4;fault++){
 struct amdgpu_device a={0,chip};struct drm_device d={&a};struct amdgpu_bo bo={0,0x1212345600ULL};struct drm_gem_object obj={&bo};struct drm_format_info format={fault==3?0xdeadbeef:DRM_FORMAT_XRGB8888,{4}};struct drm_framebuffer fb={{&obj},&format,{2560},640,480};struct plane plane={&fb};struct amdgpu_encoder encoder={3};struct amdgpu_crtc c={.base={&d,&plane,{640,480,25175}},.adjusted_clock=clock?25175:0,.encoder=&encoder,.bpc=8};
 struct drm_display_mode mode={640,480,25175};pll=timing=post=writes=reserves=unreserves=pins=0;reserve_error=fault==1?-5:0;pin_error=fault==2?-12:0;
 int ret=dce_v11_0_crtc_mode_set(&c.base,&mode,&mode,0,0,&fb);
 if(!clock){if(ret!=-EINVAL||pll||timing||post||writes||c.hw_mode.clock)return 1;}
 else {
  int expected=fault==1?-5:fault?-EINVAL:0;
#if FIXED
  if(ret!=expected)return 2;if(fault&&(post||c.hw_mode.clock))return 3;
#else
  if(ret||post!=3||c.hw_mode.clock!=25175)return 4;
#endif
  if(pll!=1||timing!=1)return 5;
  if(!fault){if(post!=3||!writes||c.hw_mode.clock!=25175)return 6;hex(c.hw_mode.clock);hex(post);hex(writes);}
 }
 cases++;
 }return cases==40?0:7;}
'''
outputs={}
for version,fn in [('old',old),('fixed',new)]:
 code=pre+span('static int dce_v11_0_crtc_do_set_base(')+fn+'\n#define FIXED '+str(int(version=='fixed'))+'\n'+main;(W/('modeset-'+version+'.c')).write_text(code)
 for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
  exe=W/('modeset-'+version+'-'+arch);cmd=[cc]+(['-mstackrealign']if arch=='x86'else[])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static',str(W/('modeset-'+version+'.c')),'-o',str(exe)]
  p=subprocess.run(cmd,capture_output=True);(W/('modeset-'+version+'-'+arch+'-compile.log')).write_bytes(p.stderr)
  if p.returncode:print(p.stderr.decode()[-2500:]);p.check_returncode()
  p=subprocess.run(runner+[str(exe)],capture_output=True);p.check_returncode();outputs[version,arch]=p.stdout
assert len(set(outputs.values()))==1
r=dict(status='PASS',actual_functions=2,scenarios_per_version_architecture=40,total_scenarios=160,patch_sha256=hashlib.sha256(patch.encode()).hexdigest(),hardware_accessed=False,old_control='Reports mode-set success and updates hw_mode despite reserve/pin/format failure',fixed='Propagates surface error and skips downstream setup/state update',limits=['PLL and timing callbacks mocked; their own ATOM status handling is a separate open contract','Not proof of physical connector or display output','Surface helper may already have partial side effects before later failures'])
(W/'modeset-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
