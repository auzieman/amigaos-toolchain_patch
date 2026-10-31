#!/usr/bin/env python3
"""Create and verify a file-backed A1222 USB boot filesystem; no block-device writes."""
import argparse,gzip,hashlib,json,os,struct,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--boot-results',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--size-mib',type=int,default=2048)
a=p.parse_args();assert 256<=a.size_mib<=16384
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
source=json.loads((a.boot_results/'receipt.json').read_text())
for name,expected in source['files_sha256'].items():assert sha(a.boot_results/name)==expected,name
a.output.mkdir(parents=True,exist_ok=False)
image=a.output/'a1222-hardware-rescue.img';size=a.size_mib*1024**2;offset=2048*512
with image.open('wb') as f:
 f.truncate(size)
 mbr=bytearray(512);mbr[446:462]=struct.pack('<B3sB3sII',0x80,b'\xfe\xff\xff',0x0c,b'\xfe\xff\xff',2048,size//512-2048)
 mbr[510:512]=b'\x55\xaa';f.write(mbr)
commands=[]
with (a.output/'build.log').open('w') as log:
 def run(c):
  c=[str(x) for x in c];commands.append(c);subprocess.run(c,stdout=log,stderr=subprocess.STDOUT,check=True)
 run(['mkfs.fat','-F','32','--offset=2048','-h','2048','-n','A1222_SPE','-i','A1222001',image])
 specification=str(image)+'@@'+str(offset)
 run(['mmd','-i',specification,'::/boot'])
 for name in ['uImage','uRamdisk','tabor.dtb']:
  run(['mcopy','-i',specification,a.boot_results/name,'::/boot/'+name])
 instructions='''A1222 experimental Linux hardware-rescue USB; no E desktop yet.
Manual U-Boot trial only. Use rear/direct USB for the first trial, as recalled
by the operator; no rear-only firmware requirement has been established.
Identify the USB storage device with usb reset / usb storage / fatls first.
Example for USB device0 partition1 (adjust if the device enumeration differs):

usb reset
fatls usb 0:1
fatload usb 0:1 0x04000000 /boot/uImage
iminfo 0x04000000
fatload usb 0:1 0x08000000 /boot/tabor.dtb
fatload usb 0:1 0x0a000000 /boot/uRamdisk
iminfo 0x0a000000
setenv bootargs console=ttyS0,115200 console=tty0 rdinit=/init panic=-1
bootm 0x04000000 0x0a000000 0x08000000

Do not saveenv. These are temporary settings, not an internal-disk install.
Wait for amdgpu initialization and SHELL_READY on HDMI. If no usable output,
retain OBS capture rather than assuming a successful boot. Serial is optional.

At the shell: cat /etc/tabor-rescue.txt
Wired DHCP and SSH start automatically in the background.
Inspect /tmp/network-boot.log. Manual retry: udhcpc -i INTERFACE; /etc/start-ssh
SSH user tabor uses the privately retained operator key. No password/root SSH.
SPE/glibc: spe-abi-check --cli
Fractal: fractal-test > /tmp/fractal.log
Native ABI results, GPU output and board boot remain unverified until observed.
'''
 readme=a.output/'BOOT-README.txt';readme.write_text(instructions)
 run(['mcopy','-i',specification,readme,'::/BOOT-README.txt'])
 for name in ['uImage','uRamdisk','tabor.dtb']:
  data=subprocess.check_output(['mtype','-i',specification,'::/boot/'+name])
  assert hashlib.sha256(data).hexdigest()==source['files_sha256'][name],name
with image.open('rb') as f:
 assert f.read(512)==mbr
 f.seek(offset);boot=f.read(512)
 assert boot[510:512]==b'\x55\xaa' and b'FAT32' in boot
receipt={'status':'file-image-built-and-filesystem-readback-verified','image_bytes':size,
 'image_sha256':sha(image),'partition_start_sector':2048,'partition_type':'0x0c FAT32 LBA',
 'boot_receipt_sha256':sha(a.boot_results/'receipt.json'),'boot_files_sha256':source['files_sha256'],
 'commands':commands,'physical_boot':False,'block_device_written':False,
 'e_desktop_installed':False}
(a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
with image.open('rb') as src,(a.output/(image.name+'.gz')).open('wb') as dst:
 with gzip.GzipFile(filename='',mode='wb',fileobj=dst,compresslevel=1,mtime=0) as zipped:
  while chunk:=src.read(1024**2):zipped.write(chunk)
print(json.dumps(receipt,indent=2))
