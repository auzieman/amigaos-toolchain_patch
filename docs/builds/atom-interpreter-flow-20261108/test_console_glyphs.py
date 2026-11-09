"""R730: Linux glyph expansion -> actual TTM copy -> actual DCE11 swap programming."""
from pathlib import Path
import subprocess,json,re,hashlib,os,resource
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
B=Path('/srv/data1/tabor-build/source-review');W=B/'atom-interpreter-flow-20261108';S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-007/source')
code=(B/'console-selected-path-20261108/console-path.c').read_text().split('int main(void){')[0]
code=code.replace('struct fb_info{void*screen_buffer;};',r'''
struct fb_info;struct fb_ops{int(*fb_sync)(struct fb_info*);};
struct fb_info{void*screen_buffer,*screen_base,*pseudo_palette;unsigned flags,state;struct{unsigned bits_per_pixel;}var;struct{unsigned visual,line_length;}fix;struct fb_ops*fbops;};
struct fb_image{unsigned dx,dy,width,height,fg_color,bg_color,depth;const u8*data;};
#define FBINFO_STATE_RUNNING 0
#define FBINFO_VIRTFB 1
#define FB_VISUAL_TRUECOLOR 2
#define FB_VISUAL_DIRECTCOLOR 4
#define __force
#define fb_warn_once(...) do{}while(0)
#define printk(...) do{}while(0)
''')
h=(S/'include/linux/fb.h').read_text()
a=h.index('static inline bool fb_be_math(');i=h.index('{',a)+1;d=1
while d:d+=(h[i]=='{')-(h[i]=='}');i+=1
code+=h[a:i]+'\n'+h[h.index('#define FB_LEFT_POS'):h.index('\n\n',h.index('#define FB_SHIFT_LOW'))]+'\n'
sys=(S/'drivers/video/fbdev/core/sysimgblt.c').read_text();code+=sys[:sys.index('#include')]+sys[sys.index('#define DEBUG'):sys.index('EXPORT_SYMBOL(sys_imageblit);')]
font=(S/'lib/fonts/font_8x16.c').read_text();a=font.index('static const struct font_data fontdata_8x16');i=font.index('{',a)+1;d=1
while d:d+=(font[i]=='{')-(font[i]=='}');i+=1
code+='\n/* Font source: GPL-2.0, lib/fonts/font_8x16.c. */\n#define FONTDATAMAX 4096\nstruct font_data{u32 extra[4];u8 data[FONTDATAMAX];};\n'+font[a:i]+';\n'
code+=r'''
int main(void){
 struct amdgpu_device a={0};struct drm_device d={&a};struct amdgpu_bo bo={0,0x1212345600ULL};struct drm_gem_object obj={&bo};struct drm_format_info format={0,{4}};struct drm_framebuffer fb={{&obj},&format,{144},32,20};struct plane plane={&fb};struct amdgpu_crtc crtc={{&d,&plane,{32,20}},0};
 static union{u64 align;u8 bytes[4096];}shadow,vram;u32 palette[16]={0};struct fb_ops ops={0};struct fb_info info={.screen_buffer=shadow.bytes,.screen_base=shadow.bytes,.pseudo_palette=palette,.flags=FBINFO_VIRTFB,.fbops=&ops};struct drm_fb_helper helper={&fb,&info};unsigned cases=0;
 unsigned cpp_values[]={1,2,4};u32 formats[]={DRM_FORMAT_C8,DRM_FORMAT_RGB565,DRM_FORMAT_XRGB8888};
 for(unsigned f=0;f<3;f++)for(unsigned xoff=0;xoff<2;xoff++)for(unsigned glyph=0;glyph<256;glyph++){
  unsigned cpp=cpp_values[f],dx=xoff?3:0;fb.pitches[0]=32*cpp+16;format.cpp[0]=cpp;format.format=formats[f];info.var.bits_per_pixel=cpp*8;info.fix.line_length=fb.pitches[0];info.fix.visual=cpp==1?0:FB_VISUAL_TRUECOLOR;
  u32 fg=cpp==1?0xe3:cpp==2?0xace1:0x0012ab34,bg=cpp==1?0x17:cpp==2?0x1234:0x00563412;palette[1]=fg;palette[0]=bg;
  memset(shadow.bytes,0x5a,4096);memset(vram.bytes,0x5a,4096);
  struct fb_image image={dx,2,8,16,cpp==1?fg:1,cpp==1?bg:0,1,fontdata_8x16.data+glyph*16};
  sys_imageblit(&info,&image);
  if(dce_v11_0_crtc_do_set_base(&crtc.base,&fb,0,0,0))return 1;
  struct drm_clip_rect clip={dx,2,dx+8,18};struct iosys_map map={vram.bytes};drm_fbdev_ttm_damage_blit_real(&helper,&clip,&map);
  u32 sw=regs[mmGRPH_SWAP_CNTL]&GRPH_SWAP_CNTL__GRPH_ENDIAN_SWAP_MASK;
  for(unsigned y=0;y<20;y++)for(unsigned x=0;x<32;x++){
   u8*p=vram.bytes+y*fb.pitches[0]+x*cpp;u32 got=0;
   for(unsigned b=0;b<cpp;b++){unsigned index=sw==ENDIAN_NONE?b:cpp-1-b;got|=(u32)p[index]<<(8*b);}
   bool inside=y>=2&&y<18&&x>=dx&&x<dx+8;u32 expected=cpp==1?0x5a:cpp==2?0x5a5a:0x5a5a5a5a;
   if(inside)expected=(fontdata_8x16.data[glyph*16+y-2]&(1u<<(7-(x-dx))))?fg:bg;
   if(got!=expected)return 2;
   if(inside)hex(got);
  }
  for(unsigned y=0;y<20;y++)for(unsigned i=32*cpp;i<fb.pitches[0];i++)if(vram.bytes[y*fb.pitches[0]+i]!=0x5a)return 3;
  cases++;
 }
 return cases==1536?0:4;
}
'''
(W/'console-glyphs.c').write_text(code);outputs={}
for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
 exe=W/('glyphs-'+arch);cmd=[cc]+(['-mstackrealign']if arch=='x86'else[])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static',str(W/'console-glyphs.c'),'-o',str(exe)]
 p=subprocess.run(cmd,capture_output=True);(W/('glyphs-'+arch+'-compile.log')).write_bytes(p.stderr)
 if p.returncode:print(p.stderr.decode()[-4000:]);p.check_returncode()
 p=subprocess.run(runner+[str(exe)],capture_output=True,timeout=30);p.check_returncode();outputs[arch]=p.stdout
assert outputs['x86']==outputs['ppc']
r=dict(status='PASS',glyphs=256,pixel_depths=[8,16,32],placements=2,scenarios_per_architecture=1536,glyph_pixels_per_architecture=196608,source_sha256=hashlib.sha256(code.encode()).hexdigest(),output_sha256=hashlib.sha256(outputs['ppc']).hexdigest(),font_sha256=hashlib.sha256((S/'lib/fonts/font_8x16.c').read_bytes()).hexdigest(),hardware_accessed=False,limits=['Actual monochrome sys_imageblit path, font, TTM copy and DCE11 surface function; modeled IO/BO/register endpoints','No VT input/parser/scroll or real display timing','Decoded pixel words validated; physical wire colors and output not observed'])
(W/'glyph-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
