#!/usr/bin/env python3
"""Run inside a digest-pinned AmigaGCConDocker image; never execute its OS4 output."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--project', type=Path, default=Path('/project'))
p.add_argument('--softfp', type=Path, default=Path('/softfp'))
p.add_argument('--output', type=Path, default=Path('/out'))
p.add_argument('--image', required=True)
a = p.parse_args()
a.output.mkdir(exist_ok=True)
receipt = {'status': 'started', 'image': a.image, 'amigaos_execution': False,
           'modern_gcc_restoration': False, 'os_spe_context_validated': False}
receipt['harness_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
log = (a.output / 'build.log').open('w')


def run(command, check=True):
    log.write('$ ' + repr(command) + '\n'); log.flush()
    result = subprocess.run([str(x) for x in command], text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log.write(result.stdout); log.flush()
    if check and result.returncode:
        raise RuntimeError(f'command failed ({result.returncode}): {command}')
    return result


try:
    assert re.fullmatch(r'(?:[\w./-]+@)?sha256:[0-9a-f]{64}', a.image), 'Digest pin required'
    cc = shutil.which('ppc-amigaos-gcc')
    assert cc, 'AmigaOS cross compiler missing'
    receipt['compiler_version'] = run([cc, '--version']).stdout
    receipt['target'] = run([cc, '-dumpmachine']).stdout.strip()
    assert receipt['target'] == 'ppc-amigaos', receipt['target']
    inputs = json.loads((a.project / 'profiles/amigaos-docker-spe.json').read_text())
    receipt['profile_sha256'] = hashlib.sha256((a.project/'profiles/amigaos-docker-spe.json').read_bytes()).hexdigest()
    receipt['softfp_sha256'] = {}
    for name, expected in inputs['softfp_sha256'].items():
        actual = hashlib.sha256((a.softfp / name).read_bytes()).hexdigest()
        assert actual == expected, name
        receipt['softfp_sha256'][name] = actual
    probe = a.output / 'compiler-spe.c'
    probe.write_text('float addf(float a,float b){return a+b;}\n'
                     'double addd(double a,double b){return a+b;}\n')
    result = run([cc, '-O2', '-mcpu=8548', '-mabi=spe', '-mspe', '-mfloat-gprs=double',
                  '-S', probe, '-o', a.output / 'compiler-spe.s'], check=False)
    receipt['compiler_spe_flags_accepted'] = result.returncode == 0
    assembly = (a.output / 'compiler-spe.s').read_text() if result.returncode == 0 else ''
    receipt['compiler_emits_efsadd'] = bool(re.search(r'\befsadd\b', assembly))
    receipt['compiler_emits_efdadd'] = bool(re.search(r'\befdadd\b', assembly))
    receipt['compiler_spe_object_assembled'] = False
    if result.returncode == 0:
        run([cc, '-O2', '-mcpu=8548', '-mabi=spe', '-mspe', '-mfloat-gprs=double',
             '-c', probe, '-o', a.output/'compiler-spe.o'])
        receipt['compiler_spe_object_assembled'] = True
        cxx = shutil.which('ppc-amigaos-g++')
        run([cxx, '-x', 'c++', '-O2', '-mcpu=8548', '-mabi=spe', '-mspe',
             '-mfloat-gprs=double', '-c', probe, '-o', a.output/'compiler-spe-cxx.o'])
        receipt['cxx_spe_object_assembled'] = True
        trace = run([cc, '-###', '-mcpu=750', '-x', 'c', '-c', '/dev/null']).stdout
        assert '-mppc' in trace and '-me500' not in trace, 'Generic 750 assembler mapping changed'
        receipt['generic_750_mapping_preserved'] = True
    flags = ['-O2', '-mcrt=newlib', '-msoft-float', '-mcpu=8548', '-msdata=none',
             '-fno-builtin', '-fno-stack-protector', '-Wall', '-Wextra']
    receipt['fractal_flags'] = flags
    runtime_flags = ['-O2', '-mcrt=newlib', '-mcpu=750', '-msdata=none',
                     '-fno-builtin', '-fno-stack-protector', '-Wall', '-Wextra']
    receipt['runtime_driver_flags'] = runtime_flags
    receipt['runtime_boundary'] = 'integer/pointer-only; runtime uses normal newlib ABI, arithmetic objects use soft-float internally'
    objects = []
    for source, symbol in [('addsf3.c','add'), ('subsf3.c','sub'), ('mulsf3.c','mul')]:
        dest = a.output / (source + '.o')
        original = {'add':'__addsf3','sub':'__subsf3','mul':'__mulsf3'}[symbol]
        run([cc, *flags, '-I' + str(a.softfp), '-D' + original + '=tabor_softfp_' + symbol,
             '-c', a.softfp / source, '-o', dest])
        objects.append(dest)
    bench = a.project / 'bench/amigaos'
    receipt['project_source_sha256'] = {}
    for source in [bench/'arithmetic.h', bench.parent/'coordinates.h']:
        receipt['project_source_sha256'][str(source.relative_to(a.project))] = hashlib.sha256(source.read_bytes()).hexdigest()
    for source in ['soft-backend.c','spe-backend.c','fractal-main.c']:
        receipt['project_source_sha256'][source] = hashlib.sha256((bench/source).read_bytes()).hexdigest()
        dest = a.output / (source + '.o')
        selected_flags = runtime_flags if source == 'fractal-main.c' else flags
        run([cc, *selected_flags, '-c', bench / source, '-o', dest]); objects.append(dest)
    # Audit our objects separately from prebuilt runtime/startup libraries.
    for obj in objects:
        dis = run(['ppc-amigaos-objdump','-d','-M','e500',obj]).stdout
        (a.output / (obj.name + '.dis')).write_text(dis)
        instructions = re.findall(r'^\s*[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+){4}(\S+)', dis, re.M)
        assert instructions, ('No decoded instructions', obj.name)
        floating = [x for x in instructions if x.startswith(('ef','ev','f','lf','stf','mffs','mtfs'))]
        if obj.name == 'spe-backend.c.o':
            assert sorted(floating) == ['efsadd','efsmul','efssub'], floating
        else:
            assert not floating, (obj.name, floating)
    binary = a.output / 'fractal-os4'
    run([cc, *runtime_flags, *objects, '-o', binary])
    run(['ppc-amigaos-readelf','-h','-A',binary])
    receipt['binary_sha256'] = hashlib.sha256(binary.read_bytes()).hexdigest()
    receipt['own_object_instruction_audit'] = 'passed; prebuilt runtime excluded'
    receipt['status'] = 'cross-build-passed-not-executed'
except Exception as error:
    receipt['status'] = 'failed'
    receipt['error'] = str(error)
finally:
    log.close()
    receipt['build_log_sha256'] = hashlib.sha256((a.output/'build.log').read_bytes()).hexdigest()
    (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
raise SystemExit(0 if receipt['status']=='cross-build-passed-not-executed' else 1)
