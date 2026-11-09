from pathlib import Path
import json,hashlib,subprocess,re,shutil,tarfile
base=Path('/srv/data1/tabor-build/linux-live-001');stage=base/'work/hardware-x-002/stage';libc=Path('/home/owner/drm-query-20261109/debian-tools/usr/lib/powerpc-linux-gnuspe');w=Path('/home/owner/gl-live-20261109-002');w.mkdir(exist_ok=False);root=w/'root';root.mkdir()
runtime=w/'runtime';runtime.mkdir()
packdir=base/'work/gcc-runtime-package-003';packreceipt=json.loads((packdir/'receipt.json').read_text())
for name,meta in packreceipt['packages'].items():
 f=packdir/name;assert hashlib.sha256(f.read_bytes()).hexdigest()==meta['sha256'];subprocess.run(['dpkg-deb','-x',str(f),str(runtime)],check=True)
r=json.loads((stage.parent/'receipt.json').read_text());hashes={**r['input_stage_files'],**r['elfs']};selected={};queue=[]
def add(src,dst):
 if dst in selected:return
 assert src.is_file(),str(src)
 if src.is_relative_to(stage):
  real=src.resolve();rel=str(real.relative_to(stage));assert hashlib.sha256(real.read_bytes()).hexdigest()==hashes[rel],rel
 p=root/dst;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,p);selected[dst]=str(src)
 if p.read_bytes()[:4]==b'\x7fELF':queue.append(p)
for n in ['Xorg','gl-spe-demo','xkbcomp']:add(stage/'usr/bin'/n,'usr/bin/'+n)
for p in (stage/'usr/lib/xorg/modules').rglob('*.so'):add(p,str(p.relative_to(stage)))
add(libc/'ld.so.1','lib/ld.so.1')
while queue:
 p=queue.pop();s=subprocess.check_output(['powerpc-linux-gnu-readelf','-d',str(p)],text=True)
 for soname in re.findall(r'NEEDED.*\[(.*?)\]',s):
  dst='lib/'+soname
  if dst in selected:continue
  choices=[libc/soname,stage/'usr/lib'/soname]+list(runtime.rglob(soname))+list((base/'sysroot').rglob(soname))
  src=next((p for p in choices if p.is_file()),None);assert src,soname
  add(src,dst)
shutil.copytree(stage/'usr/share/X11/xkb',root/'usr/share/X11/xkb',symlinks=False)
conf='''Section "ServerFlags"
 Option "AutoAddDevices" "false"
 Option "AutoEnableDevices" "false"
 Option "AllowMouseOpenFail" "true"
EndSection
Section "Device"
 Identifier "Polaris"
 Driver "modesetting"
 Option "kmsdev" "/dev/dri/card0"
 Option "AccelMethod" "none"
 Option "ShadowFB" "true"
 Option "SWcursor" "true"
EndSection
Section "Screen"
 Identifier "Screen0"
 Device "Polaris"
 DefaultDepth 24
EndSection
'''
(root/'xorg.conf').write_text(conf)
meta={'source_stage':str(stage),'source_receipt_sha256':hashlib.sha256((stage.parent/'receipt.json').read_bytes()).hexdigest(),'renderer_expected':'software Mesa; no Radeon DRI driver','files':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()},'rootfs_installation':False,'hardware_tested':False}
(w/'receipt.json').write_text(json.dumps(meta,indent=2)+'\n')
with tarfile.open(w/'runtime.tar','w') as t:
 for p in root.iterdir():t.add(p,arcname=p.name)
print('Runtime bytes',sum(p.stat().st_size for p in root.rglob('*') if p.is_file()),'tar bytes',(w/'runtime.tar').stat().st_size)
