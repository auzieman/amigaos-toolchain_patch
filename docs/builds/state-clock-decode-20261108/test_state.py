"""R730: raw VBIOS state -> native clocks -> DPM update -> trim/mask."""
from pathlib import Path
import re,subprocess,json,hashlib,difflib
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-003/source');P=S/'drivers/gpu/drm/amd/pm/powerplay'
W=Path('/srv/data1/tabor-build/source-review/state-clock-decode-20261108');W.mkdir(exist_ok=True)
def span(text,start):
 a=text.index(start);i=text.index('{',a)+1;d=1
 while d:d+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[a:i]
source=(P/'hwmgr/smu7_hwmgr.c').read_text();original=span(source,'static int smu7_get_pp_table_entry_callback_func_v1(')
# Fix all six raw clock loads in the same V1 state-construction boundary.
fixed=re.sub(r'(performance_level->(?:memory_clock|engine_clock)\s*=\s*)(.*?)(;)',lambda m:m[1]+'le32_to_cpu('+m[2]+')'+m[3],original,flags=re.S)
assert fixed.count('le32_to_cpu(')-original.count('le32_to_cpu(')==6
changed=source.replace(original,fixed);rel='drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.c'
patch=''.join(difflib.unified_diff(source.splitlines(True),changed.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(W/'0024-smu7-decode-native-state-clocks.patch').write_text(patch)
subprocess.run(['git','apply','--check',str(W/'0024-smu7-decode-native-state-clocks.patch')],cwd=S,check=True)
pre=(Path('/srv/data1/tabor-build/source-review/shared-kernel-boundary-20261108/fixed-asic-clock.c')).read_text().split('union get_clock_dividers',1)[0]
pre+='\n#define NULL ((void*)0)\n'
header=(P/'hwmgr/pptable_v1_0.h').read_text()
pre+='#pragma pack(push,1)\n'
for name in ['ATOM_Tonga_POWERPLAYTABLE','ATOM_Tonga_State','ATOM_Tonga_MCLK_Dependency_Record','ATOM_Tonga_MCLK_Dependency_Table','ATOM_Tonga_SCLK_Dependency_Record','ATOM_Tonga_SCLK_Dependency_Table','ATOM_Polaris_SCLK_Dependency_Record','ATOM_Polaris_SCLK_Dependency_Table','PPTable_Generic_SubTable_Header']:
 pre+=span(header,'typedef struct _'+name+' {')+' '+name+';\n'
pre+='#pragma pack(pop)\n'
# Keep source constants, not hand-invented classification meanings.
for line in header.splitlines():
 if any(line.startswith('#define '+n+' ') for n in ['ATOM_Tonga_DISALLOW_ON_DC','ATOM_Tonga_ENABLE_VARIBRIGHT']):pre+=line+'\n'
scaffold=r'''
#define PP_ASSERT_WITH_CODE(test,msg,action) do {if(!(test)){action;}}while(0)
#define SMU_MAX_LEVELS_GRAPHICS 0
#define DPMTABLE_OD_UPDATE_SCLK 1
#define DPMTABLE_OD_UPDATE_MCLK 2
#define DPMTABLE_UPDATE_SCLK 4
#define DPMTABLE_UPDATE_MCLK 8
#define SMU7_MINIMUM_ENGINE_CLOCK 10000
struct smu7_performance_level {u32 engine_clock,memory_clock,pcie_gen,pcie_lane;};
struct smu7_power_state {unsigned performance_level_count;struct smu7_performance_level performance_levels[8];};
struct pp_power_state {struct smu7_power_state hardware;
 struct {u32 ui_label,flags;bool temporary_state,to_be_deleted;}classification;
 struct {bool disallowOnDC;u32 supportedPowerLevels;}validation;
 struct {u32 lanes;}pcie;
 struct {bool disableFrameModulation,limitRefreshrate,enableVariBright;}display;
 struct {u32 VCLK,DCLK;}uvd_clocks;struct {u32 min,max;}temperatures;};
struct smu7_single_dpm_table {unsigned count;struct {u32 value;bool enabled;}dpm_levels[8];};
struct smu7_hwmgr {u32 pcie_gen_cap,pcie_lane_cap,need_update_smu7_dpm_table;
 struct {struct smu7_single_dpm_table sclk_table,mclk_table;}dpm_table;
 struct {u32 min_clock_in_sr,num_existing_displays;}display_timing;};
struct pp_hwmgr {void*backend;bool od_enabled;struct {unsigned hardwareActivityPerformanceLevels;}platform_descriptor;struct {unsigned num_display;}*display_config;};
struct phm_set_power_state_input {const struct smu7_power_state*pnew_state;};
struct PP_Clocks {u32 engineClockInSR;};
static const struct smu7_power_state*cast_const_phw_smu7_power_state(const struct smu7_power_state*p){return p;}
static u32 get_pcie_gen_support(u32 caps,u32 value){(void)caps;return value;}
static u32 get_pcie_lane_support(u32 caps,u32 value){(void)caps;return value;}
static unsigned smum_get_mac_definition(struct pp_hwmgr*h,unsigned type){(void)h;(void)type;return 8;}
static void put16(void*p,u16 v){u8*b=p;b[0]=v;b[1]=v>>8;}
static unsigned mask(const struct smu7_single_dpm_table*t){unsigned m=0;for(unsigned i=0;i<t->count;i++)if(t->dpm_levels[i].enabled)m|=1<<i;return m;}
'''
stateupdate=span(source,'static int smu7_find_dpm_states_clocks_in_dpm_table(')
trim=span(source,'static int smu7_trim_single_dpm_states(')
main=r'''
int main(void) {
 u32 clocks[]={21400,33500,50300,69700,87400,101900,104300,107100};
 u8 blob[2048]={0};ATOM_Tonga_POWERPLAYTABLE*pp=(void*)blob;
 put16(&pp->usSclkDependencyTableOffset,256);put16(&pp->usMclkDependencyTableOffset,1024);
 ATOM_Tonga_MCLK_Dependency_Table*mem=(void*)(blob+1024);mem->ucNumEntries=8;
 for(unsigned i=0;i<8;i++)put_unaligned_le32(30000+i*10000,&mem->entries[i].ulMclk);
 for(unsigned rev=0;rev<2;rev++) {
  PPTable_Generic_SubTable_Header*hdr=(void*)(blob+256);hdr->ucRevId=rev;
  for(unsigned i=0;i<8;i++) {
   if(rev==0)put_unaligned_le32(clocks[i],&((ATOM_Tonga_SCLK_Dependency_Table*)hdr)->entries[i].ulSclk);
   else put_unaligned_le32(clocks[i],&((ATOM_Polaris_SCLK_Dependency_Table*)hdr)->entries[i].ulSclk);
  }
  for(unsigned lo=0;lo<8;lo++)for(unsigned hi=lo;hi<8;hi++) {
   ATOM_Tonga_State raw={0};raw.ucEngineClockIndexLow=lo;raw.ucEngineClockIndexHigh=hi;raw.ucMemoryClockIndexLow=lo;raw.ucMemoryClockIndexHigh=hi;
   struct pp_power_state state={0};struct smu7_hwmgr data={0};
   struct pp_hwmgr h={.backend=&data,.platform_descriptor={8}};typeof(*h.display_config)config={0};h.display_config=&config;
   if(smu7_get_pp_table_entry_callback_func_v1(&h,&raw,&state,pp,0))return 1;
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
   u32 low=FIXED?clocks[lo]:__builtin_bswap32(clocks[lo]);u32 high=FIXED?clocks[hi]:__builtin_bswap32(clocks[hi]);
#else
   u32 low=clocks[lo],high=clocks[hi];
#endif
   if(state.hardware.performance_levels[0].engine_clock!=low||state.hardware.performance_levels[1].engine_clock!=high)return 2;
   u32 ml=30000+lo*10000,mh=30000+hi*10000;
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
   if(!FIXED){ml=__builtin_bswap32(ml);mh=__builtin_bswap32(mh);}
#endif
   if(state.hardware.performance_levels[0].memory_clock!=ml||state.hardware.performance_levels[1].memory_clock!=mh)return 6;
   for(unsigned i=0;i<8;i++){data.dpm_table.sclk_table.dpm_levels[i].value=clocks[i];data.dpm_table.mclk_table.dpm_levels[i].value=30000+i*10000;}
   data.dpm_table.sclk_table.count=8;data.dpm_table.mclk_table.count=8;
   struct phm_set_power_state_input input={&state.hardware};
   if(smu7_find_dpm_states_clocks_in_dpm_table(&h,&input))return 3;
   smu7_trim_single_dpm_states(&h,&data.dpm_table.sclk_table,low,high);
   smu7_trim_single_dpm_states(&h,&data.dpm_table.mclk_table,ml,mh);
   hex(rev);hex(lo);hex(hi);hex(low);hex(high);hex(data.dpm_table.sclk_table.dpm_levels[7].value);hex(mask(&data.dpm_table.sclk_table));hex(ml);hex(mh);hex(data.dpm_table.mclk_table.dpm_levels[7].value);hex(mask(&data.dpm_table.mclk_table));emit("\n",1);
   if(FIXED || __BYTE_ORDER__ != __ORDER_BIG_ENDIAN__) {
    unsigned expected=((1u<<(hi+1))-1)&~((1u<<lo)-1);
    if(mask(&data.dpm_table.sclk_table)!=expected||data.dpm_table.sclk_table.dpm_levels[7].value!=107100)return 4;
    if(mask(&data.dpm_table.mclk_table)!=expected||data.dpm_table.mclk_table.dpm_levels[7].value!=100000)return 7;
   }
  }
 }
 return 0;
}
'''
r={'status':'started','actual_driver_functions':3,'cases_per_version_architecture':72,'bios_revisions':[0,1],'raw_clock_loads_corrected':6,'gpu_accessed':False,'hardware_tested':False,'mask_aggregation':'Model; actual state constructor, DPM update and trim extracted.','patch_sha256':hashlib.sha256(patch.encode()).hexdigest()}
license=source.split('#include',1)[0]
for name,body in [('old',original),('fixed',fixed)]:
 code=license+pre+scaffold+body+stateupdate+trim+'\n#define FIXED '+str(int(name=='fixed'))+'\n'+main
 (W/(name+'.c')).write_text(code)
 for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
  exe=W/(name+'-'+arch);cmd=[cc]+(['-mstackrealign'] if arch=='x86' else [])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static',str(W/(name+'.c')),'-o',str(exe)]
  c=subprocess.run(cmd,capture_output=True,text=True);(W/(name+'-'+arch+'-compile.log')).write_text(c.stderr)
  if c.returncode:raise RuntimeError(c.stderr)
  c=subprocess.run(runner+[str(exe)],capture_output=True);(W/(name+'-'+arch+'.log')).write_bytes(c.stdout);c.check_returncode()
assert (W/'old-x86.log').read_bytes()==(W/'fixed-x86.log').read_bytes()==(W/'fixed-ppc.log').read_bytes()
assert (W/'old-ppc.log').read_bytes()!=(W/'old-x86.log').read_bytes()
first=(W/'old-ppc.log').read_text().splitlines()[0].split()
assert int(first[3],16)==0x98530000 and int(first[5],16)==0x98530000 and int(first[6],16)==0x80
r.update(status='PASS',original_ppc_reproduces_recorded_reversed_clock_and_mask=True,fixed_ppc_matches_unchanged_x86=True)
(W/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
