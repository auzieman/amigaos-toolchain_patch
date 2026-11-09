"""Run only after a fresh physical boot. No reload, GL, reset or persistent writes."""
from pathlib import Path
import subprocess,runpy,hashlib,json
repo=Path(__file__).resolve().parents[3]
base=runpy.run_path(str(repo/'work/modular-usb-update-20261105-001/board_access.py'))['base']
out=Path(__file__).resolve().parent/'hardware-cache-control';out.mkdir(exist_ok=False)
def ssh(cmd,limit=15):
 return subprocess.run(['ssh',*base,'root@192.168.1.249',cmd],capture_output=True,text=True,timeout=limit)
def get(cmd):
 r=ssh(cmd);r.check_returncode();return r.stdout.strip()
boot=get('cat /proc/sys/kernel/random/boot_id')
assert boot!='645ccbbf-c51a-4a08-83e1-c53c7369761a','Fresh boot required: prior GPU-failed boot is still active'
assert get('uname -r')=='6.12.113-tabor-e2e-013'
assert get('cat /proc/sys/kernel/tainted')=='0'
assert get('cat /sys/module/amdgpu/parameters/polaris11_le_user_ib')=='Y'
assert '/dev/root on / type ext4 (ro,' in get('mount')
module=get('/sbin/busybox-modules sha256sum /lib/modules/6.12.113-tabor-e2e-013/kernel/drivers/gpu/drm/amd/amdgpu/amdgpu.ko').split()[0]
assert module=='a50eb602944186f8186e633da8b687d208434af601b1afed67efcb5b7ad1cfb6'
def clean(log):
 return not any(x in log.lower() for x in ['gpu reset','blocked for more than','ring gfx timeout','ring gfx_0.0.0 timeout'])
pre=get('dmesg');(out/'before-kmsg.txt').write_text(pre);assert clean(pre),'GPU already reports a failure'
files=Path('/tmp/tabor-cache-control-artifacts')
expected={'gfx-write':'903df0d059684808a6f4616adaa7a709e76477fb69b0da5cc444a43a722accdf'}
for name in ['gfx-write','busybox-render-tools']:
 p=files/name;digest=hashlib.sha256(p.read_bytes()).hexdigest()
 if name in expected:assert digest==expected[name]
 subprocess.run(['scp','-q',*base,str(p),'root@192.168.1.249:/run/'+name],check=True,timeout=20)
 assert get('/sbin/busybox-modules sha256sum /run/'+name).split()[0]==digest
get('chmod 755 /run/gfx-write /run/busybox-render-tools')
root='/opt/tabor-piglit-20261109'
receipts=[]
for case,args in [('uswc','uswc le'),('cached','le')]:
 # Same accepted test and runtime. Only CPU_GTT_USWC allocation flag varies.
 cmd=f'/run/busybox-render-tools timeout 8 {root}/lib/ld.so.1 --library-path {root}/lib:{root}/usr/lib /run/gfx-write {args}'
 try:r=ssh(cmd,20)
 except subprocess.TimeoutExpired:
  (out/(case+'-timeout.txt')).write_text('SSH timed out; stop, no retry/reset/GL.\n');raise
 (out/(case+'-result.txt')).write_text(r.stdout+r.stderr)
 post=get('dmesg');(out/(case+'-kmsg.txt')).write_text(post)
 receipts.append({'case':case,'argv':cmd,'exit':r.returncode,'boot_id':boot})
 (out/'receipt.json').write_text(json.dumps(receipts,indent=2)+'\n')
 assert r.returncode==0 and 'GFX_NATIVE_WRITE=PASS' in r.stdout and 'REMAP_BYTES=addefeca' in r.stdout,case+' failed: stop; no retry/reset/GL'
 assert clean(post),'Kernel GPU failure: stop'
 assert get('cat /proc/sys/kernel/tainted')=='0'
 assert get('cat /proc/sys/kernel/random/boot_id')==boot
 print(case+' PASS',flush=True)
print('Both mapping policies pass this WRITE_DATA control; this is not GL acceptance.')
