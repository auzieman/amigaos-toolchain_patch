from pathlib import Path
import difflib,subprocess,hashlib,json
p=Path('/srv/data1/tabor-build/linux-live-001/work/radeonsi-aco-20261109-001/mesa-source/src/gallium/drivers/radeonsi/si_shader.c');s=p.read_text();w=Path('/home/owner/radeonsi-aco-boundary-20261109');w.mkdir(exist_ok=True)
needle='''      exec_offset += bin[i]->exec_size;''';assert s.count(needle)==1
insert='''#if UTIL_ARCH_BIG_ENDIAN
      /* ACO raw instructions and symbol fixups are CPU-native words.
       * Serialize only executable words after relocation. Constant-data
       * bytes and cached CPU-side binaries retain their own layouts.
       */
      assert(bin[i]->exec_size % 4 == 0);
      uint32_t *exec = (uint32_t *)(rx_ptr + exec_offset);
      for (unsigned j = 0; j < bin[i]->exec_size / 4; j++)
         exec[j] = util_cpu_to_le32(exec[j]);
#endif

'''+needle
new=s.replace(needle,insert);patch=''.join(difflib.unified_diff(s.splitlines(True),new.splitlines(True),fromfile='a/src/gallium/drivers/radeonsi/si_shader.c',tofile='b/src/gallium/drivers/radeonsi/si_shader.c'));(w/'0001-radeonsi-serialize-aco-exec-after-relocation.patch').write_text(patch)
def fn(t):
 a=t.index('static int upload_binary_raw(');i=t.index('{',a)+1;n=1
 while n:n+=(t[i]=='{')-(t[i]=='}');i+=1
 return t[a:i]
prefix=r'''typedef unsigned int uint32_t;typedef unsigned long long uint64_t;typedef long long int64_t;typedef _Bool bool;
#define NULL ((void *)0)
#define true 1
#define false 0
#define SI_SHADER_BINARY_RAW 1
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define UTIL_ARCH_BIG_ENDIAN 1
#define util_cpu_to_le32(v) __builtin_bswap32((uint32_t)(v))
#else
#define UTIL_ARCH_BIG_ENDIAN 0
#define util_cpu_to_le32(v) (v)
#endif
static unsigned failed;
#define assert(v) do{if(!(v))failed=1;}while(0)
void *memcpy(void *d,const void *s,__SIZE_TYPE__ n){unsigned char *a=d;const unsigned char *b=s;while(n--)*a++=*b++;return d;}
struct si_shader_binary{unsigned type,code_size,exec_size,num_symbols;char *code_buffer;};
struct si_shader{struct si_shader_binary binary;struct si_shader *previous_stage;};
struct si_screen{int unused;};struct si_context{int unused;};struct pipe_resource{int unused;};
static unsigned char output[64];static struct si_shader *other;
static unsigned get_shader_binaries(struct si_shader *s,struct si_shader_binary **b){b[0]=&s->binary;b[1]=&other->binary;return 2;}
static void *pre_upload_binary(struct si_screen *a,struct si_shader*b,unsigned n,bool d,struct si_context **c,struct pipe_resource **p,unsigned *o,int64_t bo){return output;}
static void post_upload_binary(struct si_screen*a,struct si_shader*b,void*c,unsigned n,unsigned m,bool d,struct si_context*e,struct pipe_resource*f,unsigned g){}
static void calculate_needed_lds_size(struct si_screen*a,struct si_shader*b){}
static void si_aco_resolve_symbols(struct si_shader *s,void *dest,const uint32_t *src,uint64_t scratch,unsigned offset){((uint32_t*)dest)[1]=0x12345600+(unsigned)scratch;}
'''
main=r'''
static long syscall3(long n,long a,long b,long c){
#if defined(__powerpc__)
register long nr asm("r0")=n;register long x asm("r3")=a;register long y asm("r4")=b;register long z asm("r5")=c;
asm volatile("sc":"+r"(x),"+r"(nr),"+r"(y),"+r"(z)::"memory","cr0","ctr","lr","xer","r6","r7","r8","r9","r10","r11","r12");return x;
#else
long r;asm volatile("syscall":"=a"(r):"a"(n==4?1:60),"D"(a),"S"(b),"d"(c):"rcx","r11","memory");return r;
#endif
}
void _start(void){
 for(unsigned k=0;k<64;k++){
 uint32_t a[]={0xbf810000+k,0,0};uint32_t b[]={0xbe800000+k,0,0};
 unsigned char data_a[]={0x11,0x22,0x33,0x44};unsigned char data_b[]={0xa0,0xb1,0xc2,0xd3,0xe4,0xf5,0x16,0x27};
 memcpy((char*)a+8,data_a,4);memcpy((char*)b+4,data_b,8);
 struct si_shader first={{1,12,8,1,(char*)a},0},second={{1,12,4,0,(char*)b},0};other=&second;
 assert(upload_binary_raw(0,&first,k,0,-1)==24);
 assert(a[1]==0);assert(output[12]==0x11 && output[16]==0xa0 && output[23]==0x27);
 syscall3(4,1,(long)output,24);
 }
 syscall3(1,failed,0,0);__builtin_unreachable();}
'''
results={}
for policy,t in [('old',s),('new',new)]:
 src=w/(policy+'.c');src.write_text(prefix+fn(t)+main);out={}
 for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc','-cpu','e500v2'])]:
  exe=w/(policy+'-'+arch);subprocess.run([cc]+(['-mstackrealign'] if arch=='x86' else [])+['-O2','-ffreestanding','-nostdlib','-static','-fno-pie','-no-pie','-fno-stack-protector',str(src),'-o',str(exe)],check=True)
  r=subprocess.run(runner+[str(exe)],capture_output=True,check=True);assert len(r.stdout)==64*24;out[arch]=r.stdout
 results[policy]=out
assert results['new']['x86']==results['new']['ppc']
assert results['old']['x86']!=results['old']['ppc']
assert results['old']['x86']==results['new']['x86']
r={'status':'PASS','cases_per_arch':64,'source_sha256':hashlib.sha256(s.encode()).hexdigest(),'patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),'controls':['old raw upload differs BE vs LE','new executable bytes identical BE vs LE','LE behavior unchanged','relocated words serialized after fixup','mixed constant-data bytes untouched','cached input binary not modified'],'scope':'Actual upload_binary_raw function; compiler, allocator, relocation and publication endpoints modeled','hardware_tested':False}
(w/'check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
