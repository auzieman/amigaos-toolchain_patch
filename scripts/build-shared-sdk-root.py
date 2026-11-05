#!/usr/bin/env python3
"""Install the real SDK once, export a buildd root with its payload on a RO mount.

Run as a bounded R730 provisioning job. dpkg owns actual installed package state;
only the SDK filesystem is external, like a separately mounted /usr subtree.
"""
import argparse,json,os,subprocess,hashlib,shutil
from pathlib import Path
from apt_archive_cache import mapped_root_ids,prepare,retain
p=argparse.ArgumentParser(description=__doc__)
for key in ['project','base','output','repository']:p.add_argument('--'+key,type=Path,required=True)
a=p.parse_args();a.output.mkdir(exist_ok=False)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(cmd,name):
 with (a.output/(name+'.log')).open('w') as log:subprocess.run(list(map(str,cmd)),stdout=log,stderr=subprocess.STDOUT,check=True)
parent=a.base/'work/clean-cross-buildd-002/receipt.json';previous=json.loads(parent.read_text());archive=parent.parent/'trixie-amd64.tar';assert sha(archive)==previous['sha256'];assert sha(a.project/'profiles/trixie-spe-base.lock.json')==previous['base_lock_sha256']
sdk_receipt=a.base/'work/sdk-fixed-headers-001/receipt.json';sdk=json.loads(sdk_receipt.read_text());deb=sdk_receipt.parent/'tabor-spe-toolchain_8.5.0+tabor6_amd64.deb';assert sha(deb)==sdk['package_sha256']
uid,gid=mapped_root_ids('owner');roots=a.base.parent.parent/'tabor-sbuild-roots';roots.mkdir(exist_ok=True);roots.chmod(0o755);root=roots/a.output.name;root.mkdir();os.chown(root,uid,gid)
prefix=['runuser','-u','owner','--','/usr/libexec/sbuild-usernsexec'];maps=['u:0:'+str(uid)+':65536','g:0:'+str(gid)+':65536']
with archive.open('rb') as stream, (a.output/'extract.log').open('w') as log:
 subprocess.run(list(map(str,prefix+maps+['--','tar','--exclude=./dev/*','-xf','-','-C',root])),stdin=stream,stdout=log,stderr=subprocess.STDOUT,check=True)
cache_base=a.base.parent.parent/'tabor-apt-cache';cache=prepare(cache_base,a.output.name,parent.parent/'root/var/cache/apt/archives',uid,gid)
# mmdebstrap's exported tar cleans apt lists; reuse the qualified parent's
# authenticated frozen indexes, without fetching a new baseline.
for source in (parent.parent/'root/var/lib/apt/lists').iterdir():
 if source.is_file() and source.name!='lock':
  target=root/'var/lib/apt/lists'/source.name;shutil.copyfile(source,target);os.chown(target,uid,gid)
ns=prefix+['--pivotroot','--nonet']+maps+[root,'root','/',cache,'/var/cache/apt/archives',a.repository,'/srv/tabor-extra-packages','--']
run(ns+['sh','-ec',"printf '%s\\n' 'deb [trusted=yes] file:/srv/tabor-extra-packages ./' > /etc/apt/sources.list.d/tabor-sdk-provision.list; apt-get -o APT::Get::List-Cleanup=false -o Dir::Etc::sourcelist=sources.list.d/tabor-sdk-provision.list -o Dir::Etc::sourceparts=- update; apt-get -y install tabor-spe-toolchain=8.5.0+tabor6; dpkg --audit; dpkg-query -W tabor-spe-toolchain; rm /etc/apt/sources.list.d/tabor-sdk-provision.list"],'install-sdk')
shared_parent=a.base.parent.parent/'tabor-shared-sdk';shared_parent.mkdir(exist_ok=True);shared_parent.chmod(0o755);shared=shared_parent/sha(deb)
if not shared.exists():
 shared.mkdir();run(['dpkg-deb','-x',deb,shared],'publish-sdk')
payload=shared/'usr/lib/tabor-spe-toolchain';assert payload.is_dir()
if not os.path.ismount(payload):run(['mount','--bind',payload,payload],'bind-sdk')
run(['mount','-o','remount,bind,ro',payload],'readonly-sdk')
options=subprocess.check_output(['findmnt','--noheadings','--output','VFS-OPTIONS','--target',payload],text=True).strip();assert 'ro' in options.split(',')
# Verify that installed files and external files are identical before excluding
# the mounted subtree from the root archive. Package info and wrapper symlinks stay.
manifest={}
for f in payload.rglob('*'):
 rel=f.relative_to(payload);installed=root/'usr/lib/tabor-spe-toolchain'/rel
 if f.is_symlink():assert installed.is_symlink() and os.readlink(installed)==os.readlink(f)
 elif f.is_file():assert sha(f)==sha(installed);manifest[str(rel)]=sha(f)
# Export via the same UID mapping, preserving native package UID/GID ownership.
tmp=a.base.parent.parent/'tabor-sbuild-tmp'/('shared-sdk-'+a.output.name+'.tar');assert not tmp.exists()
run(prefix+maps+['--','tar','--numeric-owner','--exclude=./dev/*','--exclude=./usr/lib/tabor-spe-toolchain/*','-C',root,'-cf',tmp,'.'],'archive')
destination=a.output/'trixie-amd64.tar';shutil.move(tmp,destination);destination.chmod(0o644)
(a.output/'sdk-files.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
record={'status':'native-buildd-root-created','base_lock_sha256':previous['base_lock_sha256'],'parent_receipt_sha256':sha(parent),'sha256':sha(destination),'recipe_sha256':sha(Path(__file__)),'target_execution':False,'staged_root':str(root),'sdk_installed_by':'normal apt/dpkg in network-disabled sbuild namespace','shared_sdk':{'path':str(payload),'mountpoint':'/usr/lib/tabor-spe-toolchain','mount_options':options,'package_sha256':sha(deb),'sdk_receipt_sha256':sha(sdk_receipt),'version':'8.5.0+tabor6','manifest_sha256':sha(a.output/'sdk-files.json'),'manifest':str((a.output/'sdk-files.json').relative_to(a.base))},'apt_archive_cache':retain(cache_base,cache)}
(a.output/'receipt.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
