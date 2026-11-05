from pathlib import Path
import json,subprocess,socket,time
p=Path('/home/owner/amigaos-pegasos2-20261105-001');g=json.loads((p/'guest.json').read_text());o=p/'loader-probe';o.mkdir();cmd=['qemu-system-ppc','-machine','pegasos2','-cpu','7457','-accel','tcg','-m','512','-display','none','-vga','none','-device','sm501','-nic','none','-serial','file:'+str(o/'serial.log'),'-monitor','none','-kernel',g['bboot_binary'],'-qmp','unix:'+str(o/'qmp.sock')+',server=on,wait=off']
log=(o/'qemu.log').open('w');proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);r={'command':cmd,'os_boot_verified':False,'scope':'Pegasos II VOF/BBoot setup probe with no OS modules, disk or ISO; missing initrd is intentional'}
try:
 for _ in range(30):
  if (o/'qmp.sock').exists() or proc.poll() is not None:break
  time.sleep(.1)
 time.sleep(2)
 r['process_running_after_probe']=proc.poll() is None
 r['serial']=(o/'serial.log').read_text(errors='replace') if (o/'serial.log').exists() else ''
 r['status']='bootloader-probe-completed-not-OS-boot'
finally:
 if proc.poll() is None:
  proc.terminate()
  try:proc.wait(timeout=3)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
 log.close();r['exit']=proc.returncode;r['qemu_log']=(o/'qemu.log').read_text();(o/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
