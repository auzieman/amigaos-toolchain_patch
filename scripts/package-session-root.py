#!/usr/bin/env python3
"""Build private SPE bootstrap/session debs and install them into a fresh offline root.

These are explicit lab bundles, not rebuilt Debian binary package identities.
No target maintainer scripts are bypassed: these bundles have none. Service
provisioning remains a separate, recorded integration step.
"""
import argparse, hashlib, json, os, stat, subprocess
from pathlib import Path, PurePosixPath
p=argparse.ArgumentParser(description=__doc__)
for n in ['base-results','overlay','output','project']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--version',required=True);a=p.parse_args();assert __import__('re').fullmatch(r'[0-9][0-9A-Za-z.+~]*',a.version);a.output.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=a.base_results/'shell.cpio';br=json.loads((a.base_results/'receipt.json').read_text());assert sha(base)==br['initramfs_sha256']
policy=json.loads((a.project/'profiles/images/session-package-policy.json').read_text())
r={'status':'started','version':a.version,'recipe_sha256':sha(Path(__file__)),'base_sha256':sha(base),'policy_sha256':sha(a.project/'profiles/images/session-package-policy.json'),'commands':[],'packages':{},'physical_boot':False,'full_distribution_bootstrap':False}
log=(a.output/'build.log').open('w')
def run(cmd):
 cmd=list(map(str,cmd));r['commands'].append(cmd);log.write(repr(cmd)+'\n');log.flush();subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
def dest(root,name):
 q=PurePosixPath(name);assert not q.is_absolute() and '..' not in q.parts and name not in ['','TRAILER!!!']
 return root/name
def build(name,tree,depends=None):
 control=tree/'DEBIAN';control.mkdir()
 (control/'control').write_text(f'Package: {name}\nVersion: {a.version}\nArchitecture: powerpcspe\nMaintainer: Tabor lab <root@localhost>\n'+(f'Depends: {depends}\n' if depends else '')+'Description: Private experimental SPE lab bundle\n Not an official Debian binary package or complete Debian system.\n')
 out=a.output/(name+'_'+a.version+'_powerpcspe.deb');run(['dpkg-deb','--build','--uniform-compression','-Zgzip',tree,out]);r['packages'][name]={'sha256':sha(out),'bytes':out.stat().st_size};return out
try:
 tree=a.output/'bootstrap';tree.mkdir();raw=base.read_bytes();o=0
 while True:
  assert raw[o:o+6]==b'070701';f=[int(raw[o+6+i*8:o+14+i*8],16) for i in range(13)];size,nlen=f[6],f[11];name=raw[o+110:o+110+nlen-1].decode();o=(o+110+nlen+3)&~3;data=raw[o:o+size];assert len(data)==size;o=(o+size+3)&~3
  if name=='TRAILER!!!':break
  if name=='.':continue
  path=dest(tree,name);assert not path.is_symlink();path.parent.mkdir(parents=True,exist_ok=True);mode=f[1]
  assert f[2] in [0,74,1000] and f[3] in [0,74,1000]
  if stat.S_ISDIR(mode):path.mkdir(exist_ok=True)
  elif stat.S_ISREG(mode):path.write_bytes(data)
  elif stat.S_ISLNK(mode):path.symlink_to(data.decode())
  elif stat.S_ISCHR(mode):
   assert name in ['dev/console','dev/null'],name
   os.mknod(path,mode,os.makedev(f[9],f[10]))
  else:raise ValueError('Unsupported base entry '+name)
  if not path.is_symlink():path.chmod(stat.S_IMODE(mode));os.chown(path,f[2],f[3])
  else:os.lchown(path,f[2],f[3])
 account=policy['service_account']; passwd=tree/'etc/passwd'; group=tree/'etc/group'
 assert not any(line.split(':')[0]==account['name'] or int(line.split(':')[2])==account['uid'] for line in passwd.read_text().splitlines())
 assert not any(line.split(':')[0]==account['name'] or int(line.split(':')[2])==account['gid'] for line in group.read_text().splitlines())
 passwd.write_text(passwd.read_text()+f"{account['name']}:x:{account['uid']}:{account['gid']}:System message bus:/nonexistent:/bin/false\n")
 group.write_text(group.read_text()+f"{account['name']}:x:{account['gid']}:\n")
 for g in policy['desktop_groups']:
  assert not any(line.split(':')[0]==g['name'] or int(line.split(':')[2])==g['gid'] for line in group.read_text().splitlines())
  group.write_text(group.read_text()+f"{g['name']}:x:{g['gid']}:{','.join(g['members'])}\n")
 for name in ['run/dbus','var/lib/dbus']:
  path=tree/name;path.mkdir(parents=True,exist_ok=True);path.chmod(0o755)
  if name=='run/dbus':os.chown(path,account['uid'],account['gid'])
 bootstrap=build('tabor-spe-bootstrap',tree)
 tree=a.output/'session';tree.mkdir();manifest=json.loads((a.overlay/'manifest.json').read_text());r['manifest_sha256']=sha(a.overlay/'manifest.json');seen=set();privileged=[]
 for item in manifest['files']:
  name=item['path'];assert name not in seen;seen.add(name);source=dest(a.overlay/'payload',name);assert sha(source)==item['sha256'];path=dest(tree,name);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(source.read_bytes());mode=item['mode']
  if name in policy['setuid_root_executables']:mode=0o4755;privileged.append(name)
  path.chmod(mode)
 assert set(privileged)==set(policy['setuid_root_executables']),privileged
 r['setuid_root_executables']=privileged
 session=build('tabor-spe-software-session',tree,'tabor-spe-bootstrap (= '+a.version+')')
 root=a.output/'root';root.mkdir();db=root/'var/lib/dpkg';db.mkdir(parents=True);(db/'status').touch();(db/'arch').write_text('powerpcspe\n')
 # Exact private packages have no maintainer scripts/triggers. Do not run foreign
 # scripts chrootless or install arbitrary incompatible PowerPC packages.
 run(['dpkg','--root='+str(root),'--force-architecture','--install',bootstrap,session])
 for name in policy['setuid_root_executables']:
  st=(root/name).stat();assert stat.S_IMODE(st.st_mode)==0o4755 and st.st_uid==0 and st.st_gid==0,name
 run(['dpkg-query','--admindir='+str(db),'-W','-f=${Package} ${Architecture} ${Status}\n'])
 r['installed_status_sha256']=sha(db/'status');r['status']='debs-built-installed-permissions-verified-not-booted'
except Exception as e:r['status']='failed';r['error']=str(e);raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');log.close()
print(r['status'])
