import subprocess,runpy,time,hashlib
from pathlib import Path
b=runpy.run_path('tabor-spe-toolchain/work/modular-usb-update-20261105-001/board_access.py')['base'];d=Path('tabor-spe-toolchain/docs/builds/mesa-le-ib-20261109/post-clear-write')
def ssh(c,**kw):return subprocess.run(['ssh',*b,'root@192.168.1.249',c],**kw)
r=ssh('uname -r; cat /sys/module/amdgpu/parameters/polaris11_le_user_ib; cat /proc/mounts',capture_output=True,text=True,check=True)
assert r.stdout.splitlines()[:2]==['6.12.113-tabor-e2e-013','Y']
assert any(len(x.split())>3 and x.split()[1]=='/' and 'ro' in x.split()[3].split(',') for x in r.stdout.splitlines()[2:])
tool='/srv/data1/tabor-build/linux-live-001/work/render-tools-20261109-001/busybox-obj/busybox'
a=subprocess.Popen(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','cat '+tool],stdout=subprocess.PIPE)
r=ssh('cat > /run/busybox-render-tools; chmod 755 /run/busybox-render-tools; /sbin/busybox-modules sha256sum /run/busybox-render-tools',stdin=a.stdout,capture_output=True,text=True);a.stdout.close();assert a.wait()==0;r.check_returncode()
h=subprocess.check_output(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','sha256sum '+tool],text=True).split()[0];assert h==r.stdout.split()[0]
src='/srv/data1/tabor-build/linux-live-001/work/gfx-write-20261109-003/gfx-write';a=subprocess.Popen(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','cat '+src],stdout=subprocess.PIPE)
r=ssh('cat > /run/gfx-write; chmod 755 /run/gfx-write; /sbin/busybox-modules sha256sum /run/gfx-write',stdin=a.stdout,capture_output=True,text=True);a.stdout.close();assert a.wait()==0;r.check_returncode();h=subprocess.check_output(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','sha256sum '+src],text=True).split()[0];assert h==r.stdout.split()[0]
with (d/'uswc-le-traced-kmsg.txt').open('w') as f:
 log=subprocess.Popen(['ssh',*b,'root@192.168.1.249','cat /dev/kmsg'],stdout=f,stderr=subprocess.STDOUT)
 try:
  time.sleep(1);assert log.poll() is None
  ssh('echo TABOR_GFX_NATIVE_WRITE_BEGIN > /dev/kmsg',check=True);time.sleep(1);assert 'TABOR_GFX_NATIVE_WRITE_BEGIN' in (d/'uswc-le-traced-kmsg.txt').read_text()
  cmd='/run/busybox-render-tools timeout 10 /opt/tabor-radeonsi-20261109/lib/ld.so.1 --library-path /opt/tabor-radeonsi-20261109/lib:/opt/tabor-radeonsi-20261109/usr/lib /run/gfx-write uswc le; r=$?; echo GFX_WRITE_EXIT=$r; echo TABOR_GFX_NATIVE_WRITE_END > /dev/kmsg; cat /proc/sys/kernel/tainted'
  r=ssh(cmd,capture_output=True,text=True,timeout=20);(d/'uswc-le-traced-result.txt').write_text(r.stdout+r.stderr);print(r.stdout,r.stderr)
 finally:
  log.terminate()
  try:log.wait(timeout=5)
  except subprocess.TimeoutExpired:log.kill()

import struct,json
r=ssh('test -e /sys/kernel/debug/dri/0/amdgpu_ring_gfx || mount -t debugfs debugfs /sys/kernel/debug; cat /sys/kernel/debug/dri/0/amdgpu_ring_gfx',capture_output=True,check=True)
blob=r.stdout;(d/'gfx-ring-013.bin').write_bytes(blob)
rp,wp,sw=struct.unpack('>3I',blob[:12]);words=struct.unpack('<'+str((len(blob)-12)//4)+'I',blob[12:]);found=[]
for i in range(len(words)-3):
 if words[i]==0xc0023f00 and (words[i+1]&~3)==0x10000 and (words[i+3]&0xffffff)==8 and words[i+3]>>24:
  found.append((i,words[i+1],words[i+3]))
assert found,'no matching userspace IB packet'
latest=max(found,key=lambda x:(x[0]-wp)%len(words))
result={'rptr':rp,'wptr':wp,'software_wptr':sw,'latest_ib_offset':latest[0],'ib_address_word':hex(latest[1]),'ib_control':hex(latest[2]),'fetch_swap_bits':latest[1]&3,'payload_pass':'GFX_NATIVE_WRITE=PASS' in (d/'uswc-le-traced-result.txt').read_text()}
(d/'fetch-013-result.json').write_text(json.dumps(result,indent=2)+'\n');assert result['fetch_swap_bits']==0
print(json.dumps(result,indent=2))
