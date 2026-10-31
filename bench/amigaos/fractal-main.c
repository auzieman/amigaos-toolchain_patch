/* SPDX-License-Identifier: MIT
 * CLI/PGM demo. No Linux syscalls or float-valued runtime interfaces.
 */
#include <stdio.h>
#include <string.h>
#include <time.h>
#include "arithmetic.h"
#include "../coordinates.h"
static unsigned char pixels[2][128*96];
typedef u32 (*operation)(u32,u32);

static u32 render(int mode)
{
 operation add=mode?spe_add:soft_add,sub=mode?spe_sub:soft_sub,mul=mode?spe_mul:soft_mul;
 u32 checksum=2166136261u,x,y,n;
 for(y=0;y<96;y++)for(x=0;x<128;x++){
  u32 zr=0,zi=0;
  for(n=0;n<96;n++){
   u32 rr=mul(zr,zr),ii=mul(zi,zi);
   if(add(rr,ii)>0x40800000u)break;
   {u32 next_i=add(mul(0x40000000u,mul(zr,zi)),ys[y]);
    zr=add(sub(rr,ii),xs[x]);zi=next_i;}
  }
  pixels[mode][y*128+x]=(unsigned char)n;
  checksum=(checksum^n)*16777619u;
 }
 return checksum;
}

static int save_image(const char *name,int mode)
{
 FILE *f=fopen(name,"wb");int ok;
 if(!f)return 0;
 ok=fprintf(f,"P5\n128 96\n96\n")>0;
 if(fwrite(pixels[mode],1,sizeof pixels[mode],f)!=sizeof pixels[mode])ok=0;
 if(fclose(f)!=0)ok=0;
 return ok;
}

int main(int argc,char **argv)
{
 int compare=0,trial,order,mode,repeat;u32 checksums[2]={0,0};
#ifdef TABOR_HOST_REFERENCE
 (void)argv;
 if(argc!=1){fputs("Host reference accepts no arguments; no SPE execution.\n",stderr);return 2;}
 puts("ENVIRONMENT HOST_REFERENCE_NOT_AMIGAOS_NOT_SPE");
#else
 if(argc==2 && strcmp(argv[1],"--spe")==0)compare=1;
 else if(argc!=1){fputs("Usage: fractal-os4 [--spe]\n",stderr);return 2;}
 puts("ENVIRONMENT AMIGAOS_TARGET; execution does not certify OS SPE context support");
#endif
 printf("FRACTAL_BEGIN width=128 height=96 max_iter=96 trials=3 batch=16 clock_ticks_per_second=%lu\n",(unsigned long)CLOCKS_PER_SEC);
 puts("CLOCK CPU time from C clock(); excludes output/image writing; not wall time");
 if(soft_add(0x3fc00000u,0x40100000u)!=0x40700000u ||
    (compare && spe_add(0x3fc00000u,0x40100000u)!=0x40700000u)){
  puts("FRACTAL_FAIL arithmetic");return 1;
 }
 render(0);if(compare)render(1);
 for(trial=0;trial<3;trial++)for(order=0;order<(compare?2:1);order++){
  clock_t start,end;mode=compare?(order^(trial&1)):0;
  start=clock();for(repeat=0;repeat<16;repeat++)checksums[mode]=render(mode);end=clock();
  if(start==(clock_t)-1 || end==(clock_t)-1 || end<=start){puts("FRACTAL_FAIL unavailable/wrapped/coarse clock");return 1;}
  printf("FRACTAL_TIME mode=%s trial=%d ticks=%lu checksum=%08lx\n",
    mode?"SPE":"SOFT",trial+1,(unsigned long)(end-start),(unsigned long)checksums[mode]);
  if(checksums[mode]!=0xabd5de74u){puts("FRACTAL_FAIL reference checksum");return 1;}
 }
 if(compare && memcmp(pixels[0],pixels[1],sizeof pixels[0])!=0){puts("FRACTAL_FAIL pixel mismatch");return 1;}
 if(!save_image("fractal-soft.pgm",0) || (compare && !save_image("fractal-spe.pgm",1))){puts("FRACTAL_FAIL image write");return 1;}
 if(compare)puts("FRACTAL_PASS identical escape-count images; no OS context/ABI/GL certification");
 else puts("FRACTAL_SOFTWARE_PASS SPE execution not requested");
 return 0;
}
