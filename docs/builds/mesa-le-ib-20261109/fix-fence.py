from pathlib import Path
import subprocess,difflib,json,hashlib
w=Path('/srv/data1/tabor-build/linux-live-001/work/radeonsi-le-ib-20261109-001');p=w/'mesa-source/src/gallium/winsys/amdgpu/drm/amdgpu_cs.cpp';s=p.read_text();n=s
assert n.count('if (*user_fence_cpu >= afence->seq_no)')==1
n=n.replace('if (*user_fence_cpu >= afence->seq_no)', 'if (util_le64_to_cpu(*user_fence_cpu) >= afence->seq_no)')
n=n.replace('assert(afence->seq_no <= *user_fence_cpu);','assert(afence->seq_no <= util_le64_to_cpu(*user_fence_cpu));')
p.write_text(n);(w/'0005-decode-gpu-user-fence-le64.patch').write_text(''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/src/gallium/winsys/amdgpu/drm/amdgpu_cs.cpp',tofile='b/src/gallium/winsys/amdgpu/drm/amdgpu_cs.cpp')))
def fn(t):
 a=t.index('bool amdgpu_fence_wait(');i=t.index('{',a)+1;depth=1
 while depth:depth+=(t[i]=='{')-(t[i]=='}');i+=1
 return t[a:i]
prefix=r'''typedef unsigned long long uint64_t;typedef long long int64_t;typedef _Bool bool;
#define true 1
#define false 0
#define NULL ((void*)0)
#define INT64_MAX 0x7fffffffffffffffLL
#define OS_TIMEOUT_INFINITE (~0ULL)
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define util_le64_to_cpu(x) __builtin_bswap64(x)
#else
#define util_le64_to_cpu(x) (x)
#endif
struct pipe_fence_handle{int unused;};struct aws{int fd;struct{bool is_virtio;}info;};
struct amdgpu_fence{bool signalled;uint64_t seq_no;uint64_t *user_fence_cpu_address;int submitted;struct aws *aws;unsigned syncobj;};
static unsigned failed;
#define assert(v) do{if(!(v))failed=1;}while(0)
static int64_t os_time_get_absolute_timeout(uint64_t t){return t;}
static bool util_queue_fence_wait_timeout(void *p,int64_t t){return true;}
static int ac_drm_cs_syncobj_wait(int fd,void *p,unsigned n,int64_t t,int f,void *r){return -1;}
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
void _start(void){struct aws aws={0};unsigned false_positive=0;
 for(unsigned k=1;k<=4096;k++){
 uint64_t seq=((uint64_t)(k%3)<<32)|k;uint64_t mapped=util_le64_to_cpu(seq);
 struct amdgpu_fence pending={false,seq+1,&mapped,0,&aws,0};
 struct amdgpu_fence complete={false,seq,&mapped,0,&aws,0};
 bool a=amdgpu_fence_wait((struct pipe_fence_handle*)&pending,0,false);
 bool b=amdgpu_fence_wait((struct pipe_fence_handle*)&complete,0,false);
 if(a)false_positive++; assert(b);
#ifndef OLD
 assert(!a);assert(!pending.signalled);
#endif
 }
#if defined(OLD) && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
 assert(false_positive>0);
#else
 assert(false_positive==0);
#endif
 sys(1,failed,0,0);__builtin_unreachable();}
'''
for mode,t in [('old',s),('new',n)]:
 src=w/('fence-'+mode+'.c');src.write_text(prefix+fn(t)+main)
 for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc','-cpu','e500v2'])]:
  exe=w/('fence-'+mode+'-'+arch)
  subprocess.run([cc,'-O2','-ffreestanding','-nostdlib','-static','-fno-pie','-no-pie','-fno-stack-protector']+(['-mstackrealign'] if arch=='x86' else [])+(['-DOLD'] if mode=='old' else [])+[str(src),'-o',str(exe)],check=True)
  subprocess.run(runner+[str(exe)],check=True)
r={'status':'PASS','pending_cases_per_arch':4096,'completed_cases_per_arch':4096,'actual_function':'amdgpu_fence_wait','old_be_false_completion_reproduced':True,'new_pending_remains_pending':True,'completed_remains_completed':True,'limits':'Mapped fence memory and submission readiness modeled; ioctl timeout path stubbed; no physical causality claimed','source_sha256':hashlib.sha256(n.encode()).hexdigest()}
(w/'fence-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
