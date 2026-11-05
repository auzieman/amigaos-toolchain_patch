#!/usr/bin/env python3
"""Build a file-backed FAT/ext4 rescue USB from verified inputs, without flashing media.

Run as root on the build server to preserve initramfs ownership/device nodes.
No target executable is run during assembly. This preserves the historical
diagnostic rescue root, not a Debian package-managed desktop installation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import struct
import subprocess


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def extract_newc(data, root):
    """Extract our verified newc input, rejecting traversal and symlink parents."""
    offset = 0
    directories = []
    while True:
        assert data[offset:offset+6] == b'070701', 'Expected newc archive'
        fields = [int(data[offset+6+i*8:offset+14+i*8], 16) for i in range(13)]
        mode, uid, gid, size, namesize = fields[1], fields[2], fields[3], fields[6], fields[11]
        raw = data[offset+110:offset+110+namesize]
        assert namesize and raw[-1:] == b'\0'
        name = raw[:-1].decode()
        offset = (offset+110+namesize+3) & ~3
        content = data[offset:offset+size]
        assert len(content) == size
        offset = (offset+size+3) & ~3
        if name == 'TRAILER!!!':
            break
        part = PurePosixPath(name)
        assert not part.is_absolute() and '..' not in part.parts and name not in ['', '.']
        dest = root / name
        for parent in reversed(dest.parents):
            if parent == root or root in parent.parents:
                assert not parent.is_symlink(), 'Symlink parent refused'
        dest.parent.mkdir(parents=True, exist_ok=True)
        assert not dest.exists() and not dest.is_symlink(), name
        if stat.S_ISDIR(mode):
            dest.mkdir()
            directories.append((dest, mode, uid, gid))
        elif stat.S_ISREG(mode):
            dest.write_bytes(content)
        elif stat.S_ISLNK(mode):
            dest.symlink_to(content.decode())
        elif stat.S_ISCHR(mode) or stat.S_ISBLK(mode):
            os.mknod(dest, mode, os.makedev(fields[9], fields[10]))
        else:
            raise ValueError('Unsupported archive type: '+name)
        os.lchown(dest, uid, gid)
        if not dest.is_symlink():
            os.chmod(dest, stat.S_IMODE(mode))
    for dest, mode, uid, gid in reversed(directories):
        os.chown(dest, uid, gid)
        os.chmod(dest, stat.S_IMODE(mode))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['boot-results', 'rescue-results', 'board-config', 'output']:
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    assert os.geteuid() == 0, 'Preserving target ownership requires root'
    boot = json.loads((a.boot_results/'receipt.json').read_text())
    rescue = json.loads((a.rescue_results/'receipt.json').read_text())
    for name in ['uImage', 'tabor.dtb']:
        assert digest(a.boot_results/name) == boot['files_sha256'][name]
    assert digest(a.rescue_results/'shell.cpio') == rescue['initramfs_sha256']
    config = a.board_config.read_text().splitlines()
    for option in ['EXT4_FS', 'USB_STORAGE', 'BLK_DEV_SD', 'MSDOS_PARTITION', 'DEVTMPFS']:
        assert 'CONFIG_'+option+'=y' in config, option+' must be built in'
    a.output.mkdir(parents=True, exist_ok=False)
    root = a.output/'root'
    root.mkdir()
    extract_newc((a.rescue_results/'shell.cpio').read_bytes(), root)
    assert (root/'init').is_file() and (root/'usr/sbin/sshd').is_file()
    # Keep the image's provisioned account and public key, never add client keys.
    assert not list(root.rglob('ssh_host_*')), 'Unexpected pre-generated host key'
    assert (root/'home/tabor/.ssh/authorized_keys').stat().st_uid == 1000
    assert stat.S_IMODE((root/'home/tabor/.ssh/authorized_keys').stat().st_mode) == 0o600
    (root/'etc/fstab').write_text('proc /proc proc defaults 0 0\nsysfs /sys sysfs defaults 0 0\n')
    disk_id = 0xa1221105
    partuuid = f'{disk_id:08x}-02'
    args = f'root=PARTUUID={partuuid} rootfstype=ext4 rootwait rw init=/init mem=3500M console=ttyS0,115200 console=tty0 loglevel=8 ignore_loglevel panic=-1'
    script = a.output/'boot.cmd'
    script.write_text('''# Temporary A1222 rescue boot; never saveenv or access internal disks.
if usb reset; then
 if fatload usb 0:1 0x04000000 /boot/uImage; then
  if iminfo 0x04000000; then
   if fatload usb 0:1 0x08000000 /boot/tabor.dtb; then
    setenv bootargs '''+args+'''
    bootm 0x04000000 - 0x08000000
   fi
  fi
 fi
fi
echo Rescue boot failed or returned; saved firmware settings unchanged.
''')
    commands = []
    with (a.output/'build.log').open('w') as log:
        def run(cmd):
            cmd = list(map(str, cmd)); commands.append(cmd)
            subprocess.run(cmd, check=True, stdout=log, stderr=subprocess.STDOUT,
                           env={**os.environ, 'PATH':'/usr/sbin:/usr/bin:/sbin:/bin', 'SOURCE_DATE_EPOCH':'0'})
        run(['mkimage', '-A', 'ppc', '-O', 'linux', '-T', 'script', '-C', 'none',
             '-n', 'A1222 ext4 rescue', '-d', script, a.output/'boot.scr'])
        fat = a.output/'boot.fat'
        ext = a.output/'root.ext4'
        with fat.open('wb') as f: f.truncate(128*1024**2)
        run(['mkfs.fat', '-F', '32', '-n', 'A1222_BOOT', fat])
        run(['mmd', '-i', fat, '::/boot'])
        files = {'boot/uImage':a.boot_results/'uImage', 'boot/tabor.dtb':a.boot_results/'tabor.dtb',
                 'boot.scr':a.output/'boot.scr', 'boot.cmd':script}
        readme = a.output/'BOOT-README.txt'
        readme.write_text('A1222 historical SPE rescue root on ext4; no E desktop or GCC14 claim.\n'
                          'Use top-right USB port, mouse disconnected if enumeration fails.\n'
                          'Temporary manual launch (USB device 0):\nusb reset\n'
                          'fatload usb 0:1 0x09000000 /boot.scr\nsource 0x09000000\n'
                          'Script support must be checked with help source. No saveenv.\n'
                          'Manual fallback:\nfatload usb 0:1 0x04000000 /boot/uImage\n'
                          'iminfo 0x04000000\nfatload usb 0:1 0x08000000 /boot/tabor.dtb\n'
                          'setenv bootargs '+args+'\nbootm 0x04000000 - 0x08000000\n'
                          'Root waits for this image PARTUUID; no internal filesystem is mounted.\n'
                          'SSH tabor/key-only. Root local shell. /tmp/network-boot.log.\n'
                          'Power down cleanly before removal; ext4 retains host keys and logs.\n'
                          'Physical boot and display still unverified.\n')
        files['BOOT-README.txt'] = readme
        for name, path in files.items():
            run(['mcopy', '-i', fat, path, '::/'+name])
            actual = subprocess.check_output(['mtype', '-i', str(fat), '::/'+name])
            assert hashlib.sha256(actual).hexdigest() == digest(path), name
        with ext.open('wb') as f: f.truncate(1919*1024**2)
        run(['mkfs.ext4', '-F', '-L', 'A1222_ROOT', '-U', 'a1221105-0000-4000-8000-000000000002', '-d', root, ext])
        run(['e2fsck', '-f', '-n', ext])
        image = a.output/'a1222-layered-rescue.img'
        first = 2048; second = first+fat.stat().st_size//512
        total = second+ext.stat().st_size//512
        mbr = bytearray(512)
        struct.pack_into('<I', mbr, 440, disk_id)
        for index, active, kind, start, length in [(0,0x80,0x0c,first,second-first),(1,0,0x83,second,total-second)]:
            struct.pack_into('<B3sB3sII', mbr, 446+16*index, active, b'\xfe\xff\xff', kind,b'\xfe\xff\xff',start,length)
        mbr[510:512] = b'\x55\xaa'
        with image.open('wb') as f:
            f.truncate(total*512); f.write(mbr)
            for start, path in [(first,fat),(second,ext)]:
                f.seek(start*512)
                with path.open('rb') as src: shutil.copyfileobj(src,f,4*1024**2)
        with image.open('rb') as f:
            assert f.read(512) == mbr
            for start,path in [(first,fat),(second,ext)]:
                f.seek(start*512); h=hashlib.sha256(); left=path.stat().st_size
                while left:
                    block=f.read(min(left,4*1024**2)); assert block
                    h.update(block);left-=len(block)
                assert h.hexdigest()==digest(path)
    receipt={'status':'layered-rescue-image-verified','image_sha256':digest(image),
             'image_bytes':image.stat().st_size,'root_partuuid':partuuid,'bootargs':args,
             'rescue_initramfs_input_sha256':rescue['initramfs_sha256'],
             'board_config_sha256':digest(a.board_config),'boot_files_sha256':{n:digest(v) for n,v in files.items()},
             'kernel_rebuilt':False,'initramfs_used_for_boot':False,'e_desktop_installed':False,
             'physical_boot':False,'block_device_written':False,'commands':commands}
    (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='commands'},indent=2))


if __name__ == '__main__':
    main()
