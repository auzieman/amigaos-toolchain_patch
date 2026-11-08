/*
 * Copyright 2014 Advanced Micro Devices, Inc.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * THE COPYRIGHT HOLDER(S) OR AUTHOR(S) BE LIABLE FOR ANY CLAIM, DAMAGES OR
 * OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 * ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 *
 * Authors: Christian König <christian.koenig@amd.com>
 */

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
struct funcs {u32 nop;int init_cond_exec;unsigned type;};
struct amdgpu_ring;struct inst {struct amdgpu_ring *ring_enc;};
struct amdgpu_device { unsigned usec_timeout;unsigned asic_type;struct {struct inst *inst;} uvd; };
struct amdgpu_ring {struct amdgpu_device *adev;u32 *ring;u32 *cond_exe_cpu_addr;struct funcs *funcs;u64 wptr;u64 ptr_mask;unsigned buf_mask;int count_dw;unsigned ring_size;};

void *memcpy(void *d,const void *s,__SIZE_TYPE__ n){unsigned char *a=d;const unsigned char *b=s;while(n--)*a++=*b++;return d;}

void *memset(void*p,int c,__SIZE_TYPE__ n){volatile unsigned char*b=p;for(__SIZE_TYPE__ i=0;i<n;i++)b[i]=c;return p;}
#define false 0
#define true 1
#define CHIP_POLARIS11 1
#define AMDGPU_RING_TYPE_GFX 0
#define AMDGPU_RING_TYPE_KIQ 1
#define AMDGPU_RING_TYPE_COMPUTE 2
#define AMDGPU_RING_TYPE_UVD 3
#define AMDGPU_RING_TYPE_UVD_ENC 4
#define AMDGPU_RING_TYPE_SDMA 5
#define upper_32_bits(x) ((u32)((u64)(x)>>32))
#define lower_32_bits(x) ((u32)(x))
#define AMDGPU_FENCE_FLAG_64BIT 1
#define AMDGPU_JOB_GET_VMID(job) ((job)->vmid)
struct amdgpu_job {unsigned vmid;};
struct amdgpu_ib {u64 gpu_addr;unsigned length_dw;u32 *ptr;};
#define ETIMEDOUT 110
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define __BIG_ENDIAN 4321
#endif
#define HEVC_ENC_CMD_NO_OP         0x00000000
#define HEVC_ENC_CMD_END           0x00000001
#define HEVC_ENC_CMD_FENCE         0x00000003
#define HEVC_ENC_CMD_TRAP          0x00000004
#define HEVC_ENC_CMD_IB_VM         0x00000102
#define HEVC_ENC_CMD_WAIT_GE       0x00000106
#define HEVC_ENC_CMD_UPDATE_PTB    0x00000107
#define HEVC_ENC_CMD_FLUSH_TLB     0x00000108
#define mmUVD_RB_RPTR2                                                          0x3c24
#define mmUVD_RB_WPTR2                                                          0x3c25
#define mmUVD_RB_RPTR                                                           0x3c29
#define mmUVD_RB_WPTR                                                           0x3c2a
static bool amdgpu_ring_uses_sw_le(struct amdgpu_ring *ring)
{
#ifdef __BIG_ENDIAN
	return ring->adev->asic_type == CHIP_POLARIS11 &&
	       (ring->funcs->type == AMDGPU_RING_TYPE_GFX ||
		ring->funcs->type == AMDGPU_RING_TYPE_KIQ ||
		ring->funcs->type == AMDGPU_RING_TYPE_COMPUTE);
#else
	return false;
#endif
}
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


static u32 register_bytes[4],read_start;
static u32 le_device_load(u32 raw){return cpu_to_le32(raw);}
static u32 mock_read(unsigned reg) {unsigned i=reg==mmUVD_RB_RPTR?0:1;return le_device_load(register_bytes[i]);}
static void mock_write(unsigned reg,u32 value){unsigned i=reg==mmUVD_RB_WPTR?2:3;register_bytes[i]=cpu_to_le32(value);}
#define RREG32(reg) ((void)adev,mock_read(reg))
#define WREG32(reg,value) do {(void)adev;mock_write(reg,value);}while(0)
#define udelay(n) do {(void)(n);}while(0)
static u64 uvd_v6_0_enc_ring_get_rptr(struct amdgpu_ring *ring)
{
	struct amdgpu_device *adev = ring->adev;

	if (ring == &adev->uvd.inst->ring_enc[0])
		return RREG32(mmUVD_RB_RPTR);
	else
		return RREG32(mmUVD_RB_RPTR2);
}
static void uvd_v6_0_enc_ring_set_wptr(struct amdgpu_ring *ring)
{
	struct amdgpu_device *adev = ring->adev;

	if (ring == &adev->uvd.inst->ring_enc[0])
		WREG32(mmUVD_RB_WPTR,
			lower_32_bits(ring->wptr));
	else
		WREG32(mmUVD_RB_WPTR2,
			lower_32_bits(ring->wptr));
}
static u32 amdgpu_ring_get_rptr(struct amdgpu_ring*r){return uvd_v6_0_enc_ring_get_rptr(r);}
static int amdgpu_ring_alloc(struct amdgpu_ring*r,int n){read_start=r->wptr;r->count_dw=n;return 0;}
static void amdgpu_ring_commit(struct amdgpu_ring*r) {
 u32 command=le_device_load(r->ring[read_start&r->buf_mask]);
 uvd_v6_0_enc_ring_set_wptr(r);
 if(command==HEVC_ENC_CMD_END) {
  unsigned i=r==&r->adev->uvd.inst->ring_enc[0]?0:1;
  register_bytes[i]=cpu_to_le32((u32)r->wptr);
 }
}
static int uvd_v6_0_enc_ring_test_ring(struct amdgpu_ring *ring)
{
	struct amdgpu_device *adev = ring->adev;
	uint32_t rptr;
	unsigned i;
	int r;

	r = amdgpu_ring_alloc(ring, 16);
	if (r)
		return r;

	rptr = amdgpu_ring_get_rptr(ring);

	amdgpu_ring_write(ring, HEVC_ENC_CMD_END);
	amdgpu_ring_commit(ring);

	for (i = 0; i < adev->usec_timeout; i++) {
		if (amdgpu_ring_get_rptr(ring) != rptr)
			break;
		udelay(1);
	}

	if (i >= adev->usec_timeout)
		r = -ETIMEDOUT;

	return r;
}
static void uvd_v6_0_enc_ring_insert_end(struct amdgpu_ring *ring)
{
	amdgpu_ring_write(ring, HEVC_ENC_CMD_END);
}
static void uvd_v6_0_enc_ring_emit_fence(struct amdgpu_ring *ring, u64 addr,
			u64 seq, unsigned flags)
{
	WARN_ON(flags & AMDGPU_FENCE_FLAG_64BIT);

	amdgpu_ring_write(ring, HEVC_ENC_CMD_FENCE);
	amdgpu_ring_write(ring, addr);
	amdgpu_ring_write(ring, upper_32_bits(addr));
	amdgpu_ring_write(ring, seq);
	amdgpu_ring_write(ring, HEVC_ENC_CMD_TRAP);
}
static void uvd_v6_0_enc_ring_emit_ib(struct amdgpu_ring *ring,
					struct amdgpu_job *job,
					struct amdgpu_ib *ib,
					uint32_t flags)
{
	unsigned vmid = AMDGPU_JOB_GET_VMID(job);

	amdgpu_ring_write(ring, HEVC_ENC_CMD_IB_VM);
	amdgpu_ring_write(ring, vmid);
	amdgpu_ring_write(ring, lower_32_bits(ib->gpu_addr));
	amdgpu_ring_write(ring, upper_32_bits(ib->gpu_addr));
	amdgpu_ring_write(ring, ib->length_dw);
}
void amdgpu_ring_insert_nop(struct amdgpu_ring *ring, uint32_t count)
{
	int i;

	for (i = 0; i < count; i++)
		amdgpu_ring_write(ring, ring->funcs->nop);
}
#define FIXED 0

int main(void) {
 u32 mem[2][64],shadow;struct funcs f={HEVC_ENC_CMD_NO_OP,1,AMDGPU_RING_TYPE_UVD_ENC};
 struct amdgpu_ring rings[2];struct inst inst={rings};struct amdgpu_device dev={4,CHIP_POLARIS11,{&inst}};
 for(unsigned ringid=0;ringid<2;ringid++) {
  struct amdgpu_ring*r=&rings[ringid];
  *r=(struct amdgpu_ring){.adev=&dev,.ring=mem[ringid],.cond_exe_cpu_addr=&shadow,.funcs=&f,.ptr_mask=0xffffffff,.buf_mask=63,.ring_size=256};
  for(unsigned start=0;start<64;start++) {
   r->wptr=start;register_bytes[ringid]=cpu_to_le32(start);
   amdgpu_ring_clear_ring(r);
   int result=uvd_v6_0_enc_ring_test_ring(r);
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
   int expected=FIXED?0:-ETIMEDOUT;
#else
   int expected=0;
#endif
   if(result!=expected)return 1;
   hex(ringid);hex(start);hex(result);hex(le_device_load(mem[ringid][start]));hex(amdgpu_ring_get_rptr(r));emit("\n",1);
  }
  if(FIXED || __BYTE_ORDER__ != __ORDER_BIG_ENDIAN__) {
   r->wptr=61;r->count_dw=32;
   struct amdgpu_job job={7};struct amdgpu_ib ib={0x000000ff12345678ULL,37,0};
   uvd_v6_0_enc_ring_emit_ib(r,&job,&ib,0);
   uvd_v6_0_enc_ring_emit_fence(r,0x000000ff87654320ULL,0x12345678,0);
   uvd_v6_0_enc_ring_insert_end(r);amdgpu_ring_insert_nop(r,3);
   u32 expected[]={HEVC_ENC_CMD_IB_VM,7,0x12345678,0xff,37,HEVC_ENC_CMD_FENCE,0x87654320,0xff,0x12345678,HEVC_ENC_CMD_TRAP,HEVC_ENC_CMD_END,0,0,0};
   for(unsigned i=0;i<14;i++)if(le_device_load(r->ring[(61+i)&63])!=expected[i])return 2;
  }
 }
 /* Predicate isolates this encoder: decoder/SDMA and other ASICs unchanged. */
 f.type=AMDGPU_RING_TYPE_UVD;if(amdgpu_ring_uses_sw_le(&rings[0]))return 3;
 f.type=AMDGPU_RING_TYPE_SDMA;if(amdgpu_ring_uses_sw_le(&rings[0]))return 4;
 f.type=AMDGPU_RING_TYPE_UVD_ENC;dev.asic_type=999;if(amdgpu_ring_uses_sw_le(&rings[0]))return 5;
 return failed?6:0;
}
