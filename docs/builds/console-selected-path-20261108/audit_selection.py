"""R730: pin exact Polaris IP descriptors and display callback selection."""
from pathlib import Path
import re,json,hashlib,os,resource
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(3*1024**3,3*1024**3))
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-007/source');A=S/'drivers/gpu/drm/amd/amdgpu';W=Path('/srv/data1/tabor-build/source-review/console-selected-path-20261108')
t=(A/'vi.c').read_text();start=t.index('case CHIP_POLARIS10:',t.index('int vi_set_ip_blocks('));end=t.index('case CHIP_CARRIZO:',start);selection=t[start:end]
names=re.findall(r'amdgpu_device_ip_block_add\(adev, &(\w+)\)',selection)
config=(S.parent/'output/.config').read_text();assert '# CONFIG_DRM_AMD_DC is not set' in config
# Current physical adapter is not configured as a virtual display; exclude the guarded alternatives.
selected=[n for n in names if n not in ['amdgpu_vkms_ip_block','dm_ip_block']]
definitions={}
for p in list(A.glob('*.c'))+list((S/'drivers/gpu/drm/amd/pm/powerplay').glob('*.c')):
 text=p.read_text()
 for m in re.finditer(r'const struct amdgpu_ip_block_version\s+(\w+)\s*=\s*\{([^}]+)\}',text,re.S):
  if m[1] in selected:
   definitions[m[1]]={'file':str(p.relative_to(S)),'line':text[:m.start()].count('\n')+1,'fields':dict(re.findall(r'\.(\w+)\s*=\s*&?(\w+)',m[2]))}
assert set(definitions)==set(selected),(selected,definitions.keys())
assert definitions['dce_v11_2_ip_block']['fields']['funcs']=='dce_v11_0_ip_funcs'
dce=(A/'dce_v11_0.c').read_text();callbacks={}
for name in ['dce_v11_0_ip_funcs','dce_v11_0_crtc_helper_funcs','dce_v11_0_dig_helper_funcs']:
 m=re.search(r'\b'+name+r'\s*=\s*\{([^}]+)\}',dce,re.S);assert m,name
 callbacks[name]={'line':dce[:m.start()].count('\n')+1,'functions':dict(re.findall(r'\.(\w+)\s*=\s*&?(\w+)',m[1]))}
files=['vi.c','dce_v11_0.c','atombios_crtc.c','amdgpu_device.c','amdgpu_drv.c']
report={'selected_ip_order':selected,'ip_definitions':definitions,'display_callbacks':callbacks,'source_sha256':{n:hashlib.sha256((A/n).read_bytes()).hexdigest()for n in files},'config_sha256':hashlib.sha256(config.encode()).hexdigest(),'assumptions':['Physical RX560/Polaris11, DC disabled, no virtual-display override'],'previous_selection_error':'DCE10 neighboring-path tests do not qualify Polaris11 display; corrected to DCE11.2 IP with shared DCE11 callbacks','hardware_accessed':False}
(W/'selected-path.json').write_text(json.dumps(report,indent=2)+'\n');(W/'polaris-ip-selection.c.txt').write_text(selection)
print(json.dumps({'selected_ip_order':selected,'display':definitions['dce_v11_2_ip_block']},indent=2))
