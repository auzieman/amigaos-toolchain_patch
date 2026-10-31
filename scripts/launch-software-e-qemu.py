#!/usr/bin/env python3
"""Launch a separate SPE guest for software X11/E; leave existing guests alone."""
import argparse,hashlib,json,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['kernel','initramfs','output']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--receipt',type=Path);p.add_argument('--ssh-port',type=int,default=22126);p.add_argument('--rfb-port',type=int,default=5911);a=p.parse_args()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt_path=a.receipt or a.initramfs.parent/'receipt.json'
receipt=json.loads(receipt_path.read_text());assert receipt['status'] in ['rescue-initramfs-extended','rescue-initramfs-compressed']
assert sha(a.initramfs)==receipt['initramfs_sha256'],'Initramfs receipt/hash mismatch'
a.output.mkdir(parents=True,exist_ok=False)
cmd=['qemu-system-ppc','-M','ppce500','-cpu','e500v2','-accel','tcg','-smp','2','-m','2048M','-display','none','-serial','file:'+str(a.output/'serial.log'),'-monitor','none','-qmp','unix:'+str(a.output/'qmp.sock')+',server=on,wait=off','-no-reboot','-nic','none','-object','rng-random,id=rng0,filename=/dev/urandom','-device','virtio-rng-pci,rng=rng0','-netdev',f'user,id=net0,hostfwd=tcp:127.0.0.1:{a.ssh_port}-:22,hostfwd=tcp:127.0.0.1:{a.rfb_port}-:5900','-device','virtio-net-pci,netdev=net0','-kernel',str(a.kernel),'-initrd',str(a.initramfs),'-append','console=ttyS0,115200 rootfstype=ramfs rdinit=/desktop-init panic=-1']
with (a.output/'qemu.log').open('wb') as log:proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
r={'status':'launched-not-yet-boot-validated','pid':proc.pid,'command':cmd,'receipt_sha256':sha(receipt_path),'launcher_sha256':sha(Path(__file__)),'kernel_sha256':sha(a.kernel),'initramfs_sha256':sha(a.initramfs),'qemu_version':subprocess.check_output(['qemu-system-ppc','--version'],text=True).splitlines()[0],'physical_boot':False,'GPU_validated':False}
(a.output/'qemu.pid').write_text(str(proc.pid)+'\n');(a.output/'launch.json').write_text(json.dumps(r,indent=2)+'\n');time.sleep(2);assert proc.poll() is None,(a.output/'qemu.log').read_text();print('Started separate software-session guest',proc.pid)
