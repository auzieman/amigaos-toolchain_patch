typedef unsigned int u32;typedef _Bool bool;
#define true 1
#define CHIP_POLARIS11 1
#define AMDGPU_RING_TYPE_GFX 1
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define __BIG_ENDIAN 1
#endif
struct device{int asic_type;};struct parser{struct device *adev;};struct functions{int type;};struct ring{struct functions *funcs;};struct ib{bool is_le;};
static bool amdgpu_polaris11_le_user_ib;
static void select(struct parser *p,struct ring *ring,struct ib *ib){
#ifdef __BIG_ENDIAN
	/* This option changes the fetch contract, not the command values. */
	if (amdgpu_polaris11_le_user_ib &&
	    p->adev->asic_type == CHIP_POLARIS11 &&
	    ring->funcs->type == AMDGPU_RING_TYPE_GFX)
		ib->is_le = true;
#endif
}
static unsigned char result[24];
void _start(void){unsigned n=0;struct device d;struct parser p={&d};struct functions f;struct ring r={&f};
for(unsigned enabled=0;enabled<2;enabled++)for(unsigned asic=0;asic<2;asic++)for(unsigned type=1;type<=3;type++)for(unsigned initial=0;initial<2;initial++){
d.asic_type=asic;f.type=type;amdgpu_polaris11_le_user_ib=enabled;struct ib ib={initial};select(&p,&r,&ib);result[n++]=ib.is_le;
}
#if defined(__powerpc__)
register long nr asm("r0")=4,x asm("r3")=1,y asm("r4")=(long)result,z asm("r5")=24;
asm volatile("sc" : "+r"(nr),"+r"(x),"+r"(y),"+r"(z) : : "memory","cr0","ctr","lr","xer","r6","r7","r8","r9","r10","r11","r12");nr=1;x=0;asm volatile("sc"::"r"(nr),"r"(x):"memory");
#else
asm volatile("syscall"::"a"(1L),"D"(1L),"S"(result),"d"(24L):"rcx","r11","memory");asm volatile("syscall"::"a"(60L),"D"(0L):"rcx","r11","memory");
#endif
__builtin_unreachable();}
