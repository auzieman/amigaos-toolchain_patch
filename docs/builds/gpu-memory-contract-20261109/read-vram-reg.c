#define _FILE_OFFSET_BITS 64
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
int main(int argc,char **argv){
 if(argc==3 && !strcmp(argv[1],"--vmreg")){
  unsigned vmid=strtoul(argv[2],0,10);if(vmid>15)return 2;
  unsigned reg=vmid<8?0x54f+vmid:0x50e + vmid-8;uint32_t value=0;
  int fd=open("/sys/kernel/debug/dri/0/amdgpu_regs",O_RDONLY);if(fd<0)return 2;
  if(pread(fd,&value,4,(off_t)reg*4)!=4){perror("vmreg");return 2;}
  printf("VMID=%u REGISTER=%x VALUE=%08x\n",vmid,reg,value);return 0;
 }
 if(argc!=2)return 2;uint64_t offset=strtoull(argv[1],0,16);
 if(argv[1][0]=='-' || offset>0xfffffff8ULL || (offset&3))return 2;
 uint32_t words[2]={0};
 int fd=open("/sys/kernel/debug/dri/0/amdgpu_vram",O_RDONLY);if(fd<0){perror("open");return 2;}
 if(pread(fd,words,sizeof(words),(off_t)offset)!=sizeof(words)){perror("pread");return 2;}
 printf("VRAM_OFFSET=%llx LOW=%08x HIGH=%08x ENTRY=%016llx\n",(unsigned long long)offset,words[0],words[1],((unsigned long long)words[1]<<32)|words[0]);return 0;
}
