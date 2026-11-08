"""R730-only compiled LE/BE tests from pinned producer declarations/statements."""
from pathlib import Path
import hashlib,json,re,subprocess
W=Path('/srv/data1/tabor-build/source-review/atom-channel-review-20261108')
S=Path('/srv/data1/tabor-build/linux-live-001/work/polaris-powerplay-20261108-003/source')
def run(args):return subprocess.run(args,cwd=W,check=True,capture_output=True,text=True).stdout
result={'hardware_tested':False,'tables':{},'atom':{}}
# Compare complete compiled table sections, not synthetic individual integers.
for arch,cc,oc in [('x86','gcc','objcopy'),('ppc','powerpc-linux-gnu-gcc','powerpc-linux-gnu-objcopy')]:
 for version in ['old','fixed']:
  obj=f'{version}-{arch}.o'
  run([cc,'-Wall','-Wextra','-Werror','-ffreestanding','-fno-common','-O2','-c',f'{version}-tables.c','-o',obj])
  for section in ['gfx','mem','vr']:
   dest=f'{version}-{arch}-{section}.bin'
   run([oc,'--dump-section',f'.audit_{section}={dest}',obj])
for section in ['gfx','mem','vr']:
 data={a:(W/f'{a}-{section}.bin').read_bytes() for a in ['old-x86','old-ppc','fixed-x86','fixed-ppc']}
 assert data['old-x86']==data['fixed-x86']==data['fixed-ppc'],section
 assert data['old-x86']!=data['old-ppc'],section
 result['tables'][section]={'bytes':len(data['old-x86']),'fixed_sha256':hashlib.sha256(data['fixed-ppc']).hexdigest(),'old_BE_differs':True,'fixed_x86_preserved':True,'fixed_BE_matches_x86':True}
# Extract the actual bitfield type and actual AI input statements.
h=(S/'drivers/gpu/drm/amd/include/atombios.h').read_text()
typ=re.search(r'typedef struct _COMPUTE_MEMORY_ENGINE_PLL_PARAMETERS_V4\n\{.*?\}COMPUTE_MEMORY_ENGINE_PLL_PARAMETERS_V4;',h,re.S).group(0)
old=(S/'drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomctrl.c').read_text();fixed=(W/'ppatomctrl.fixed.c').read_text()
def input_block(s):
 f=s[s.index('int atomctrl_get_engine_pll_dividers_ai('):]
 return f[f.index('\tpll_patameters.ulClock.ulClock =') if 'pll_patameters.ulClock.ulClock =' in f.split('result = PP_INIT_CALL',1)[0] else f.index('\tatomctrl_set_clock_word('):f.index('\n\tresult = PP_INIT_CALL')]
helpers=fixed[fixed.index('static void atomctrl_set_clock_word'):fixed.index('union voltage_object_info')]
pre=old[:old.index('#include')]+r'''
typedef unsigned char uint8_t;
typedef unsigned int uint32_t;
typedef uint32_t ULONG;
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define ATOM_BIG_ENDIAN 1
#define cpu_to_le32(x) __builtin_bswap32(x)
#else
#define ATOM_BIG_ENDIAN 0
#define cpu_to_le32(x) (x)
#endif
#define COMPUTE_GPUCLK_INPUT_FLAG_SCLK 1
static uint32_t get_unaligned_le32(const void *p) {
 const uint8_t *b=p; return (uint32_t)b[0]|((uint32_t)b[1]<<8)|((uint32_t)b[2]<<16)|((uint32_t)b[3]<<24);
}
static void put_unaligned_le32(uint32_t n,void *p) {
 uint8_t *b=p; b[0]=n;b[1]=n>>8;b[2]=n>>16;b[3]=n>>24;
}
'''
io=r'''
void *memcpy(void *dst, const void *src, __SIZE_TYPE__ n) {
 volatile unsigned char *d=dst; const volatile unsigned char *s=src;
 for (__SIZE_TYPE__ i=0;i<n;i++) { d[i]=s[i]; }
 return dst;
}
static void emit(const char *p, unsigned n) {
#ifdef __powerpc__
 register unsigned r0 __asm__("r0")=4;
 register unsigned r3 __asm__("r3")=1;
 register const char *r4 __asm__("r4")=p;
 register unsigned r5 __asm__("r5")=n;
 __asm__ volatile("sc" : "+r"(r0),"+r"(r3) : "r"(r4),"r"(r5) : "cr0","memory");
#else
 long result;
 __asm__ volatile("syscall" : "=a"(result) : "0"(1L),"D"(1L),"S"(p),"d"((unsigned long)n) : "rcx","r11","memory");
#endif
}
static void hex(uint32_t n) {
 char b[9];const char *digits="0123456789abcdef";
 for(unsigned i=0;i<8;i++) b[i]=digits[(n >> (28-i*4))&15];
 b[8]=' ';emit(b,9);
}
void _start(void) {
 int r=main();
#ifdef __powerpc__
 register unsigned r0 __asm__("r0")=1;
 register unsigned r3 __asm__("r3")=r;
 __asm__ volatile("sc" : "+r"(r0),"+r"(r3) : : "cr0","memory");
#else
 __asm__ volatile("syscall" : : "a"(60L),"D"((long)r) : "rcx","r11","memory");
#endif
 __builtin_unreachable();
}
'''
for ver,s in [('old',old),('fixed',fixed)]:
 # Retain all helper functions in baseline fixture too, so warning checks match.
 code=pre+typ+'\n'+helpers+'\nint main(void);\n'+io+r'''
int main(void) {
 uint32_t clocks[]={30000,40000,50000,60000,70000,80000,90000,100000,0x123456,0xffffff};
 struct { COMPUTE_MEMORY_ENGINE_PLL_PARAMETERS_V4 ulClock; } pll_patameters;
 for (unsigned i=0;i<sizeof(clocks)/sizeof(clocks[0]);i++) {
  uint32_t clock_value=clocks[i];
  pll_patameters.ulClock.ulClock=0;
  pll_patameters.ulClock.ucPostDiv=0;
'''+input_block(s)+r'''
  hex(clock_value);hex(get_unaligned_le32(&pll_patameters.ulClock));emit("\n",1);
 }
 uint32_t output;
 atomctrl_set_clock_word(&output,0x123456,5);
 emit("out ",4);hex(atomctrl_clock_word_frequency(&output));hex(atomctrl_clock_word_flags(&output));emit("\n",1);
 return 0;
}
'''
 (W/f'{ver}-atom.c').write_text(code)
 for arch,cc,cmd in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
  binary=f'{ver}-atom-{arch}'
  run([cc,'-O2','-Wall','-Wextra','-Werror','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static',f'{ver}-atom.c','-o',binary])
  output=run(cmd+['./'+binary]);(W/f'{binary}.log').write_text(output)
  result['atom'][f'{ver}-{arch}']=output.splitlines()
assert result['atom']['old-x86']==result['atom']['fixed-x86']==result['atom']['fixed-ppc']
assert result['atom']['old-ppc']!=result['atom']['old-x86']
for line in result['atom']['fixed-ppc'][:-1]:
 c,v=line.split();assert int(v,16)==(int(c,16)|(1<<24))
result['status']='PASS-complete-calibration-objects-and-ATOM-input'
(W/'tests.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
