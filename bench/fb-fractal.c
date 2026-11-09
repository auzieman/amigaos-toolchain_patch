/* SPDX-License-Identifier: MIT
 * PPC32 integer-only framebuffer presenter. No GPU commands or modesetting.
 * Accepts escape counts verified equal by the software/SPE benchmark.
 */
#include <linux/fb.h>
#include <asm/unistd.h>
#include <asm/fcntl.h>
typedef unsigned int u32;
static unsigned char counts[128*96];
static unsigned char row[16384] __attribute__((aligned(4)));
static unsigned char verify[16384] __attribute__((aligned(4)));
static struct fb_var_screeninfo var;
static struct fb_fix_screeninfo fix;
struct saved { u32 magic, xres, yres, stride, bpp, x, y, width, height; };

__attribute__((noinline)) static long sys3(long n,long a,long b,long c) {
 register long r0 __asm__("r0")=n,r3 __asm__("r3")=a;
 register long r4 __asm__("r4")=b,r5 __asm__("r5")=c;
 unsigned long cr;
 __asm__ volatile("sc\n\tmfcr %0":"=&r"(cr),"+r"(r0),"+r"(r3),"+r"(r4),"+r"(r5)
  ::"r6","r7","r8","r9","r10","r11","r12","ctr","cr0","memory");
 return cr&0x10000000u ? -r3 : r3;
}
static u32 length(const char *s){u32 n=0;while(s[n])n++;return n;}
static void text(const char *s){sys3(__NR_write,1,(long)s,length(s));}
static void number(u32 n){char s[12];u32 i=11;s[i]=0;do{s[--i]='0'+n%10;n/=10;}while(n);text(s+i);}
static int equal(const char *a,const char *b){while(*a&&*a==*b)a++,b++;return *a==*b;}
static int transfer(int fd,void *data,u32 size,int writing){
 unsigned char *p=data;while(size){long n=sys3(writing?__NR_write:__NR_read,fd,(long)p,size);
  if(n<=0)return 0;
  p+=n;size-=n;
 }return 1;
}
static int seek(int fd,u32 offset){return sys3(__NR_lseek,fd,offset,0)==(long)offset;}
static int failure(const char *where){text("FB_FRACTAL_FAIL ");text(where);text("\n");return 1;}
static u32 channel(u32 c,struct fb_bitfield field){return ((c*((1u<<field.length)-1)+127)/255)<<field.offset;}
static u32 pixel(u32 n){
 if(n==96)return 0;
 return channel(n*13%256,var.red)|channel(n*7%256,var.green)|channel(n*19%256,var.blue);
}
__attribute__((used)) static int app(int argc,char **argv){
 if(argc<2)return failure("arguments");
 int fixture=equal(argv[1],"--fixture")||equal(argv[1],"--fixture-restore");
 int restore=equal(argv[1],"--restore")||equal(argv[1],"--fixture-restore");
 int info=equal(argv[1],"--info");
 if(!fixture&&!restore&&!info&&!equal(argv[1],"--draw"))return failure("operation");
 if((restore&&argc!=(fixture?4:3))||(!restore&&!info&&argc!=(fixture?5:4)))return failure("arguments");
 const char *device=fixture?argv[restore?3:4]:"/dev/fb0";
 int fb=sys3(__NR_open,(long)device,info?O_RDONLY:O_RDWR,0);
 if(fb<0)return failure("open framebuffer");
 if(fixture){
  var.xres=1920;var.yres=1080;var.xres_virtual=1920;var.yres_virtual=1080;
  var.bits_per_pixel=32;var.red.offset=16;var.red.length=8;
  var.green.offset=8;var.green.length=8;var.blue.length=8;
  fix.line_length=1920*4;fix.smem_len=1920*1080*4;fix.visual=FB_VISUAL_TRUECOLOR;
 }else if(sys3(__NR_ioctl,fb,FBIOGET_VSCREENINFO,(long)&var)<0 ||
           sys3(__NR_ioctl,fb,FBIOGET_FSCREENINFO,(long)&fix)<0)return failure("framebuffer geometry");
 text("FB_GEOMETRY width=");number(var.xres);text(" height=");number(var.yres);
 text(" bpp=");number(var.bits_per_pixel);text(" stride=");number(fix.line_length);
 text(" red=");number(var.red.offset);text(" green=");number(var.green.offset);
 text(" blue=");number(var.blue.offset);text("\n");
 if(info){sys3(__NR_close,fb,0,0);return 0;}
 if(fix.visual!=FB_VISUAL_TRUECOLOR || var.bits_per_pixel!=32 ||
    var.xres<1024 || var.yres<768 || var.xres>4096 || var.yres>4096 ||
    var.xoffset || var.yoffset || fix.line_length<var.xres*4 ||
    fix.line_length>16384 || fix.smem_len<fix.line_length*var.yres)
  return failure("unsupported mode; no framebuffer changes");
 struct fb_bitfield fields[3]={var.red,var.green,var.blue};
 u32 masks=0;
 for(u32 i=0;i<3;i++){
  if(fields[i].length!=8 || fields[i].offset>24 || fields[i].msb_right)
   return failure("unsupported channel layout");
  u32 mask=255u<<fields[i].offset;if(mask&masks)return failure("overlapping channels");masks|=mask;
 }
 struct saved h={0x46524631,var.xres,var.yres,fix.line_length,32,
                  (var.xres-1024)/2,(var.yres-768)/2,1024,768};
 int backup;
 if(restore){
  backup=sys3(__NR_open,(long)argv[2],O_RDONLY,0);
  struct saved old;
  if(backup<0||!transfer(backup,&old,sizeof old,0))return failure("read backup");
  u32 *a=(u32*)&h,*b=(u32*)&old;
  for(u32 i=0;i<sizeof h/sizeof(u32);i++)if(a[i]!=b[i])return failure("backup mode mismatch");
  for(u32 y=0;y<h.height;y++){
   if(!transfer(backup,row,h.width*4,0)||!seek(fb,(h.y+y)*h.stride+h.x*4)||
      !transfer(fb,row,h.width*4,1))return failure("restore row");
  }
  text("FB_FRACTAL_RESTORED\n");
 }else{
  int input=sys3(__NR_open,(long)argv[2],O_RDONLY,0);
  if(input<0||!transfer(input,counts,sizeof counts,0))return failure("read escape counts");
  sys3(__NR_close,input,0,0);
  u32 sum=2166136261u;
  for(u32 i=0;i<sizeof counts;i++){if(counts[i]>96)return failure("escape count range");sum=(sum^counts[i])*16777619u;}
  if(sum!=0xabd5de74u)return failure("escape count checksum");
  backup=sys3(__NR_open,(long)argv[3],O_WRONLY|O_CREAT|O_EXCL,0600);
  if(backup<0||!transfer(backup,&h,sizeof h,1))return failure("create exclusive backup");
  for(u32 y=0;y<h.height;y++){
   if(!seek(fb,(h.y+y)*h.stride+h.x*4)||!transfer(fb,row,h.width*4,0)||
      !transfer(backup,row,h.width*4,1))return failure("backup row; screen unchanged");
  }
  sys3(__NR_close,backup,0,0);backup=-1;
  for(u32 y=0;y<h.height;y++){
   u32 *pixels=(u32*)row;
   for(u32 x=0;x<h.width;x++)pixels[x]=pixel(counts[(y/8)*128+x/8]);
   u32 offset=(h.y+y)*h.stride+h.x*4;
   if(!seek(fb,offset)||!transfer(fb,row,h.width*4,1)||!seek(fb,offset)||
      !transfer(fb,verify,h.width*4,0))return failure("draw/readback row; backup retained");
   for(u32 x=0;x<h.width*4;x++)if(row[x]!=verify[x])return failure("readback mismatch; backup retained");
  }
  text("FB_FRACTAL_DRAWN width=1024 height=768 scale=8 readback=PASS\n");
 }
 if(backup>=0)sys3(__NR_close,backup,0,0);
 sys3(__NR_close,fb,0,0);return 0;
}
__asm__(".text\n.globl _start\n_start:\nlwz 3,0(1)\naddi 4,1,4\nbl app\nli 0,1\nsc\n1: b 1b\n");
