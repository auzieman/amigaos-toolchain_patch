#!/usr/bin/env python3
"""Stage immutable cached Debian inputs and project source via BKC CLI/core."""
from pathlib import Path
import hashlib,io,json,subprocess,tarfile,shlex
r=Path(__file__).resolve().parents[1];w=r/'work/bkc';w.mkdir(parents=True,exist_ok=True)
bundle=w/'source.tar'
with tarfile.open(bundle,'w') as t:
 for folder in ['scripts','docker','profiles','patches']:
  for f in (r/folder).rglob('*'):
   if f.is_file() and '__pycache__' not in f.parts:t.add(f,arcname='project/'+str(f.relative_to(r)))
 t.add(r/'.dockerignore',arcname='project/.dockerignore')
lock=json.loads((r/'profiles/debian-trixie.lock.json').read_text())
h=hashlib.sha256(bundle.read_bytes()).hexdigest();remote='/var/lib/bkc/tabor-inputs/'+h+'.tar'
p=r/'pipeline/tabor-debian-iteration';(p/'source.json').write_text(json.dumps({'sha256':h,'remote_bundle':remote},indent=2)+'\n')
ssh=['ssh','-i','/home/auzieman/Projects/BlackKnightController/keys/bkc_id_rsa','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','root@192.168.1.15']
subprocess.run(ssh+['install -d -m 0700 /var/lib/bkc/tabor-inputs /var/lib/bkc/tabor-source-cache'],check=True)
# Cached archives are independent of each small project/patch bundle.
for component in lock['components'].values():
 for file in component['files']:
  name=file['filename']
  if Path(name).name!=name:raise SystemExit('Invalid cache filename')
  target='/var/lib/bkc/tabor-source-cache/'+name
  check="from pathlib import Path; import hashlib; p=Path("+repr(target)+"); print(hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else 'missing')"
  actual=subprocess.check_output(ssh+['python3 -c '+shlex.quote(check)],text=True).strip()
  if actual==file['sha256']:continue
  if actual!='missing':raise SystemExit('Remote cache mismatch: '+name)
  local=r/'downloads/debian'/name
  if hashlib.sha256(local.read_bytes()).hexdigest()!=file['sha256']:raise SystemExit('Local cache mismatch: '+name)
  temporary=target+'.partial-'+h
  with local.open('rb') as src:subprocess.run(ssh+['cat > '+shlex.quote(temporary)],stdin=src,check=True,timeout=180)
  finish="from pathlib import Path; import hashlib; p=Path("+repr(temporary)+"); assert hashlib.sha256(p.read_bytes()).hexdigest()=="+repr(file['sha256'])+"; p.rename("+repr(target)+")"
  subprocess.run(ssh+['python3 -c '+shlex.quote(finish)],check=True)

with bundle.open('rb') as f:subprocess.run(ssh+['cat > '+remote],stdin=f,check=True,timeout=180)
b=io.BytesIO()
with tarfile.open(fileobj=b,mode='w') as t:
 for f in p.rglob('*'):
  if f.is_file() and 'artifacts' not in f.parts and '__pycache__' not in f.parts:t.add(f,arcname=p.name+'/'+str(f.relative_to(p)))
for cid in ['c22f6618ad75','9d4c1f5bd02d','b9406e159a06']:
 for dest in ['/app/pipelines','/app/runtime/pipelines']:
  subprocess.run(ssh+['docker exec -i '+cid+' tar -xf - -C '+dest],input=b.getvalue(),check=True)
head=subprocess.check_output(['git','-C',str(r),'rev-parse','HEAD'],text=True).strip()
subprocess.run(ssh+['docker exec c22f6618ad75 python3 /app/bkc_cli.py trigger-pipeline --pipeline-id tabor-debian-iteration --ref refs/heads/development --commit '+head],check=True)
