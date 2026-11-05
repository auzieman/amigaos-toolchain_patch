#!/usr/bin/env python3
"""Native offline cache check through sbuild's real UID maps and bind backend."""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
from apt_archive_cache import prepare, mapped_root_ids, retain
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--base',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--package',default='libbrotli1=1.1.0-2+deb13u1',help='Exact native package/version to acquire without networking')
a=p.parse_args();a.output.mkdir(exist_ok=False)
assert re.fullmatch(r'[a-z0-9][a-z0-9+.-]*=[A-Za-z0-9.+:~_-]+',a.package)
cache=a.base.parent.parent/'tabor-apt-cache';uid,gid=mapped_root_ids('owner')
root=cache/(a.output.name+'-root');root.mkdir();os.chown(root,uid,gid)
seed=a.base/'work/native-cross-resolver-001/root/var/cache/apt/archives'
w=prepare(cache,a.output.name,seed,uid,gid)
maps=['u:0:'+str(uid)+':65536','g:0:'+str(gid)+':65536']
prefix=['runuser','-u','owner','--','/usr/libexec/sbuild-usernsexec']
receipt=a.base/'work/frozen-buildd-root-002/receipt.json';record=json.loads(receipt.read_text());tar=receipt.parent/'trixie-amd64.tar'
assert hashlib.file_digest(tar.open('rb'),'sha256').hexdigest()==record['sha256']
with tar.open('rb') as archive:
 subprocess.run(prefix+maps+['--','tar','--exclude=./dev/*','-xf','-','-C',str(root)],stdin=archive,check=True)
# Existing native metadata, no new fetch or installed-state editing.
source=a.base/'work/native-cross-resolver-001/root/var/lib/apt/lists'
subprocess.run(['cp','-a',str(source)+'/.',str(root/'var/lib/apt/lists')],check=True)
cmd=prefix+['--pivotroot','--nonet']+maps+[str(root),'root','/',str(w),'/var/cache/apt/archives','--','sh','-ec',
 'id; mkdir -p /var/cache/apt/archives/partial; touch /var/cache/apt/archives/partial/namespace-write-proof; apt-get -o Acquire::Retries=0 -o Acquire::http::Timeout=2 --download-only --reinstall -y install "$1"','cache-proof',a.package]
r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
(a.output/'namespace-apt.log').write_text(r.stdout)
result={'exit':r.returncode,'command':cmd,'mapped_root_uid':uid,'mapped_root_gid':gid,'native_tar_sha256':record['sha256'],'cache':retain(cache,w),'network':'sbuild-usernsexec --nonet','apt_output':r.stdout}
(a.output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2));assert r.returncode==0 and 'Need to get 0 B/' in r.stdout
