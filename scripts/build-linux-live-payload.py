#!/usr/bin/env python3
"""Build the CLI fractal and stage verified ABI binary/Polaris firmware, not an OS desktop."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for name in ['project','softfp','abi-results','firmware-deb','output']:
    p.add_argument('--'+name,type=Path,required=True)
p.add_argument('--image-id',required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
receipt={'status':'started','image_id':a.image_id,'physical_boot':False,'commands':[]}
with (a.output/'build.log').open('w') as log:
    def run(command):
        command=[str(x) for x in command];receipt['commands'].append(command)
        log.write('$ '+repr(command)+'\n');log.flush()
        subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    try:
        vendor=json.loads((a.project/'docs/builds/20261030-fractal-inputs.json').read_text())
        receipt['softfp_sha256']={}
        for name,expected in vendor['inputs'].items():
            if '/softfp/' not in name:continue
            path=a.softfp/Path(name).name
            assert sha(path)==expected,path
            receipt['softfp_sha256'][path.name]=expected
        firmware=json.loads((a.project/'profiles/images/polaris-firmware.json').read_text())
        assert sha(a.firmware_deb)==firmware['sha256']
        receipt['firmware_input']=firmware
        abi=json.loads((a.abi_results/'receipt.json').read_text())
        assert sha(a.abi_results/'abi-init')==abi['binary_sha256']
        assert abi['source_sha256']==sha(a.project/'bench/spe-abi-smoke.c')
        receipt['abi_validation_status']=abi['status']
        receipt['abi_receipt_sha256']=sha(a.abi_results/'receipt.json')
        flags=['-O2','-msoft-float','-mcpu=8548','-ffreestanding','-fno-builtin',
               '-fno-stack-protector','-fno-pie','-msdata=none']
        objects=[]
        for source in ['addsf3.c','subsf3.c','mulsf3.c']:
            dest=a.output/(source+'.o')
            run(['powerpc-linux-gnu-gcc',*flags,'-I'+str(a.softfp),'-c',a.softfp/source,'-o',dest])
            objects.append(dest)
        payload=a.output/'payload';(payload/'bin').mkdir(parents=True)
        binary=payload/'bin/fractal-test'
        run(['powerpc-linux-gnu-gcc',*flags,'-DTABOR_FRACTAL_CLI','-nostdlib','-static','-no-pie',
             '-Wl,-e,_start','-I'+str(a.project/'bench'),a.project/'bench/fractal.c',*objects,'-o',binary])
        receipt['fractal_source_sha256']=sha(a.project/'bench/fractal.c')
        receipt['fractal_binary_sha256']=sha(binary)
        for obj in objects:
            dis=subprocess.check_output(['powerpc-linux-gnu-objdump','-d','-M','e500',str(obj)],text=True)
            (a.output/(obj.name+'.dis')).write_text(dis)
            import re
            instructions=re.findall(r'^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+){4}(\S+)',dis,re.M)
            assert instructions and not any(x.startswith(('ef','ev','f','lf','stf','mffs','mtfs')) for x in instructions),obj
        dis=subprocess.check_output(['powerpc-linux-gnu-objdump','-d','-M','e500',str(binary)])
        (a.output/'fractal.dis').write_bytes(dis)
        for opcode in [b'efsadd',b'efssub',b'efsmul']:assert opcode in dis
        shutil.copyfile(a.abi_results/'abi-init',payload/'bin/spe-abi-check')
        extracted=a.output/'firmware-package'
        run(['dpkg-deb','-x',a.firmware_deb,extracted])
        firmware_root=extracted/'usr/lib/firmware/amdgpu'
        dest=payload/'lib/firmware/amdgpu';dest.mkdir(parents=True)
        selected=sorted(firmware_root.glob('polaris1[01]*'))
        assert selected
        for source in selected:
            assert source.resolve().is_relative_to(extracted.resolve())
            shutil.copyfile(source,dest/source.name)
        license_dir=payload/'usr/share/licenses/firmware-amd-graphics';license_dir.mkdir(parents=True)
        shutil.copyfile(extracted/'usr/share/doc/firmware-amd-graphics/copyright',license_dir/'copyright')
        etc=payload/'etc';etc.mkdir()
        (etc/'tabor-rescue.txt').write_text('''A1222 experimental Linux hardware-rescue image; not yet an E desktop.
Console follows the last console= kernel option; tty0 uses tty1 for keyboard.
Wired networking: inspect ip link, then udhcpc -i INTERFACE.
This image has no sshd, systemd or E yet. Do not expect desktop-stage acceptance.
SPE/glibc check: spe-abi-check --cli (reports failures and returns).
Explicit-instruction/no-libc demo: fractal-test > /tmp/fractal.log
Do not confuse this demo with complete floating ABI or GPU/GL validation.
Firmware/driver compilation does not establish actual Radeon HDMI output.
Do not install to or format internal disks. Use manual USB boot; no saved firmware changes.
''')
        files=[]
        for file in sorted(payload.rglob('*')):
            if file.is_file():files.append({'path':str(file.relative_to(payload)),'sha256':sha(file),
                                           'mode':0o755 if file.parent==payload/'bin' else 0o644})
        (a.output/'payload-manifest.json').write_text(json.dumps({'files':files,'firmware_input':firmware,
            'abi_validation_status':abi['status']},indent=2)+'\n')
        receipt['files']=files;receipt['status']='hardware-rescue-payload-built-not-desktop'
    except Exception as error:
        receipt.update(status='failed',error=str(error));raise
    finally:(a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(receipt['status'])
