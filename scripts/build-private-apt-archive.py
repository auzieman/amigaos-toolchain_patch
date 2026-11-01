#!/usr/bin/env python3
"""Index only receipt-pinned artifacts and sign an experimental, private apt archive."""
import argparse,gzip,hashlib,json,os,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','base','manifest','output','gnupg-home']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--image-id',required=True);p.add_argument('--create-signing-key',action='store_true')
a=p.parse_args();a.output.mkdir(exist_ok=False)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
spec=json.loads(a.manifest.read_text());assert spec['schema']==1
assert spec['architectures']==['powerpcspe'], 'This archive is SPE-only'
assert a.gnupg_home.resolve()!=a.output.resolve() and not a.gnupg_home.resolve().is_relative_to(a.output.resolve())
a.gnupg_home.mkdir(parents=True,exist_ok=True);a.gnupg_home.chmod(0o700)
env={**os.environ,'GNUPGHOME':str(a.gnupg_home),'LC_ALL':'C.UTF-8'}
def run(cmd,**kwargs):return subprocess.check_output(cmd,env=env,**kwargs)
keys=run(['gpg','--batch','--with-colons','--list-keys'],text=True)
if not any(l.startswith('pub:') for l in keys.splitlines()):
 assert a.create_signing_key, 'Explicit key creation required for initial archive'
 run(['gpg','--batch','--pinentry-mode','loopback','--passphrase','','--quick-generate-key','Tabor SPE experimental lab archive','ed25519','sign','1y'])
 keys=run(['gpg','--batch','--with-colons','--list-keys'],text=True)
assert sum(l.startswith('pub:') for l in keys.splitlines())==1
fingerprint=next(l.split(':')[9] for l in keys.splitlines() if l.startswith('fpr:'))
keyring=a.output/'keyrings/tabor-archive.gpg';keyring.parent.mkdir();keyring.write_bytes(run(['gpg','--batch','--export',fingerprint]))
artifacts=[]
for item in spec['inputs']:
 rp=(a.base/item['receipt']).resolve();assert rp.is_relative_to(a.base.resolve())
 assert sha(rp)==item['receipt_sha256'], 'Receipt changed: '+str(rp)
 r=json.loads(rp.read_text())
 assert item['kind']=='debian-build'
 assert r['status']=='debian-packages-built-not-target-installed'
 packages={name:entry['sha256'] for name,entry in r['packages'].items() if name.endswith('.deb')}
 for name,digest in packages.items():
  assert Path(name).name==name
  source=rp.parent/name;assert sha(source)==digest
  arch=run(['dpkg-deb','-f',str(source),'Architecture'],text=True).strip();assert arch in spec['architectures']+['all']
  dest=a.output/'pool'/item['component']/name;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():assert sha(dest)==digest
  else:shutil.copyfile(source,dest);dest.chmod(0o644)
  artifacts.append({'file':str(dest.relative_to(a.output)),'sha256':digest,'architecture':arch,'receipt':item['receipt']})
release_dir=a.output/'dists'/spec['suite']
for component in spec['components']:
 for arch in spec['architectures']:
  dest=release_dir/component/('binary-'+arch);dest.mkdir(parents=True)
  data=run(['dpkg-scanpackages','--multiversion','--arch',arch,'pool/'+component,'/dev/null'],cwd=a.output)
  (dest/'Packages').write_bytes(data);(dest/'Packages.gz').write_bytes(gzip.compress(data,mtime=0))
options=['apt-ftparchive']
for key,value in {'Origin':'Tabor lab','Label':'Tabor SPE experimental bootstrap','Suite':spec['suite'],'Codename':spec['suite'],'Architectures':' '.join(spec['architectures']),'Components':' '.join(spec['components']),'NotAutomatic':'yes','Description':spec['status']}.items():options+=['-o','APT::FTPArchive::Release::'+key+'='+value]
release=release_dir/'Release';release.write_bytes(run(options+['release',str(release_dir)]))
for flags,filename in [(['--armor','--detach-sign'],'Release.gpg'),(['--clearsign'],'InRelease')]:
 run(['gpg','--batch','--yes','--local-user',fingerprint,*flags,'--output',str(release_dir/filename),str(release)])
run(['gpgv','--keyring',str(keyring),str(release_dir/'InRelease')])
(a.output/'tabor.sources').write_text('Types: deb\nURIs: file:/repo\nSuites: '+spec['suite']+'\nComponents: '+' '.join(spec['components'])+'\nArchitectures: '+' '.join(spec['architectures'])+'\nSigned-By: /repo/keyrings/tabor-archive.gpg\n')
(a.output/'manifest.json').write_text(json.dumps(spec,indent=2)+'\n')
(a.output/'receipt.json').write_text(json.dumps({'status':'signed-binary-archive-built-not-target-installed','image_id':a.image_id,'recipe_sha256':sha(Path(__file__)),'manifest_sha256':sha(a.manifest),'public_key_fingerprint':fingerprint,'source_indexes':False,'artifacts':artifacts,'release_sha256':sha(release),'inrelease_sha256':sha(release_dir/'InRelease')},indent=2)+'\n')
print('Signed archive:',len(artifacts),'artifacts; public fingerprint',fingerprint)
