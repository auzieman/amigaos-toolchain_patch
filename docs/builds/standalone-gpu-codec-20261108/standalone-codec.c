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
struct amdgpu_device { unsigned usec_timeout; };
struct amdgpu_ring {struct amdgpu_device *adev;u32 *ring;u32 *cond_exe_cpu_addr;struct funcs *funcs;u64 wptr;u64 ptr_mask;unsigned buf_mask;int count_dw;unsigned ring_size;};
static int software_le;
static int amdgpu_ring_uses_sw_le(struct amdgpu_ring *r){(void)r;return software_le;}
void *memcpy(void *d,const void *s,__SIZE_TYPE__ n){unsigned char *a=d;const unsigned char *b=s;while(n--)*a++=*b++;return d;}
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
int main(void);
static void emit(const char *p, unsigned n) {
#ifdef __powerpc__
 register unsigned r0 __asm__("r0")=4;
 register unsigned r3 __asm__("r3")=1;
 register const char *r4 __asm__("r4")=p;
 register unsigned r5 __asm__("r5")=n;
 __asm__ volatile("sc" : "+r"(r0),"+r"(r3) : "r"(r4),"r"(r5) : "cr0","memory");
#else
 long result;
 __asm__ volatile("syscall" : "=a"(result) : "0"(1L),"D"(1L),"S"(p),"d"((unsigned long)n) : "rcx","r11","memory");
#endif
}
static void hex(uint32_t n) {
 char b[9];const char *digits="0123456789abcdef";
 for(unsigned i=0;i<8;i++) b[i]=digits[(n >> (28-i*4))&15];
 b[8]=' ';emit(b,9);
}
void _start(void) {
 int r=main();
#ifdef __powerpc__
 register unsigned r0 __asm__("r0")=1;
 register unsigned r3 __asm__("r3")=r;
 __asm__ volatile("sc" : "+r"(r0),"+r"(r3) : : "cr0","memory");
#else
 __asm__ volatile("syscall" : : "a"(60L),"D"((long)r) : "rcx","r11","memory");
#endif
 __builtin_unreachable();
}

#define mmUVD_CONTEXT_ID                                                        0x3dbd
#define PACKET0(reg, n) ((PACKET_TYPE0 << 30) |				\
                         ((reg) & 0xFFFF) |				\
                         ((n) & 0x3FFF) << 16)

#define ETIMEDOUT 110
#define PACKET_TYPE0 0
static u32 context,read_start;static int hardware_swap;
static u32 device_word(u32 raw) {
 u32 value=cpu_to_le32(raw); /* LE device load of native memory bytes */
 return hardware_swap?__builtin_bswap32(value):value;
}
#define WREG32(reg,value) do {(void)(reg);context=(value);}while(0)
#define RREG32(reg) ((void)(reg),context)
#define udelay(n) do {(void)(n);}while(0)
static int amdgpu_ring_alloc(struct amdgpu_ring*r,int n){r->count_dw=n;read_start=r->wptr;return 0;}
static void amdgpu_ring_commit(struct amdgpu_ring*r) {
 u32 header=device_word(r->ring[read_start&r->buf_mask]);
 if(header==PACKET0(mmUVD_CONTEXT_ID,0))
  context=device_word(r->ring[(read_start+1)&r->buf_mask]);
}
static int uvd_v6_0_ring_test_ring(struct amdgpu_ring *ring)
{
	struct amdgpu_device *adev = ring->adev;
	uint32_t tmp = 0;
	unsigned i;
	int r;

	WREG32(mmUVD_CONTEXT_ID, 0xCAFEDEAD);
	r = amdgpu_ring_alloc(ring, 3);
	if (r)
		return r;

	amdgpu_ring_write(ring, PACKET0(mmUVD_CONTEXT_ID, 0));
	amdgpu_ring_write(ring, 0xDEADBEEF);
	amdgpu_ring_commit(ring);
	for (i = 0; i < adev->usec_timeout; i++) {
		tmp = RREG32(mmUVD_CONTEXT_ID);
		if (tmp == 0xDEADBEEF)
			break;
		udelay(1);
	}

	if (i >= adev->usec_timeout)
		r = -ETIMEDOUT;

	return r;
}
int main(void) {
 u32 memory[8],shadow;struct funcs f={0x80000000,1};
 struct amdgpu_device dev={4};
 struct amdgpu_ring r={.adev=&dev,.ring=memory,.cond_exe_cpu_addr=&shadow,.funcs=&f,.ptr_mask=0xffffffff,.buf_mask=7,.ring_size=32};
 unsigned cases=0;
 for(unsigned mode=0;mode<4;mode++)for(unsigned start=0;start<8;start++) {
  software_le=(mode==1||mode==3);
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
  hardware_swap=(mode==0||mode==3);
  int expected=mode<2?0:-ETIMEDOUT;
#else
  hardware_swap=0;int expected=0;
#endif
  r.wptr=start;amdgpu_ring_clear_ring(&r);
  int result=uvd_v6_0_ring_test_ring(&r);
  hex(mode);hex(start);hex(result);hex(context);emit("\n",1);
  if(result!=expected)return 1;
  cases++;
 }
 /* Exercise actual bulk, wrap, conditional patch and shadow writers. */
 software_le=1;r.wptr=6;r.count_dw=32;
 amdgpu_ring_clear_ring(&r);
 u32 words[]={0xc0017900,0x40,0xdeadbeef};
 amdgpu_ring_write_multiple(&r,words,3);
 r.wptr=2;amdgpu_ring_write(&r,0);amdgpu_ring_write(&r,0x12345678);
 amdgpu_ring_patch_cond_exec(&r,2);amdgpu_ring_set_preempt_cond_exec(&r,1);
 if(cpu_to_le32(memory[6])!=words[0]||cpu_to_le32(memory[7])!=words[1]||cpu_to_le32(memory[0])!=words[2]||cpu_to_le32(memory[2])!=1||cpu_to_le32(shadow)!=1||failed)return 2;
 return cases==32?0:3;
}
