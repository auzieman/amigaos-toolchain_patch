"""Audit pinned SMU7 byte contracts without loading a driver or changing source."""
from pathlib import Path
import hashlib,json,re
src=Path('/srv/data1/tabor-build/linux-live-001/work/polaris-powerplay-20261108-003/source')
p=src/'drivers/gpu/drm/amd/pm/powerplay/smumgr/polaris10_smumgr.c'
s=p.read_text();h=src/'drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.c'
# Derive values from this exact producer, not a guessed firmware payload.
vr=int(re.search(r'vr_config = (0x[0-9a-f]+);',s).group(1),16)
arr=re.search(r'avfs_graphics_level_polaris10\[8\] = \{(.*?)\n\};',s,re.S).group(1)
first=next(line for line in arr.splitlines() if line.strip().startswith('{'))
frequency=int(re.findall(r'\{\s*(0x[0-9a-f]+)',first)[1],16)
activity=int(first.split(',')[3].strip(),16)
checks=[]
for name,value,size in [('VRConfig',vr,4),('AVFS GraphicsLevel[0].SclkFrequency',frequency,4),('AVFS GraphicsLevel[0].ActivityLevel',activity,2)]:
 le=value.to_bytes(size,'little');be=value.to_bytes(size,'big')
 checks.append({'field':name,'literal':hex(value),'x86_memory_bytes':le.hex(),'ppc_be_memory_bytes':be.hex(),'x86_bytes_as_smc_be_integer':int.from_bytes(le,'big'),'ppc_bytes_as_smc_be_integer':int.from_bytes(be,'big'),'equal':le==be})
assert all(not row['equal'] for row in checks)
assert checks[1]['x86_bytes_as_smc_be_integer']==30000
assert checks[2]['x86_bytes_as_smc_be_integer']==50
receipt={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'hwmgr_sha256':hashlib.sha256(h.read_bytes()).hexdigest(),'display_voltage_fix_implementation_present':'smu7_init_voltage_dependency_on_display_clock_table' in h.read_text(),'avfs_native_literal_bytes':checks,'avfs_taken_on_hardware':'unproven','root_cause_proven':False,'source_changed':False,'hardware_retried':False}
print(json.dumps(receipt,indent=2))
