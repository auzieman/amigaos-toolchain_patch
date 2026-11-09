from pathlib import Path
import subprocess,json,hashlib
w=Path('/srv/data1/tabor-build/linux-live-001/work/radeonsi-le-ib-20261109-001');s=(w/'mesa-source/src/gallium/winsys/amdgpu/drm/amdgpu_cs.cpp').read_text()
def function(name):
 a=s.index('static ',s.rfind('\n}',0,s.index(name))+2) if False else s.rfind('static ',0,s.index(name))
 i=s.index('{',s.index(name))+1;n=1
 while n:n+=(s[i]=='{')-(s[i]=='}');i+=1
 return s[a:i]
selector=function('tabor_explicit_le_gfx_ib(');serialize=function('tabor_serialize_gfx_ib(')
assert s.index('amdgpu_ib_finalize(aws, rcs') < s.index('/* Sizes, padding and optional noop replacement') < s.index('/* Swap command streams.')
assert 'tabor_serialize_gfx_ib(rcs->prev[i].buf, rcs->prev[i].cdw)' in s
assert s.index('amdgpu_pad_gfx_compute_ib(aws, cs->ip_type, map') < s.index('tabor_serialize_gfx_ib(map, preamble_num_dw)') < s.index('amdgpu_bo_unmap(&aws->dummy_sws.base, preamble_bo)')
prefix=r'''typedef unsigned int uint32_t;typedef _Bool bool;
#define true 1
#define false 0
#define AMD_IP_GFX 0
#define CHIP_POLARIS11 11
enum amd_ip_type{gfx=0,compute=1,sdma=2};
struct amdgpu_winsys{struct{int family;}info;};
static bool option;
static bool debug_get_bool_option(const char *s,bool fallback){return option;}
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define UTIL_ARCH_BIG_ENDIAN 1
#define util_cpu_to_le32(v) __builtin_bswap32(v)
#else
#define UTIL_ARCH_BIG_ENDIAN 0
#define util_cpu_to_le32(v) (v)
#endif
static unsigned failed;
#define assert(v) do{if(!(v))failed=1;}while(0)
static long sys(long n,long a,long b,long c){
#if defined(__powerpc__)
register long nr asm("r0")=n;register long x asm("r3")=a;register long y asm("r4")=b;register long z asm("r5")=c;
asm volatile("sc":"+r"(x),"+r"(nr),"+r"(y),"+r"(z)::"memory","cr0","ctr","lr","xer","r6","r7","r8","r9","r10","r11","r12");return x;
#else
long r;asm volatile("syscall":"=a"(r):"a"(n==4?1:60),"D"(a),"S"(b),"d"(c):"rcx","r11","memory");return r;
#endif
}
'''
main=r'''
void _start(void){
 struct amdgpu_winsys aws={{CHIP_POLARIS11}};
 for(unsigned enabled=0;enabled<2;enabled++)for(unsigned fam=10;fam<13;fam++)for(unsigned ip=0;ip<3;ip++){
 option=enabled;aws.info.family=fam;
 assert(tabor_explicit_le_gfx_ib(&aws,ip)==(UTIL_ARCH_BIG_ENDIAN && enabled && fam==11 && ip==0));
 }
 for(unsigned k=0;k<128;k++){
 uint32_t words[25]={0xc0023f00,0x10000,0,0,0xffff1000,0xc0033700,0x100500,0x10800,0,0xcafedead,0xffff1000,0xffff1000,0xc0033700,0x100500,0x20800,0,0x12340000+k,0xffff1000,0xffff1000,0xffff1000,0xc0001000,0,0xffff1000,0xffff1000,0xc0061000};
 /* Finalize a chain length in native CPU representation before publication. */
 words[3]=8|(1u<<20)|(1u<<23);
 uint32_t metadata=48;
#ifndef OLD
 tabor_serialize_gfx_ib(words,12);tabor_serialize_gfx_ib(words+12,8);
 tabor_serialize_gfx_ib(words+20,4);tabor_serialize_gfx_ib(words+24,1);
#endif
 assert(metadata==48);sys(4,1,(long)words,sizeof(words));
 }
 sys(1,failed,0,0);__builtin_unreachable();}
'''
outputs={}
for mode in ['old','new']:
 p=w/('contract-'+mode+'.c');p.write_text(prefix+selector+serialize+main);outputs[mode]={}
 for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc','-cpu','e500v2'])]:
  exe=w/('contract-'+mode+'-'+arch)
  subprocess.run([cc,'-O2','-ffreestanding','-nostdlib','-static','-fno-pie','-no-pie','-fno-stack-protector']+(['-mstackrealign'] if arch=='x86' else [])+(['-DOLD'] if mode=='old' else [])+[str(p),'-o',str(exe)],check=True)
  r=subprocess.run(runner+[str(exe)],capture_output=True,check=True);assert len(r.stdout)==128*100;outputs[mode][arch]=r.stdout
assert outputs['new']['x86']==outputs['new']['ppc'];assert outputs['old']['x86']==outputs['new']['x86'];assert outputs['old']['ppc']!=outputs['new']['ppc']
r={'status':'PASS','selector_cases_per_arch':18,'buffer_cases_per_arch':128,'serialized_bytes_per_arch':12800,'controls':['actual selector and serializer extracted from patched source','default off and non-GFX/non-Polaris exclusion','main/chained/preamble/reset-nop bytes','native chain-length fixup before serialization','old BE bytes fail equivalence','LE output unchanged'],'limitations':'Buffer lifecycle/queue/GPU fetch modeled; call-site ordering statically checked. Does not execute complete Mesa or simulate GPU.','source_sha256':hashlib.sha256(s.encode()).hexdigest()}
(w/'contract-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
