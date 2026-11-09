/* Test scaffolding only; production functions are extracted by review.py. */
typedef unsigned int u32; typedef unsigned long long u64;
typedef u32 uint32_t; typedef u64 uint64_t; typedef _Bool bool;
#define true 1
#define false 0
#define __force
#define EINVAL 22
#define ETIMEDOUT 110
#define NULL ((void *)0)
#define READ_ONCE(x) (*(volatile __typeof__(x) *)&(x))
#define atomic_read(p) (*(p))
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define __BIG_ENDIAN 4321
#define cpu_to_le32(x) __builtin_bswap32((u32)(x))
#define le32_to_cpu(x) __builtin_bswap32((u32)(x))
#else
#define cpu_to_le32(x) ((u32)(x))
#define le32_to_cpu(x) ((u32)(x))
#endif
#define lower_32_bits(x) ((u32)(x))
#define upper_32_bits(x) ((u32)((u64)(x)>>32))
#include "@VID@"
#include "@GFXENUM@"
#define AMDGPU_JOB_GET_VMID(job) 0
#define amdgpu_sriov_vf(adev) false
/* These flags/register are not activated by the actual no-job test caller. */
#define AMDGPU_IB_FLAG_CE 1
#define AMDGPU_IB_FLAG_PREEMPT 2
#define AMDGPU_IB_FLAG_RESET_GDS_MAX_WAVE_ID 4
#define mmGDS_COMPUTE_MAX_WAVE_ID 0
/* Copied from the pinned amdgpu_ring.h; review.py verifies these values. */
#define AMDGPU_FENCE_FLAG_64BIT (1 << 0)
#define AMDGPU_FENCE_FLAG_INT (1 << 1)
#define AMDGPU_FENCE_FLAG_EXEC (1 << 3)
#define AMDGPU_IB_POOL_DIRECT 0
struct amdgpu_device;
struct amdgpu_fence_driver { u32 *cpu_addr; u32 sync_seq, last_seq; };
struct amdgpu_ring {
 struct amdgpu_device *adev; const char *name;
 u32 *ring, wptr, ptr_mask, buf_mask; int count_dw, engine;
 struct amdgpu_fence_driver fence_drv;
};
struct amdgpu_device {
 struct {u32 *wb;u64 gpu_addr;} wb;
 struct {u32 gds_compute_max_wave_id;} gds;
 void *dev;
};
struct amdgpu_job {int unused;};
struct amdgpu_ib {u32 *ptr,length_dw,flags;u64 gpu_addr;};
struct dma_fence {int unused;};
static int failed,model,completed,wait_result,diagnostic_seen;
static u32 diagnostic_payload,diagnostic_fence,diagnostic_emitted;
static u32 ib_memory[8],fence_cell,ring_start,sequence;
static struct dma_fence the_fence;
static bool amdgpu_ring_uses_sw_le(struct amdgpu_ring *r){(void)r;return true;}
#define DRM_ERROR(...) do{failed=1;}while(0)
static void gfx_v8_0_ring_emit_de_meta(struct amdgpu_ring *r){(void)r;failed=1;}
static void capture(const char *name,u32 payload,u32 fence,u32 emitted,
                    u32 signaled,u32 lo,u32 hi,u32 length){
 (void)name;(void)signaled;(void)lo;(void)hi;
 if(length!=5)failed=1;
 diagnostic_seen=1;diagnostic_payload=payload;diagnostic_fence=fence;diagnostic_emitted=emitted;
}
#define dev_err(dev,fmt,...) capture(__VA_ARGS__)
void *memset(void *p,int v,__SIZE_TYPE__ n){
 volatile unsigned char *b=p;while(n--)*b++=v;return p;
}
static int amdgpu_device_wb_get(struct amdgpu_device *a,unsigned *i){(void)a;*i=0;return 0;}
static void amdgpu_device_wb_free(struct amdgpu_device *a,unsigned i){(void)a;(void)i;}
static int amdgpu_ib_get(struct amdgpu_device *a,void *vm,unsigned size,int pool,struct amdgpu_ib *ib){
 (void)a;(void)vm;(void)pool;if(size!=20)failed=1;
 ib->ptr=ib_memory;ib->gpu_addr=0x123456780000ULL+(u64)ring_start*256;
 return 0;
}
static void amdgpu_ib_free(struct amdgpu_device *a,struct amdgpu_ib *ib,void *f){(void)a;(void)ib;(void)f;}
static void dma_fence_put(struct dma_fence *f){(void)f;}
static long dma_fence_wait_timeout(struct dma_fence *f,bool intr,long timeout){
 (void)f;(void)intr;(void)timeout;return wait_result;
}
static int amdgpu_ib_schedule(struct amdgpu_ring *,unsigned,struct amdgpu_ib *,void *,struct dma_fence **);
