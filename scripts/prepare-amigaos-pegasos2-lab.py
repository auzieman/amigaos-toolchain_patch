from pathlib import Path
import json,urllib.request,hashlib,tarfile,subprocess,shutil
p=Path('/home/owner/amigaos-pegasos2-20261105-001');p.mkdir(mode=0o700);profile=json.loads(Path('/home/owner/amigaos-pegasos2-profile.json').read_text());cache=Path('/home/owner/.cache/tabor-bboot');cache.mkdir(parents=True,exist_ok=True);archive=cache/'bboot-0.8.tar.xz'
if not archive.exists():
 with urllib.request.urlopen(profile['bboot']['url'],timeout=30) as source,archive.with_suffix('.partial').open('wb') as target:shutil.copyfileobj(source,target)
 archive.with_suffix('.partial').rename(archive)
assert archive.stat().st_size==57368
assert hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()==profile['bboot']['sha256']
with tarfile.open(archive) as t:
 t.extractall(p/'loader',filter='data')
files=list((p/'loader').rglob('*'));binary=next(f for f in files if f.name=='bboot' and f.is_file());sha=lambda f:hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
assert sha(binary)==profile['bboot']['binary_sha256']
subprocess.run(['qemu-img','create','-f','raw',str(p/'disk.raw'),'8G'],check=True)
info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(p/'disk.raw')],text=True));assert info['virtual-size']==profile['disk_bytes'] and info['format']=='raw'
r={'status':'prepared-awaiting-matching-media','profile':profile,'bboot_archive_sha256':sha(archive),'bboot_binary':str(binary),'bboot_binary_sha256':sha(binary),'download_verification':'HTTPS author versioned release URL and observed content hash; no detached signature independently verified','qemu_version':subprocess.check_output(['qemu-system-ppc','--version'],text=True).splitlines()[0],'disk_info':info,'os_boot_verified':False,'missing':['Pegasos II AmigaOS install ISO','Prepared updated Pegasos II Kickstart.zip with emulated graphics driver'],'a1222_guest_changed':False}
(p/'guest.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));print('Release files:',[f.name for f in files if f.is_file()])
