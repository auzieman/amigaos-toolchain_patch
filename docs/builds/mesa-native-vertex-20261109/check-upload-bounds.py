"""Run on R730: exercise exact Mesa upload loop with guarded mocked storage.

Checks allocation arithmetic and relocation write bounds; not a GPU/PPC emulator.
"""
import hashlib
import json
import subprocess
import resource
from pathlib import Path

source = Path('/srv/data1/tabor-build/linux-live-001/work/native-vertex-contract-20261109-001/mesa-source/src/gallium/drivers/radeonsi/si_shader.c')
root = Path('/home/owner/upload-bounds-review-20261109-001')
root.mkdir(exist_ok=True)
text = source.read_text()

def extract(signature):
    start = text.index(signature)
    opening = text.index('{', start)
    depth = 1
    pos = opening + 1
    while depth:
        depth += (text[pos] == '{') - (text[pos] == '}')
        pos += 1
    return text[start:pos]

functions = extract('static unsigned get_shader_binaries(') + '\n' + extract('static int upload_binary_raw(')
prefix = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <stdbool.h>
#ifndef UTIL_ARCH_BIG_ENDIAN
#define UTIL_ARCH_BIG_ENDIAN 0
#endif
#define SI_SHADER_BINARY_RAW 1
#define util_cpu_to_le32(x) __builtin_bswap32(x)
struct si_shader_binary { unsigned type, code_size, exec_size, num_symbols; char *code_buffer; };
struct si_context {};
struct pipe_resource {};
struct si_screen {};
struct si_shader_part { struct si_shader_binary binary; };
struct si_shader { struct si_shader_binary binary; struct si_shader_part *prolog,*epilog; struct si_shader *previous_stage; };
static unsigned char *allocation;
static unsigned allocation_size;
static unsigned calls;
static void *pre_upload_binary(struct si_screen *s, struct si_shader *sh,unsigned n,int dma,struct si_context **c,struct pipe_resource **r,unsigned *off,int64_t bo) {
 allocation=malloc(n+128); assert(allocation); memset(allocation,0xa7,n+128); allocation_size=n; return allocation+64;
}
static void post_upload_binary(struct si_screen *s,struct si_shader *sh,void *p,unsigned size,unsigned total,int dma,struct si_context *c,struct pipe_resource *r,unsigned off) {
 assert(size==allocation_size && total==allocation_size);
 for(unsigned i=0;i<64;i++) {assert(allocation[i]==0xa7); assert(allocation[64+allocation_size+i]==0xa7);} calls++;
}
static void calculate_needed_lds_size(struct si_screen *s,struct si_shader *sh) {}
/* Deliberate bounded stand-in for symbol resolution; tests upload placement,
 * not ACO symbol semantics. Writes the first executable word. */
static void si_aco_resolve_symbols(struct si_shader *sh,uint32_t *dst,const uint32_t *src,uint64_t scratch,unsigned offset) { dst[getenv("BAD_SYMBOL") ? 16 : 0]=src[0]+offset; }
'''
suffix = r'''
static char data[4][64];
int main(void) {
 struct si_screen screen={};
 for(unsigned mask=0;mask<8;mask++) {
  struct si_shader sh={},prev={}; struct si_shader_part pro={},epi={};
  struct si_shader_binary *bins[]={&pro.binary,&prev.binary,&sh.binary,&epi.binary};
  for(unsigned i=0;i<4;i++) {bins[i]->type=1; bins[i]->exec_size=4*(i+1);bins[i]->code_size=bins[i]->exec_size+4*(4-i);bins[i]->code_buffer=data[i];memset(data[i],0x30+i,64);}
  sh.prolog=mask&1?&pro:NULL; sh.previous_stage=mask&2?&prev:NULL;sh.epilog=mask&4?&epi:NULL;
  sh.binary.num_symbols=1;prev.binary.num_symbols=1;
  if(getenv("BAD_SIZE")) {sh.prolog=NULL;sh.previous_stage=NULL;sh.epilog=NULL;sh.binary.code_size=4;sh.binary.exec_size=32;}
  int size=upload_binary_raw(&screen,&sh,0,0,-1); assert(size>0);
  struct si_shader_binary *ordered[4];unsigned count=get_shader_binaries(&sh,ordered),exec=0;
  for(unsigned i=0;i<count;i++)exec+=ordered[i]->exec_size;
  unsigned pos=exec;
  for(unsigned i=0;i<count;i++) {unsigned n=ordered[i]->code_size-ordered[i]->exec_size;assert(!memcmp(allocation+64+pos,ordered[i]->code_buffer+ordered[i]->exec_size,n));pos+=n;}
  assert(pos==(unsigned)size);free(allocation);
 }
 assert(calls==8);puts("PASS: 8 part combinations, allocation guards and constant-tail placement");return 0;
}
'''
harness = prefix + functions + suffix
(root/'harness.c').write_text(harness)
records=[]
for mode in (0,1):
    exe=root/f'check-{mode}'
    compile_result=subprocess.run(['cc','-O0','-g','-fsanitize=undefined','-fno-sanitize-recover=all',f'-DUTIL_ARCH_BIG_ENDIAN={mode}',str(root/'harness.c'),'-o',str(exe)],capture_output=True,text=True)
    if compile_result.returncode: raise RuntimeError(compile_result.stderr[-3000:])
    result=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10)
    records.append({'conversion_branch':mode,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    assert result.returncode==0
    negative=[]
    for key in ('BAD_SIZE','BAD_SYMBOL'):
        import os
        env=os.environ.copy();env[key]='1'
        result=subprocess.run([str(exe)],env=env,capture_output=True,text=True,timeout=10,
                              preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_CORE,(0,0)))
        assert result.returncode != 0, 'negative control escaped guards'
        negative.append({'case':key,'exit':result.returncode,'process_failed_as_expected':True})
    records[-1]['negative_controls']=negative
out={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'extracted_functions_sha256':hashlib.sha256(functions.encode()).hexdigest(),'records':records,'limits':['native compiler only; branch1 exercises bswap logic, not PPC ABI','pre/post allocator and symbol resolver mocked','synthetic invalid size triggers native SIGSEGV from underflow/copy; out-of-range mocked relocation triggers guard assertion; actual ACO symbol resolver not extracted; no GPU execution, DMA, mapping or visibility proof']}
(root/'result.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
