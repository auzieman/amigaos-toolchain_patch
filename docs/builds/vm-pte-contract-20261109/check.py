from pathlib import Path
import difflib,hashlib,json,subprocess,struct
w=Path('/home/owner/vm-pte-contract-20261109');w.mkdir(exist_ok=True)
p=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261109-011/source/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_sdma.c');s=p.read_text();old='''			pte[i] = amdgpu_vm_map_gart(p->pages_addr, addr);
			pte[i] |= flags;''';new='''			/* SDMA copies these bytes without interpreting IB words. */
			pte[i] = cpu_to_le64(amdgpu_vm_map_gart(p->pages_addr,
							    addr) | flags);''';assert s.count(old)==1
n=s.replace('uint64_t *pte;','__le64 *pte;').replace('pte = (uint64_t *)&','pte = (__le64 *)&').replace(old,new)
patch=''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_sdma.c',tofile='b/drivers/gpu/drm/amd/amdgpu/amdgpu_vm_sdma.c'));(w/'0032-vm-sdma-serialize-copied-pte-array.patch').write_text(patch)
header='''typedef unsigned int u32;typedef unsigned long long uint64_t;typedef uint64_t __le64;
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define cpu_to_le64(v) __builtin_bswap64((uint64_t)(v))
#else
#define cpu_to_le64(v) ((uint64_t)(v))
#endif
struct params {uint64_t *pages_addr;};
static uint64_t pages[256],output[256];
static uint64_t amdgpu_vm_map_gart(const uint64_t *p,uint64_t a){return p[a>>12]|(a&4095);}
void _start(void){
for(unsigned i=0;i<256;i++)pages[i]=0x123450000ULL+((uint64_t)i<<12);
struct params params={pages},*p=&params;uint64_t *pte=output;uint64_t addr=0;
for(unsigned i=0;i<256;i++,addr+=4096){uint64_t flags=(i&1)?0x67:0x3;
'''
footer='''}
#if defined(__powerpc__)
register long nr asm("r0")=4,x asm("r3")=1,y asm("r4")=(long)output,z asm("r5")=sizeof(output);
asm volatile("sc" : "+r"(nr),"+r"(x),"+r"(y),"+r"(z) : : "memory","cr0","ctr","lr","xer","r6","r7","r8","r9","r10","r11","r12");nr=1;x=0;asm volatile("sc"::"r"(nr),"r"(x):"memory");
#else
asm volatile("syscall"::"a"(1L),"D"(1L),"S"(output),"d"((long)sizeof(output)):"rcx","r11","memory");asm volatile("syscall"::"a"(60L),"D"(0L):"rcx","r11","memory");
#endif
__builtin_unreachable();}
'''
results={}
for mode,body in [('old',old),('fixed',new)]:
 c=w/(mode+'.c');c.write_text(header+body+footer)
 for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc','-cpu','e500v2'])]:
  exe=w/(mode+'-'+arch);subprocess.run([cc,'-O2','-ffreestanding','-nostdlib','-static','-fno-pie','-no-pie','-fno-stack-protector',str(c),'-o',str(exe)],check=True)
  r=subprocess.run(runner+[str(exe)],capture_output=True,check=True);assert len(r.stdout)==2048;results[mode+'-'+arch]=r.stdout
expected=b''.join(struct.pack('<Q',(0x123450000+(i<<12))| (0x67 if i&1 else 3)) for i in range(256))
assert results['old-x86']==results['fixed-x86']==results['fixed-ppc']==expected
assert results['old-ppc']!=expected
r={'status':'PASS','cases_per_arch':256,'source_sha256':hashlib.sha256(s.encode()).hexdigest(),'patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),'scope':'Actual PTE producer block; DMA copy modeled as byte-preserving; supplied address/flags modeled','negative_control':'old BE PTE array differs from GPU LE entries','fixed_sha256':hashlib.sha256(expected).hexdigest(),'hardware_causality_proven':False};(w/'check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
