#!/usr/bin/env python3
"""Verify that a fresh serial shell executes commands in the e500v2 guest."""
import argparse,hashlib,json,re,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--kernel',type=Path,required=True);p.add_argument('--initramfs',type=Path,required=True)
p.add_argument('--output',type=Path,required=True);p.add_argument('--image-id',required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
receipt={'status':'started','kernel_sha256':sha(a.kernel),'initramfs_sha256':sha(a.initramfs),'image_id':a.image_id,'spe_full_abi_validated':False,'physical_boot':False}
cmd=['qemu-system-ppc','-M','ppce500','-cpu','e500v2','-accel','tcg','-smp','2','-m','512M','-display','none','-serial','stdio','-monitor','none','-nic','none','-no-reboot','-kernel',str(a.kernel),'-initrd',str(a.initramfs),'-append','console=ttyS0,115200 rdinit=/init panic=-1']
receipt['command']=cmd;serial=a.output/'serial.log';proc=None
try:
 with serial.open('wb',buffering=0) as stream:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=stream,stderr=subprocess.STDOUT)
  deadline=time.monotonic()+60;sent=False
  while time.monotonic()<deadline:
   data=serial.read_bytes().replace(b'\r',b'')
   if b'Kernel panic' in data or proc.poll() is not None:break
   if b'SHELL_READY\n' in data and not sent:
    time.sleep(.5)
    proc.stdin.write(b"printf '\\nSHELL_COMMAND_OK\\n'; uname -m; head -n 2 /proc/meminfo; echo SHELL_DONE\n");proc.stdin.flush();sent=True
   if re.search(rb'^SHELL_DONE$',data,re.M):break
   time.sleep(.2)
  receipt['commands_sent']=sent
finally:
 if proc is not None and proc.poll() is None:
  proc.terminate()
  try:proc.wait(timeout=5)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
 raw=serial.read_bytes();data=raw.replace(b'\r',b'')
 receipt['shell_command_passed']=bool(re.search(rb'^SHELL_COMMAND_OK$',data,re.M)) and bool(re.search(rb'^SHELL_DONE$',data,re.M))
 receipt['machine_reported_ppc']=bool(re.search(rb'^ppc$',data,re.M))
 receipt['proc_meminfo_read']=bool(re.search(rb'^MemTotal:\s+\d+ kB$',data,re.M))
 receipt['panic_seen']=b'Kernel panic' in data
 receipt['status']='passed' if all(receipt.get(k) for k in ['commands_sent','shell_command_passed','machine_reported_ppc','proc_meminfo_read']) and not receipt['panic_seen'] else 'failed'
 receipt['serial_sha256']=sha(serial)
 (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2));raise SystemExit(0 if receipt['status']=='passed' else 1)
