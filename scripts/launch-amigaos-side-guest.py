#!/usr/bin/env python3
"""Run the separate prepared Pegasos II guest with matching private boot inputs.

Run on R730 in a bounded systemd unit, never on the laptop. Original ISO and
Kickstart archive remain read-only inputs; only the new guest disk is writable.
"""
import argparse,hashlib,json,subprocess,time,zipfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for name in ['guest','iso','kickstart']:p.add_argument('--'+name,type=Path,required=True)
p.add_argument('--seconds',type=int,default=600)
a=p.parse_args();assert 1<=a.seconds<=3600
spec=json.loads((a.guest/'guest.json').read_text());profile=spec['profile'];assert profile['machine']=='pegasos2'
def sha(f):
 with f.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
iso=a.iso.resolve(strict=True);kickstart=a.kickstart.resolve(strict=True);bboot=Path(spec['bboot_binary']);disk=a.guest/'disk.raw'
assert iso.is_file() and disk.is_file() and sha(bboot)==spec['bboot_binary_sha256']
assert disk.stat().st_size==profile['disk_bytes']
with zipfile.ZipFile(kickstart) as z:
 info=z.getinfo('Kickstart/Kicklayout');assert info.file_size<1024*1024
 layout=z.read(info).decode(errors='replace').lower()
 assert 'pegasos' in layout and not any(x in layout for x in ['a1222','tabor']), 'This guest requires prepared Pegasos II Kickstart, not A1222 modules'
run=a.guest/('run-'+str(time.time_ns()));run.mkdir()
cmd=['qemu-system-ppc','-machine','pegasos2','-cpu',profile['cpu'],'-accel','tcg','-smp','1','-m',str(profile['memory_mib']),'-rtc','base=localtime','-display','none',*profile['graphics'],'-nic','none','-vnc','127.0.0.1:'+str(profile['vnc_port']-5900),'-serial','file:'+str(run/'serial.log'),'-monitor','none','-qmp','unix:'+str(run/'qmp.sock')+',server=on,wait=off','-kernel',str(bboot),'-initrd',str(kickstart),'-drive','media=disk,format=raw,file='+str(disk),'-drive','media=cdrom,format=raw,readonly=on,file='+str(iso)]
r={'status':'launching','command':cmd,'iso_sha256':sha(iso),'kickstart_sha256':sha(kickstart),'guest_definition_sha256':sha(a.guest/'guest.json'),'os_boot_verified':False,'scope':profile['scope']}
try:
 with (run/'qemu.log').open('w') as log:
  proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
  r.update(status='running-not-boot-validated',pid=proc.pid);(run/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
  try:r['exit']=proc.wait(timeout=a.seconds);r['status']='qemu-exited-not-boot-validated'
  except subprocess.TimeoutExpired:
   proc.terminate()
   try:proc.wait(timeout=5)
   except subprocess.TimeoutExpired:proc.kill();proc.wait()
   r.update(status='time-limit-ended-not-boot-validated',exit=proc.returncode)
finally:
 if 'proc' in globals() and proc.poll() is None:
  proc.terminate()
  try:proc.wait(timeout=5)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
 (run/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
