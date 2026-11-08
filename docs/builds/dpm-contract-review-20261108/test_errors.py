"""Fault-inject the extracted real startup routine; native control, no GPU access."""
from pathlib import Path
import re, subprocess, tempfile, json
root=Path('/srv/data1/tabor-build/source-review/dpm-contract-review-20261108')
source=Path('/srv/data1/tabor-build/linux-live-001/work/polaris-powerplay-20261108-003/source/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.c').read_text()
a=source.index('static int smu7_enable_dpm_tasks(');b=source.index('\n}\n',a)+3
baseline=source[a:b];fixed=baseline
for message in ['Failed to initialize SMC table!','Failed to start DPM!']:
 fixed=fixed.replace('"'+message+'", result = tmp_result);','"'+message+'", return tmp_result);')
calls=set(re.findall(r'PP_INIT_CALL\(hwmgr, (\w+)\(hwmgr\)\)',baseline))
header='''
#include <stdio.h>
typedef int PPSMC_Msg;
struct pp_hwmgr {int chip_id; struct {int platformCaps;} platform_descriptor;};
static int fail_table,fail_dpm,late_calls;
#define CHIP_VEGAM 10
#define CHIP_POLARIS10 5
#define PHM_PlatformCaps_EngineSpreadSpectrumSupport 1
#define PHM_PlatformCaps_ThermalController 2
#define phm_cap_enabled(a,b) 0
#define PHM_WRITE_INDIRECT_FIELD(...) ((void)0)
#define PP_INIT_CALL(h,c) (c)
#define PP_ASSERT_WITH_CODE(c,m,a) do { if (!(c)) { a; } } while(0)
static int smu7_voltage_control(struct pp_hwmgr *h) {return 0;}
static int smum_initialize_mc_reg_table(struct pp_hwmgr *h) {return 0;}
static int smum_send_msg_to_smc(struct pp_hwmgr *h,int m,void*p){return 0;}
#define PPSMC_NoDisplay 0
static void smu7_populate_umdpstate_clocks(struct pp_hwmgr*h){}
'''
for call in sorted(calls):
 body='return 0;'
 if call=='smum_init_smc_table':body='return fail_table ? -5 : 0;'
 if call=='smu7_start_dpm':body='return fail_dpm ? -22 : 0;'
 if call=='smu7_enable_smc_cac':body='late_calls++; return 0;'
 header+=f'static int {call}(struct pp_hwmgr*h){{{body}}}\n'
main='''
int main(void){struct pp_hwmgr h={.chip_id=5};int r;
fail_table=1; late_calls=0; r=baseline_run(&h);
if(r!=0 || late_calls!=1)return 1;
late_calls=0;r=fixed_run(&h);if(r!=-5 || late_calls!=0)return 2;
fail_table=0;fail_dpm=1;late_calls=0;r=baseline_run(&h);
if(r!=0 || late_calls!=1)return 3;
late_calls=0;r=fixed_run(&h);if(r!=-22 || late_calls!=0)return 4;
fail_dpm=0;late_calls=0;r=fixed_run(&h);
if(r!=0 || late_calls!=1)return 5;
puts("PASS: baseline masks both faults; candidate propagates both and stops late calls; success path preserved");return 0;}
'''
code=header+baseline.replace('smu7_enable_dpm_tasks','baseline_run',1)+fixed.replace('smu7_enable_dpm_tasks','fixed_run',1)+main
(root/'error-flow-test.c').write_text(code)
subprocess.run(['cc','-O0',str(root/'error-flow-test.c'),'-o',str(root/'error-flow-test')],check=True)
r=subprocess.run([str(root/'error-flow-test')],capture_output=True,text=True,check=True)
(root/'error-flow-test.log').write_text(r.stdout);print(r.stdout)
