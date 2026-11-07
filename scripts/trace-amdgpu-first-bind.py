#!/usr/bin/env python3
"""Scoped x86 control: trace first AMDGPU bind after the prepared held-driver boot.
Run as root on the reference tower, not on the laptop. Requires no bound GPU.
Uses existing tracepoints; does not reset or flash the GPU.
"""
import pathlib,subprocess,time,json
out=pathlib.Path('/var/log/a1222-x86-reference/first-bind-trace-001')
t=pathlib.Path('/sys/kernel/tracing/instances/a1222-smu-reference')
driver=pathlib.Path('/sys/bus/pci/drivers/amdgpu');pci='0000:01:00.0'
def write(p,s):p.write_text(str(s))
assert 'modprobe.blacklist=amdgpu' in pathlib.Path('/proc/cmdline').read_text()
device=pathlib.Path('/sys/bus/pci/devices')/pci
assert not (device/'driver').exists(), 'GPU already bound; first-bind condition lost'
assert not pathlib.Path('/sys/module/amdgpu').exists(), 'AMDGPU already loaded'
assert (device/'vendor').read_text().strip() == '0x1002'
assert (device/'device').read_text().strip() == '0x67ff'
out.mkdir(exist_ok=False)
t.mkdir(exist_ok=False)
write(device/'driver_override','a1222-reference-hold')
try:
 subprocess.run(['modprobe','amdgpu'],check=True)
finally:
 write(device/'driver_override','\n')
reader=None;unbound=True
try:
 write(t/'tracing_on',0);write(t/'buffer_size_kb',4096)
 filt='did == 26623 && (reg == 428 || reg == 429 || reg == 146 || reg == 148 || reg == 149 || reg == 164)'
 for event in ('amdgpu_device_wreg','amdgpu_device_rreg'):
  ep=t/'events/amdgpu'/event
  write(ep/'filter',filt);write(ep/'enable',1)
 f=(out/'registers.trace').open('w')
 reader=subprocess.Popen(['cat',str(t/'trace_pipe')],stdout=f,stderr=subprocess.DEVNULL)
 write(t/'tracing_on',1)
 write(driver/'bind',pci);unbound=False
 time.sleep(1)
finally:
 if unbound:
  try:write(driver/'bind',pci)
  except Exception as e:(out/'recovery-error.txt').write_text(str(e))
 write(t/'tracing_on',0)
 if reader:
  time.sleep(.3);reader.terminate();reader.wait(timeout=5);f.close()
 stats={p.parent.name:p.read_text() for p in (t/'per_cpu').glob('cpu*/stats')}
 (out/'trace-stats.json').write_text(json.dumps(stats,indent=2))
 for event in ('amdgpu_device_wreg','amdgpu_device_rreg'):write(t/'events/amdgpu'/event/'enable',0)
 t.rmdir()
result={'driver_bound':(pathlib.Path('/sys/bus/pci/devices')/pci/'driver').exists(),'framebuffer':pathlib.Path('/proc/fb').read_text(),'trace_bytes':(out/'registers.trace').stat().st_size}
(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
