#!/usr/bin/env python3
"""Archive a verified offline dpkg root without flattening ownership or modes."""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--installed',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((a.installed/'receipt.json').read_text());assert r['status']=='debs-built-installed-permissions-verified-not-booted';root=a.installed/'root';assert sha(root/'var/lib/dpkg/status')==r['installed_status_sha256']
for name in r['setuid_root_executables']:
 st=(root/name).stat();assert st.st_mode&0o7777==0o4755 and st.st_uid==0 and st.st_gid==0
# Walk without following absolute links into the builder host filesystem.
names=['.']
for parent,dirs,files in os.walk(root,followlinks=False):
 for name in dirs+files:names.append('./'+str((Path(parent)/name).relative_to(root)))
a.output.mkdir(parents=True,exist_ok=False)
with (a.output/'shell.cpio').open('xb') as out:
 subprocess.run(['cpio','--create','--format=newc','--null','--quiet'],cwd=root,input=('\0'.join(sorted(names))+'\0').encode(),stdout=out,check=True)
(a.output/'receipt.json').write_text(json.dumps({'status':'package-installed-initramfs-built','installed_receipt_sha256':sha(a.installed/'receipt.json'),'initramfs_sha256':sha(a.output/'shell.cpio'),'initramfs_bytes':(a.output/'shell.cpio').stat().st_size,'physical_boot':False},indent=2)+'\n')
print('Installed-root metadata preserved in newc archive')
