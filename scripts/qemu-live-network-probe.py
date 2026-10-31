#!/usr/bin/env python3
"""Hold an isolated PPC guest for an external native SSH client on host loopback."""
import argparse,hashlib,json,shutil,socket,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for name in ['kernel','initramfs','output']:p.add_argument('--'+name,type=Path,required=True)
p.add_argument('--port',type=int,default=22122)
p.add_argument('--timeout',type=int,default=300)
a=p.parse_args();assert 1024<a.port<65536 and 30<=a.timeout<=600
a.output.mkdir(parents=True,exist_ok=False)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
binary=Path(shutil.which('qemu-system-ppc'))
with socket.socket() as check:check.bind(('127.0.0.1',a.port))
command=[str(binary),'-M','ppce500','-cpu','e500v2','-accel','tcg','-smp','2','-m','1024M',
 '-display','none','-serial','stdio','-monitor','none','-nic','none','-no-reboot',
 '-object','rng-random,id=rng0,filename=/dev/urandom','-device','virtio-rng-pci,rng=rng0',
 '-netdev',f'user,id=net0,hostfwd=tcp:127.0.0.1:{a.port}-:22','-device','virtio-net-pci,netdev=net0',
 '-kernel',str(a.kernel),'-initrd',str(a.initramfs),'-append','console=ttyS0,115200 rdinit=/init panic=-1']
r={'status':'started','command':command,'kernel_sha256':sha(a.kernel),
 'initramfs_sha256':sha(a.initramfs),'qemu_sha256':sha(binary),
 'qemu_version':subprocess.check_output([str(binary),'--version'],text=True).splitlines()[0],
 'physical_boot':False,'full_spe_abi_validated':False,'host_listener':'loopback only'}
serial=a.output/'serial.log'
try:
 with serial.open('wb',buffering=0) as log:
  proc=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT)
  deadline=time.monotonic()+a.timeout;announced=False
  while time.monotonic()<deadline:
   console_command=a.output/'console-command.txt'
   if console_command.exists():
    proc.stdin.write(console_command.read_bytes()+b'\n');proc.stdin.flush();console_command.unlink()
   data=serial.read_bytes()
   if b'Kernel panic' in data or proc.poll() is not None:break
   if b'NETWORK_SSH_READY' in data and not announced:
    announced=True;print('Guest DHCP/sshd ready on host loopback port '+str(a.port),flush=True)
   proof=a.output/'client-proof.json'
   if proof.exists():
    r['client_proof']=json.loads(proof.read_text());break
   time.sleep(.25)
  r['network_ready']=announced
finally:
 if 'proc' in locals() and proc.poll() is None:
  proc.terminate()
  try:proc.wait(timeout=5)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
 data=serial.read_bytes()
 r['panic_seen']=b'Kernel panic' in data
 r['serial_sha256']=sha(serial)
 r['status']='passed-native-client-probe' if r.get('network_ready') and not r['panic_seen'] and r.get('client_proof',{}).get('status')=='passed' else 'failed'
 (a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
raise SystemExit(0 if r['status']=='passed-native-client-probe' else 1)
