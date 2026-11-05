from pathlib import Path
import subprocess,time,socket,json,hashlib
p=Path('/home/owner/os4-e500-entry-20261105-001');kernel=p/'kernel';assert kernel.stat().st_size==807744
sock=p/'qmp.sock';cmd=['qemu-system-ppc','-M','ppce500','-cpu','e500v2','-accel','tcg','-smp','1','-m','512','-display','none','-serial','file:'+str(p/'serial.log'),'-monitor','none','-nic','none','-no-reboot','-kernel',str(kernel),'-S','-qmp','unix:'+str(sock)+',server=on,wait=off']
r={'scope':'Unmodified A1222 AmigaOS kernel direct-entry diagnostic on existing generic e500v2 platform; not firmware/Kickstart-complete boot','command':cmd,'kernel_sha256':hashlib.file_digest(kernel.open('rb'),'sha256').hexdigest(),'qemu_version':subprocess.check_output(['qemu-system-ppc','--version'],text=True).splitlines()[0],'os_boot_verified':False,'installed_disk':False,'network':False,'register_samples':[]}
log=(p/'qemu.log').open('w');proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);s=None
try:
 for _ in range(40):
  if proc.poll() is not None:break
  if sock.exists():break
  time.sleep(.1)
 if not sock.exists():raise RuntimeError('QEMU rejected kernel/platform before QMP became available')
 s=socket.socket(socket.AF_UNIX);s.settimeout(3);s.connect(str(sock));f=s.makefile('rwb',buffering=0);greeting=json.loads(f.readline())
 def qmp(name,args=None):
  f.write((json.dumps({'execute':name,**({'arguments':args} if args else {})})+'\n').encode())
  while True:
   response=json.loads(f.readline())
   if 'return' in response or 'error' in response:return response
 qmp('qmp_capabilities');r['register_samples'].append({'phase':'before-entry','result':qmp('human-monitor-command',{'command-line':'info registers'})});qmp('cont');time.sleep(2);r['status_after_run']=qmp('query-status');qmp('stop');r['register_samples'].append({'phase':'after-two-seconds','result':qmp('human-monitor-command',{'command-line':'info registers'})});r['status']='direct-entry-probe-completed-no-OS-acceptance'
except Exception as e:r.update(status='direct-entry-probe-failed',error=str(e))
finally:
 if s:s.close()
 if proc.poll() is None:
  proc.terminate()
  try:proc.wait(timeout=3)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
 log.close();r['qemu_exit']=proc.returncode;r['qemu_log']=(p/'qemu.log').read_text();r['serial_bytes']=(p/'serial.log').stat().st_size if (p/'serial.log').exists() else 0;(p/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='register_samples'},indent=2))
