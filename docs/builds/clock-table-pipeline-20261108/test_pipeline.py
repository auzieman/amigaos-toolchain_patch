"""R730: actual ATOM decode -> native PLL -> complete SMU level objects -> SRAM."""
from pathlib import Path
import re,subprocess,json,hashlib
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-003/source');P=S/'drivers/gpu/drm/amd/pm/powerplay'
W=Path('/srv/data1/tabor-build/source-review/clock-table-pipeline-20261108');W.mkdir(exist_ok=True)
def span(text,start):
 a=text.index(start);i=text.index('{',a)+1;depth=1
 while depth:depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[a:i]
old=(Path('/srv/data1/tabor-build/source-review/shared-kernel-boundary-20261108/fixed-asic-clock.c')).read_text()
pre=old[:old.index('union get_clock_dividers')]
pre=pre.replace('static uint32_t get_unaligned_le32','static uint32_t get_unaligned_le32')
pre+='''
typedef unsigned long long uint64_t;typedef uint64_t u64;
#define NULL ((void*)0)
#define CHIP_POLARIS11 1
#define PP_INIT_CALL(h,expr) (expr)
#define pr_info(...) do {}while(0)
#define PP_ASSERT_WITH_CODE(test,msg,action) do {if(!(test)){action;}}while(0)
#define PHM_PlatformCaps_SclkDeepSleep 1
#define PPSMC_DISPLAY_WATERMARK_LOW 0
#define NUM_SCLK_RANGE 8
#define do_div(n,b) ((n)/=(b))
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define cpu_to_be32(x) (x)
#define cpu_to_be16(x) (x)
#define be32_to_cpu(x) (x)
#define be16_to_cpu(x) (x)
#else
#define cpu_to_be32(x) __builtin_bswap32(x)
#define cpu_to_be16(x) __builtin_bswap16(x)
#define be32_to_cpu(x) __builtin_bswap32(x)
#define be16_to_cpu(x) __builtin_bswap16(x)
#endif
'''
pre+='#include "'+str(P/'inc/pp_endian.h')+'"\n'
h=(S/'drivers/gpu/drm/amd/amdgpu/atom.h').read_text();pre+=h[h.index('/* The ATOM parameter word is LE:'):h.index('struct drm_device;')]
header=(P/'inc/smu74_discrete.h').read_text();pre+='typedef uint32_t SMU_VoltageLevel;\n#pragma pack(push,1)\n'
for name in ['sclkFcwRange_t','SMU_SclkSetting','SMU74_Discrete_GraphicsLevel','SMU74_Discrete_MemoryLevel']:
 pre+=span(header,'struct '+name+' {')+';\ntypedef struct '+name+' '+name+';\n'
pre+='#pragma pack(pop)\n'
ctrl=(P/'hwmgr/ppatomctrl.h').read_text();pre+=span(ctrl,'struct pp_atomctrl_clock_dividers_ai {')+';\ntypedef struct pp_atomctrl_clock_dividers_ai pp_atomctrl_clock_dividers_ai;\n'
scaffold=r'''
struct phm_ppt_v1_clock_voltage_dependency_table {u32 tag;};
typedef struct phm_ppt_v1_clock_voltage_dependency_table phm_ppt_v1_clock_voltage_dependency_table;
struct phm_ppt_v1_information {phm_ppt_v1_clock_voltage_dependency_table *vdd_dep_on_sclk,*vdd_dep_on_mclk;};
struct profile {u32 sclk_activity,sclk_up_hyst,sclk_down_hyst,mclk_activity,mclk_up_hyst,mclk_down_hyst;};
struct timing {u32 min_clock_in_sr,num_existing_displays,vrefresh;};
struct smu7_hwmgr {struct profile current_profile_setting;struct timing display_timing;
 struct {phm_ppt_v1_clock_voltage_dependency_table vdd_dependency_on_sclk,vdd_dependency_on_mclk;} odn_dpm_table;
 u32 update_up_hyst,update_down_hyst,up_hyst,down_hyst;};
typedef struct {sclkFcwRange_t SclkFcwRangeTable[8];} SMU74_Discrete_DpmTable;
struct polaris10_smumgr {SMU74_Discrete_DpmTable smc_state_table;struct {u32 trans_lower_frequency,trans_upper_frequency;}range_table[8];};
struct atom_context {int unused;};
struct amdgpu_device {void*dev;struct {struct atom_context*atom_context;}mode_info;};
struct config {u32 min_core_set_clock_in_sr,num_display,vrefresh;};
struct pp_hwmgr {struct amdgpu_device*adev;void*backend,*smu_backend,*pptable,*device;bool od_enabled;u32 chip_id;struct config*display_config;struct {u32 platformCaps;}platform_descriptor;};
static int phm_cap_enabled(u32 caps,u32 cap){return !!(caps&cap);}
static u32 amdgpu_asic_get_xclk(struct amdgpu_device*a){(void)a;return 2700;}
static u32 smu7_get_sleep_divider_id_from_clock(u32 clock,u32 min){return clock>min?2:0;}
static int polaris10_get_dependency_volt_by_clk(struct pp_hwmgr*h,struct phm_ppt_v1_clock_voltage_dependency_table*t,u32 clock,SMU_VoltageLevel*v,u32*mvdd){(void)h;*v=(clock^0x1234abcd)+t->tag;*mvdd=(clock^0x76543210)+t->tag;return 0;}
static const struct {u32 clock;u16 integer,fraction;u8 range,ssc;} observed[]={{21400,34,15728,0,1},{33500,53,39321,0,1},{50300,40,15728,1,1},{69700,55,49807,1,1},{87400,34,62914,2,1},{101900,40,49807,2,1},{104300,41,47185,2,1},{107100,42,55050,2,1}};
static int atom_failure;static u32 last_request;
static void put_le16(void*p,u16 v){u8*b=p;b[0]=v;b[1]=v>>8;}
static int amdgpu_atom_execute_table(struct atom_context*c,int index,u32*buffer,int size) {
 (void)c;(void)index;(void)size;last_request=get_unaligned_le32(buffer);
 if(atom_failure)return -5;
 COMPUTE_GPU_CLOCK_OUTPUT_PARAMETERS_V1_7*p=(void*)buffer;
 unsigned k=0;while(k<8 && observed[k].clock!=(last_request&0xffffff))k++;if(k==8)return -5;
 put_le16(&p->usSclk_fcw_frac,observed[k].fraction);put_le16(&p->usSclk_fcw_int,observed[k].integer);
 p->ucSclkPostDiv=3;p->ucSclkVcoMode=1;p->ucSclkPllRange=observed[k].range;p->ucSscEnable=observed[k].ssc;
 put_le16(&p->usSsc_fcw1_frac,0x3456);put_le16(&p->usSsc_fcw1_int,0x4567);
 put_le16(&p->usPcc_fcw_int,0x5678);put_le16(&p->usSsc_fcw_slew_frac,0x6789);put_le16(&p->usPcc_fcw_slew_frac,0x789a);
 return 0;
}
static u8 ram[512];static u32 address;
#define mmSMC_IND_DATA_11 1
static int smu7_set_smc_sram_address(struct pp_hwmgr*h,u32 a,u32 limit){(void)h;if(a>=limit)return -EINVAL;address=a;return 0;}
static void cgs_write_register(void*d,u32 r,u32 v){(void)d;(void)r;ram[address]=v>>24;ram[address+1]=v>>16;ram[address+2]=v>>8;ram[address+3]=v;}
static u32 cgs_read_register(void*d,u32 r){(void)d;(void)r;return ((u32)ram[address]<<24)|((u32)ram[address+1]<<16)|((u32)ram[address+2]<<8)|ram[address+3];}
'''
fn=[]
for file,name in [('hwmgr/ppatomctrl.c','int atomctrl_get_engine_pll_dividers_ai('),('smumgr/polaris10_smumgr.c','static int polaris10_calculate_sclk_params('),('smumgr/polaris10_smumgr.c','static int polaris10_populate_single_graphic_level('),('smumgr/polaris10_smumgr.c','static int polaris10_populate_single_memory_level('),('smumgr/smu7_smumgr.c','int smu7_copy_bytes_to_smc(')]:fn.append(span((P/file).read_text(),name))
main=r'''
int main(void) {
 struct amdgpu_device adev={0};struct smu7_hwmgr data={0};struct polaris10_smumgr smu={0};
 phm_ppt_v1_clock_voltage_dependency_table dep={7};struct phm_ppt_v1_information info={&dep,&dep};struct config cfg={10000,1,60};
 struct pp_hwmgr h={.adev=&adev,.backend=&data,.smu_backend=&smu,.pptable=&info,.display_config=&cfg,.chip_id=CHIP_POLARIS11};
 data.current_profile_setting=(struct profile){0x1234,3,4,0x5678,5,6};data.up_hyst=8;data.down_hyst=9;
 data.odn_dpm_table.vdd_dependency_on_sclk.tag=11;data.odn_dpm_table.vdd_dependency_on_mclk.tag=13;
 smu.range_table[0].trans_upper_frequency=0xffffffff;smu.smc_state_table.SclkFcwRangeTable[0].postdiv=1;
 u32 clocks[]={21400,33500,50300,69700,87400,101900,104300,107100};
 for(unsigned fail=0;fail<2;fail++)for(unsigned od=0;od<2;od++)for(unsigned deep=0;deep<2;deep++)for(unsigned hyst=0;hyst<4;hyst++)for(unsigned i=0;i<8;i++) {
  struct SMU74_Discrete_GraphicsLevel g={0};struct SMU74_Discrete_MemoryLevel m={0};
  atom_failure=fail;h.od_enabled=od;h.platform_descriptor.platformCaps=deep;data.update_up_hyst=hyst&1;data.update_down_hyst=hyst&2;
  if(polaris10_populate_single_graphic_level(&h,clocks[i],&g)||polaris10_populate_single_memory_level(&h,clocks[i],&m))return 1;
  if(last_request!=(clocks[i]|0x01000000))return 2;
  if(be32_to_cpu(g.SclkSetting.SclkFrequency)!=clocks[i]||be32_to_cpu(m.MclkFrequency)!=clocks[i])return 3;
  if(!fail&&(be16_to_cpu(g.SclkSetting.Fcw_int)!=observed[i].integer||be16_to_cpu(g.SclkSetting.Fcw_frac)!=observed[i].fraction||be16_to_cpu(g.SclkSetting.Pcc_up_slew_rate)!=0x789a||be16_to_cpu(g.SclkSetting.Sclk_ss_slew_rate)!=0x6789))return 4;
  if(be16_to_cpu(g.ActivityLevel)!=0x1234||be16_to_cpu(m.ActivityLevel)!=0x5678)return 5;
  if(be32_to_cpu(g.MinVoltage)!=(clocks[i]^0x1234abcd)+(od?11:7))return 6;
  if(be32_to_cpu(m.MinMvdd)!=(clocks[i]^0x76543210)+(od?13:7))return 7;
  if(smu7_copy_bytes_to_smc(&h,0,(u8*)&g,sizeof(g),512)||smu7_copy_bytes_to_smc(&h,128,(u8*)&m,sizeof(m),512))return 8;
  for(unsigned j=0;j<sizeof(g);j++)if(ram[j]!=((u8*)&g)[j])return 9;
  for(unsigned j=0;j<sizeof(m);j++)if(ram[128+j]!=((u8*)&m)[j])return 10;
  emit((char*)&g,sizeof(g));emit((char*)&m,sizeof(m));
 }
 return 0;
}
'''
# Stutter register input is fixed off in this deterministic model.
pre+='\n#define PHM_READ_FIELD(...) 0\n'
code=pre+scaffold+'\n'.join(fn)+main;(W/'pipeline.c').write_text(code)
r={'status':'started','actual_driver_functions':5,'scenarios_per_architecture':256,'objects_per_scenario':2,'gpu_accessed':False,'hardware_tested':False,'mock_inputs':['Four partial captured ATOM fields; other response fields synthetic','voltage dependency helper','display/profile data','sleep-divider helper','indexed SRAM registers'],'limits':'Complete individual GraphicsLevel/MemoryLevel objects, not full DPM table. Four response fields captured; remaining fields and voltage/profile inputs synthetic. Out-of-range physical request retained separately, not silently normalized.'}
for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
 exe=W/('pipeline-'+arch)
 cmd=[cc]+(['-mstackrealign'] if arch=='x86' else [])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static','-Wall','-Wextra',str(W/'pipeline.c'),'-lgcc','-o',str(exe)]
 c=subprocess.run(cmd,capture_output=True,text=True);(W/(arch+'-compile.log')).write_text(c.stderr)
 if c.returncode:raise RuntimeError(c.stderr[-4000:])
 c=subprocess.run(runner+[str(exe)],capture_output=True);(W/(arch+'.bin')).write_bytes(c.stdout);c.check_returncode()
a=(W/'x86.bin').read_bytes();b=(W/'ppc.bin').read_bytes();assert a==b
r.update(status='PASS',complete_object_bytes_match=True,output_bytes_per_architecture=len(a),output_sha256=hashlib.sha256(a).hexdigest())
(W/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
