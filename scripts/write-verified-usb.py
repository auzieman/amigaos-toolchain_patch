#!/usr/bin/env python3
"""Write an explicitly selected USB serial, then verify every image byte by readback."""
import argparse,fcntl,hashlib,json,os,stat,struct,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['image','device','receipt']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--image-sha256',required=True);p.add_argument('--expected-serial',required=True)
p.add_argument('--write',action='store_true',required=True)
a=p.parse_args();a.device=a.device.resolve();a.image=a.image.resolve()
assert not a.receipt.exists() and a.image.is_file() and stat.S_ISBLK(a.device.stat().st_mode)
assert len(a.image_sha256)==64 and hashlib.file_digest(a.image.open('rb'),'sha256').hexdigest()==a.image_sha256
size=a.image.stat().st_size
with a.image.open('rb') as f:
 mbr=f.read(512)
assert mbr[510:512]==b'\x55\xaa' and mbr[450]==0x0c and struct.unpack_from('<I',mbr,454)[0]==2048

def identity():
 props=dict(line.split('=',1) for line in subprocess.check_output(['udevadm','info','--query=property','--name',str(a.device)],text=True).splitlines() if '=' in line)
 assert props.get('ID_BUS')=='usb' and props.get('ID_SERIAL')==a.expected_serial, 'USB identity differs'
 devices=json.loads(subprocess.check_output(['lsblk','--json','--output','NAME,TYPE,SIZE,MOUNTPOINTS','--bytes',str(a.device)],text=True))['blockdevices']
 assert len(devices)==1 and devices[0]['type']=='disk' and devices[0]['size']>=size
 def unmounted(d):
  assert not any(d.get('mountpoints') or []),'Mounted device refused'
  for child in d.get('children',[]):unmounted(child)
 unmounted(devices[0]);return {k:props.get(k) for k in ['ID_BUS','ID_SERIAL','ID_MODEL','ID_VENDOR_ID','ID_MODEL_ID']}
info=identity();r={'status':'started','device':str(a.device),'identity':info,'image_bytes':size,'image_sha256':a.image_sha256,'physical_boot':False}
a.receipt.parent.mkdir(parents=True,exist_ok=True)
try:
 fd=os.open(a.device,os.O_RDWR|os.O_EXCL)
 try:
  assert identity()==info
  assert struct.unpack('Q',fcntl.ioctl(fd,0x80081272,b'\0'*8))[0]>=size
  copied=0;report=time.monotonic()
  with a.image.open('rb') as src:
   while chunk:=src.read(4*1024**2):
    view=memoryview(chunk)
    while view:view=view[os.write(fd,view):]
    copied+=len(chunk)
    if time.monotonic()-report>10:print(f'Wrote {copied//1024**2}/{size//1024**2} MiB',flush=True);report=time.monotonic()
  os.fsync(fd);fcntl.ioctl(fd,0x1261);os.lseek(fd,0,os.SEEK_SET)
  h=hashlib.sha256();remaining=size
  while remaining:
   chunk=os.read(fd,min(4*1024**2,remaining));assert chunk,'Short readback'
   h.update(chunk);remaining-=len(chunk)
  r['readback_sha256']=h.hexdigest();assert h.hexdigest()==a.image_sha256,'USB readback mismatch'
  r['status']='written-and-full-image-readback-verified'
 finally:os.close(fd)
 subprocess.run(['blockdev','--rereadpt',str(a.device)],check=True)
except Exception as e:
 r['error']=str(e)
 if r['status']=='started':r['status']='failed'
 raise
finally:a.receipt.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
