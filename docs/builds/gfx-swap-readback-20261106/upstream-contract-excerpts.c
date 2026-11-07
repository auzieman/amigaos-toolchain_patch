static int gfx_v8_0_cp_gfx_resume(struct amdgpu_device *adev)
{
	struct amdgpu_ring *ring;
	u32 tmp;
	u32 rb_bufsz;
	u64 rb_addr, rptr_addr, wptr_gpu_addr;

	/* Set the write pointer delay */
	WREG32(mmCP_RB_WPTR_DELAY, 0);

	/* set the RB to use vmid 0 */
	WREG32(mmCP_RB_VMID, 0);

	/* Set ring buffer size */
	ring = &adev->gfx.gfx_ring[0];
	rb_bufsz = order_base_2(ring->ring_size / 8);
	tmp = REG_SET_FIELD(0, CP_RB0_CNTL, RB_BUFSZ, rb_bufsz);
	tmp = REG_SET_FIELD(tmp, CP_RB0_CNTL, RB_BLKSZ, rb_bufsz - 2);
	tmp = REG_SET_FIELD(tmp, CP_RB0_CNTL, MTYPE, 3);
	tmp = REG_SET_FIELD(tmp, CP_RB0_CNTL, MIN_IB_AVAILSZ, 1);
#ifdef __BIG_ENDIAN
	tmp = REG_SET_FIELD(tmp, CP_RB0_CNTL, BUF_SWAP, 1);
#endif
	WREG32(mmCP_RB0_CNTL, tmp);

	/* Initialize the ring buffer's read and write pointers */
	WREG32(mmCP_RB0_CNTL, tmp | CP_RB0_CNTL__RB_RPTR_WR_ENA_MASK);
	ring->wptr = 0;
	WREG32(mmCP_RB0_WPTR, lower_32_bits(ring->wptr));

	/* set the wb address whether it's enabled or not */
	rptr_addr = ring->rptr_gpu_addr;
	WREG32(mmCP_RB0_RPTR_ADDR, lower_32_bits(rptr_addr));
	WREG32(mmCP_RB0_RPTR_ADDR_HI, upper_32_bits(rptr_addr) & 0xFF);

	wptr_gpu_addr = ring->wptr_gpu_addr;
	WREG32(mmCP_RB_WPTR_POLL_ADDR_LO, lower_32_bits(wptr_gpu_addr));
	WREG32(mmCP_RB_WPTR_POLL_ADDR_HI, upper_32_bits(wptr_gpu_addr));
	mdelay(1);
	WREG32(mmCP_RB0_CNTL, tmp);

	rb_addr = ring->gpu_addr >> 8;
	WREG32(mmCP_RB0_BASE, rb_addr);
	WREG32(mmCP_RB0_BASE_HI, upper_32_bits(rb_addr));

	gfx_v8_0_set_cpg_door_bell(adev, ring);
	/* start the ring */
	amdgpu_ring_clear_ring(ring);
	gfx_v8_0_cp_gfx_start(adev);

	return 0;
}


static u64 gfx_v8_0_ring_get_rptr(struct amdgpu_ring *ring)
{
	return *ring->rptr_cpu_addr;
}

static u64 gfx_v8_0_ring_get_wptr_gfx(struct amdgpu_ring *ring)
{
	struct amdgpu_device *adev = ring->adev;

	if (ring->use_doorbell)
		/* XXX check if swapping is necessary on BE */
		return *ring->wptr_cpu_addr;
	else
		return RREG32(mmCP_RB0_WPTR);
}

static void gfx_v8_0_ring_set_wptr_gfx(struct amdgpu_ring *ring)
{
	struct amdgpu_device *adev = ring->adev;

	if (ring->use_doorbell) {
		/* XXX check if swapping is necessary on BE */
		*ring->wptr_cpu_addr = lower_32_bits(ring->wptr);
		WDOORBELL32(ring->doorbell_index, lower_32_bits(ring->wptr));
	} else {
		WREG32(mmCP_RB0_WPTR, lower_32_bits(ring->wptr));
		(void)RREG32(mmCP_RB0_WPTR);
	}
}


static inline void amdgpu_ring_clear_ring(struct amdgpu_ring *ring)
{
	memset32(ring->ring, ring->funcs->nop, ring->buf_mask + 1);
}

static inline void amdgpu_ring_clear_ring_and_ptrs(struct amdgpu_ring *ring)
{
	/* Clear the contents of the ring. */
	amdgpu_ring_clear_ring(ring);

	/* Clear the ring pointers on the CPU. */
	ring->wptr = 0;

	/*
	 * Clear the ring pointers allocated in writeback.
	 *
	 * Note: we always allocate 64 bits for these pointers,
	 * but older HW generations only use the lower 32 bits.
	 * Use 64-bit atomics for simplicity.
	 */
	atomic64_set((atomic64_t *)ring->wptr_cpu_addr, 0);
	atomic64_set((atomic64_t *)ring->rptr_cpu_addr, 0);
}

static inline void amdgpu_ring_write(struct amdgpu_ring *ring, uint32_t v)
{
	ring->ring[ring->wptr++ & ring->buf_mask] = v;
	ring->wptr &= ring->ptr_mask;
	ring->count_dw--;
}

static inline void amdgpu_ring_write_multiple(struct amdgpu_ring *ring,
					      void *src, int count_dw)
{
	unsigned occupied, chunk1, chunk2;

	occupied = ring->wptr & ring->buf_mask;
	chunk1 = ring->buf_mask + 1 - occupied;
	chunk1 = (chunk1 >= count_dw) ? count_dw : chunk1;
	chunk2 = count_dw - chunk1;
	chunk1 <<= 2;
	chunk2 <<= 2;

	if (chunk1)
		memcpy(&ring->ring[occupied], src, chunk1);

	if (chunk2) {
		src += chunk1;
		memcpy(ring->ring, src, chunk2);
	}

	ring->wptr += count_dw;
	ring->wptr &= ring->ptr_mask;
	ring->count_dw -= count_dw;
}
