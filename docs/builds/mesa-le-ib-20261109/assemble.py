from pathlib import Path
import shutil,subprocess,re,json,hashlib,tarfile
b=Path('/srv/data1/tabor-build/linux-live-001');m=b/'work/radeonsi-le-ib-20261109-001';k=b/'work/kmscube-build-20261109-001';w=Path('/home/owner/radeonsi-le-ib-live-20261109-001');w.mkdir(exist_ok=False);root=w/'root';root.mkdir();queue=[];selected={}
def add(src,dst):
 if dst in selected:return
 p=root/dst;p.parent.mkdir(parents=True,exist_ok=True)
 if src.is_symlink():
  target=src.readlink();assert not target.is_absolute();p.symlink_to(target)
  add(src.resolve(),str((Path(dst).parent/target)))
 else:
  shutil.copy2(src,p)
  if p.read_bytes()[:4]==b'\x7fELF':queue.append(p)
 selected[dst]=str(src)
for p in (m/'output/usr/lib').rglob('*'):
 if (p.is_file() or p.is_symlink()) and '.so' in p.name:add(p,str(p.relative_to(m/'output')))
add(k/'output/usr/bin/kmscube','usr/bin/kmscube')
libc=Path('/home/owner/drm-query-20261109/debian-tools/usr/lib/powerpc-linux-gnuspe')
add(libc/'ld.so.1','lib/ld.so.1')
while queue:
 p=queue.pop();s=subprocess.check_output(['powerpc-linux-gnu-readelf','-d',str(p)],text=True)
 for soname in re.findall(r'NEEDED.*\[(.*?)\]',s):
  if (root/'usr/lib'/soname).exists() or (root/'lib'/soname).exists():continue
  choices=[libc/soname,k/'stage/usr/lib/powerpc-linux-gnuspe'/soname]+list((k/'stage').rglob(soname))
  src=next((p for p in choices if p.is_file()),None);assert src,soname
  # Dependencies are copied by SONAME to avoid absolute package symlinks.
  add(src.resolve(),'lib/'+soname)
for n in ['dev','proc','sys','run','tmp']: (root/n).mkdir(exist_ok=True)
files={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and not p.is_symlink()}
(w/'receipt.json').write_text(json.dumps({'files':files,'hardware_tested':False,'package_managed_image':False,'mesa':str(m),'kmscube':str(k)},indent=2)+'\n')
with tarfile.open(w/'runtime.tar','w') as t:
 for p in root.iterdir():t.add(p,arcname=p.name)
print('bytes',sum(p.stat().st_size for p in root.rglob('*') if p.is_file() and not p.is_symlink()))
r=subprocess.run(['qemu-ppc','-cpu','e500v2','-L',str(root),str(root/'lib/ld.so.1'),'--library-path',str(root/'lib')+':'+str(root/'usr/lib'),'--list',str(root/'usr/bin/kmscube')],capture_output=True,text=True);(w/'loader-check.txt').write_text(r.stdout+r.stderr);r.check_returncode();print(r.stdout)
