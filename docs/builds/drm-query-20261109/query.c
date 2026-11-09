/* Native PPC32 read-only AMDGPU_INFO query. No CS ioctl, BO, modeset or reset. */
#include "amdgpu_drm.h"
typedef unsigned int u32;
static long call(long n,long a,long b,long c){
 register long nr asm("r0")=n;register long x asm("r3")=a;
 register long y asm("r4")=b;register long z asm("r5")=c;
 asm volatile("sc\n\tbns+ 1f\n\tneg %0,%0\n1:":"+r"(x),"+r"(nr),"+r"(y),"+r"(z)::"memory","cr0","ctr","lr","xer","r6","r7","r8","r9","r10","r11","r12");return x;
}
void *memset(void *p,int v,unsigned long n){volatile unsigned char *q=p;while(n--)*q++=v;return p;}
static u32 result[16];
void _start(void){
 long fd=call(5,(long)"/dev/dri/renderD128",2,0);result[0]=0x44524d31;result[1]=fd;
 if(fd>=0){
  struct drm_amdgpu_info q;u32 accel=0;memset(&q,0,sizeof(q));
  q.return_pointer=(unsigned long)&accel;q.return_size=sizeof(accel);q.query=AMDGPU_INFO_ACCEL_WORKING;
  result[2]=call(54,fd,DRM_IOCTL_AMDGPU_INFO,(long)&q);result[3]=accel;
  unsigned types[]={AMDGPU_HW_IP_GFX,AMDGPU_HW_IP_COMPUTE,AMDGPU_HW_IP_DMA,AMDGPU_HW_IP_UVD,AMDGPU_HW_IP_VCE,AMDGPU_HW_IP_UVD_ENC};
  for(unsigned i=0;i<6;i++){
   struct drm_amdgpu_info_hw_ip ip;memset(&ip,0,sizeof(ip));memset(&q,0,sizeof(q));
   q.return_pointer=(unsigned long)&ip;q.return_size=sizeof(ip);q.query=AMDGPU_INFO_HW_IP_INFO;q.query_hw_ip.type=types[i];
   result[4+i*2]=call(54,fd,DRM_IOCTL_AMDGPU_INFO,(long)&q);result[5+i*2]=ip.available_rings;
  }
  call(6,fd,0,0);
 }
 call(4,1,(long)result,sizeof(result));call(1,0,0,0);__builtin_unreachable();
}
