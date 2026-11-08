"""Exercise installed-mode ordering with a fake SSH endpoint; never contact a board."""
from pathlib import Path
import json,os,subprocess,sys,tempfile
script=Path(__file__).resolve().parents[3]/'scripts/test-polaris-offboard.py'
assert script.is_file()
with tempfile.TemporaryDirectory() as t:
 d=Path(t);endpoint=d/'ssh'
 endpoint.write_text('''#!/usr/bin/env python3
import os,sys,time,json
c=sys.argv[-1]
with open(os.environ['COMMAND_LOG'],'a') as f:f.write(json.dumps(c)+'\\n')
if c.startswith('test "$(uname -r)"'):
 print('6.12.113-tabor-e2e-001\\n1.0 2.0\\n'+'a'*64+' /lib/modules/6.12.113-tabor-e2e-001/kernel/drivers/gpu/drm/amd/amdgpu/amdgpu.ko')
elif c=='cat /dev/kmsg':
 print('TABOR_CAPTURE_READY',flush=True)
 time.sleep(10)
elif c.startswith('sync && mount'):
 print('/dev/root / ext4 '+os.environ['ROOT_MODE']+',relatime 0 0')
''');endpoint.chmod(0o755)
 for mode in ['ro','rw']:
  output=d/mode;log=d/(mode+'.commands')
  p=subprocess.run([sys.executable,str(script),'--key','unused','--known-hosts','unused','--installed-release','6.12.113-tabor-e2e-001','--sha256','a'*64,'--output',str(output)],capture_output=True,text=True,env={**os.environ,'PATH':str(d)+':'+os.environ['PATH'],'COMMAND_LOG':str(log),'ROOT_MODE':mode},timeout=15)
  r=json.loads((output/'receipt.json').read_text());commands=[json.loads(x) for x in log.read_text().splitlines()]
  assert not any(any(x in c for x in ['driver_override','insmod ','rmmod ']) for c in commands)
  assert commands.index(next(x for x in commands if x.startswith('sync && mount')))>commands.index("printf '<6>TABOR_CAPTURE_READY\\n' > /dev/kmsg")
  if mode=='ro':
   assert r['status']=='test-returned-review-hardware-state',r
   assert 'modprobe amdgpu' in commands
  else:
   assert r['status']=='incomplete' and 'root not verified read-only' in r['error'],r
   assert 'modprobe amdgpu' not in commands
  print(mode+': PASS; installed mode has no override and read-only gate precedes driver load')
