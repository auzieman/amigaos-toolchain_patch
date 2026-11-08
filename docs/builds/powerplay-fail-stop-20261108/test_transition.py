"""R730-only: actual common PowerPlay transition with fault injection at each step."""
from pathlib import Path
import subprocess,json,hashlib,difflib,os,resource
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
B=Path('/srv/data1/tabor-build/source-review');W=B/'powerplay-fail-stop-20261108';W.mkdir(exist_ok=True)
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-004/source');rel='drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.c';original=(S/rel).read_text()
def span(t,name):
 a=t.index(name);i=t.index('{',a)+1;d=1
 while d:d+=(t[i]=='{')-(t[i]=='}');i+=1
 return t[a:i]
apply=span(original,'static void smu7_apply_minimum_dce_voltage_request(')
newapply=apply.replace('static void','static int',1).replace('\n\tsmum_send_msg_to_smc_with_parameter(','\n\treturn smum_send_msg_to_smc_with_parameter(')
upload=span(original,'static int smu7_upload_dpm_level_enable_mask(')
newupload='''static int smu7_upload_dpm_level_enable_mask(struct pp_hwmgr *hwmgr)
{
	struct smu7_hwmgr *data = (struct smu7_hwmgr *)(hwmgr->backend);
	int ret;

	ret = smu7_apply_minimum_dce_voltage_request(hwmgr);
	if (ret)
		return ret;

	if (!data->sclk_dpm_key_disabled &&
	    data->dpm_level_enable_mask.sclk_dpm_enable_mask) {
		ret = smum_send_msg_to_smc_with_parameter(hwmgr,
				PPSMC_MSG_SCLKDPM_SetEnabledMask,
				data->dpm_level_enable_mask.sclk_dpm_enable_mask,
				NULL);
		if (ret)
			return ret;
	}
	if (!data->mclk_dpm_key_disabled &&
	    data->dpm_level_enable_mask.mclk_dpm_enable_mask) {
		ret = smum_send_msg_to_smc_with_parameter(hwmgr,
				PPSMC_MSG_MCLKDPM_SetEnabledMask,
				data->dpm_level_enable_mask.mclk_dpm_enable_mask,
				NULL);
		if (ret)
			return ret;
	}

	return 0;
}'''
tasks=span(original,'static int smu7_set_power_state_tasks(')
newtasks=tasks.replace('int tmp_result, result = 0;','int tmp_result;').replace('result = tmp_result','return tmp_result').replace('return result;','return 0;')
assert newtasks.count('return tmp_result')==11
fixed=original.replace(apply,newapply).replace(upload,newupload).replace(tasks,newtasks)
patch=''.join(difflib.unified_diff(original.splitlines(True),fixed.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(W/'0025-smu7-stop-state-transition-on-error.patch').write_text(patch)
subprocess.run(['git','apply','--check',str(W/'0025-smu7-stop-state-transition-on-error.patch')],cwd=S,check=True)
pre=(B/'shared-kernel-boundary-20261108/fixed-asic-clock.c').read_text().split('union get_clock_dividers')[0]
pre+=r'''
#define NULL ((void*)0)
#define DPMTABLE_OD_UPDATE_VDDC 8
#define PHM_PlatformCaps_PCIEPerformanceRequest 1
#define VOLTAGE_SCALE 4
#define PPSMC_MSG_VddC_Request 0
#define PPSMC_MSG_SCLKDPM_SetEnabledMask 1
#define PPSMC_MSG_MCLKDPM_SetEnabledMask 2
#define PP_ASSERT_WITH_CODE(test,msg,action) do{if(!(test)){action;}}while(0)
struct smu7_hwmgr {u32 need_update_smu7_dpm_table;bool apply_optimized_settings,sclk_dpm_key_disabled,mclk_dpm_key_disabled;struct{u32 sclk_dpm_enable_mask,mclk_dpm_enable_mask;}dpm_level_enable_mask;};
struct pp_hwmgr{void*backend,*hardcode_pp_table;struct{u32 platformCaps;}platform_descriptor;};
static bool phm_cap_enabled(u32 c,u32 b){return !!(c&b);}
static int fail_step,error_code,calls,seen[32],command_fail,command_count,command_seen[4];
static int step(int id){seen[calls++]=id;return id==fail_step?error_code:0;}
static int smum_send_msg_to_smc_with_parameter(struct pp_hwmgr*h,u16 msg,u32 arg,void*out){(void)h;(void)arg;(void)out;command_seen[command_count++]=msg;return (int)msg==command_fail?error_code:0;}
static u32 smu7_lookup_vddc_from_dispclk(struct pp_hwmgr*h){(void)h;return 875;}
'''
callbacks=[('smu7_find_dpm_states_clocks_in_dpm_table',True),('smu7_request_link_speed_change_before_state_change',True),('smu7_freeze_sclk_mclk_dpm',False),('smu7_populate_and_upload_sclk_mclk_dpm_levels',True),('smu7_update_avfs',False),('smu7_generate_dpm_level_enable_mask',True),('smum_update_sclk_threshold',False),('smu7_unfreeze_sclk_mclk_dpm',False),('smu7_upload_dpm_level_enable_mask',False),('smu7_notify_smc_display',False),('smu7_notify_link_speed_change_after_state_change',True)]
# Keep actual upload helper. A wrapper records its place before running its nested requests.
for i,(name,hasinput)in enumerate(callbacks):
 if name=='smu7_upload_dpm_level_enable_mask':continue
 pre+='static int '+name+'(struct pp_hwmgr*h'+(',const void*input'if hasinput else'')+'){(void)h;'+('(void)input;'if hasinput else'')+'return step('+str(i)+');}\n'
main=r'''
int main(void){
 unsigned scenarios=0;int errors[]={-5,-6,-95};
 for(unsigned pcie=0;pcie<2;pcie++)for(unsigned custom=0;custom<2;custom++)for(unsigned e=0;e<3;e++)for(int failure=-1;failure<11;failure++){
  struct smu7_hwmgr data={.apply_optimized_settings=true,.dpm_level_enable_mask={0xff,0xff}};struct pp_hwmgr h={&data,custom?&data:0,{pcie}};
  calls=command_count=0;fail_step=failure;error_code=errors[e];command_fail=-1;
  int ret=smu7_set_power_state_tasks(&h,0);bool active=failure>=0&&(pcie||(failure!=1&&failure!=10));
  if(ret!=(active?error_code:0))return 1;
  unsigned expected=0;for(int id=0;id<11;id++){
   if(!pcie&&(id==1||id==10))continue;
   if(seen[expected++]!=id)return 2;
#if FIXED
   if(active&&id==failure)break;
#endif
  }
  if(calls!=(int)expected)return 3;
#if FIXED
  if(data.apply_optimized_settings==!active)return 4;
#else
  if(data.apply_optimized_settings)return 5;
#endif
  if(!active){for(unsigned i=0;i<expected;i++)hex(seen[i]);hex(data.need_update_smu7_dpm_table);}
  scenarios++;
 }
 for(unsigned disabled=0;disabled<4;disabled++)for(unsigned masks=0;masks<4;masks++)for(unsigned e=0;e<3;e++)for(int bad=-1;bad<3;bad++){
  struct smu7_hwmgr data={.sclk_dpm_key_disabled=disabled&1,.mclk_dpm_key_disabled=disabled&2,.dpm_level_enable_mask={masks&1?0xff:0,masks&2?0xff:0}};struct pp_hwmgr h={&data,0,{0}};
  command_count=0;command_fail=bad;error_code=errors[e];int ret=upload_impl(&h);
  bool active=bad==0||(bad==1&&!(disabled&1)&&(masks&1))||(bad==2&&!(disabled&2)&&(masks&2));
#if FIXED
  if(ret!=(active?error_code:0))return 6;
#else
  if(ret)return 7;
#endif
  unsigned count=0;for(int id=0;id<3;id++){
   if(id==1&&((disabled&1)||!(masks&1)))continue;if(id==2&&((disabled&2)||!(masks&2)))continue;
   if(command_seen[count++]!=id)return 8;
#if FIXED
   if(active&&id==bad)break;
#endif
  }
  if(command_count!=(int)count)return 9;scenarios++;
 }

 for(unsigned pcie=0;pcie<2;pcie++)for(unsigned custom=0;custom<2;custom++)for(unsigned e=0;e<3;e++)for(int bad=0;bad<3;bad++){
  struct smu7_hwmgr data={.apply_optimized_settings=true,.dpm_level_enable_mask={0xff,0xff}};struct pp_hwmgr h={&data,custom?&data:0,{pcie}};
  calls=command_count=0;fail_step=-1;command_fail=bad;error_code=errors[e];int ret=smu7_set_power_state_tasks(&h,0);
#if FIXED
  if(ret!=error_code||calls!=(pcie?9:8)||seen[calls-1]!=8||command_count!=bad+1||!data.apply_optimized_settings)return 10;
#else
  if(ret||calls!=(pcie?11:9)||command_count!=3||data.apply_optimized_settings)return 11;
#endif
  scenarios++;
 }
 if(scenarios!=372)return 12;return 0;
}
'''
results={}
for version,text in [('old',original),('fixed',fixed)]:
 a=span(text,'static '+('void'if version=='old'else'int')+' smu7_apply_minimum_dce_voltage_request(');u=span(text,'static int smu7_upload_dpm_level_enable_mask(').replace('smu7_upload_dpm_level_enable_mask(','upload_impl(',1)
 wrapper='static int smu7_upload_dpm_level_enable_mask(struct pp_hwmgr*h){int ret=step(8);return ret?ret:upload_impl(h);}\n'
 code=pre+a+u+wrapper+span(text,'static int smu7_set_power_state_tasks(')+'\n#define FIXED '+str(int(version=='fixed'))+'\n'+main
 (W/(version+'.c')).write_text(code)
 for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
  exe=W/(version+'-'+arch);cmd=[cc]+(['-mstackrealign']if arch=='x86'else[])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static',str(W/(version+'.c')),'-o',str(exe)]
  c=subprocess.run(cmd,capture_output=True);(W/(version+'-'+arch+'-compile.log')).write_bytes(c.stderr);c.check_returncode();c=subprocess.run(runner+[str(exe)],capture_output=True);(W/(version+'-'+arch+'.log')).write_bytes(c.stdout);c.check_returncode();results[version,arch]=c.stdout
assert len(set(results.values()))==1
r=dict(status='PASS',scenarios_per_version_architecture=372,total_scenarios=1488,actual_functions=3,old_control='Continues after callback failure and discards nested voltage/mask errors',fixed='Returns first error and issues no downstream callback or nested mask command',success_flow_unchanged=True,patch_sha256=hashlib.sha256(patch.encode()).hexdigest(),hardware_accessed=False,limitations=['Callbacks and SMU endpoint fault-injected, no hardware execution','Cannot cancel a request that already wedges PCIe or CPU','Failure after freeze may leave DPM frozen; no speculative recovery commands issued','Root cause of first hardware fault remains unproven'])
(W/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
