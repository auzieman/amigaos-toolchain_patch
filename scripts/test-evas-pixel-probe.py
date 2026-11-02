#!/usr/bin/env python3
"""Run the SPE Evas isolation probe on a private display without touching recording X11."""
import argparse,hashlib,json,subprocess,shlex
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['remote-helper','identity','known-hosts','output']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--build',required=True);p.add_argument('--port',type=int,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False)
sha=lambda b:hashlib.sha256(b).hexdigest()
ssh=['ssh','-F','/dev/null','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(a.known_hosts),'-i',str(a.identity),'-p',str(a.port),'tabor@127.0.0.1']
def fetch(path):return subprocess.check_output(['python3',str(a.remote_helper),'cat '+shlex.quote(path)],timeout=30)
def run(cmd,**kw):return subprocess.run(ssh+[cmd],timeout=60,**kw)
r={'status':'started','scope':'Private display2 in existing guest; existing libraries, no package install or recording display change','tests':{}}
home='/home/tabor/'+Path(a.build).name;started=False
try:
 raw=fetch(a.build+'/receipt.json');b=json.loads(raw);assert b['status']=='compiled-not-executed'
 binary=fetch(a.build+'/probe');assert sha(binary)==b['binary_sha256']
 run('test ! -e /tmp/.X2-lock && mkdir '+home,check=True)
 run('cat > '+home+'/probe && chmod 755 '+home+'/probe',input=binary,check=True)
 readback=run('cat '+home+'/probe',capture_output=True,check=True).stdout;assert sha(readback)==sha(binary)
 r.update(build_receipt_sha256=sha(raw),binary_sha256=sha(binary))
 run('Xvfb :2 -screen 0 1024x768x24 -nolisten tcp -ac -noreset -extension MIT-SHM </dev/null >'+home+'/Xvfb.log 2>&1 & echo $! > '+home+'/Xvfb.pid; sleep 2',check=True);started=True
 for name,flag in [('rectangles',''),('automatic',' --auto'),('alpha',' --alpha'),('wallpaper',' --wallpaper')]:
  t=run('DISPLAY=:2 LANG=C LC_ALL=C EVAS_NO_DRI_SWAPBUF=1 '+home+'/probe'+flag,capture_output=True)
  data=t.stdout+t.stderr;(a.output/(name+'.log')).write_bytes(data)
  r['tests'][name]={'exit':t.returncode,'log_sha256':sha(data)}
 r['status']='direct-evas-checks-'+('passed' if all(t['exit']==0 for t in r['tests'].values()) else 'failed')
except Exception as e:r.update(status='failed',error=str(e));raise
finally:
 if started:run('kill $(cat '+home+'/Xvfb.pid)',capture_output=True)
 (a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['status']);print({name:t['exit'] for name,t in r['tests'].items()})
