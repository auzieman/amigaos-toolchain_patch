"""Run CPU-only serialization fixtures on a fresh A1222; never bind/probe GPU."""
from pathlib import Path
import subprocess,runpy,json,hashlib,shlex,time
root=Path(__file__).resolve().parents[3]
art=root/'work/shared-boundary-test-20261108'
out=art/('physical-cpu-results-'+str(time.time_ns()))
out.mkdir(exist_ok=False)
base=runpy.run_path(str(root/'work/modular-usb-update-20261105-001/board_access.py'))['base']
ssh=['flatpak-spawn','--host','ssh',*base,'root@192.168.1.249']
def run(cmd,data=None):
 r=subprocess.run(ssh+[cmd],input=data,capture_output=True,timeout=20)
 if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace'))
 return r.stdout
receipt={'gpu_accessed':False,'boot_changed':False,'test':'CPU-only ATOM serialization with mock endpoint','status':'started'}
try:
 pre=run("uname -a; cat /proc/uptime; cat /proc/modules; cat /proc/mounts")
 (out/'preflight.txt').write_bytes(pre)
 assert not any(l.startswith(b'amdgpu ') for l in pre.splitlines()),'Require fresh boot without AMDGPU loaded'
 run('mkdir -p /run/tabor-byte-contract && mount -t tmpfs -o size=2m,mode=700 tmpfs /run/tabor-byte-contract')
 mounts=run('cat /proc/mounts')
 assert any(len(l.split())>2 and l.split()[1:3]==[b'/run/tabor-byte-contract',b'tmpfs'] for l in mounts.splitlines()),'Require private RAM-backed test directory'
 results={}
 for name in ['old-asic-clock-ppc','fixed-asic-clock-ppc']:
  data=(art/name).read_bytes();dest='/run/tabor-byte-contract/'+name
  run('cat > '+shlex.quote(dest)+' && chmod 700 '+shlex.quote(dest),data)
  digest=hashlib.sha256(data).hexdigest()
  assert run('/sbin/busybox-modules sha256sum '+dest).decode().split()[0]==digest
  result=run(dest);(out/(name+'.log')).write_bytes(result);results[name]=result
 reference=(art/'old-asic-clock-x86.log').read_bytes()
 assert results['fixed-asic-clock-ppc']==reference,'Corrected PPC differs from x86'
 assert results['old-asic-clock-ppc']!=reference,'Expected original PPC mismatch not reproduced'
 receipt.update(status='PASS',cases=56,corrected_ppc_matches_x86=True,original_ppc_mismatch=True)
except Exception as exc:
 receipt.update(status='incomplete',error=str(exc))
 raise
finally:
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
