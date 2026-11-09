"""Stage an isolated runtime. Never bind devices, launch EGL, draw, or reboot."""
from pathlib import Path
import subprocess,runpy,shlex,json
repo=Path(__file__).resolve().parents[3]
base=runpy.run_path(str(repo/'work/modular-usb-update-20261105-001/board_access.py'))['base']
d=Path(__file__).resolve().parent/'staging';d.mkdir(exist_ok=True)
root='/opt/tabor-native-vertex-20261109'
remote=repo.parent/'lab/consolidation-20261002/r730-prep-20261031/remote.py'
def ssh(cmd,**kw):return subprocess.run(['ssh',*base,'root@192.168.1.249',cmd],**kw)
def get(cmd,timeout=20):
 r=ssh(cmd,capture_output=True,text=True,timeout=timeout)
 if r.returncode:raise RuntimeError(r.stderr[-1000:])
 return r.stdout
pre=get('uname -r; cat /proc/sys/kernel/tainted; cat /sys/module/amdgpu/parameters/polaris11_le_user_ib; mount')
assert pre.splitlines()[:3]==['6.12.113-tabor-e2e-013','0','Y']
assert '/dev/root on / type ext4 (ro,' in pre
w='/home/owner/native-vertex-live-20261109-001'
r=subprocess.run(['python3',str(remote),'cat '+w+'/receipt.json'],capture_output=True,check=True,timeout=20)
receipt=json.loads(r.stdout);(d/'runtime-receipt.json').write_bytes(r.stdout)
expected=json.loads((d.parent/'evidence/native-vertex-regression.json').read_text())['candidate_libgallium_sha256']
assert receipt['libgallium_sha256']==expected
assert not any('shim' in n or 'stat-compat' in n for n in receipt['files'])
source=subprocess.Popen(['python3',str(remote),'cat '+w+'/runtime.tar'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
try:
 cmd="set -e; test ! -e "+root+"; trap 'sync; mount -o remount,ro /' EXIT; mount -o remount,rw /; mkdir "+root+"; /sbin/busybox-modules tar -xf - -C "+root
 r=ssh(cmd,stdin=source.stdout,capture_output=True,text=True,timeout=90)
 source.stdout.close();source.wait(timeout=10)
 (d/'transfer.txt').write_text(r.stdout+r.stderr)
 if r.returncode or source.returncode:raise RuntimeError('Staging transfer failed; preserve partial directory for review')
finally:
 if source.poll() is None:source.terminate();source.wait(timeout=10)
 r=ssh('sync; mount -o remount,ro /; mount',capture_output=True,text=True,timeout=20)
 (d/'restored-mounts.txt').write_text(r.stdout+r.stderr)
 assert r.returncode==0 and '/dev/root on / type ext4 (ro,' in r.stdout
cmd='/sbin/busybox-modules sha256sum '+' '.join(shlex.quote(root+'/'+n) for n in receipt['files'])
readback=get(cmd,35);(d/'hash-readback.txt').write_text(readback)
seen=set()
for line in readback.splitlines():
 digest,p=line.split(None,1);name=p.removeprefix(root+'/');assert receipt['files'][name]==digest,name;seen.add(name)
assert seen==set(receipt['files'])
# ld.so --list resolves dependencies without executing program initializers/main.
loader=get(root+'/lib/ld.so.1 --library-path '+root+'/lib:'+root+'/usr/lib --list '+root+'/usr/bin/shader_runner_gles2',20)
(d/'loader-readback.txt').write_text(loader)
mounts=get('mount');assert not any(root+'/'+n+' ' in mounts for n in ['dev','proc','sys','run'])
state=get('cat /proc/sys/kernel/random/boot_id; cat /proc/sys/kernel/tainted; cat /proc/fb; mount')
assert state.splitlines()[1]=='0' and '/dev/root on / type ext4 (ro,' in state
(d/'after-state.txt').write_text(state)
(d/'staging-result.json').write_text(json.dumps({'status':'STAGED AND HASH VERIFIED','root':root,'verified_regular_files':len(seen),'libgallium_sha256':expected,'loader_dependency_check':True,'device_interfaces_mounted':False,'GPU_or_render_commands_executed':False,'boot_changed':False,'root_readonly_after':True},indent=2)+'\n')
print('Staged isolated candidate; all',len(seen),'regular file hashes match; loader dependencies resolve; rootRO; no device mounts, rendering or reboot.')
