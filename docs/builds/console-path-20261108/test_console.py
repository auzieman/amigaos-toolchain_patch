"""R730: actual framebuffer damage copy -> DCE10 surface programming -> modeled pixel fetch."""
from pathlib import Path
import subprocess,re,json,hashlib,os,resource
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
B=Path('/srv/data1/tabor-build/source-review');W=B/'console-path-20261108';W.mkdir(exist_ok=True)
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-006/source');A=S/'drivers/gpu/drm/amd/amdgpu'
def span(p,key):
 t=p.read_text();a=t.index(key);i=t.index('{',a)+1;d=1
 while d:d+=(t[i]=='{')-(t[i]=='}');i+=1
 return t[a:i]
pre=(B/'shared-kernel-boundary-20261108/fixed-asic-clock.c').read_text().split('union get_clock_dividers')[0]
# DCE enums own the scanout constants; do not mix legacy SID macro names.
for name in ['dce_10_0_d.h','dce_10_0_sh_mask.h','dce_10_0_enum.h']:pre+='\n#include "'+str(S/'drivers/gpu/drm/amd/include/asic_reg/dce'/name)+'"\n'
pre+='''\n#define fourcc_code(a,b,c,d) ((u32)(a)|((u32)(b)<<8)|((u32)(c)<<16)|((u32)(d)<<24))\n'''
formats=['C8','XRGB4444','ARGB4444','XRGB1555','ARGB1555','BGRX5551','BGRA5551','RGB565','XRGB8888','ARGB8888','XRGB2101010','ARGB2101010','BGRX1010102','BGRA1010102','XBGR8888','ABGR8888']
uapi=(S/'include/uapi/drm/drm_fourcc.h').read_text().splitlines()
for name in formats:pre+=next(l for l in uapi if re.match(r'#define\s+DRM_FORMAT_'+name+r'\s',l))+'\n'
pre+=r'''
typedef unsigned long long uint64_t;typedef uint64_t u64;typedef __SIZE_TYPE__ size_t;
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define __BIG_ENDIAN 4321
#endif
#define REG_SET_FIELD(orig,reg,field,val) (((orig)&~reg##__##field##_MASK)|(((u32)(val)<<reg##__##field##__SHIFT)&reg##__##field##_MASK))
#define upper_32_bits(x) ((u32)((u64)(x)>>32))
#define unlikely(x) (x)
#define DRM_DEBUG_KMS(...) do{}while(0)
#define DRM_ERROR(...) do{}while(0)
#define AMDGPU_GEM_CREATE_VRAM_CONTIGUOUS 1
#define AMDGPU_GEM_DOMAIN_VRAM 4
#define AMDGPU_TILING_GET(flags,field) 0
#define ADDR_SURF_MICRO_TILING_DISPLAY 0
struct amdgpu_device {int unused;};
struct amdgpu_bo {unsigned flags;u64 addr;};struct drm_gem_object{struct amdgpu_bo*bo;};
struct drm_format_info{u32 format;unsigned cpp[1];};
struct drm_framebuffer{struct drm_gem_object*obj[1];struct drm_format_info*format;unsigned pitches[1],width,height;};
struct drm_device{struct amdgpu_device*adev;};struct plane{struct drm_framebuffer*fb;};
struct drm_crtc{struct drm_device*dev;struct plane*primary;struct{unsigned hdisplay,vdisplay;}mode;};
struct amdgpu_crtc{struct drm_crtc base;unsigned crtc_offset;};
#define to_amdgpu_crtc(c) ((struct amdgpu_crtc*)(c))
#define drm_to_adev(d) ((d)->adev)
#define gem_to_amdgpu_bo(o) ((o)->bo)
static int reserve_error,pin_error,reserves,unreserves,pins,unpins,writes;
static int amdgpu_bo_reserve(struct amdgpu_bo*b,bool interrupt){(void)b;(void)interrupt;reserves++;return reserve_error;}
static int amdgpu_bo_pin(struct amdgpu_bo*b,unsigned domain){(void)b;(void)domain;pins++;return pin_error;}
static void amdgpu_bo_unreserve(struct amdgpu_bo*b){(void)b;unreserves++;}
static void amdgpu_bo_unpin(struct amdgpu_bo*b){(void)b;unpins++;}
static u64 amdgpu_bo_gpu_offset(struct amdgpu_bo*b){return b->addr;}
static void amdgpu_bo_get_tiling_flags(struct amdgpu_bo*b,u64*f){(void)b;*f=0;}
static void dce_v10_0_vga_enable(struct drm_crtc*c,bool enabled){(void)c;(void)enabled;}
static void dce_v10_0_grph_enable(struct drm_crtc*c,bool enabled){(void)c;(void)enabled;}
static void dce_v10_0_bandwidth_update(struct amdgpu_device*a){(void)a;}
static u32 regs[65536];
#define RREG32(reg) ((void)adev,regs[(reg)])
#define WREG32(reg,v) do{(void)adev;regs[(reg)]=(v);writes++;}while(0)
struct fb_info{void*screen_buffer;};struct drm_fb_helper{struct drm_framebuffer*fb;struct fb_info*info;};
struct drm_clip_rect{unsigned x1,y1,x2,y2;};struct iosys_map{u8*ptr;};
#define DIV_ROUND_UP(n,d) (((n)+(d)-1)/(d))
static unsigned drm_format_info_bpp(struct drm_format_info*f,unsigned plane){(void)plane;return f->cpp[0]*8;}
static void iosys_map_incr(struct iosys_map*m,unsigned n){m->ptr+=n;}
static void iosys_map_memcpy_to(struct iosys_map*m,unsigned off,const void*s,unsigned n){u8*d=m->ptr+off;const u8*b=s;for(unsigned i=0;i<n;i++)d[i]=b[i];}
'''
code=pre+span(A/'dce_v10_0.c','static int dce_v10_0_crtc_do_set_base(')+span(S/'drivers/gpu/drm/drm_fbdev_ttm.c','static void drm_fbdev_ttm_damage_blit_real(')
code+='\nstatic u32 formats[]={'+','.join('DRM_FORMAT_'+x for x in formats)+'};\n'
code+=r'''
int main(void){
 struct amdgpu_device adev={0};struct drm_device dev={&adev};struct amdgpu_bo bo={0,0x1212345600ULL};struct drm_gem_object obj={&bo};struct drm_format_info format={0,{4}};struct drm_framebuffer fb={{&obj},&format,{80},16,8};struct plane plane={&fb};struct amdgpu_crtc crtc={{&dev,&plane,{16,7}},0};
 u8 shadow[640],vram[640];struct fb_info info={shadow};struct drm_fb_helper helper={&fb,&info};unsigned cases=0;
 for(unsigned f=0;f<16;f++)for(unsigned atomic=0;atomic<2;atomic++)for(unsigned offset=0;offset<2;offset++){
  format.format=formats[f];format.cpp[0]=f==0?1:f<8?2:4;fb.pitches[0]=16*format.cpp[0]+16;crtc.crtc_offset=offset?0x300:0;
  reserves=unreserves=pins=unpins=writes=reserve_error=pin_error=0;
  if(dce_v10_0_crtc_do_set_base(&crtc.base,&fb,7,3,atomic))return 1;
  unsigned o=crtc.crtc_offset;u32 sw=regs[mmGRPH_SWAP_CNTL+o]&GRPH_SWAP_CNTL__GRPH_ENDIAN_SWAP_MASK;
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
  u32 expected_swap=format.cpp[0]==1?ENDIAN_NONE:format.cpp[0]==2?ENDIAN_8IN16:ENDIAN_8IN32;
#else
  u32 expected_swap=ENDIAN_NONE;
#endif
  if(sw!=expected_swap||regs[mmGRPH_PITCH+o]!=fb.pitches[0]/format.cpp[0]||regs[mmGRPH_PRIMARY_SURFACE_ADDRESS_HIGH+o]!=0x12||regs[mmGRPH_PRIMARY_SURFACE_ADDRESS+o]!=0x12345600||regs[mmGRPH_X_END+o]!=16||regs[mmGRPH_Y_END+o]!=8||regs[mmVIEWPORT_START+o]!=((4u<<16)|2)||regs[mmVIEWPORT_SIZE+o]!=((16u<<16)|8))return 2;
  if(reserves!=1||unreserves!=1||pins!=!atomic)return 3;
  for(unsigned i=0;i<640;i++){shadow[i]=0xa5;vram[i]=0x5a;}
  /* Native fbcon-style pixel values. Damage helper must copy bytes unchanged. */
  for(unsigned y=0;y<8;y++)for(unsigned x=0;x<16;x++){
   u32 pixel=(x*0x123457u+y*0x3517u)^0x12345678u;u8*p=shadow+y*fb.pitches[0]+x*format.cpp[0];
   if(format.cpp[0]==1)*p=pixel;else if(format.cpp[0]==2){u16 v=pixel;memcpy(p,&v,2);}else memcpy(p,&pixel,4);
  }
  struct drm_clip_rect clip={3,1,13,6};struct iosys_map map={vram};drm_fbdev_ttm_damage_blit_real(&helper,&clip,&map);
  for(unsigned i=0;i<640;i++){
   unsigned y=i/fb.pitches[0],x=i%fb.pitches[0];bool copied=y>=1&&y<6&&x>=3*format.cpp[0]&&x<13*format.cpp[0];
   if(vram[i]!=(copied?shadow[i]:0x5a))return 4;
  }
  for(unsigned y=1;y<6;y++)for(unsigned x=3;x<13;x++){
   u8*p=vram+y*fb.pitches[0]+x*format.cpp[0];u32 got=0;
   for(unsigned b=0;b<format.cpp[0];b++){
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
    unsigned src=format.cpp[0]-1-b;
#else
    unsigned src=b;
#endif
    got|=(u32)p[src]<<(8*b);
   }
   u32 expected=((x*0x123457u+y*0x3517u)^0x12345678u)&(format.cpp[0]==1?0xffu:format.cpp[0]==2?0xffffu:0xffffffffu);
   if(got!=expected)return 5;hex(got);
  }
  cases++;
 }
 reserve_error=-5;writes=0;if(dce_v10_0_crtc_do_set_base(&crtc.base,&fb,0,0,0)!=-5||writes)return 6;
 reserve_error=0;pin_error=-12;writes=0;if(dce_v10_0_crtc_do_set_base(&crtc.base,&fb,0,0,0)!=-EINVAL||writes)return 7;
 pin_error=0;plane.fb=0;writes=0;if(dce_v10_0_crtc_do_set_base(&crtc.base,&fb,0,0,0)||writes)return 8;
 plane.fb=&fb;format.format=0xdeadbeef;writes=0;if(dce_v10_0_crtc_do_set_base(&crtc.base,&fb,0,0,0)!=-EINVAL||writes)return 9;
 return cases==64?0:10;
}
'''
(W/'console-path.c').write_text(code);outputs={}
for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
 exe=W/('console-'+arch);cmd=[cc]+(['-mstackrealign']if arch=='x86'else[])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static',str(W/'console-path.c'),'-o',str(exe)]
 r=subprocess.run(cmd,capture_output=True);(W/(arch+'-compile.log')).write_bytes(r.stderr)
 if r.returncode:print(r.stderr.decode()[-5000:]);r.check_returncode()
 r=subprocess.run(runner+[str(exe)],capture_output=True);r.check_returncode();outputs[arch]=r.stdout
assert outputs['x86']==outputs['ppc']
r=dict(status='PASS',actual_functions=2,formats=16,successful_scenarios_per_architecture=64,error_scenarios_per_architecture=4,checked_pixels_per_architecture=3200,pixel_semantics_match=True,source_sha256=hashlib.sha256(code.encode()).hexdigest(),hardware_accessed=False,limits=['Linear scanout only; tiling metadata mocked zero','Register, BO and iosys IO endpoints mocked','Pixel fetch modeled using selected swap mode; physical effect not observed','No EDID, connector detection, PLL/link training, timing or fbcon glyph renderer execution'])
(W/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
