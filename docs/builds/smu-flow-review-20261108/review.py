"""R730: retain full state-flow source graph and test actual common SMU transport."""
from pathlib import Path
import re,json,subprocess,hashlib
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-003/source');P=S/'drivers/gpu/drm/amd/pm/powerplay'
W=Path('/srv/data1/tabor-build/source-review/smu-flow-review-20261108');W.mkdir(exist_ok=True)
files=['hwmgr/smu7_hwmgr.c','smumgr/polaris10_smumgr.c','smumgr/smu7_smumgr.c','hwmgr/ppatomctrl.c','hwmgr/process_pptables_v1_0.c','smumgr/smumgr.c','hwmgr/hwmgr.c']
functions={};origins={}
for name in files:
 text=(P/name).read_text()
 for m in re.finditer(r'(?:static\s+)?(?:int|void|bool|uint32_t|u32)\s+(\w+)\s*\([^;{}]*\)\s*\{',text,re.S):
  start=m.start();i=m.end();depth=1
  while depth:depth+=(text[i]=='{')-(text[i]=='}');i+=1
  fn=m[1];functions[fn]=text[start:i];origins[fn]={'file':name,'line':text[:start].count('\n')+1}
roots=['polaris10_init_smc_table','polaris10_populate_all_graphic_levels','polaris10_populate_all_memory_levels','smu7_set_power_state_tasks','smu7_force_dpm_level','smu7_force_dpm_highest','smu7_upload_dpm_level_enable_mask','smu7_send_msg_to_smc_with_parameter','smu7_copy_bytes_to_smc']
seen=set();edges={}
def walk(name):
 if name in seen or name not in functions:return
 seen.add(name)
 calls=list(dict.fromkeys(re.findall(r'\b(\w+)\s*\(',functions[name].split('{',1)[1])))
 edges[name]={'definition':origins[name],'resolved_calls':[n for n in calls if n in functions],'external_or_macro_calls':[n for n in calls if n not in functions and n not in ['if','while','for','switch','sizeof','offsetof','return']]}
 for n in edges[name]['resolved_calls']:walk(n)
for name in roots:walk(name)
(W/'flow.json').write_text(json.dumps({'source':str(S),'files_sha256':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in files},'roots':roots,'functions_reached':len(seen),'nodes':edges,'limits':'Static direct calls only; callback/PP_INIT_CALL/virtual dispatch must be resolved explicitly, not considered absent.'},indent=2)+'\n')
(W/'flow-source.c.txt').write_text('\n\n'.join('/* '+str(origins[n])+' */\n'+functions[n] for n in sorted(seen)))
base=(Path('/srv/data1/tabor-build/source-review/shared-kernel-boundary-20261108/fixed-asic-clock.c')).read_text();io=base[base.index('static void emit('):base.index('union get_clock_dividers')]
pre=r'''
typedef unsigned char uint8_t;typedef unsigned short uint16_t;typedef unsigned int uint32_t;typedef uint32_t u32;
#define EINVAL 22
#define EIO 5
#define ENXIO 6
#define EOPNOTSUPP 95
#define CHIP_POLARIS11 1
#define mmSMC_IND_DATA_11 1
#define mmSMC_MSG_ARG_0 2
#define mmSMC_RESP_0 3
#define mmSMC_MESSAGE_0 4
struct amdgpu_device {void*dev;};
struct pp_hwmgr {int chip_id;void*device;struct amdgpu_device*adev;};
#define pr_info(...) do {}while(0)
#define dev_info(...) do {}while(0)
#define dev_dbg(...) do {}while(0)
#define PP_ASSERT_WITH_CODE(test,msg,action) do {if(!(test)){action;}}while(0)
#define PHM_WAIT_FIELD_UNEQUAL(...) do {}while(0)
static uint8_t ram[512];static uint32_t address,arg,message,response=1,injected=1;
static int smu7_set_smc_sram_address(struct pp_hwmgr*h,uint32_t a,uint32_t limit){(void)h;if(a>=limit)return -EINVAL;address=a;return 0;}
/* Numeric registers, as provided by the kernel accessors. SMC SRAM is MSB-first. */
static void cgs_write_register(void*d,uint32_t reg,uint32_t value) {
 (void)d;
 if(reg==mmSMC_IND_DATA_11){ram[address]=value>>24;ram[address+1]=value>>16;ram[address+2]=value>>8;ram[address+3]=value;}
 else if(reg==mmSMC_MSG_ARG_0)arg=value;
 else if(reg==mmSMC_RESP_0)response=value;
 else if(reg==mmSMC_MESSAGE_0){message=value;response=injected;}
}
static uint32_t cgs_read_register(void*d,uint32_t reg){(void)d;(void)reg;return ((uint32_t)ram[address]<<24)|((uint32_t)ram[address+1]<<16)|((uint32_t)ram[address+2]<<8)|ram[address+3];}
#define PHM_READ_FIELD(...) response
int main(void);
'''
# Retain original driver license on extracted production functions.
license=(P/'smumgr/smu7_smumgr.c').read_text().split('#include',1)[0]
main=r'''
int main(void) {
 struct amdgpu_device dev={0};struct pp_hwmgr h={CHIP_POLARIS11,0,&dev};
 uint8_t source[128];unsigned transfer_cases=0,message_cases=0;
 for(unsigned i=0;i<128;i++)source[i]=(i*73+19)&255;
 for(unsigned offset=0;offset<16;offset+=4)for(unsigned n=1;n<=64;n++) {
  for(unsigned i=0;i<512;i++)ram[i]=0xa5;
  if(smu7_copy_bytes_to_smc(&h,offset,source,n,512))return 1;
  for(unsigned i=0;i<512;i++) {
   uint8_t expected=(i>=offset&&i<offset+n)?source[i-offset]:0xa5;
   if(ram[i]!=expected)return 2;
  }
  transfer_cases++;
 }
 if(smu7_copy_bytes_to_smc(&h,1,source,4,512)!=-EINVAL)return 3;
 if(smu7_copy_bytes_to_smc(&h,508,source,4,512)!=-EINVAL)return 4;
 uint32_t codes[]={1,0xfe,0xffff,0,2,0x1234};int results[]={0,-EOPNOTSUPP,-ENXIO,-EIO,-EIO,-EIO};
 for(unsigned mask=1;mask<256;mask++)for(unsigned r=0;r<6;r++) {
  injected=codes[r];
  int result=smu7_send_msg_to_smc_with_parameter(&h,0x145,mask);
  if(arg!=mask||message!=0x145||result!=results[r])return 5;
  message_cases++;
 }
 hex(transfer_cases);hex(message_cases);hex(2);emit("\n",1);return 0;
}
'''
code=license+pre+io+'\n'.join(functions[n] for n in ['smu7_copy_bytes_to_smc','smu7_send_msg_to_smc','smu7_send_msg_to_smc_with_parameter'])+main
(W/'transport.c').write_text(code)
r={'status':'started','gpu_accessed':False,'hardware_tested':False,'actual_common_transport_functions':3,'table_transfer_cases_per_architecture':256,'argument_response_cases_per_architecture':1530,'invalid_transfer_cases_per_architecture':2,'production_source_functions_in_graph':len(seen),'limits':'Numeric register endpoint and SRAM simulated; firmware table construction/semantics, PCIe/coherency and actual timing not validated.'}
for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
 exe=W/('transport-'+arch);cmd=[cc]+(['-mstackrealign'] if arch=='x86' else [])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static','-Wall','-Wextra',str(W/'transport.c'),'-o',str(exe)]
 c=subprocess.run(cmd,capture_output=True,text=True);(W/(arch+'-compile.log')).write_text(c.stderr)
 if c.returncode:raise RuntimeError(c.stderr)
 c=subprocess.run(runner+[str(exe)],capture_output=True);(W/(arch+'.log')).write_bytes(c.stdout);c.check_returncode()
assert (W/'x86.log').read_bytes()==(W/'ppc.log').read_bytes()
r.update(status='PASS',x86_ppc_results_identical=True)
(W/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
