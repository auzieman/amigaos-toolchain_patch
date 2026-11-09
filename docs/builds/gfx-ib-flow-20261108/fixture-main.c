static __attribute__((noinline)) void emit(const char *p,unsigned n){
#ifdef __powerpc__
 register unsigned r0 __asm__("r0")=4,r3 __asm__("r3")=1;
 register const char *r4 __asm__("r4")=p;register unsigned r5 __asm__("r5")=n;
 __asm__ volatile("sc":"+r"(r0),"+r"(r3),"+r"(r4),"+r"(r5)::
                  "r6","r7","r8","r9","r10","r11","r12","ctr","cr0","memory");
#else
 long result;__asm__ volatile("syscall":"=a"(result):"0"(1L),"D"(1L),"S"(p),"d"((unsigned long)n):"rcx","r11","memory");
#endif
}
static int main(void){
 u32 words[128],payload;
 struct amdgpu_device a={.wb={&payload,0x5678abcd0000ULL}};
 struct amdgpu_ring r={.adev=&a,.name="fixture",.ring=words,.ptr_mask=0xffffffff,.buf_mask=127};
 u32 seqs[]={1,128,0x12345678,0xfffffffe};unsigned cases=0;
 for(unsigned version=0;version<2;version++)for(unsigned engine=0;engine<2;engine++)
 for(model=0;model<4;model++)for(unsigned start=0;start<8;start++)for(unsigned sn=0;sn<4;sn++){
  ring_start=start*17;sequence=seqs[sn];r.wptr=ring_start;r.count_dw=128;r.engine=engine;
  r.fence_drv.cpu_addr=&fence_cell;r.fence_drv.sync_seq=sequence;r.fence_drv.last_seq=0;
  completed=0;fence_cell=0;diagnostic_seen=0;wait_result=0;
  long got=version?test_candidate(&r,1000):test_original(&r,1000);
  int expect=0;
  if(model==2)expect=-ETIMEDOUT;
#ifdef __BIG_ENDIAN
  if(model==1||model==3)expect=-ETIMEDOUT;
  if(version==0 && model==0)expect=-EINVAL;
#endif
  if(got!=expect||failed)return 1;
  if(amdgpu_fence_read(&r)!=(completed?sequence:0))return 2;
  if(version && expect==-ETIMEDOUT){
   if(!diagnostic_seen||diagnostic_payload!=(completed?0xDEADBEEF:0xCAFEDEAD)||
      diagnostic_fence!=(completed?sequence:0)||diagnostic_emitted!=sequence)return 3;
  }
  if(version && model==0){emit((char*)&payload,4);emit((char*)&fence_cell,4);}
  cases++;
 }
 return cases==512?0:4;
}
void _start(void){
 int result=main();
#ifdef __powerpc__
 register unsigned r0 __asm__("r0")=1,r3 __asm__("r3")=result;
 __asm__ volatile("sc":"+r"(r0),"+r"(r3)::"cr0","memory");
#else
 __asm__ volatile("syscall"::"a"(60L),"D"((long)result):"rcx","r11","memory");
#endif
 __builtin_unreachable();
}
