#!/usr/bin/env python3
"""Stage runtime-only target files as a verified overlay for a fresh rescue root."""
import argparse,hashlib,json,os,stat,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','stage','font-root','base-results','output']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--theme-root',type=Path);p.add_argument('--allow-server-only',action='store_true')
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);payload=a.output/'payload';payload.mkdir();sha=lambda d:hashlib.sha256(d).hexdigest()
base=(a.base_results/'shell.cpio').read_bytes();receipt=json.loads((a.base_results/'receipt.json').read_text());assert sha(base)==receipt['initramfs_sha256']
existing={};o=0
while True:
 assert base[o:o+6]==b'070701';f=[int(base[o+6+i*8:o+14+i*8],16) for i in range(13)];size,nlen=f[6],f[11];name=base[o+110:o+110+nlen-1].decode();o=(o+110+nlen+3)&~3;data=base[o:o+size];o=(o+size+3)&~3
 if name=='TRAILER!!!':break
 existing[name]=(f[1],sha(data))
manifest={'files':[]};inputs={}
def add(name,data,mode,origin):
 assert not name.startswith('/') and '..' not in Path(name).parts
 if name in existing:
  assert existing[name][1]==sha(data),'Existing root file differs: '+name
  return
 if name in inputs:
  assert sha((payload/name).read_bytes())==sha(data),'Conflicting overlay data: '+name
  return
 dest=payload/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 manifest['files'].append({'path':name,'sha256':sha(data),'mode':mode});inputs[name]=origin
skip_bins={'eolian_gen','eolian_cxx','edje_cc','edje_decc','edje_codegen','embryo_cc','elementary_codegen','elm_prefs_cc','eet'}
for f in sorted(a.stage.rglob('*')):
 if not f.is_file() and not f.is_symlink():continue
 name=str(f.relative_to(a.stage));parts=Path(name).parts
 if name.endswith(('.a','.la','.pc','.h')):continue
 if name.startswith(('usr/include/','usr/share/doc/','usr/share/man/','usr/share/info/','usr/share/aclocal/','usr/share/pkgconfig/','usr/lib/pkgconfig/','usr/lib/cmake/','usr/lib/python')):continue
 if name.startswith('usr/share/enlightenment/data/backgrounds/'):continue
 if name.startswith('usr/bin/') and f.name in skip_bins:continue
 if not (parts[0]=='etc' or name.startswith(('usr/lib/','usr/libexec/','usr/bin/','usr/sbin/','usr/share/'))):continue
 source=f
 for _ in range(32):
  if not source.is_symlink():break
  link=os.readlink(source);source=a.stage/link.lstrip('/') if link.startswith('/') else source.parent/link
 source=source.resolve();assert source.is_relative_to(a.stage.resolve()) and source.is_file(),f
 data=source.read_bytes();mode=0o755 if source.stat().st_mode&0o111 else 0o644
 if data[:4]==b'\x7fELF':
  assert data[:6]==b'\x7fELF\x01\x02' and data[18:20]==b'\x00\x14',f
  dest=a.output/'strip.tmp';subprocess.run(['powerpc-linux-gnu-strip','--strip-unneeded','-o',str(dest),str(source)],check=True);data=dest.read_bytes();dest.unlink()
 add(name,data,mode,{'path':str(source),'sha256':sha(source.read_bytes())})
for f in sorted(a.font_root.rglob('*')):
 if f.is_file() and str(f.relative_to(a.font_root)).startswith('usr/share/'):add(str(f.relative_to(a.font_root)),f.read_bytes(),0o644,{'font_input':str(f),'sha256':sha(f.read_bytes())})
if a.theme_root:
 for f in sorted(a.theme_root.rglob('*')):
  if f.is_file():add(str(f.relative_to(a.theme_root)),f.read_bytes(),0o644,{'private_theme_input':str(f),'sha256':sha(f.read_bytes())})
for source,name in [('boot/desktop-init.sh','desktop-init'),('boot/start-e-session.sh','usr/bin/start-e-session')]:
 f=a.project/source;add(name,f.read_bytes(),0o755,{'source':source,'sha256':sha(f.read_bytes())})
required=['usr/bin/Xvfb','usr/bin/x11vnc','usr/bin/enlightenment_start','usr/bin/enlightenment','usr/bin/dbus-run-session','usr/bin/dbus-uuidgen','usr/bin/xkbcomp']
if a.allow_server_only:required=[n for n in required if 'enlightenment' not in n]
names={i['path'] for i in manifest['files']};assert all(n in names or n in existing for n in required),[n for n in required if n not in names and n not in existing]
(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(a.output/'inputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
(a.output/'receipt.json').write_text(json.dumps({'status':'runtime-overlay-staged-not-booted','files':len(names),'bytes':sum((payload/i['path']).stat().st_size for i in manifest['files']),'base_sha256':sha(base),'physical_boot':False,'GPU_validated':False},indent=2)+'\n')
print('Staged',len(names),'runtime files')
