from pathlib import Path
import difflib,hashlib,json,subprocess
w=Path('/home/owner/predicate-contract-20261109');w.mkdir(exist_ok=True)
d=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-010/source/drivers/gpu/drm/amd/amdgpu');s=(d/'amdgpu_ring.c').read_text();h=(d/'amdgpu_ring.h').read_text()
old='*ring->cond_exe_cpu_addr = 1;';new='amdgpu_ring_set_preempt_cond_exec(ring, true);';assert s.count(old)==1
patch=''.join(difflib.unified_diff(s.splitlines(True),s.replace(old,new).splitlines(True),fromfile='a/drivers/gpu/drm/amd/amdgpu/amdgpu_ring.c',tofile='b/drivers/gpu/drm/amd/amdgpu/amdgpu_ring.c'))
(w/'0031-ring-initialize-predicate-through-encoder.patch').write_text(patch)
def fn(sig):
 a=h.index(sig);i=h.index('{',a)+1;n=1
 while n:n+=(h[i]=='{')-(h[i]=='}');i+=1
 return h[a:i]
code='''typedef unsigned int u32;typedef _Bool bool;
#define true 1
#define __force
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define cpu_to_le32(v) __builtin_bswap32((u32)(v))
#else
#define cpu_to_le32(v) ((u32)(v))
#endif
struct amdgpu_ring {volatile u32 *cond_exe_cpu_addr;bool selected;};
static bool amdgpu_ring_uses_sw_le(struct amdgpu_ring *r){return r->selected;}
'''+fn('static inline u32 amdgpu_ring_encode_dw(')+fn('static inline void amdgpu_ring_set_preempt_cond_exec(')+'''
static u32 words[4];
void _start(void){struct amdgpu_ring r={words,1};struct amdgpu_ring *ring=&r;
'''+old+'''r.cond_exe_cpu_addr=&words[1];amdgpu_ring_set_preempt_cond_exec(ring,true);
r.cond_exe_cpu_addr=&words[2];'''+new+'''
r.cond_exe_cpu_addr=&words[3];r.selected=0;'''+new+'''
#if defined(__powerpc__)
register long nr asm("r0")=4;register long fd asm("r3")=1;register void *buf asm("r4")=words;register long len asm("r5")=16;
asm volatile("sc":"+r"(nr),"+r"(fd):"r"(buf),"r"(len):"memory","cr0");nr=1;fd=0;asm volatile("sc"::"r"(nr),"r"(fd):"memory");
#else
asm volatile("syscall"::"a"(1L),"D"(1L),"S"(words),"d"(16L):"rcx","r11","memory");asm volatile("syscall"::"a"(60L),"D"(0L):"rcx","r11","memory");
#endif
__builtin_unreachable();}
'''
(w/'predicate.c').write_text(code);results={}
for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc','-cpu','e500v2'])]:
 exe=w/arch;subprocess.run([cc,'-O2','-ffreestanding','-nostdlib','-static','-fno-pie','-no-pie','-fno-stack-protector',str(w/'predicate.c'),'-o',str(exe)],check=True)
 p=subprocess.run(runner+[str(exe)],capture_output=True,check=True);results[arch]=p.stdout.hex();assert len(p.stdout)==16
assert results['x86']=='01000000'*4
assert results['ppc']=='00000001'+'01000000'*2+'00000001'
r={'status':'PASS','source_release':'6.12.113-tabor-e2e-010','patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),'source_sha256':hashlib.sha256(s.encode()).hexdigest(),'outputs_hex':results,'word_order':['old_initializer','existing_runtime_setter','fixed_initializer','unselected_ring_fixed_initializer'],'scope':'Actual shared encoding helper and setter; selection predicate modeled, no GPU hardware','hardware_causality_proven':False}
(w/'check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
