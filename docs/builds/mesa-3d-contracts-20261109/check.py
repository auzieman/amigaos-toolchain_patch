from pathlib import Path
import subprocess,json,hashlib
w=Path('/srv/data1/tabor-build/linux-live-001/work/mesa-3d-contracts-20261109-001')
def fn(s,name):
 pos=s.index(name+'(');a=s.rfind('static ',0,pos);i=s.index('{',pos)+1;depth=1
 while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
 return s[a:i]
prefix=r'''typedef unsigned int uint32_t;typedef unsigned long long uint64_t;typedef _Bool bool;
#define true 1
#define false 0
#define NULL ((void*)0)
#define PIPE_QUERY_OCCLUSION_COUNTER 1
#define PIPE_QUERY_OCCLUSION_PREDICATE 2
#define PIPE_QUERY_OCCLUSION_PREDICATE_CONSERVATIVE 3
#define PIPE_MAP_WRITE 1
#define PIPE_MAP_UNSYNCHRONIZED 2
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define util_cpu_to_le32(x) __builtin_bswap32((uint32_t)(x))
#define util_le32_to_cpu(x) __builtin_bswap32((uint32_t)(x))
#define util_le64_to_cpu(x) __builtin_bswap64((uint64_t)(x))
#else
#define util_cpu_to_le32(x) (x)
#define util_le32_to_cpu(x) (x)
#define util_le64_to_cpu(x) (x)
#endif
struct si_resource{struct{struct{unsigned width0;}b;}b;void *buf;};
struct si_query_buffer{struct si_resource *buf;};
struct si_query_hw{struct{unsigned type;}b;struct si_query_buffer buffer;unsigned result_size;};
#define container_of(p,t,m) ((t*)((char*)(p)-__builtin_offsetof(t,m)))
struct winsys{void *(*buffer_map)(void*,void*,void*,unsigned);};
struct si_screen{struct winsys *ws;struct{unsigned max_render_backends;uint64_t enabled_rb_mask;}info;};
struct si_context{struct si_screen *screen;void *ws;};
struct si_query_counter{unsigned base,stride,qwords;};
struct si_query_pc{unsigned num_counters;struct si_query_counter *counters;};
struct batch_result{uint64_t u64;};
union pipe_query_result{uint64_t u64;struct batch_result *batch;};
static unsigned char bytes[128];
void *memset(void *p,int v,__SIZE_TYPE__ n){unsigned char *b=p;while(n--)*b++=v;return p;}
static void *map(void*a,void*b,void*c,unsigned d){return bytes;}
static long sys(long n,long a,long b,long c){
#if defined(__powerpc__)
register long nr asm("r0")=n;register long x asm("r3")=a;register long y asm("r4")=b;register long z asm("r5")=c;
asm volatile("sc":"+r"(x),"+r"(nr),"+r"(y),"+r"(z)::"memory","cr0","ctr","lr","xer","r6","r7","r8","r9","r10","r11","r12");return x;
#else
long r;asm volatile("syscall":"=a"(r):"a"(n==4?1:60),"D"(a),"S"(b),"d"(c):"rcx","r11","memory");return r;
#endif
}
static unsigned bad, badline;
#define check(x) do{if(!(x)){if(!bad)badline=__LINE__;bad++;}}while(0)
static void store64(unsigned off,uint64_t value){for(unsigned j=0;j<8;j++)bytes[off+j]=(value>>(j*8))&255;}
'''
main=r'''
void _start(void){struct winsys ws={map};struct si_screen screen={&ws,{4,5}};struct si_context ctx={&screen,0};struct si_resource bo={{{128}},0};
 for(unsigned type=1;type<=3;type++)for(unsigned mask=0;mask<16;mask++){
  struct si_query_hw q={{type},{&bo},64};screen.info.enabled_rb_mask=mask;
  check(si_query_hw_prepare_buffer(&ctx,&q.buffer));
  for(unsigned row=0;row<2;row++)for(unsigned rb=0;rb<4;rb++){
   unsigned off=row*64+rb*16;
   /* GPU-visible status high bit is byte7/15 in LE, not native u32 storage. */
   check(bytes[off+7]==((mask&(1<<rb))?0:128));check(bytes[off+15]==((mask&(1<<rb))?0:128));
   check(bytes[off+4]==0 && bytes[off+12]==0);
  }
 }
 for(unsigned k=0;k<1024;k++)for(unsigned status=0;status<4;status++){
  uint64_t first=0x100000000ULL+k*3, last=first+19+k;
  if(status&1)first|=0x8000000000000000ULL;if(status&2)last|=0x8000000000000000ULL;
  store64(0,first);store64(8,last);
  check(si_query_read_result(bytes,0,2,true)==(status==3?19+k:0));
  check(si_query_read_result(bytes,0,2,false)==(unsigned)(last-first));
  store64(0,0x1234567800000000ULL+k);check(read_timestamp(bytes)==0x1234567800000000ULL+k);
  struct si_query_counter counters[2]={{0,2,2},{1,2,2}};struct si_query_pc pc={2,counters};
  union pipe_query_result result;struct batch_result batch[2]={{0},{0}};result.batch=batch;
  store64(0,k+1);store64(8,k+2);store64(16,k+3);store64(24,k+4);
  si_pc_query_add_result(&pc,bytes,&result);check(batch[0].u64==2*k+4);check(batch[1].u64==2*k+6);
 }
sys(4,1,(long)&badline,4);
#ifdef OLD
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
 check(bad>0);sys(1,bad?0:1,0,0);
#else
 sys(1,bad?1:0,0,0);
#endif
#else
 sys(1,bad?1:0,0,0);
#endif
 __builtin_unreachable();}
'''
for mode in ['before','after']:
 q=(w/('query-'+mode+'.c')).read_text();p=(w/('perfcounter-'+mode+'.c')).read_text()
 assignment=next(x.strip() for x in q.splitlines() if 'result->u64 =' in x and 'buffer' in x)
 timestamp='static uint64_t read_timestamp(void *buffer){ union pipe_query_result r; union pipe_query_result *result=&r; '+assignment+' return r.u64;}\n'
 source=prefix+fn(q,'si_query_hw_prepare_buffer')+fn(q,'si_query_read_result')+fn(p,'si_pc_query_add_result')+timestamp+main
 src=w/('query-contract-'+mode+'.c');src.write_text(source)
 for arch,cc,runner in [('x86','gcc',[]),('ppc','/srv/data1/tabor-build/linux-live-001/tools/cxx-reference-002/bin/powerpc-linux-gnuspe-gcc',['qemu-ppc','-cpu','e500v2'])]:
  exe=w/('query-contract-'+mode+'-'+arch);subprocess.run([cc,'-O2','-ffreestanding','-nostdlib','-static','-fno-pie','-no-pie','-fno-stack-protector']+(['-mstackrealign'] if arch=='x86' else [])+(['-DOLD'] if mode=='before' else [])+[str(src),'-o',str(exe)],check=True);r=subprocess.run(runner+[str(exe)],capture_output=True)
  if r.returncode:
   line=int.from_bytes(r.stdout[:4],'big' if arch=='ppc' else 'little');print(mode,arch,'first failing fixture line',line,source.splitlines()[line-1] if line else '',flush=True);r.check_returncode()
r={'status':'PASS','prepare_cases_per_arch':48,'response_scenarios_per_arch':4096,'actual_source':['si_query_hw_prepare_buffer','si_query_read_result','si_pc_query_add_result','timestamp assignment from si_query_hw_add_result'],'controls':['old BE wire/status mismatch reproduced','unchanged x86 expectations pass','fixed BE status/counters/timestamp match known LE inputs','status missing/partial/complete cases','counter accumulation across base/stride/qwords'],'limits':'GPU status/counter writes and mapping endpoint modeled; no hardware or application query execution. Not a cause claim for attribute-free point hang.'}
(w/'query-contract-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
