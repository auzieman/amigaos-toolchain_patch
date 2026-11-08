"""Run only on R730: connect actual state, level, upload and mailbox functions."""
from pathlib import Path
import subprocess,json,hashlib,os,resource
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
B=Path('/srv/data1/tabor-build/source-review');W=B/'connected-gpu-flow-20261108';W.mkdir(exist_ok=True)
state_tail=r'''
int state_export(unsigned rev,unsigned lo,unsigned hi,u32*out) {
 u32 clocks[]={21400,33500,50300,69700,87400,101900,104300,107100};
 u8 blob[2048]={0};ATOM_Tonga_POWERPLAYTABLE*pp=(void*)blob;
 put16(&pp->usSclkDependencyTableOffset,256);put16(&pp->usMclkDependencyTableOffset,1024);
 ATOM_Tonga_MCLK_Dependency_Table*mem=(void*)(blob+1024);mem->ucNumEntries=8;
 PPTable_Generic_SubTable_Header*hdr=(void*)(blob+256);hdr->ucRevId=rev;
 for(unsigned i=0;i<8;i++){
  put_unaligned_le32(30000+i*10000,&mem->entries[i].ulMclk);
  if(!rev)put_unaligned_le32(clocks[i],&((ATOM_Tonga_SCLK_Dependency_Table*)hdr)->entries[i].ulSclk);
  else put_unaligned_le32(clocks[i],&((ATOM_Polaris_SCLK_Dependency_Table*)hdr)->entries[i].ulSclk);
 }
 ATOM_Tonga_State raw={0};raw.ucEngineClockIndexLow=lo;raw.ucEngineClockIndexHigh=hi;raw.ucMemoryClockIndexLow=lo;raw.ucMemoryClockIndexHigh=hi;
 struct pp_power_state state={0};struct smu7_hwmgr data={0};struct pp_hwmgr h={.backend=&data,.platform_descriptor={8}};
 typeof(*h.display_config)config={0};h.display_config=&config;
 if(smu7_get_pp_table_entry_callback_func_v1(&h,&raw,&state,pp,0))return 1;
 for(unsigned i=0;i<8;i++){data.dpm_table.sclk_table.dpm_levels[i].value=clocks[i];data.dpm_table.mclk_table.dpm_levels[i].value=30000+i*10000;}
 data.dpm_table.sclk_table.count=8;data.dpm_table.mclk_table.count=8;
 struct phm_set_power_state_input input={&state.hardware};
 if(smu7_find_dpm_states_clocks_in_dpm_table(&h,&input))return 2;
 smu7_trim_single_dpm_states(&h,&data.dpm_table.sclk_table,state.hardware.performance_levels[0].engine_clock,state.hardware.performance_levels[1].engine_clock);
 smu7_trim_single_dpm_states(&h,&data.dpm_table.mclk_table,state.hardware.performance_levels[0].memory_clock,state.hardware.performance_levels[1].memory_clock);
 for(unsigned i=0;i<8;i++){out[i]=data.dpm_table.sclk_table.dpm_levels[i].value;out[8+i]=data.dpm_table.mclk_table.dpm_levels[i].value;}
 out[16]=mask(&data.dpm_table.sclk_table);out[17]=mask(&data.dpm_table.mclk_table);return 0;
}
'''
# Separate translation units keep each original fixture's mock hwmgr layout private.
pipeline=(B/'clock-table-pipeline-20261108/pipeline.c').read_text().split('int main(void) {')[0]
transport=(B/'smu-flow-review-20261108/transport.c').read_text()
senders=transport[transport.index('int smu7_send_msg_to_smc('):transport.index('int main(void) {')]
pipeline=pipeline.replace('static void cgs_write_register(void*d,u32 r,u32 v){(void)d;(void)r;', 'static u32 arg,message,response=1,injected=1;static unsigned sends;\n#define mmSMC_RESP_0 2\n#define mmSMC_MESSAGE_0 3\n#define mmSMC_MSG_ARG_0 4\nstatic void cgs_write_register(void*d,u32 r,u32 v){(void)d;if(r==2){response=v;return;}if(r==3){message=v;response=injected;sends++;return;}if(r==4){arg=v;return;}')
pipeline+='''\n#undef PHM_READ_FIELD
#define PHM_READ_FIELD(...) response
#define PHM_WAIT_FIELD_UNEQUAL(...) do {}while(0)
#define dev_info(...) do {}while(0)
#define dev_dbg(...) do {}while(0)
#define EOPNOTSUPP 95
#define EIO 5
#define ENXIO 6
'''+senders
main=r'''
extern int state_export(unsigned,unsigned,unsigned,u32*);
int main(void){
 struct amdgpu_device adev={0};struct smu7_hwmgr data={0};struct polaris10_smumgr smu={0};
 phm_ppt_v1_clock_voltage_dependency_table dep={7};struct phm_ppt_v1_information info={&dep,&dep};struct config cfg={10000,1,60};
 struct pp_hwmgr h={.adev=&adev,.backend=&data,.smu_backend=&smu,.pptable=&info,.display_config=&cfg,.chip_id=CHIP_POLARIS11};
 data.current_profile_setting=(struct profile){0x1234,3,4,0x5678,5,6};
 smu.range_table[0].trans_upper_frequency=0xffffffff;smu.smc_state_table.SclkFcwRangeTable[0].postdiv=1;
 unsigned accepted=0,rejected=0;
 for(unsigned rev=0;rev<2;rev++)for(unsigned lo=0;lo<8;lo++)for(unsigned hi=lo;hi<8;hi++){
  u32 clocks[18];if(state_export(rev,lo,hi,clocks))return 1;
  /* Offline admission: all native values must remain inside this input fixture's domain. */
  bool valid=true;for(unsigned i=0;i<8;i++)if(clocks[i]>107100||clocks[8+i]>100000)valid=false;
  if(!valid){if(sends)return 2;rejected++;continue;}
  unsigned expected=((1u<<(hi+1))-1)&~((1u<<lo)-1);
  if(clocks[16]!=expected||clocks[17]!=expected)return 3;
  for(unsigned i=0;i<8;i++){
   struct SMU74_Discrete_GraphicsLevel g={0};struct SMU74_Discrete_MemoryLevel m={0};
   if(polaris10_populate_single_graphic_level(&h,clocks[i],&g)||polaris10_populate_single_memory_level(&h,clocks[8+i],&m))return 4;
   if(last_request!=(clocks[i]|0x01000000)||be32_to_cpu(g.SclkSetting.SclkFrequency)!=clocks[i]||be32_to_cpu(m.MclkFrequency)!=clocks[8+i])return 5;
   if(smu7_copy_bytes_to_smc(&h,0,(u8*)&g,sizeof(g),512)||smu7_copy_bytes_to_smc(&h,128,(u8*)&m,sizeof(m),512))return 6;
   for(unsigned j=0;j<sizeof(g);j++)if(ram[j]!=((u8*)&g)[j])return 7;
   for(unsigned j=0;j<sizeof(m);j++)if(ram[128+j]!=((u8*)&m)[j])return 8;
   emit((char*)ram,sizeof(g));emit((char*)ram+128,sizeof(m));
  }
  u32 replies[]={1,0xfe,0xffff,0,2,0x1234};int results[]={0,-EOPNOTSUPP,-ENXIO,-EIO,-EIO,-EIO};
  for(unsigned c=16;c<17;c++)for(unsigned r=0;r<6;r++){
   injected=replies[r];int ret=smu7_send_msg_to_smc_with_parameter(&h,0x145,clocks[c]);
   if(ret!=results[r]||message!=0x145||arg!=clocks[c])return 9;
   hex(arg);hex(ret);
  }
  accepted++;
 }
#if NEGATIVE && __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
 if(accepted||rejected!=72||sends)return 10;
#else
 if(accepted!=72||rejected||sends!=432)return 11;
#endif
 hex(accepted);hex(rejected);hex(sends);return 0;
}
'''
# Only the generated SCLK mask is submitted; MCLK selection is checked above.
inputs={};outputs={}
for version in ('old','fixed'):
 original=(B/f'state-clock-decode-20261108/{version}.c').read_text()
 state=original.split('int main(void) {')[0]+state_tail
 state='#define main unused_state_main\n#define _start unused_state_start\n#define memcpy state_memcpy\n#define memset state_memset\n'+state
 (W/f'{version}-state.c').write_text(state)
 (W/f'{version}-flow.c').write_text(pipeline+'\n#define NEGATIVE '+str(int(version=='old'))+'\n'+main)
 for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
  exe=W/f'{version}-{arch}'
  cmd=[cc]+(['-mstackrealign']if arch=='x86'else[])+['-O2','-ffunction-sections','-Wl,--gc-sections','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static',str(W/f'{version}-state.c'),str(W/f'{version}-flow.c'),'-lgcc','-o',str(exe)]
  p=subprocess.run(cmd,capture_output=True);(W/f'{version}-{arch}-compile.log').write_bytes(p.stderr);p.check_returncode()
  p=subprocess.run(runner+[str(exe)],capture_output=True);(W/f'{version}-{arch}.bin').write_bytes(p.stdout);p.check_returncode();outputs[version,arch]=p.stdout
 for name in ('state','flow'):inputs[f'{version}-{name}.c']=hashlib.sha256((W/f'{version}-{name}.c').read_bytes()).hexdigest()
assert outputs['fixed','x86']==outputs['fixed','ppc']==outputs['old','x86']
assert outputs['old','ppc']!=outputs['fixed','ppc']
r=dict(status='PASS',scenarios_per_build=72,accepted_fixed_per_architecture=72,old_ppc_rejected_before_upload_or_message=72,fixed_mailbox_checks_per_architecture=432,actual_source_functions=10,hardware_accessed=False,deployment_allowed=False,source_sha256=inputs,output_bytes=len(outputs['fixed','ppc']),output_sha256=hashlib.sha256(outputs['fixed','ppc']).hexdigest(),limitations=['Synthetic raw state indices and voltage inputs; four observed PLL response fields only','Individual level objects, not whole DPM table or complete hardware init','Numeric register mock, no DMA/coherency/timing or physical GPU execution','Admission guard belongs to offline test only; not a kernel patch','SCLK mask submitted only; MCLK mask checked without command sequencing'])
(W/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
