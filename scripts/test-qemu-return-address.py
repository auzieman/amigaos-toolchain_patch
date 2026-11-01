#!/usr/bin/env python3
"""Verify and run the compiler flag matrix in an existing SSH-accessible QEMU guest."""
import argparse, hashlib, json, re, shlex, subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for name in ['remote-helper','identity','known-hosts','output']:
 p.add_argument('--'+name,type=Path,required=True)
for name in ['artifact-dir','guest-dir','candidate-loader','candidate-libs']:
 p.add_argument('--'+name,required=True)
p.add_argument('--port',type=int,required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
ssh=['ssh','-F','/dev/null','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
     '-o','UserKnownHostsFile='+str(a.known_hosts),'-i',str(a.identity),
     '-p',str(a.port),'tabor@127.0.0.1']
def remote_file(name):
 return subprocess.check_output(['python3',str(a.remote_helper),'cat '+shlex.quote(a.artifact_dir+'/'+name)])
def guest(command,**kwargs):
 return subprocess.run(ssh+[command],timeout=40,check=True,**kwargs)
build=json.loads(remote_file('receipt.json'))
r={'status':'started','scope':'Existing system QEMU guest, not physical hardware',
   'build':build,'tests':{},'uploaded_sha256':{}}
try:
 guest('mkdir -p '+shlex.quote(a.guest_dir))
 for mode,item in build['modes'].items():
  name='probe-'+mode; data=remote_file(name)
  assert hashlib.sha256(data).hexdigest()==item['sha256']
  dest=a.guest_dir+'/'+name
  guest('cat > '+shlex.quote(dest)+'; chmod 755 '+shlex.quote(dest),input=data)
  returned=subprocess.check_output(ssh+['cat '+shlex.quote(dest)],timeout=40)
  assert hashlib.sha256(returned).hexdigest()==item['sha256']
  r['uploaded_sha256'][mode]=item['sha256']
  for runtime,command in [('baseline',[dest]),('candidate',[a.candidate_loader,'--library-path',a.candidate_libs,dest])]:
   command=shlex.join(command)
   run=guest('ulimit -c 0; '+command+'; result=$?; echo TABOR_EXIT=$result; exit 0',capture_output=True,text=True)
   match=re.search(r'^TABOR_EXIT=(\d+)$',run.stdout,re.M);assert match
   code=int(match[1]); valid=code==0 and 'RETURN_ADDRESS ' in run.stdout and 'PHDR_COUNT ' in run.stdout
   r['tests'][mode+'/'+runtime]={'command':command,'exit':code,'passed':valid,'stdout':run.stdout,'stderr':run.stderr}
 r['status']='passed' if all(t['passed'] for t in r['tests'].values()) else 'failed'
finally:
 (a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['status'])
for name,t in r['tests'].items():print(name,'PASS' if t['passed'] else 'FAIL',t['exit'])
raise SystemExit(r['status']!='passed')
