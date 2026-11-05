from pathlib import Path
import json,subprocess,sys,os,hashlib,time
sys.path.insert(0,'/tmp/tabor-repository-proof-scripts')
from sbuild_local_repository import prepare,digest
from apt_archive_cache import mapped_root_ids
b=Path('/srv/data1/tabor-build/linux-live-001');o=b/'work/sbuild-repository-proof-001';o.mkdir();parent=b.parent.parent/'tabor-sbuild-repositories';extras=b/'work/port-pipeline-20261104-020-binary-rebuilds-libxkbfile/extra-packages'
t=time.monotonic();repo,record=prepare(extras,parent);elapsed=time.monotonic()-t;second,reused=prepare(extras,parent);assert second==repo and record==reused
uid,gid=mapped_root_ids('owner');root=parent/'namespace-proof-001';root.mkdir();os.chown(root,uid,gid)
rp=b/'work/clean-cross-buildd-002/receipt.json';r=json.loads(rp.read_text());tar=rp.parent/'trixie-amd64.tar';assert digest(tar)==r['sha256']
prefix=['runuser','-u','owner','--','/usr/libexec/sbuild-usernsexec'];maps=['u:0:'+str(uid)+':65536','g:0:'+str(gid)+':65536']
with tar.open('rb') as f:subprocess.run(prefix+maps+['--','tar','--exclude=./dev/*','-xf','-','-C',str(root)],stdin=f,check=True)
cmd=prefix+['--pivotroot','--nonet']+maps+[str(root),'root','/',str(repo),'/srv/tabor-extra-packages','--','sh','-ec', '''dpkg --add-architecture powerpcspe
printf '%s\n' 'deb [trusted=yes] file:/srv/tabor-extra-packages ./' > /etc/apt/sources.list.d/local-proof.list
apt-get -o Dir::Etc::sourcelist=sources.list.d/local-proof.list -o Dir::Etc::sourceparts=- update
cd /tmp
apt-cache policy libxkbfile-dev:powerpcspe
apt-get download libxkbfile-dev:powerpcspe
! touch /srv/tabor-extra-packages/namespace-write-must-fail
''']
r=subprocess.run(cmd,text=True,capture_output=True);(o/'namespace.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
f=next((root/'tmp').glob('libxkbfile-dev*.deb'));assert digest(f)==record['inputs'][f.name]
(o/'receipt.json').write_text(json.dumps({'status':'offline-sbuild-namespace-apt-repository-qualified','artifact_count':len(record['inputs']),'repository_prepare_seconds':elapsed,'repository':str(repo),'repository_receipt':record,'command':cmd,'root_sha256':digest(tar),'downloaded_sha256':digest(f),'exit':r.returncode,'limits':'actual sbuild UID maps/pivotroot/bind/--nonet with standard apt index+download; complete sbuild source build pending'},indent=2)+'\n');print('PASS',len(record['inputs']),'artifacts; offline namespace apt index and verified target download;',round(elapsed,2),'seconds repository preparation')
