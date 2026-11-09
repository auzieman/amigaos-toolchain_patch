typedef unsigned int u32;typedef _Bool bool;
#define true 1
#define __force
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define cpu_to_le32(v) __builtin_bswap32((u32)(v))
#else
#define cpu_to_le32(v) ((u32)(v))
#endif
struct amdgpu_ring {volatile u32 *cond_exe_cpu_addr;bool selected;};
static bool amdgpu_ring_uses_sw_le(struct amdgpu_ring *r){return r->selected;}
static inline u32 amdgpu_ring_encode_dw(struct amdgpu_ring *ring, u32 value)
{
	return amdgpu_ring_uses_sw_le(ring) ? (__force u32)cpu_to_le32(value) : value;
}static inline void amdgpu_ring_set_preempt_cond_exec(struct amdgpu_ring *ring,
							bool cond_exec)
{
	*ring->cond_exe_cpu_addr = amdgpu_ring_encode_dw(ring, cond_exec);
}
static u32 words[4];
void _start(void){struct amdgpu_ring r={words,1};struct amdgpu_ring *ring=&r;
*ring->cond_exe_cpu_addr = 1;r.cond_exe_cpu_addr=&words[1];amdgpu_ring_set_preempt_cond_exec(ring,true);
r.cond_exe_cpu_addr=&words[2];amdgpu_ring_set_preempt_cond_exec(ring, true);
r.cond_exe_cpu_addr=&words[3];r.selected=0;amdgpu_ring_set_preempt_cond_exec(ring, true);
#if defined(__powerpc__)
register long nr asm("r0")=4;register long fd asm("r3")=1;register void *buf asm("r4")=words;register long len asm("r5")=16;
asm volatile("sc":"+r"(nr),"+r"(fd):"r"(buf),"r"(len):"memory","cr0");nr=1;fd=0;asm volatile("sc"::"r"(nr),"r"(fd):"memory");
#else
asm volatile("syscall"::"a"(1L),"D"(1L),"S"(words),"d"(16L):"rcx","r11","memory");asm volatile("syscall"::"a"(60L),"D"(0L):"rcx","r11","memory");
#endif
__builtin_unreachable();}
