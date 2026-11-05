#!/usr/bin/env python3
"""Apply the reviewed early-firmware/admin update to the exact offline lab USB."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

p=argparse.ArgumentParser(description=__doc__)
for name in ['device','firmware-results','output']:
    p.add_argument('--'+name,type=Path,required=True)
p.add_argument('--expected-serial',required=True)
a=p.parse_args();assert os.geteuid()==0 and not a.output.exists()
device=a.device.resolve()
props=dict(line.split('=',1) for line in subprocess.check_output(['udevadm','info','--query=property','--name',str(device)],text=True).splitlines() if '=' in line)
assert props.get('ID_BUS')=='usb' and props.get('ID_SERIAL')==a.expected_serial
tree=json.loads(subprocess.check_output(['lsblk','--json','--tree','-o','NAME,PATH,TYPE,MOUNTPOINTS',str(device)],text=True))['blockdevices'][0]
assert tree['type']=='disk' and len(tree.get('children',[]))==2
for item in [tree,*tree['children']]:assert not any(item.get('mountpoints') or []),'Unmount USB first'
bootdev,rootdev=[x['path'] for x in tree['children']]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=json.loads((a.firmware_results/'receipt.json').read_text())
assert spec['archive_has_init'] is False
for name in ['uRamdisk-fw','boot.cmd','boot.scr']:
    assert sha(a.firmware_results/name)==spec['artifacts'][name]
a.output.mkdir(mode=0o700,parents=True)
backup=a.output/'private-backup';backup.mkdir(mode=0o700)
receipt={'status':'started','serial':a.expected_serial,'physical_display_verified':False}
with tempfile.TemporaryDirectory(prefix='a1222-display-admin-') as temp:
    boot=Path(temp)/'boot';root=Path(temp)/'root';boot.mkdir();root.mkdir();mounted=[]
    try:
        subprocess.run(['mount','-o','rw,nosuid,nodev,noexec',bootdev,str(boot)],check=True);mounted.append(boot)
        assert sha(boot/'boot/uImage')=='90fe78857d06b66186c3a9698803015ed63907e15ccd0f1620f74376ea866146'
        assert sha(boot/'boot.scr')=='cc5faaeb387ece18e6461985dd98912771f87dccf822ad6b03816c86dd94a89b'
        unchanged={n:sha(boot/n) for n in ['boot/uImage','boot/tabor.dtb']}
        for name in ['boot.scr','boot.cmd','BOOT-README.txt']:shutil.copyfile(boot/name,backup/name)
        subprocess.run(['mount','-o','rw,nosuid,nodev,noexec',rootdev,str(root)],check=True);mounted.append(root)
        for name in ['etc/ssh/sshd_config','etc/shadow']:
            dest=backup/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/name,dest);dest.chmod(0o600)
        subprocess.run([sys.executable,str(Path(__file__).with_name('configure-rescue-admin.py')),
                        '--root',str(root),'--receipt',str(a.output/'admin-config.json')],check=True)
        inventory=Path(__file__).resolve().parent.parent/'boot/a1222-qemu-inventory.sh'
        target=root/'usr/sbin/a1222-qemu-inventory';target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(inventory,target);os.chown(target,0,0);target.chmod(0o755)
        # Payload first, script last; interrupted copying retains the old launcher.
        for name,destname in [('uRamdisk-fw','boot/uRamdisk-fw'),('boot.cmd','boot.cmd'),('boot.scr','boot.scr')]:
            dest=boot/destname;staged=dest.with_name(dest.name+'.next');assert not staged.exists()
            shutil.copyfile(a.firmware_results/name,staged)
            with staged.open('rb') as f:os.fsync(f.fileno())
            assert sha(staged)==spec['artifacts'][name];os.replace(staged,dest)
        readme=boot/'BOOT-README.txt'
        readme.write_text('A1222 ext4 rescue with early Polaris firmware.\n'
                          'usb reset\nfatload usb 0:1 0x09000000 /boot.scr\nsource 0x09000000\n'
                          'No saveenv. Same kernel/DTB and mem=3500M.\n'
                          'SSH tabor or root with the existing operator key; passwords disabled.\n'
                          'Root inventory: /usr/sbin/a1222-qemu-inventory /root/qemu-inventory-001\n'
                          'No automatic ROM reads or firmware flashing. Physical display test pending.\n')
        os.sync()
        assert unchanged=={n:sha(boot/n) for n in unchanged}
        receipt.update(status='display-admin-files-written-and-verified',
                       unchanged_files_sha256=unchanged,
                       firmware_sha256=sha(boot/'boot/uRamdisk-fw'),
                       boot_script_sha256=sha(boot/'boot.scr'),
                       inventory_sha256=sha(target),root_admin='operator key only')
    except Exception as error:
        receipt['error']=str(error);raise
    finally:
        for mount in reversed(mounted):subprocess.run(['umount',str(mount)],check=True)
        (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
