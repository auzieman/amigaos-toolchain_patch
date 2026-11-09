#define _FILE_OFFSET_BITS 64
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
int main(int argc,char **argv){
 if(argc!=2)return 2;uint64_t offset=strtoull(argv[1],0,16);uint32_t words[2]={0};
 int fd=open("/sys/kernel/debug/dri/0/amdgpu_vram",O_RDONLY);if(fd<0){perror("open");return 2;}
 if(pread(fd,words,sizeof(words),(off_t)offset)!=sizeof(words)){perror("pread");return 2;}
 printf("VRAM_OFFSET=%llx LOW=%08x HIGH=%08x ENTRY=%016llx\n",(unsigned long long)offset,words[0],words[1],((unsigned long long)words[1]<<32)|words[0]);return 0;
}
