"""Server-only read-only recovery/inventory of retained GPU traces."""
from pathlib import Path
import subprocess,json,hashlib,re,collections,shutil,os
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))})
base=Path('/srv/data1/tabor-build/source-review/usb-audit-20261108')
receipt=json.loads((base/'receipt.json').read_text())
identity=json.loads(subprocess.check_output(['lsblk','--tree','-J','-o','NAME,SERIAL,PARTUUID,MOUNTPOINTS','/dev/sde'],text=True))['blockdevices'][0]
assert identity['serial']=='03001919041721081205'
assert identity['children'][1]['partuuid']=='a1221105-02'
assert not any(identity['children'][1]['mountpoints'])
root=Path('/mnt/tabor-audit-root');dest=Path('/srv/data1/tabor-build/linux-live-001/hardware-evidence/recovered-usb-20261108');dest.mkdir(exist_ok=True)
rx=re.compile(rb'amdgpu_device_([wr])reg: (0x[0-9a-f]+), (0x[0-9a-f]+), (0x[0-9a-f]+)')
subprocess.run(['mount','-o','ro,noload','/dev/sde2',str(root)],check=True)
report={'usb_changed':False,'traces':[]}
try:
 for item in receipt['retained_rom_or_trace_files']:
  src=root/item['path'];out=dest/Path(item['path']).parent.name/'registers.trace';out.parent.mkdir(exist_ok=True)
  assert src.stat().st_size==item['bytes']
  if not out.exists():shutil.copyfile(src,out);out.chmod(0o644)
  counters=collections.Counter();digest=hashlib.sha256();lines=0;matched=0
  with out.open('rb') as f:
   for line in f:
    digest.update(line);lines+=1;m=rx.search(line)
    if m:matched+=1;counters[(m[1]+b':'+m[3]).decode()]+=1
  with src.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==digest.hexdigest()
  record={'source':item['path'],'cached':str(out),'bytes':item['bytes'],'sha256':digest.hexdigest(),'lines':lines,'matched_register_events':matched,'register_channels':dict(sorted(counters.items()))}
  report['traces'].append(record);print(json.dumps({k:record[k] for k in ['source','bytes','matched_register_events']}),flush=True)
finally:
 subprocess.run(['umount',str(root)],check=True)
 (base/'recovered-traces.json').write_text(json.dumps(report,indent=2)+'\n')
