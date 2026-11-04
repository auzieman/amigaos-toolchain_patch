#!/usr/bin/env python3
"""Cache exact native package requests using frozen index hashes and apt-helper.

A download query avoids a failing Snapshot redirect/cache route. The origin,
snapshot, filename, version and SHA256 stay pinned; apt still installs packages.
"""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
from debian.deb822 import Packages
p=argparse.ArgumentParser(description=__doc__)
for name in ['audit','lock','cache','output']:p.add_argument('--'+name,type=Path,required=True)
p.add_argument('requests',nargs='+',help='Explicit package=version from retained apt failures')
a=p.parse_args();a.output.mkdir(exist_ok=False);a.cache.mkdir(exist_ok=True)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r={'status':'preparing','target_execution':False,'installed_state_changed':False,'items':[]}
def save():(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
try:
 audit=json.loads((a.audit/'receipt.json').read_text());lock=json.loads(a.lock.read_text())
 assert sha(a.lock)==audit['base_lock_sha256']
 assert sha(a.audit/'NativePackages')==audit['native_packages_sha256']
 r.update(audit_receipt_sha256=sha(a.audit/'receipt.json'),base_lock_sha256=sha(a.lock),recipe_sha256=sha(Path(__file__)))
 wanted={tuple(x.split('=',1)) for x in a.requests};entries={}
 with (a.audit/'NativePackages').open() as f:
  for x in Packages.iter_paragraphs(f):
   key=(x['Package'],x['Version'])
   if key in wanted and x['Architecture'] in ['amd64','all']:
    assert key not in entries or entries[key]['SHA256']==x['SHA256'];entries[key]=x
 assert set(entries)==wanted,'Exact request missing from frozen native index'
 for key,x in entries.items():
  dest=a.cache/Path(x['Filename']).name;expected=x['SHA256'];item={'package':key[0],'version':key[1],'sha256':expected,'filename':dest.name}
  if dest.exists():assert sha(dest)==expected;item['status']='reused'
  else:
   url=lock['repositories'][0]['url'].rstrip('/')+'/'+x['Filename']+'?download=1'
   downloaded=a.output/dest.name
   cmd=['timeout','45','/usr/lib/apt/apt-helper','-o','Acquire::Retries=1','download-file',url,str(downloaded),'SHA256:'+expected]
   with (a.output/(key[0]+'.log')).open('w') as log:code=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT).returncode
   item.update(url=url,exit=code)
   if code==0:
    assert sha(downloaded)==expected
    try:os.link(downloaded,dest)
    except FileExistsError:assert sha(dest)==expected
    item['status']='cached-verified'
   else:item['status']='acquisition-failed'
  r['items'].append(item);save()
 r['status']='cached' if all(x['status']!='acquisition-failed' for x in r['items']) else 'partial-acquisition-failure'
finally:save()
