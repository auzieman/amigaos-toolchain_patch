"""Bounded remote log display: selected current iteration, no compiler-line flood."""
from pathlib import Path
import json, os, sys, time
base=Path('/srv/data1/tabor-build/linux-live-001');script=Path(__file__);stamp=script.stat().st_mtime_ns
last=None
try:
 while True:
  if script.stat().st_mtime_ns!=stamp:os.execv(sys.executable,[sys.executable,str(script)])
  try:state=json.loads((base/'viewport-live-001/current.json').read_text())
  except (OSError,ValueError):state={}
  iteration=state.get('iteration','debian-glibc-004');p=base/'work'/iteration/'build.log'
  try:r=json.loads((p.parent/'receipt.json').read_text())
  except (OSError,ValueError):r={}
  if p.exists():
   with p.open('rb') as f:
    f.seek(max(0,p.stat().st_size-24000));lines=f.read().decode(errors='replace').splitlines()[-10:]
   snapshot=(iteration,r.get('status','unknown'),tuple(lines))
   if snapshot!=last:
    print('\033[H\033[2JR730 BUILD LOG — '+iteration+'\nSTATUS: '+snapshot[1]+'\nBounded tail, refreshed every 4 seconds. Completed logs are not active jobs.\n\n'+'\n'.join(line[:160] for line in lines),flush=True);last=snapshot
  time.sleep(4)
except KeyboardInterrupt:pass
