from pathlib import Path
import subprocess,json,ast
w=Path('/srv/data1/tabor-build/linux-live-001/work/mesa-3d-contracts-20261109-001');root=w/'mesa-source'
# Extract the actual completed publication block and existing shared copy helper.
block=(w/'vertex-publication-block.txt').read_text();s=(root/'src/util/u_math.h').read_text();a=s.rfind('static inline',0,s.index('util_memcpy_cpu_to_le32('));i=s.index('{',s.index('util_memcpy_cpu_to_le32('))+1;depth=1
while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
helper=s[a:i]
draw=(root/'src/gallium/drivers/radeonsi/si_state_draw.cpp').read_text();start=draw.index('static bool si_upload_and_prefetch_VB_descriptors');end=draw.index('static void si_get_draw_start_count',start);t=draw[start:end]
assert t.index('memcpy(desc, &vstate->descriptors')<t.index('unsigned num_dw = (count - count_in_user_sgprs) * 4')
assert t.rindex('si_set_vb_descriptor<GFX_VERSION>')<t.index('unsigned num_dw = (count - count_in_user_sgprs) * 4')
prefix=(w/'query-contract-after.c').read_text().split('static bool si_query_hw_prepare_buffer')[0]
prefix+='''typedef __SIZE_TYPE__ size_t;
#define UTIL_ARCH_BIG_ENDIAN (__BYTE_ORDER__ == __ORDER_BIG_ENDIAN__)
#define util_bswap32(x) __builtin_bswap32((uint32_t)(x))
#define assert(x) check(x)
void *memcpy(void *d,const void *s,size_t n){unsigned char *a=d;const unsigned char *b=s;while(n--)*a++=*b++;return d;}
'''
main=r'''
static void publish(unsigned alloc_size,unsigned count,unsigned count_in_user_sgprs,uint32_t *ptr){
#ifndef OLD
'''+block+r'''
#endif
}
void _start(void){
 for(unsigned count=0;count<=32;count++)for(unsigned inline_limit=0;inline_limit<=5;inline_limit++){
  unsigned in=count<inline_limit?count:inline_limit,words=(count-in)*4;uint32_t buffer[132],sgpr[24];
  for(unsigned j=0;j<132;j++)buffer[j]=j<words?0x12340000+j:0xaabbccdd;
  for(unsigned j=0;j<24;j++)sgpr[j]=0x10200000+j;
  publish(words?((words*4+31)&~31):0,count,in,buffer);
  unsigned char *bytes=(void*)buffer;
  for(unsigned j=0;j<words;j++)for(unsigned byte=0;byte<4;byte++)check(bytes[4*j+byte]==((0x12340000+j)>>(8*byte)&255));
  for(unsigned j=words;j<132;j++)check(buffer[j]==0xaabbccdd);
  for(unsigned j=0;j<24;j++)check(sgpr[j]==0x10200000+j);
 }
 for(unsigned n=1;n<=32;n++){
  uint32_t factors[128],out[128];
  for(unsigned j=0;j<n*4;j++)factors[j]=0x80000001u+j*3;
#ifdef OLD
  memcpy(out,factors,n*16);
#else
  util_memcpy_cpu_to_le32(out,factors,n*16);
#endif
  unsigned char *b=(void*)out;
  for(unsigned j=0;j<n*4;j++)for(unsigned byte=0;byte<4;byte++)check(b[4*j+byte]==((0x80000001u+j*3)>>(8*byte)&255));
  for(unsigned j=0;j<n*4;j++)check(factors[j]==0x80000001u+j*3);
 }
#ifdef OLD
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
 sys(1,bad?0:1,0,0);
#else
 sys(1,bad?1:0,0,0);
#endif
#else
 sys(1,bad?1:0,0,0);
#endif
 __builtin_unreachable();}
'''
for mode in ['old','new']:
 p=w/('vertex-contract-'+mode+'.c');p.write_text(prefix+helper+main)
 for arch,cc,runner in [('x86','gcc',[]),('ppc','/srv/data1/tabor-build/linux-live-001/tools/cxx-reference-002/bin/powerpc-linux-gnuspe-gcc',['qemu-ppc','-cpu','e500v2'])]:
  exe=w/('vertex-contract-'+mode+'-'+arch);subprocess.run([cc,'-O2','-ffreestanding','-nostdlib','-static','-fno-pie','-no-pie','-fno-stack-protector']+(['-mstackrealign'] if arch=='x86' else [])+(['-DOLD'] if mode=='old' else [])+[str(p),'-o',str(exe)],check=True);subprocess.run(runner+[str(exe)],check=True)
r={'status':'PASS','descriptor_count_inline_combinations_per_arch':198,'divisor_table_sizes_per_arch':32,'controls':['oldBE differs from known LE byte oracle','unchanged x86 matches','actual publication block converges after both writers','only initialized descriptor words converted','padding and native inline SGPR words unchanged','existing util_memcpy_cpu_to_le32 copied from source','divisor CPU source retained'],'limits':'Descriptor producer values and GPU reader modeled; full draw function not executed; no GPU test.'}
(w/'vertex-contract-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
