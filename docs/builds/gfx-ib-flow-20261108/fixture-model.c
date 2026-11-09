/* Model endpoints, not a GPU emulator or the kernel scheduler implementation. */
static u32 ring_word(struct amdgpu_ring *r,u32 n){return le32_to_cpu(r->ring[(ring_start+n)&127]);}
static u32 fetch_word(struct amdgpu_ib *ib,unsigned n,u32 swap){
 u32 value=le32_to_cpu(ib->ptr[n]);
 if(swap==2 && model!=1)value=__builtin_bswap32(value);
 return value;
}
static int amdgpu_ib_schedule(struct amdgpu_ring *r,unsigned n,struct amdgpu_ib *ib,
                              void *job,struct dma_fence **f){
 (void)job;if(n!=1)failed=1;
 if(model==3)for(unsigned i=0;i<ib->length_dw;i++)ib->ptr[i]=cpu_to_le32(ib->ptr[i]);
 if(r->engine==0){
  gfx_v8_0_ring_emit_ib_gfx(r,0,ib,0);
  gfx_v8_0_ring_emit_fence_gfx(r,0x5678abcd0040ULL,sequence,AMDGPU_FENCE_FLAG_INT);
 }else{
  gfx_v8_0_ring_emit_ib_compute(r,0,ib,0);
  gfx_v8_0_ring_emit_fence_compute(r,0x5678abcd0040ULL,sequence,AMDGPU_FENCE_FLAG_INT);
 }
 *f=&the_fence;
 u32 lo=ring_word(r,1),hi=ring_word(r,2),control=ring_word(r,3);
 u64 addr=((u64)hi<<32)|(lo&~3u);u32 swap=lo&3;
 if(ring_word(r,0)!=PACKET3(PACKET3_INDIRECT_BUFFER,2)||addr!=ib->gpu_addr||
    (control&0xfffff)!=5)failed=1;
 if(r->engine==1 && !(control&INDIRECT_BUFFER_VALID))failed=1;
 if(fetch_word(ib,0,swap)!=PACKET3(PACKET3_WRITE_DATA,3)||
    fetch_word(ib,1,swap)!=(WRITE_DATA_DST_SEL(5)|WR_CONFIRM)||
    fetch_word(ib,2,swap)!=lower_32_bits(r->adev->wb.gpu_addr)||
    fetch_word(ib,3,swap)!=upper_32_bits(r->adev->wb.gpu_addr)||
    fetch_word(ib,4,swap)!=0xDEADBEEF){wait_result=0;return 0;}
 r->adev->wb.wb[0]=cpu_to_le32(fetch_word(ib,4,swap));
 if(r->engine==0){
  if(ring_word(r,10)!=PACKET3(PACKET3_EVENT_WRITE_EOP,4)||
     ring_word(r,12)!=0xabcd0040|| (ring_word(r,13)&0xffff)!=0x5678||
     ring_word(r,14)!=sequence||ring_word(r,15)!=0)failed=1;
 }else{
  if(ring_word(r,4)!=PACKET3(PACKET3_RELEASE_MEM,5)||
     ring_word(r,7)!=0xabcd0040||ring_word(r,8)!=0x5678||
     ring_word(r,9)!=sequence||ring_word(r,10)!=0)failed=1;
 }
 fence_cell=cpu_to_le32(sequence);completed=1;
 wait_result=model==2?0:1;
 return 0;
}
