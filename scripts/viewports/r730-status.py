"""Low-rate host monitor; reloads itself when updated, with explicit acceptance labels."""
import json, os, sys, time, shutil
from pathlib import Path
base=Path('/srv/data1/tabor-build/linux-live-001')
script=Path(__file__); stamp=script.stat().st_mtime_ns
def cpu():
 v=list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:9]));return sum(v),v[3]+v[4]
last=cpu()
try:
 while True:
  time.sleep(4)
  if script.stat().st_mtime_ns!=stamp:os.execv(sys.executable,[sys.executable,str(script)])
  now=cpu();delta=now[0]-last[0];usage=100*(1-(now[1]-last[1])/delta) if delta else 0;last=now
  mem={l.split(':')[0]:int(l.split()[1]) for l in Path('/proc/meminfo').read_text().splitlines()}
  try:state=json.loads((base/'viewport-live-001/current.json').read_text())
  except (OSError,ValueError):state={}
  iteration=state.get('iteration','debian-glibc-004')
  try:r=json.loads((base/'work'/iteration/'receipt.json').read_text())
  except (OSError,ValueError):r={}
  rows=['A1222 / SPE — CURRENT BUILD',time.strftime('%Y-%m-%d %H:%M:%S %Z'),
   f'HOST CPU {usage:.1f}% | RAM {(mem["MemTotal"]-mem["MemAvailable"])/1024**2:.1f}/{mem["MemTotal"]/1024**2:.1f}GiB',
   f'DATA FREE {shutil.disk_usage(base).free/1024**3:.0f}GiB',
   '',f'ITERATION: {iteration}',f'BUILD: {r.get("status","pending")}',
   'Compiler gcc-unwind-003: BUILD PASS',
   'QEMU compiler matrix: 18/18 PASS (SPE PIC fix)',
   state.get('runtime','New libc / original C++ test: pending rebuild'),
   'Fenv rounding: OPEN #3 | physical A1222: UNTESTED',
   '', 'QEMU software-e010: 8GiB, 2 e500v2 TCG CPUs',
   'Software GL: diagnostic PASS; E compositor: OPEN #8',
   state.get('viewer','noVNC: older graphical baseline; new candidate pending'),
   'USB unchanged | Debian Essential root not accepted',
   '', 'Host metrics above are not guest benchmark results.']
  print('\033[H\033[2J'+'\n'.join(rows),flush=True)
except KeyboardInterrupt:pass
