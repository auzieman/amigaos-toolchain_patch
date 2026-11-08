"""Inspect immutable candidate inputs and emit error-propagation patch; no bind."""
from pathlib import Path
import difflib, hashlib, json, subprocess
source=Path('/srv/data1/tabor-build/linux-live-001/work/polaris-powerplay-20261108-003/source')
out=Path('/srv/data1/tabor-build/source-review/dpm-contract-review-20261108')
out.mkdir(exist_ok=True)
changes={}
name='drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.c'
before=(source/name).read_text()
# Fail only at table construction and DPM start: do not change optional features.
start=before.index('static int smu7_enable_dpm_tasks(')
end=before.index('\n}\n',start)+3
function=before[start:end]
for call,message in [('smum_init_smc_table(hwmgr)','Failed to initialize SMC table!'),('smu7_start_dpm(hwmgr)','Failed to start DPM!')]:
 old=f'"{message}", result = tmp_result);'
 new=f'"{message}", return tmp_result);'
 assert function.count(old)==1
 function=function.replace(old,new)
changes[name]=(before,before[:start]+function+before[end:])
patch=''.join(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+name,tofile='b/'+name)) for name,(a,b) in changes.items())
path=out/'0018-polaris-dpm-prerequisite-errors.patch';path.write_text(patch)
check=subprocess.run(['git','apply','--check',str(path)],cwd=source,capture_output=True,text=True)
receipt={'source':str(source),'patch_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'input_sha256':{name:hashlib.sha256(a.encode()).hexdigest() for name,(a,b) in changes.items()},'apply_check_exit':check.returncode,'apply_check_output':check.stdout+check.stderr,'source_modified':False,'built':False,'hardware_tested':False}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
check.check_returncode()
