"""Read standard PCI config/sysfs only; no BAR MMIO, driver load or config write."""
from pathlib import Path
import subprocess,runpy,json,struct,time
root=Path(__file__).resolve().parents[3]
base=runpy.run_path(str(root/'work/modular-usb-update-20261105-001/board_access.py'))['base']
ssh=['flatpak-spawn','--host','ssh',*base,'root@192.168.1.249']
pci='/sys/bus/pci/devices/0001:01:00.0'
def read(cmd):
 r=subprocess.run(ssh+[cmd],capture_output=True,timeout=15)
 if r.returncode:raise RuntimeError(r.stderr.decode(errors='replace'))
 return r.stdout
out=root/'work/shared-boundary-test-20261108'/('passive-pci-'+str(time.time_ns()));out.mkdir()
r={'test':'standard PCI configuration read-only','gpu_mmio_accessed':False,'driver_loaded_by_test':False,'configuration_written':False,'clock_fix_exercised':False,'status':'started'}
try:
 before=read('uname -r; cat /proc/uptime; cat /proc/modules');(out/'before.txt').write_bytes(before)
 assert not any(l.startswith(b'amdgpu ') for l in before.splitlines()),'Require unbound fresh-boot state'
 read('test ! -e '+pci+'/driver')
 data=read('cat '+pci+'/config');assert 64<=len(data)<=4096
 data=data[:64]
 (out/'config-first64.bin').write_bytes(data)
 values={}
 for name in ['vendor','device','class','revision','resource']:
  text=read('cat '+pci+'/'+name).decode();(out/(name+'.txt')).write_text(text);values[name]=text
 vendor,device=struct.unpack_from('<HH',data)
 assert vendor==int(values['vendor'],16)==0x1002
 assert device==int(values['device'],16)==0x67ff
 assert data[8]==int(values['revision'],16)
 assert int.from_bytes(data[9:12],'little')==int(values['class'],16)
 bars=[];i=0
 resources=[x.split() for x in values['resource'].splitlines()]
 while i<6:
  word=struct.unpack_from('<I',data,16+4*i)[0];is_io=bool(word&1);wide=not is_io and ((word>>1)&3)==2
  address=word&(~3 if is_io else ~15)
  if wide:
   assert i<5
   address|=struct.unpack_from('<I',data,20+4*i)[0]<<32
  cpu_start=int(resources[i][0],16)
  bars.append({'bar':i,'raw_word':hex(word),'type':'io' if is_io else 'memory','width':64 if wide else 32,'pci_bus_address':hex(address),'kernel_cpu_resource_start':hex(cpu_start),'addresses_equal':address==cpu_start})
  i+=2 if wide else 1
 # CPU and bus addresses may differ legitimately; retain translation, do not assert equality.
 after=read('cat /proc/uptime; cat /proc/modules');(out/'after.txt').write_bytes(after)
 assert not any(l.startswith(b'amdgpu ') for l in after.splitlines())
 r.update(status='PASS',vendor=hex(vendor),device=hex(device),identification_and_class_decode_match=True,bars=bars,ssh_alive_after=True)
except Exception as exc:r.update(status='incomplete',error=str(exc));raise
finally:(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(str(out));print(json.dumps(r,indent=2))
