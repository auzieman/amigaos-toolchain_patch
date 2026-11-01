#!/usr/bin/env python3
"""Verify that a fresh serial shell executes commands in the e500v2 guest."""
import argparse,hashlib,json,re,shutil,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--kernel',type=Path,required=True);p.add_argument('--initramfs',type=Path,required=True)
p.add_argument('--output',type=Path,required=True);p.add_argument('--image-id',required=True)
p.add_argument('--qemu',default='qemu-system-ppc')
p.add_argument('--platform-checks',action='store_true',help='Check 8GiB, two CPUs, cgroups and a disposable virtio/ext4 disk; not a Debian root install')
p.add_argument('--rescue',action='store_true',help='Also require richer rescue applets')
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
receipt={'status':'started','kernel_sha256':sha(a.kernel),'initramfs_sha256':sha(a.initramfs),'image_id':a.image_id,'spe_full_abi_validated':False,'physical_boot':False}
receipt['rescue_checks_requested']=a.rescue
receipt['platform_checks_requested']=a.platform_checks
binary=shutil.which(a.qemu)
if binary is None:p.error('QEMU executable missing')
receipt['qemu_sha256']=sha(Path(binary));receipt['qemu_version']=subprocess.check_output([binary,'--version'],text=True).splitlines()[0]
cmd=[binary,'-M','ppce500','-cpu','e500v2','-accel','tcg','-smp','2','-m','8192M' if a.platform_checks else '512M','-display','none','-serial','stdio','-monitor','none','-nic','none','-no-reboot','-kernel',str(a.kernel),'-initrd',str(a.initramfs),'-append','console=ttyS0,115200 rdinit=/init panic=-1']
if a.platform_checks:
 disk=a.output/'scratch.ext4'
 with disk.open('xb') as f:f.truncate(64*1024**2)
 subprocess.run(['mkfs.ext4','-q','-F',str(disk)],check=True)
 cmd+=['-drive','file='+str(disk)+',format=raw,if=none,id=testdisk','-device','virtio-blk-pci,drive=testdisk']
receipt['command']=cmd;serial=a.output/'serial.log';proc=None
try:
 with serial.open('wb',buffering=0) as stream:
  proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=stream,stderr=subprocess.STDOUT)
  deadline=time.monotonic()+(120 if a.platform_checks else 60);sent=False
  while time.monotonic()<deadline:
   data=serial.read_bytes().replace(b'\r',b'')
   if b'Kernel panic' in data or proc.poll() is not None:break
   if b'SHELL_READY\n' in data and not sent:
    time.sleep(.5)
    command=b"printf '\\nSHELL_COMMAND_OK\\n'; uname -m; head -n 2 /proc/meminfo; "
    if a.rescue:command+=b"ip link show && ps && df && free && test -x /etc/udhcpc.script && echo RESCUE_COMMANDS_DONE; "
    if a.platform_checks:
     command+=b"test $(grep -c '^processor' /proc/cpuinfo) -eq 2 && (set -- $(head -n 1 /proc/meminfo); test \"$2\" -gt 7340032) && echo CPU_MEMORY_CHECKS_DONE && mkdir -p /tmp/cgroup-test && mount -t cgroup2 none /tmp/cgroup-test && grep -q memory /tmp/cgroup-test/cgroup.controllers && cat /tmp/cgroup-test/cgroup.controllers && echo CGROUP_CHECKS_DONE && mkdir -p /tmp/block-test && mount -t ext4 /dev/vda /tmp/block-test && echo SPE_BOOT_STORAGE_OK > /tmp/block-test/probe && sync && umount /tmp/block-test && mount -t ext4 /dev/vda /tmp/block-test && grep -q SPE_BOOT_STORAGE_OK /tmp/block-test/probe && umount /tmp/block-test && echo PLATFORM_CHECKS_DONE; "
    command+=b"echo SHELL_DONE\n"
    proc.stdin.write(command);proc.stdin.flush();sent=True
   if re.search(rb'^SHELL_DONE$',data,re.M):break
   time.sleep(.2)
  receipt['commands_sent']=sent
finally:
 if proc is not None and proc.poll() is None:
  proc.terminate()
  try:proc.wait(timeout=5)
  except subprocess.TimeoutExpired:proc.kill();proc.wait()
 raw=serial.read_bytes();data=raw.replace(b'\r',b'')
 receipt['shell_command_passed']=bool(re.search(rb'^SHELL_COMMAND_OK$',data,re.M)) and bool(re.search(rb'^SHELL_DONE$',data,re.M))
 receipt['machine_reported_ppc']=bool(re.search(rb'^ppc$',data,re.M))
 receipt['proc_meminfo_read']=bool(re.search(rb'^MemTotal:\s+\d+ kB$',data,re.M))
 receipt['panic_seen']=b'Kernel panic' in data
 receipt['rescue_commands_passed']=bool(re.search(rb'^RESCUE_COMMANDS_DONE$',data,re.M)) if a.rescue else None
 receipt['status']='passed' if all(receipt.get(k) for k in ['commands_sent','shell_command_passed','machine_reported_ppc','proc_meminfo_read']) and not receipt['panic_seen'] else 'failed'
 if a.rescue and not receipt['rescue_commands_passed']:receipt['status']='failed'
 receipt['platform_checks_passed']=bool(re.search(rb'^PLATFORM_CHECKS_DONE$',data,re.M)) if a.platform_checks else None
 if a.platform_checks and not receipt['platform_checks_passed']:receipt['status']='failed'
 receipt['serial_sha256']=sha(serial)
 (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2));raise SystemExit(0 if receipt['status']=='passed' else 1)
