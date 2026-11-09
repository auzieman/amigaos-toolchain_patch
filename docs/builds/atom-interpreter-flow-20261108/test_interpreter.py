"""R730: actual ATOM execution engine, PS/WS/register round trips and partial writes."""
from pathlib import Path
import subprocess,json,hashlib,os,resource
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
B=Path('/srv/data1/tabor-build/source-review');W=B/'atom-interpreter-flow-20261108';W.mkdir(exist_ok=True)
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-007/source');A=S/'drivers/gpu/drm/amd/amdgpu'
base=(B/'shared-kernel-boundary-20261108/fixed-asic-clock.c').read_text().split('union get_clock_dividers')[0]
header=(A/'atom.h').read_text();atom=(A/'atom.c').read_text()
pre=base+r'''
typedef unsigned long long uint64_t;typedef uint64_t u64;typedef __SIZE_TYPE__ size_t;
#define NULL ((void*)0)
#define ENOMEM 12
#define GFP_KERNEL 0
#define lower_32_bits(v) ((u32)(v))
#define upper_32_bits(v) ((u32)((u64)(v)>>32))
#define do_div(n,b) ((n)/=(b))
#define pr_info(...) do{}while(0)
#define DRM_ERROR(...) do{}while(0)
#define printk(...) do{}while(0)
struct mutex{int unused;};
static void mutex_lock(struct mutex*m){(void)m;}static void mutex_unlock(struct mutex*m){(void)m;}
static unsigned long jiffies;
#define time_after(a,b) ((long)((b)-(a))<0)
#define jiffies_to_msecs(x) (x)
static int drm_can_sleep(void){return 1;}
static void udelay(unsigned n){jiffies+=n/1000;}static void mdelay(unsigned n){jiffies+=n;}static void msleep(unsigned n){jiffies+=n;}
static union{u64 align;u8 bytes[32768];}arena;static unsigned used;
static void*kcalloc(unsigned a,unsigned b,unsigned flags){(void)flags;unsigned n=a*b;n=(n+7)&~7u;if(n>32768-used)return 0;void*p=arena.bytes+used;used+=n;memset(p,0,n);return p;}
static void kfree(void*p){(void)p;}
'''
pre+=header[header.index('#define ATOM_BIOS_MAGIC'):header.index('extern int amdgpu_atom_debug;')]
pre+='\n#include "'+str(S/'drivers/gpu/drm/amd/include/atom-bits.h')+'"\n'
pre+=(S/'drivers/gpu/drm/amd/include/atom-names.h').read_text().replace('#include "atom.h"','')
engine=atom[atom.index('#define ATOM_COND_ABOVE'):atom.index('static void atom_index_iio(')]
code=pre+engine+r'''
static u8 rom[8192];static u32 registers[512];static unsigned writes;
static u32 reg_read(struct card_info*c,u32 i){(void)c;return registers[i];}
static void reg_write(struct card_info*c,u32 i,u32 v){(void)c;registers[i]=v;writes++;}
static void put16(void*p,u16 v){u8*b=p;b[0]=v;b[1]=v>>8;}
static unsigned pos;
static void byte(u8 b){rom[pos++]=b;}
static void half(u16 v){byte(v);byte(v>>8);}
static void begin(unsigned base,unsigned index,unsigned ps_bytes){put16(rom+0x44+2*index,base);rom[base+4]=8;rom[base+5]=ps_bytes;pos=base+6;}
static void finish(unsigned base){byte(ATOM_OP_EOT);put16(rom+base,pos-base);}
/* Actual VM execution, not a mock of amdgpu_atom_execute_table. */
int engine_roundtrip(u32*params,unsigned bytes){
 if(bytes%4||bytes>128)return -EINVAL;
 struct card_info card={.reg_write=reg_write,.reg_read=reg_read,.mc_write=reg_write,.mc_read=reg_read,.pll_write=reg_write,.pll_read=reg_read};struct atom_context ctx={.card=&card,.bios=rom,.cmd_table=0x40};
 u32 expected[32];for(unsigned i=0;i<bytes/4;i++)expected[i]=get_unaligned_le32(params+i);
 memset(rom,0,sizeof(rom));used=writes=0;begin(0x100,0,0);
 for(unsigned i=0;i<bytes/4;i++){
  byte(3);byte(ATOM_ARG_PS);byte(0);byte(i); /* PS -> native workspace */
  byte(1);byte(ATOM_ARG_WS);half(0x100+i);byte(0); /* workspace -> register */
  byte(2);byte(ATOM_ARG_REG);byte(i);half(0x100+i); /* register -> LE PS */
 }
 finish(0x100);int ret=amdgpu_atom_execute_table(&ctx,0,params,bytes);if(ret)return ret;
 if(writes!=bytes/4)return -22;
 for(unsigned i=0;i<bytes/4;i++)if(registers[0x100+i]!=expected[i]||get_unaligned_le32(params+i)!=expected[i])return -5;
 return 0;
}
#ifndef ENGINE_LIBRARY
int main(void){unsigned cases=0;u32 params[32];
 for(unsigned words=1;words<=32;words++)for(unsigned seed=0;seed<16;seed++){
  for(unsigned i=0;i<words;i++)put_unaligned_le32(0x12345678u^(seed*0x0103070bu)^(i*0x07234359u),params+i);
  if(engine_roundtrip(params,words*4))return 1;emit((char*)params,words*4);cases++;
 }
 struct card_info card={.reg_write=reg_write,.reg_read=reg_read};struct atom_context ctx={.card=&card,.bios=rom,.cmd_table=0x40};
 for(unsigned seed=0;seed<16;seed++)for(unsigned kind=0;kind<2;kind++)for(unsigned dst=0;dst<(kind?3u:4u);dst++){
  memset(rom,0,sizeof(rom));used=0;u32 initial=0x12345678u^(seed*0x0103070bu);put_unaligned_le32(initial,params);
  unsigned bits=kind?16:8,shift=dst*8;u32 value=kind?0xa1b2:0xc3;u32 mask=((1u<<bits)-1)<<shift;
  begin(0x100,0,0);byte(2);byte(ATOM_ARG_IMM|((kind?ATOM_SRC_WORD0:ATOM_SRC_BYTE0)<<3)|(dst<<6));byte(0);if(kind)half(value);else byte(value);finish(0x100);
  if(amdgpu_atom_execute_table(&ctx,0,params,4)||get_unaligned_le32(params)!=((initial&~mask)|((value<<shift)&mask)))return 2;
  emit((char*)params,4);cases++;
 }
 /* Nested parent reserves one parameter dword; child reads/writes the remainder. */
 for(unsigned seed=0;seed<32;seed++){
  memset(rom,0,sizeof(rom));used=writes=0;put_unaligned_le32(0xdeadbeef,params);put_unaligned_le32(0x12345678u+seed,params+1);
  begin(0x100,0,4);byte(82);byte(1);finish(0x100); /* CALLTABLE */
  begin(0x400,1,0);byte(1);byte(ATOM_ARG_PS);half(0x123);byte(0);byte(2);byte(ATOM_ARG_REG);byte(0);half(0x123);finish(0x400);
  if(amdgpu_atom_execute_table(&ctx,0,params,8)||writes!=1||registers[0x123]!=0x12345678u+seed||get_unaligned_le32(params)!=0xdeadbeef||get_unaligned_le32(params+1)!=0x12345678u+seed)return 3;
  emit((char*)params,8);cases++;
 }
 return cases==656?0:4;
}
#endif
'''
(W/'engine.c').write_text(code);outputs={}
for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
 exe=W/('engine-'+arch);cmd=[cc]+(['-mstackrealign']if arch=='x86'else[])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static',str(W/'engine.c'),'-lgcc','-o',str(exe)]
 p=subprocess.run(cmd,capture_output=True);(W/(arch+'-compile.log')).write_bytes(p.stderr)
 if p.returncode:print(p.stderr.decode()[-5000:]);p.check_returncode()
 p=subprocess.run(runner+[str(exe)],capture_output=True,timeout=30);(W/(arch+'.bin')).write_bytes(p.stdout);p.check_returncode();outputs[arch]=p.stdout
assert outputs['x86']==outputs['ppc']
r=dict(status='PASS',source_sha256=hashlib.sha256(code.encode()).hexdigest(),actual_interpreter_lines=len(engine.splitlines()),scenarios_per_architecture=656,output_sha256=hashlib.sha256(outputs['ppc']).hexdigest(),output_bytes=len(outputs['ppc']),hardware_accessed=False,limits=['Synthetic valid BIOS instruction streams, not captured GPU VBIOS','Register/PLL/MC endpoints numeric memory models; allocation, locks and time shimmed','Invalid table bounds/units investigated separately; no broad interpreter correctness claim','No hardware register side effects or firmware timing'])
(W/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
