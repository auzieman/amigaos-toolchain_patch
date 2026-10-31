#define _GNU_SOURCE
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <stdint.h>
#include <sys/mman.h>
#include <unistd.h>
struct result { int cpu, error; double value; };
static void *worker(void *arg) {
 struct result *r=arg; cpu_set_t set; CPU_ZERO(&set); CPU_SET(r->cpu,&set);
 if (pthread_setaffinity_np(pthread_self(),sizeof set,&set)) {r->error=1;return 0;}
 const size_t bytes=64u*1024u*1024u; const long page=sysconf(_SC_PAGESIZE);
 if(page<=0) {r->error=2;return 0;}
 uint32_t *m=mmap(0,bytes,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
 if(m==MAP_FAILED) {r->error=3;return 0;}
 for(size_t off=0;off<bytes;off+=(size_t)page) m[off/4]=(uint32_t)off ^ (uint32_t)(r->cpu+1);
 volatile double value=0;
 for(int i=0;i<65536;i++) {value+=0.25; if(!(i%256)) sched_yield();}
 r->value=value;
 for(size_t off=0;off<bytes;off+=(size_t)page)
  if(m[off/4]!=((uint32_t)off ^ (uint32_t)(r->cpu+1))) r->error=4;
 if(sched_getcpu()!=r->cpu) r->error=5;
 if(value!=16384.0) r->error=6;
 munmap(m,bytes);return 0;
}
int main(void) {
 pthread_t threads[2]; struct result r[2]={{.cpu=0},{.cpu=1}};
 for(int i=0;i<2;i++) if(pthread_create(&threads[i],0,worker,&r[i]))return 10+i;
 for(int i=0;i<2;i++) if(pthread_join(threads[i],0))return 12+i;
 int failed=0;
 for(int i=0;i<2;i++) {printf("CPU%d affinity + 64MiB page pattern + SPE-built arithmetic: %s (error=%d value=%.0f)\n",i,r[i].error?"FAIL":"PASS",r[i].error,r[i].value);failed|=r[i].error;}
 puts("CPU affinity/arithmetic smoke only; not a full ABI, GPU or physical-board validation.");return failed?1:0;
}
