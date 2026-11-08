typedef _Bool bool;typedef unsigned int u32;typedef unsigned long long u64;typedef unsigned int uint32_t;
#define __force
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define cpu_to_le32(x) __builtin_bswap32(x)
#else
#define cpu_to_le32(x) (x)
#endif
#define unlikely(x) (x)
#define DRM_ERROR(...) do { failed=1; }while(0)
#define WARN_ON(x) do {if(x)failed=1;}while(0)
static int failed;
struct funcs {u32 nop;int init_cond_exec;};
struct amdgpu_ring {u32 *ring;u32 *cond_exe_cpu_addr;struct funcs *funcs;u64 wptr;u64 ptr_mask;unsigned buf_mask;int count_dw;unsigned ring_size;};
static int amdgpu_ring_uses_sw_le(struct amdgpu_ring *r){return 1;}
void *memcpy(void *d,const void *s,unsigned long n){unsigned char *a=d;const unsigned char *b=s;while(n--)*a++=*b++;return d;}
static inline u32 amdgpu_ring_encode_dw(struct amdgpu_ring *ring, u32 value)
{
	return amdgpu_ring_uses_sw_le(ring) ? (__force u32)cpu_to_le32(value) : value;
}

static inline void amdgpu_ring_set_preempt_cond_exec(struct amdgpu_ring *ring,
							bool cond_exec)
{
	*ring->cond_exe_cpu_addr = amdgpu_ring_encode_dw(ring, cond_exec);
}

static inline void amdgpu_ring_clear_ring(struct amdgpu_ring *ring)
{
	int i = 0;
	while (i <= ring->buf_mask)
		ring->ring[i++] = amdgpu_ring_encode_dw(ring, ring->funcs->nop);

}

static inline void amdgpu_ring_write(struct amdgpu_ring *ring, uint32_t v)
{
	if (ring->count_dw <= 0)
		DRM_ERROR("amdgpu: writing more dwords to the ring than expected!\n");
	ring->ring[ring->wptr++ & ring->buf_mask] = amdgpu_ring_encode_dw(ring, v);
	ring->wptr &= ring->ptr_mask;
	ring->count_dw--;
}

static inline void amdgpu_ring_write_multiple(struct amdgpu_ring *ring,
					      void *src, int count_dw)
{
	unsigned occupied, chunk1, chunk2;
	void *dst;

	if (amdgpu_ring_uses_sw_le(ring)) {
		const u32 *words = src;
		int i;

		for (i = 0; i < count_dw; i++)
			amdgpu_ring_write(ring, words[i]);
		return;
	}

	if (unlikely(ring->count_dw < count_dw))
		DRM_ERROR("amdgpu: writing more dwords to the ring than expected!\n");

	occupied = ring->wptr & ring->buf_mask;
	dst = (void *)&ring->ring[occupied];
	chunk1 = ring->buf_mask + 1 - occupied;
	chunk1 = (chunk1 >= count_dw) ? count_dw : chunk1;
	chunk2 = count_dw - chunk1;
	chunk1 <<= 2;
	chunk2 <<= 2;

	if (chunk1)
		memcpy(dst, src, chunk1);

	if (chunk2) {
		src += chunk1;
		dst = (void *)ring->ring;
		memcpy(dst, src, chunk2);
	}

	ring->wptr += count_dw;
	ring->wptr &= ring->ptr_mask;
	ring->count_dw -= count_dw;
}

static inline unsigned int amdgpu_ring_get_dw_distance(struct amdgpu_ring *ring,
						       u64 start_wptr, u64 end_wptr)
{
	unsigned int start = start_wptr & ring->buf_mask;
	unsigned int end = end_wptr & ring->buf_mask;

	if (end < start)
		end += ring->ring_size >> 2;
	return end - start;
}

/**
 * amdgpu_ring_patch_cond_exec - patch dw count of conditional execute
 * @ring: amdgpu_ring structure
 * @offset: offset returned by amdgpu_ring_init_cond_exec
 *
 * Calculate the dw count and patch it into a cond_exec command.
 */
static inline void amdgpu_ring_patch_cond_exec(struct amdgpu_ring *ring,
					       unsigned int offset)
{
	if (!ring->funcs->init_cond_exec)
		return;

	WARN_ON(offset > ring->buf_mask);
	WARN_ON(ring->ring[offset] != 0);

	ring->ring[offset] = amdgpu_ring_encode_dw(ring,
		amdgpu_ring_get_dw_distance(ring, offset, ring->wptr - 1));
}

static u32 output[9];
static void run(void){struct funcs f={0x80000000,1};struct amdgpu_ring r={output,&output[8],&f,0,0xffffffff,7,32,32};u32 words[3]={0xc0017900,0x40,0xdeadbeef};
amdgpu_ring_clear_ring(&r);r.wptr=6;amdgpu_ring_write_multiple(&r,words,3);r.wptr=2;amdgpu_ring_write(&r,0);amdgpu_ring_write(&r,0x12345678);amdgpu_ring_patch_cond_exec(&r,2);amdgpu_ring_set_preempt_cond_exec(&r,1);if(r.wptr!=4||r.count_dw!=27)failed=1;}
#ifdef __powerpc__
void _start(void){run();register unsigned r0 __asm__("r0")=4;register unsigned r3 __asm__("r3")=1;register void *r4 __asm__("r4")=output;register unsigned r5 __asm__("r5")=sizeof(output);__asm__ volatile("sc" : "+r"(r0),"+r"(r3):"r"(r4),"r"(r5):"memory","cr0");r0=1;r3=failed;__asm__ volatile("sc"::"r"(r0),"r"(r3):"memory");for(;;){}}
#else
#include <unistd.h>
int main(void){run();return write(1,output,sizeof(output))!=sizeof(output)||failed;}
#endif
