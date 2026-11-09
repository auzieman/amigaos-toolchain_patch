#include <amdgpu.h>
#include <amdgpu_drm.h>
#include <stdio.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#define OK(x) do { int r=(x); if(r){fprintf(stderr,"FAIL %s ret=%d\n",#x,r);return 2;} }while(0)
int main(int argc, char **argv) {
 setvbuf(stdout,NULL,_IOLBF,0);
 int fd=open("/dev/dri/renderD128",O_RDWR); if(fd<0)return 2;
 amdgpu_device_handle dev;amdgpu_context_handle ctx;amdgpu_bo_handle bo;amdgpu_va_handle range;uint32_t major,minor;uint64_t va;void *cpu;
 OK(amdgpu_device_initialize(fd,&major,&minor,&dev));
 OK(amdgpu_cs_ctx_create(dev,&ctx));
 struct amdgpu_bo_alloc_request alloc={.alloc_size=4096,.phys_alignment=4096,.preferred_heap=AMDGPU_GEM_DOMAIN_GTT,.flags=AMDGPU_GEM_CREATE_CPU_ACCESS_REQUIRED};
 for(int i=1;i<argc;i++){if(!strcmp(argv[i],"vram"))alloc.preferred_heap=AMDGPU_GEM_DOMAIN_VRAM;if(!strcmp(argv[i],"uswc"))alloc.flags|=AMDGPU_GEM_CREATE_CPU_GTT_USWC;}
 printf("ALLOCATION heap=%u flags=%llx\n",alloc.preferred_heap,(unsigned long long)alloc.flags);
 OK(amdgpu_bo_alloc(dev,&alloc,&bo));OK(amdgpu_bo_cpu_map(bo,&cpu));
 OK(amdgpu_va_range_alloc(dev,amdgpu_gpu_va_range_general,4096,4096,0,&va,&range,AMDGPU_VA_RANGE_32_BIT));
 OK(amdgpu_bo_va_op(bo,0,4096,va,AMDGPU_VM_PAGE_READABLE|AMDGPU_VM_PAGE_WRITEABLE|AMDGPU_VM_PAGE_EXECUTABLE,AMDGPU_VA_OP_MAP));
 memset(cpu,0,4096);uint32_t *ib=cpu;uint64_t target=va+2048;
 ib[0]=0xc0033700;ib[1]=(5u<<8)|(1u<<20);ib[2]=(uint32_t)target;ib[3]=target>>32;ib[4]=0xcafedead;
 ib[5]=ib[6]=ib[7]=0xffff1000;
 int le=0;for(int i=1;i<argc;i++)if(!strcmp(argv[i],"le"))le=1;
 if(le)for(unsigned j=0;j<8;j++)ib[j]=__builtin_bswap32(ib[j]);
 printf("GFX_TEST_ENCODING=%s\n",le?"explicit-little-endian":"native-big-endian");
 unsigned char *bytes=cpu;
 printf("GFX_NATIVE_WRITE va=%llx target=%llx first_bytes=%02x%02x%02x%02x\n",(unsigned long long)va,(unsigned long long)target,bytes[0],bytes[1],bytes[2],bytes[3]);
 __sync_synchronize();amdgpu_bo_list_handle list;OK(amdgpu_bo_list_create(dev,1,&bo,NULL,&list));
 struct amdgpu_cs_ib_info info={.ib_mc_address=va,.size=8};
 struct amdgpu_cs_request req={.ip_type=AMDGPU_HW_IP_GFX,.resources=list,.number_of_ibs=1,.ibs=&info};
 OK(amdgpu_cs_submit(ctx,0,&req,1));
 printf("SUBMIT seq=%llx ib_count=%u ip=%u ib_va=%llx ib_size=%u\n",(unsigned long long)req.seq_no,req.number_of_ibs,req.ip_type,(unsigned long long)info.ib_mc_address,info.size);
 if(!req.seq_no || req.seq_no==~0ULL)return 3;
 struct amdgpu_cs_fence fence={.context=ctx,.ip_type=AMDGPU_HW_IP_GFX,.fence=req.seq_no};uint32_t expired=0;
 OK(amdgpu_cs_query_fence_status(&fence,1000000000,0,&expired));__sync_synchronize();bytes=(unsigned char*)cpu+2048;
 printf("GFX_NATIVE_WRITE fence_complete=%u bytes=%02x%02x%02x%02x\n",expired,bytes[0],bytes[1],bytes[2],bytes[3]);
 int pass=expired&&bytes[0]==0xad&&bytes[1]==0xde&&bytes[2]==0xfe&&bytes[3]==0xca;
 printf("GFX_NATIVE_WRITE=%s\n",pass?"PASS":"FAIL");
 OK(amdgpu_bo_cpu_unmap(bo));OK(amdgpu_bo_cpu_map(bo,&cpu));bytes=(unsigned char*)cpu+2048;
 printf("REMAP_BYTES=%02x%02x%02x%02x\n",bytes[0],bytes[1],bytes[2],bytes[3]);
 /* Process exit closes its allocation/context; no reset or driver unbind. */
 return pass?0:1;
}
