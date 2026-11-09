"""R730-only, identified SanDisk update; activate boot.scr last, retain e2e003."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import struct
import subprocess
import time
import zlib

WORK = Path('/srv/data1/tabor-build/source-review/e2e007-usb-test-20261108')
CANDIDATE = Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-007')
ROOT = Path('/mnt/tabor-e2e007-root')
FAT = Path('/mnt/tabor-e2e007-fat')
RELEASE = '6.12.113-tabor-e2e-007'
OLD_SCRIPT = '550078f018abe3a200b9e9c2f240b72f1c448bfbd38b1ba2dbcc18638fd151ee'
INIT = 'f4adcd1fee09de1ba8c96f5bc7dd75f6ee920dcc2455ac7d198826cafa10a761'
INITRD = '239e7aa7140b5e5474259fd2e12c7396243067acc5385a43cd37e0d219236745'


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def check(path, expected):
    assert sha(path) == expected, str(path)


def image_crc(path):
    blob = path.read_bytes()
    magic, hcrc, _, size, _, _, dcrc = struct.unpack_from('>7I', blob)
    header = bytearray(blob[:64]); header[4:8] = b'\0' * 4
    assert magic == 0x27051956 and len(blob) == size + 64
    assert zlib.crc32(header) == hcrc and zlib.crc32(blob[64:]) == dcrc
    return blob


def atomic_copy(source, dest, mount):
    # Every destination is contained in an explicitly verified mounted filesystem.
    assert dest.is_relative_to(mount) and not dest.is_symlink()
    for parent in dest.parents:
        assert not parent.is_symlink(), str(parent)
        if parent == mount:
            break
    dest.parent.mkdir(parents=True, exist_ok=True)
    temp = dest.with_name(dest.name + '.e2e007-next')
    assert not temp.exists() and not temp.is_symlink()
    with source.open('rb') as src, temp.open('xb') as out:
        shutil.copyfileobj(src, out)
        out.flush(); os.fsync(out.fileno())
    check(temp, sha(source))
    os.replace(temp, dest)
    fd = os.open(dest.parent, os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    check(dest, sha(source))


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    assert not (WORK / 'install-receipt.json').exists(), 'Inspect previous receipt; do not rerun blindly.'
    assert not (WORK / 'before-boot.scr').exists(), 'Prior activation backup already exists.'
    report = {'status': 'started', 'release': RELEASE, 'gpu_loaded': False,
              'hardware_booted': False, 'boot_selected': False, 'filesystems': {}}
    mounted = []
    try:
        identity = json.loads(run('lsblk', '--tree', '-J', '-o',
            'NAME,PATH,SERIAL,TRAN,PARTUUID,MOUNTPOINTS', '/dev/sde'))['blockdevices'][0]
        assert identity['serial'] == '03001919041721081205' and identity['tran'] == 'usb'
        assert {x['path']: x['partuuid'] for x in identity['children']} == {
            '/dev/sde1': 'a1221105-01', '/dev/sde2': 'a1221105-02'}
        assert not any(identity['mountpoints'])
        assert all(not any(x['mountpoints']) for x in identity['children'])
        report['usb_identity'] = identity
        receipt = json.loads((WORK / 'build-receipt.json').read_text())
        assert receipt['kernel_release'] == RELEASE
        check(CANDIDATE / 'update.tar', receipt['tar_sha256'])
        bundle = CANDIDATE / 'bundle'
        for name, digest in receipt['bundle_files_sha256'].items():
            source = bundle / name
            assert source.resolve().is_relative_to(bundle.resolve())
            check(source, digest)
        assert len(list((bundle / 'root/lib/modules' / RELEASE).rglob('*.ko'))) == 43
        image_crc(bundle / 'fat/boot/e2e/uImage')
        new_script = WORK / 'boot-e2e007.scr'
        run('mkimage', '-A', 'ppc', '-O', 'linux', '-T', 'script', '-C', 'none',
            '-n', 'A1222 e2e007 matched test', '-d', str(WORK / 'boot-e2e007.cmd'), str(new_script))
        assert image_crc(new_script)[72:] == (WORK / 'boot-e2e007.cmd').read_bytes()
        for name, args in [('root-before', ['e2fsck', '-fn', '/dev/sde2']),
                           ('fat-before', ['fsck.fat', '-n', '/dev/sde1'])]:
            result = subprocess.run(args, capture_output=True, text=True)
            (WORK / (name + '.txt')).write_text(result.stdout + result.stderr)
            report['filesystems'][name] = result.returncode
            assert result.returncode == 0, name
        for mount, device, opts in [(ROOT, '/dev/sde2', 'ro,noload'), (FAT, '/dev/sde1', 'ro')]:
            mount.mkdir(exist_ok=True)
            run('mount', '-o', opts, device, str(mount)); mounted.append(mount)
            assert run('findmnt', '-n', '-o', 'SOURCE', '--target', str(mount)).strip() == device
        check(FAT / 'boot.scr', OLD_SCRIPT)
        check(ROOT / 'init', INIT)
        check(FAT / 'boot/uRamdisk-fw', INITRD)
        old_kernel = FAT / 'boot/e2e-003/uImage'
        old_module = ROOT / 'lib/modules/6.12.113-tabor-e2e-003/kernel/drivers/gpu/drm/amd/amdgpu/amdgpu.ko'
        old_hashes = {str(p): sha(p) for p in [old_kernel, old_module]}
        assert not (ROOT / 'lib/modules' / RELEASE).exists()
        assert not (FAT / 'boot/e2e-007').exists()
        for name, digest in receipt['bundle_files_sha256'].items():
            if name.startswith('root/lib/firmware/'):
                dest = ROOT / name[5:]
                assert dest.resolve().is_relative_to(ROOT.resolve()), str(dest)
                check(dest, digest)  # Preserve existing aliases; no firmware rewrite.
        for name in ['boot.scr', 'boot.cmd']:
            shutil.copyfile(FAT / name, WORK / ('before-' + name))
        run('mount', '-o', 'remount,rw', str(ROOT))
        run('mount', '-o', 'remount,rw', str(FAT))
        for name, digest in receipt['bundle_files_sha256'].items():
            if name.startswith('root/lib/modules/'):
                atomic_copy(bundle / name, ROOT / name[5:], ROOT)
            elif name.startswith('fat/boot/e2e/'):
                atomic_copy(bundle / name, FAT / 'boot/e2e-007' / Path(name).name, FAT)
        atomic_copy(WORK / 'before-boot.scr', FAT / 'boot-before-e2e007.scr', FAT)
        atomic_copy(new_script, FAT / 'boot-e2e007.scr', FAT)
        atomic_copy(WORK / 'boot-e2e007.cmd', FAT / 'boot-e2e007.cmd', FAT)
        for path, digest in old_hashes.items():
            check(Path(path), digest)
        check(ROOT / 'init', INIT)
        check(FAT / 'boot/uRamdisk-fw', INITRD)
        for name, digest in receipt['bundle_files_sha256'].items():
            dest = (ROOT / name[5:] if name.startswith('root/') else
                    FAT / 'boot/e2e-007' / Path(name).name)
            check(dest, digest)
        os.sync()
        atomic_copy(WORK / 'boot-e2e007.cmd', FAT / 'boot.cmd', FAT)
        atomic_copy(new_script, FAT / 'boot.scr', FAT)  # Activate only after all payloads verify.
        os.sync()
        report.update(status='installed-selected-awaiting-physical-boot', boot_selected=True,
            boot_script_sha256=sha(FAT / 'boot.scr'), rollback_script_sha256=OLD_SCRIPT,
            module_sha256=receipt['module_verification']['module_sha256'],
            verified_bundle_files=len(receipt['bundle_files_sha256']),
            init_unchanged=sha(ROOT / 'init') == INIT, firmware_initrd_unchanged=True)
    except BaseException as exc:
        report.update(status='incomplete', error=str(exc))
        raise
    finally:
        os.sync()
        unmounted = []
        for mount in reversed(mounted):
            result = subprocess.run(['umount', str(mount)], capture_output=True, text=True)
            unmounted.append({'mount': str(mount), 'rc': result.returncode, 'error': result.stderr})
        report['unmounts'] = unmounted
        report['time_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        (WORK / 'install-receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    assert all(x['rc'] == 0 for x in report['unmounts'])
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
