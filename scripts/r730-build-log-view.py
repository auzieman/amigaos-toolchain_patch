from pathlib import Path
import json,time
base=Path('/srv/data1/tabor-build/linux-live-001');positions={};last=None;status=None
print('R730 BUILD LOG — follows the newest iteration\nHistorical failed iterations remain on disk; not shown as active work.\n',flush=True)
try:
 while True:
  files=[*base.glob('results/*.log'),*base.glob('work/*/build.log')]
  if files:
   p=max(files,key=lambda p:p.stat().st_mtime)
   try:receipt=json.loads((p.parent/'receipt.json').read_text())
   except (OSError,ValueError):receipt={}
   now=(str(p.relative_to(base)),receipt.get('status','log available; running state unknown'),receipt.get('active_component',''))
   if now!=status:
    print('\nITERATION: '+now[0]+'\nSTATUS: '+now[1]+' | '+now[2],flush=True);status=now
   with p.open(errors='replace') as f:
    if p!=last:
     lines=f.readlines();print(''.join(lines[-12:]),end='',flush=True);last=p
    else:
     f.seek(positions.get(p,0));print(f.read(),end='',flush=True)
    positions[p]=f.tell()
  time.sleep(2)
except KeyboardInterrupt:pass
