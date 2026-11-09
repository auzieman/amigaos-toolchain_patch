typedef unsigned int u32;typedef unsigned long long uint64_t;typedef uint64_t __le64;
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
			pte[i] = amdgpu_vm_map_gart(p->pages_addr, addr);
			pte[i] |= flags;}
#if defined(__powerpc__)
register long nr asm("r0")=4,x asm("r3")=1,y asm("r4")=(long)output,z asm("r5")=sizeof(output);
asm volatile("sc" : "+r"(nr),"+r"(x),"+r"(y),"+r"(z) : : "memory","cr0","ctr","lr","xer","r6","r7","r8","r9","r10","r11","r12");nr=1;x=0;asm volatile("sc"::"r"(nr),"r"(x):"memory");
#else
asm volatile("syscall"::"a"(1L),"D"(1L),"S"(output),"d"((long)sizeof(output)):"rcx","r11","memory");asm volatile("syscall"::"a"(60L),"D"(0L):"rcx","r11","memory");
#endif
__builtin_unreachable();}
