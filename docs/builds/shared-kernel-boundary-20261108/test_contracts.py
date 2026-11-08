"""R730: compile/execute the real ASIC clock routine with a fake ATOM endpoint."""
from pathlib import Path
import subprocess,json,re,hashlib
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-001/source');W=Path('/srv/data1/tabor-build/source-review/shared-kernel-boundary-20261108')
old=(S/'drivers/gpu/drm/amd/amdgpu/amdgpu_atombios.c').read_text();fixed=(W/'amdgpu_atombios.c.fixed').read_text();head=(W/'atom.h.fixed').read_text()
def span(text,start):
 a=text.index(start);b=text.index('{',a);i=b+1;depth=1
 while depth:
  depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[a:i]
union=span(old,'union get_clock_dividers {')+';\n'
divheader=(S/'drivers/gpu/drm/amd/amdgpu/amdgpu_atombios.h').read_text();div=span(divheader,'struct atom_clock_dividers {')+';\n'
helper=head[head.index('/* The ATOM parameter word is LE:'):head.index('struct drm_device;')]
# Reuse the already-qualified freestanding syscall output layer, no target libc.
fixture=Path('/srv/data1/tabor-build/source-review/atom-channel-review-20261108/fixed-atom.c').read_text()
io=fixture[fixture.index('void *memcpy('):fixture.index('int main(void) {')]
pre=old[:old.index('#include')]+r'''
typedef unsigned char uint8_t;typedef unsigned short uint16_t;typedef unsigned int uint32_t;
typedef uint8_t u8;typedef uint16_t u16;typedef uint32_t u32;typedef _Bool bool;
#define true 1
#define false 0
#define EINVAL 22
#define __counted_by(x)
#define offsetof(t,f) __builtin_offsetof(t,f)
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define ATOM_BIG_ENDIAN 1
#define __BIG_ENDIAN 4321
#define cpu_to_le32(x) __builtin_bswap32(x)
#define le32_to_cpu(x) __builtin_bswap32(x)
#define le16_to_cpu(x) __builtin_bswap16(x)
#else
#define ATOM_BIG_ENDIAN 0
#define cpu_to_le32(x) (x)
#define le32_to_cpu(x) (x)
#define le16_to_cpu(x) (x)
#endif
typedef uint32_t ULONG;typedef uint16_t USHORT;typedef uint8_t UCHAR;
typedef signed char CHAR;typedef int LONG;
'''+f'#include "{S}/drivers/gpu/drm/amd/include/atombios.h"\n'+r'''
static uint32_t get_unaligned_le32(const void *p) {
 const uint8_t*b=p;return (uint32_t)b[0]|((uint32_t)b[1]<<8)|((uint32_t)b[2]<<16)|((uint32_t)b[3]<<24);
}
static void put_unaligned_le32(uint32_t n,void*p) {
 uint8_t*b=p;b[0]=n;b[1]=n>>8;b[2]=n>>16;b[3]=n>>24;
}
void *memset(void*p,int c,__SIZE_TYPE__ n) {
 volatile unsigned char*b=p;for(__SIZE_TYPE__ i=0;i<n;i++){b[i]=c;}return p;
}
int main(void);
'''
stubs=r'''
struct atom_context {int unused;};
struct amdgpu_device {struct {struct atom_context *atom_context;} mode_info;int asic_type;};
#define CHIP_TAHITI 10
static u8 revision;
static u32 request_word;
static int failure;
static bool amdgpu_atom_parse_cmd_header(struct atom_context*c,int i,u8*f,u8*r) {
 (void)c;(void)i;*f=1;*r=revision;return true;
}
static int amdgpu_atom_execute_table(struct atom_context*c,int i,u32*p,int size) {
 (void)c;(void)i;(void)size;request_word=get_unaligned_le32(p);
 if(failure)return failure;
 put_unaligned_le32(0x05123456,p);return 0;
}
'''
main=r'''
int main(void) {
 struct amdgpu_device dev={0};struct atom_clock_dividers d;
 u32 clocks[]={0,10000,21400,30000,107100,0x123456,0xffffff};
 u8 flags[]={0,1,2,255};
 for (unsigned r=4;r<=6;r+=2) {
  revision=r;
  for(unsigned f=0;f<4;f++)for(unsigned i=0;i<7;i++) {
   int result=amdgpu_atombios_get_clock_dividers(&dev,flags[f],clocks[i],false,&d);
   hex(r);hex(flags[f]);hex(clocks[i]);hex(request_word);hex(d.real_clock);hex(d.post_divider);hex(result);emit("\n",1);
  }
 }
 revision=6;failure=-5;
 int result=amdgpu_atombios_get_clock_dividers(&dev,0,10000,false,&d);
 if(result!=-EINVAL)return 1;
 return 0;
}
'''
results={}
def run(args):
 r=subprocess.run(args,cwd=W,capture_output=True,text=True)
 if r.returncode:raise RuntimeError(repr(args)+'\n'+r.stderr[-3000:])
 return r.stdout
for name,text in [('old',old),('fixed',fixed)]:
 function=span(text,'int amdgpu_atombios_get_clock_dividers(')
 code=pre+io+union+div+(helper if name=='fixed' else '')+stubs+function+'\n'+main
 (W/(name+'-asic-clock.c')).write_text(code)
 for arch,cc,cmd in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
  exe=name+'-asic-clock-'+arch
  run([cc]+(['-mstackrealign'] if arch=='x86' else [])+['-O2','-Wall','-Wextra','-Werror','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static',name+'-asic-clock.c','-o',exe])
  out=run(cmd+['./'+exe]);(W/(exe+'.log')).write_text(out);results[name+'-'+arch]=out.splitlines()
assert results['old-x86']==results['fixed-x86']==results['fixed-ppc']
assert results['old-ppc']!=results['old-x86']
for line in results['fixed-ppc']:
 rev,flag,clock,request,freq,post,result=[int(x,16) for x in line.split()]
 assert request==clock|((flag if rev==6 else 0)<<24)
 assert freq==0x123456 and post==5 and result==0
r={'status':'PASS','cases_per_architecture':len(results['fixed-ppc']),'full_original_function_extracted':True,'original_x86_preserved':True,'original_ppc_mismatch_reproduced':True,'corrected_ppc_matches_x86':True,'response_frequency_and_postdivider_verified':True,'interpreter_error_propagation_verified':True,'hardware_tested':False,'fixture_sha256':{n:hashlib.sha256((W/(n+'-asic-clock.c')).read_bytes()).hexdigest() for n in ['old','fixed']}}
(W/'tests.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
