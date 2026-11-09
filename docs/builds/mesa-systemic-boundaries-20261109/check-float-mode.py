from pathlib import Path
import subprocess,json,hashlib,difflib
root=Path('/srv/data1/tabor-build/linux-live-001/work/radeonsi-le-ib-20261109-001/mesa-source');src=root/'src/amd/compiler/aco_ir.h';s=src.read_text()
a=s.index('enum fp_round {');z=s.index('\nenum wait_type',a);old=s[a:z]
fields='''         fp_round round32 : 2;
         fp_round round16_64 : 2;
         unsigned denorm32 : 2;
         unsigned denorm16_64 : 2;'''
reverse='''#if UTIL_ARCH_BIG_ENDIAN
         unsigned denorm16_64 : 2;
         unsigned denorm32 : 2;
         fp_round round16_64 : 2;
         fp_round round32 : 2;
#else
'''+fields+'''
#endif'''
assert old.count(fields)==1;new=old.replace(fields,reverse)
fields='''         uint8_t round : 4;
         uint8_t denorm : 4;''';assert new.count(fields)==1
new=new.replace(fields,'''#if UTIL_ARCH_BIG_ENDIAN
         uint8_t denorm : 4;
         uint8_t round : 4;
#else
'''+fields+'''
#endif''')
w=Path('/srv/data1/tabor-build/linux-live-001/work/mesa-systemic-boundaries-20261109-001');w.mkdir(exist_ok=False)
patch=''.join(difflib.unified_diff(s.splitlines(True),s.replace(old,new).splitlines(True),fromfile='a/src/amd/compiler/aco_ir.h',tofile='b/src/amd/compiler/aco_ir.h'));(w/'0006-aco-float-mode-host-layout.patch').write_text(patch)
prefix='''typedef unsigned char uint8_t;
#define UTIL_ARCH_BIG_ENDIAN (__BYTE_ORDER__ == __ORDER_BIG_ENDIAN__)
'''
helper=r'''
static long sys(long n,long a,long b,long c){
#if defined(__powerpc__)
register long nr asm("r0")=n;register long x asm("r3")=a;register long y asm("r4")=b;register long z asm("r5")=c;
asm volatile("sc":"+r"(x),"+r"(nr),"+r"(y),"+r"(z)::"memory","cr0","ctr","lr","xer","r6","r7","r8","r9","r10","r11","r12");return x;
#else
long r;asm volatile("syscall":"=a"(r):"a"(n==4?1:60),"D"(a),"S"(b),"d"(c):"rcx","r11","memory");return r;
#endif
}
extern "C" void _start(){unsigned failed=0;
for(unsigned k=0;k<256;k++){
 float_mode mode{};mode.round32=(fp_round)(k&3);mode.round16_64=(fp_round)((k>>2)&3);mode.denorm32=(k>>4)&3;mode.denorm16_64=(k>>6)&3;
 unsigned char bytes[]={mode.val,(uint8_t)mode.round,(uint8_t)mode.denorm};
#ifndef OLD
 if(mode.val!=k || mode.round!=(k&15) || mode.denorm!=(k>>4))failed=1;
 float_mode decoded{};decoded.val=k;
 if(decoded.round32!=(k&3) || decoded.round16_64!=((k>>2)&3) || decoded.denorm32!=((k>>4)&3) || decoded.denorm16_64!=((k>>6)&3))failed=1;
#endif
 sys(4,1,(long)bytes,3);
}
sys(1,failed,0,0);__builtin_unreachable();}
'''
outputs={}
for policy,t in [('old',old),('new',new)]:
 p=w/(policy+'.cpp');p.write_text(prefix+t+helper);outputs[policy]={}
 for arch,cc,runner in [('x86','g++',[]),('ppc','/srv/data1/tabor-build/linux-live-001/tools/cxx-reference-002/bin/powerpc-linux-gnuspe-g++',['qemu-ppc','-cpu','e500v2'])]:
  exe=w/(policy+'-'+arch)
  subprocess.run([cc,'-std=c++17','-O2','-ffreestanding','-nostdlib','-static','-fno-pie','-no-pie','-fno-stack-protector','-fno-exceptions','-fno-rtti']+(['-mstackrealign'] if arch=='x86' else [])+(['-DOLD'] if policy=='old' else [])+[str(p),'-o',str(exe)],check=True)
  r=subprocess.run(runner+[str(exe)],capture_output=True,check=True);assert len(r.stdout)==768;outputs[policy][arch]=r.stdout
assert outputs['new']['x86']==outputs['new']['ppc'];assert outputs['old']['x86']==outputs['new']['x86'];assert outputs['old']['ppc']!=outputs['new']['ppc']
r={'status':'PASS','cases_per_arch':256,'actual_source_type':'aco::float_mode','old_be_layout_mismatch':True,'new_encode_decode_exact':True,'le_unchanged':True,'source_sha256':hashlib.sha256(s.encode()).hexdigest(),'patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),'hardware_causality':'not established','applied_to_mesa':False,'old_be_default_keep_denorm_register':outputs['old']['ppc'][240*3],'correct_default_keep_denorm_register':240}
(w/'float-mode-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
