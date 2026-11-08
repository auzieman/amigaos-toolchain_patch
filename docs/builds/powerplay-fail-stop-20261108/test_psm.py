"""R730: preserve first transition error through PSM, without publishing false state."""
from pathlib import Path
import subprocess,json,hashlib,difflib,os,resource
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
B=Path('/srv/data1/tabor-build/source-review');W=B/'powerplay-fail-stop-20261108';S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-005/source');rel='drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_psm.c';old=(S/rel).read_text()
def span(t,key):
 a=t.index(key);i=t.index('{',a)+1;d=1
 while d:d+=(t[i]=='{')-(t[i]=='}');i+=1
 return t[a:i]
a=span(old,'static void power_state_management(');newa=a.replace('static void','static int',1).replace('\tbool equal;','\tbool equal;\n\tint ret;').replace('\t\tphm_set_power_state(hwmgr, &pcurrent->hardware, &requested->hardware);','\t\tret = phm_set_power_state(hwmgr, &pcurrent->hardware, &requested->hardware);\n\t\tif (ret)\n\t\t\treturn ret;');newa=newa[:-1]+'\treturn 0;\n}'
b=span(old,'int psm_adjust_power_state_dynamic(');newb=b.replace('\tuint32_t index;','\tuint32_t index;\n\tint ret;').replace('\t\tif (hwmgr->ps)\n\t\t\tpower_state_management(hwmgr, new_ps);\n\t\telse','\t\tif (hwmgr->ps) {\n\t\t\tret = power_state_management(hwmgr, new_ps);\n\t\t\tif (ret)\n\t\t\t\treturn ret;\n\t\t} else')
assert newa!=a and newb!=b
fixed=old.replace(a,newa).replace(b,newb);patch=''.join(difflib.unified_diff(old.splitlines(True),fixed.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel));(W/'0026-powerplay-propagate-state-transition-failure.patch').write_text(patch);subprocess.run(['git','apply','--check',str(W/'0026-powerplay-propagate-state-transition-failure.patch')],cwd=S,check=True)
pre=(B/'shared-kernel-boundary-20261108/fixed-asic-clock.c').read_text().split('union get_clock_dividers')[0]+r'''
#define NULL ((void*)0)
#define AMD_DPM_FORCED_LEVEL_MANUAL 99
#define Workload_Policy_Max 8
struct pp_hw_power_state{u32 clock;};struct pp_power_state{struct pp_hw_power_state hardware;u32 id;};
struct pp_hwmgr;struct ops{int(*set_power_profile_mode)(struct pp_hwmgr*,long*,unsigned);};
struct pp_hwmgr{struct pp_power_state*current_ps,*request_ps;unsigned ps_size;bool not_vf,ps;unsigned request_dpm_level,dpm_level,workload_mask;long workload_setting[8],power_profile_mode;struct ops*hwmgr_func;};
static int transition_error,transitions,post,pre_calls;static bool states_equal,display_update;
static int phm_apply_state_adjust_rules(struct pp_hwmgr*h,struct pp_power_state*r,struct pp_power_state*c){(void)h;(void)r;(void)c;return 0;}
static int phm_check_states_equal(struct pp_hwmgr*h,void*c,void*r,bool*equal){(void)h;(void)c;(void)r;*equal=states_equal;return 0;}
static bool phm_check_smc_update_required_for_display_configuration(struct pp_hwmgr*h){(void)h;return display_update;}
static int phm_set_power_state(struct pp_hwmgr*h,void*c,void*r){(void)h;(void)c;(void)r;transitions++;return transition_error;}
static void phm_display_configuration_changed(struct pp_hwmgr*h){(void)h;pre_calls++;}
static void phm_apply_clock_adjust_rules(struct pp_hwmgr*h){(void)h;post++;}
static void phm_notify_smc_display_config_after_ps_adjustment(struct pp_hwmgr*h){(void)h;post++;}
static int phm_force_dpm_levels(struct pp_hwmgr*h,unsigned l){(void)h;(void)l;post++;return 0;}
static int profile(struct pp_hwmgr*h,long*w,unsigned n){(void)h;(void)w;(void)n;post++;return 0;}
static unsigned fls(unsigned v){unsigned n=0;while(v){n++;v>>=1;}return n;}
'''
main=r'''
int main(void){unsigned cases=0;int errors[]={0,-5,-6,-95};
 for(unsigned skip=0;skip<2;skip++)for(unsigned equal=0;equal<2;equal++)for(unsigned display=0;display<2;display++)for(unsigned explicit=0;explicit<2;explicit++)for(unsigned err=0;err<4;err++){
  struct pp_power_state current={{21400},1},requested={{107100},2},other={{87400},3};struct ops ops={profile};struct pp_hwmgr h={&current,&requested,sizeof(current),true,true,2,1,1,{7},0,&ops};
  transition_error=errors[err];states_equal=equal;display_update=display;transitions=post=pre_calls=0;
  bool attempted=!equal||display,failed=attempted&&transition_error;
  int ret=psm_adjust_power_state_dynamic(&h,skip,explicit?&other:0);
#if FIXED
  if(ret!=(failed?transition_error:0))return 1;
  if(failed&&(post||current.id!=1||current.hardware.clock!=21400||h.dpm_level!=1))return 2;
#else
  if(ret)return 3;
  if(failed&&(current.id!=2||!post||h.dpm_level!=2))return 4;
#endif
  if(transitions!=attempted||pre_calls!=!skip)return 5;
  if(!failed){if(current.id!=(attempted?2:1))return 6;hex(current.hardware.clock);hex(current.id);hex(post);hex(h.dpm_level);}
  cases++;
 }
 if(cases!=64)return 7;return 0;}
'''
outputs={}
for ver,t in [('old',old),('fixed',fixed)]:
 code=pre+span(t,'static '+('void'if ver=='old'else'int')+' power_state_management(')+span(t,'int psm_adjust_power_state_dynamic(')+'\n#define FIXED '+str(int(ver=='fixed'))+'\n'+main;(W/('psm-'+ver+'.c')).write_text(code)
 for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
  exe=W/('psm-'+ver+'-'+arch);cmd=[cc]+(['-mstackrealign']if arch=='x86'else[])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static',str(W/('psm-'+ver+'.c')),'-o',str(exe)]
  c=subprocess.run(cmd,capture_output=True);(W/('psm-'+ver+'-'+arch+'-compile.log')).write_bytes(c.stderr);c.check_returncode();c=subprocess.run(runner+[str(exe)],capture_output=True);c.check_returncode();outputs[ver,arch]=c.stdout
assert len(set(outputs.values()))==1
r=dict(status='PASS',actual_functions=2,scenarios_per_version_architecture=64,total_scenarios=256,patch_sha256=hashlib.sha256(patch.encode()).hexdigest(),success_flow_unchanged=True,hardware_accessed=False,limits=['Transition and side effects mocked; first-fault cause not established','Preserves preexisting successful-state copy semantics','No GPU recovery or display acceptance'])
(W/'psm-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
