from pathlib import Path
import subprocess,json,hashlib
w=Path('/home/owner/user-ib-fetch-20261109');p=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261109-013/source/drivers/gpu/drm/amd/amdgpu/amdgpu_cs.c');s=p.read_text();a=s.index('#ifdef __BIG_ENDIAN',s.index('ib->flags = chunk_ib->flags;'));z=s.index('#endif',a)+len('#endif');block=s[a:z]
code='''typedef unsigned int u32;typedef _Bool bool;
#define true 1
#define CHIP_POLARIS11 1
#define AMDGPU_RING_TYPE_GFX 1
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define __BIG_ENDIAN 1
#endif
struct device{int asic_type;};struct parser{struct device *adev;};struct functions{int type;};struct ring{struct functions *funcs;};struct ib{bool is_le;};
static bool amdgpu_polaris11_le_user_ib;
static void select(struct parser *p,struct ring *ring,struct ib *ib){
'''+block+'''
}
static unsigned char result[24];
void _start(void){unsigned n=0;struct device d;struct parser p={&d};struct functions f;struct ring r={&f};
for(unsigned enabled=0;enabled<2;enabled++)for(unsigned asic=0;asic<2;asic++)for(unsigned type=1;type<=3;type++)for(unsigned initial=0;initial<2;initial++){
d.asic_type=asic;f.type=type;amdgpu_polaris11_le_user_ib=enabled;struct ib ib={initial};select(&p,&r,&ib);result[n++]=ib.is_le;
}
#if defined(__powerpc__)
register long nr asm("r0")=4,x asm("r3")=1,y asm("r4")=(long)result,z asm("r5")=24;
asm volatile("sc" : "+r"(nr),"+r"(x),"+r"(y),"+r"(z) : : "memory","cr0","ctr","lr","xer","r6","r7","r8","r9","r10","r11","r12");nr=1;x=0;asm volatile("sc"::"r"(nr),"r"(x):"memory");
#else
asm volatile("syscall"::"a"(1L),"D"(1L),"S"(result),"d"(24L):"rcx","r11","memory");asm volatile("syscall"::"a"(60L),"D"(0L):"rcx","r11","memory");
#endif
__builtin_unreachable();}
'''
c=w/'selector.c';c.write_text(code);outputs={}
for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc','-cpu','e500v2'])]:
 exe=w/('selector-'+arch);subprocess.run([cc,'-O2','-ffreestanding','-nostdlib','-static','-fno-pie','-no-pie','-fno-stack-protector',str(c),'-o',str(exe)],check=True);got=subprocess.check_output(runner+[str(exe)]);expected=bytes(1 if (arch=='ppc' and enabled and asic==1 and kind==1) else initial for enabled in range(2) for asic in range(2) for kind in range(1,4) for initial in range(2));assert got==expected;outputs[arch]=got.hex()
r={'status':'PASS','cases_per_arch':24,'source_sha256':hashlib.sha256(s.encode()).hexdigest(),'scope':'Actual selector block; default off, only BE Polaris11 GFX; preexisting LE flags preserved; other ASICs and rings unchanged','outputs':outputs,'hardware_tested':False};(w/'check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
