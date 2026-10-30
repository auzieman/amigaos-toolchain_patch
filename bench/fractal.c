/* SPDX-License-Identifier: MIT
 * Freestanding PPC32 demo. Bit-pattern API keeps both paths independent of
 * a restored compiler SPE ABI. Not a glibc or compiler-backend benchmark.
 */
typedef unsigned int u32;
extern float __addsf3(float, float), __subsf3(float, float), __mulsf3(float, float);
typedef union { float f; u32 u; } bits;
#define NOINLINE __attribute__((noinline))
NOINLINE u32 soft_add(u32 a,u32 b){bits x={.u=a},y={.u=b},z;z.f=__addsf3(x.f,y.f);return z.u;}
NOINLINE u32 soft_sub(u32 a,u32 b){bits x={.u=a},y={.u=b},z;z.f=__subsf3(x.f,y.f);return z.u;}
NOINLINE u32 soft_mul(u32 a,u32 b){bits x={.u=a},y={.u=b},z;z.f=__mulsf3(x.f,y.f);return z.u;}
NOINLINE u32 spe_add(u32 a,u32 b){u32 r;__asm__("efsadd %0,%1,%2":"=r"(r):"r"(a),"r"(b));return r;}
NOINLINE u32 spe_sub(u32 a,u32 b){u32 r;__asm__("efssub %0,%1,%2":"=r"(r):"r"(a),"r"(b));return r;}
NOINLINE u32 spe_mul(u32 a,u32 b){u32 r;__asm__("efsmul %0,%1,%2":"=r"(r):"r"(a),"r"(b));return r;}
#include "coordinates.h"
static unsigned char pixels[2][128*96];
NOINLINE static long call3(long n,long a,long b,long c){
 register long r0 __asm__("r0")=n,r3 __asm__("r3")=a,r4 __asm__("r4")=b,r5 __asm__("r5")=c;
 __asm__ volatile("sc":"+r"(r3),"+r"(r0),"+r"(r4),"+r"(r5)::"r6","r7","r8","r9","r10","r11","r12","ctr","cr0","memory");return r3;
}
static void text(const char *s){u32 n=0;while(s[n])n++;call3(4,1,(long)s,n);}
static void number(u32 n){char b[12];u32 i=12;b[--i]=0;do{b[--i]='0'+n%10;n/=10;}while(n);text(b+i);}
static void hexbyte(unsigned char c){const char *h="0123456789abcdef";char b[3]={h[c>>4],h[c&15],0};text(b);}
struct stamp {long long sec,nsec;};
static int now(struct stamp *t){return call3(403,1,(long)t,0)==0;}
static u32 elapsed(struct stamp a,struct stamp b){long sec=(long)(b.sec-a.sec),nano=(long)b.nsec-(long)a.nsec;if(nano<0){sec--;nano+=1000000000;}return (u32)sec*1000000+(u32)nano/1000;}
typedef u32 (*op)(u32,u32);
static u32 render(int mode){
 op add=mode?spe_add:soft_add,sub=mode?spe_sub:soft_sub,mul=mode?spe_mul:soft_mul;
 u32 checksum=2166136261u;
 for(u32 y=0;y<96;y++)for(u32 x=0;x<128;x++){
  u32 zr=0,zi=0,n;
  for(n=0;n<96;n++){
   u32 rr=mul(zr,zr),ii=mul(zi,zi);
   if(add(rr,ii)>0x40800000u)break;
   u32 next_i=add(mul(0x40000000u,mul(zr,zi)),ys[y]);
   zr=add(sub(rr,ii),xs[x]);zi=next_i;
  }
  pixels[mode][y*128+x]=n;checksum=(checksum^n)*16777619u;
 }
 return checksum;
}
void benchmark(void){
 text("FRACTAL_BEGIN width=128 height=96 max_iter=96 trials=3 warmup=1\n");
 if(soft_add(0x3fc00000u,0x40100000u)!=0x40700000u || spe_add(0x3fc00000u,0x40100000u)!=0x40700000u){text("FRACTAL_FAIL arithmetic precheck\n");return;}
 render(0);render(1);
 for(u32 trial=0;trial<3;trial++)for(u32 order=0;order<2;order++){
  u32 mode=order^(trial&1);struct stamp start,end;
  if(!now(&start)){text("FRACTAL_FAIL clock\n");return;}
  u32 sum=render(mode);
  if(!now(&end)){text("FRACTAL_FAIL clock\n");return;}
  text("FRACTAL_TIME mode=");text(mode?"SPE":"SOFT");text(" trial=");number(trial+1);text(" us=");number(elapsed(start,end));text(" checksum=");number(sum);text("\n");
 }
 for(u32 i=0;i<128*96;i++)if(pixels[0][i]!=pixels[1][i]){text("FRACTAL_FAIL pixel mismatch\n");return;}
 for(u32 mode=0;mode<2;mode++){
  text("FRACTAL_PIXELS mode=");text(mode?"SPE ":"SOFT ");
  for(u32 i=0;i<128*96;i++)hexbyte(pixels[mode][i]);text("\n");
 }
 text("FRACTAL_PASS identical escape-count images\nTABOR_QEMU_INIT_OK: fractal benchmark complete; full ABI/glibc/GL not tested.\n");
}
__asm__(".text\n.globl _start\n_start:\nbl benchmark\n1: li 0,29\nsc\nb 1b\n");
