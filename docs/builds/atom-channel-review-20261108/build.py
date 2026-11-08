"""Build the private 6.12 candidate under normal, fully populated Kbuild."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess

w = Path('/candidate')
src = Path('/base/work/tabor-smu-diagnostics-20261105-003/source')
out = Path('/base/work/tabor-smu-diagnostics-20261105-003/output')
reference = Path('/base/work/gfx-map-stage-20261107-001/output/Module.symvers')
inspect = runpy.run_path('/qualification/verify-ppc32-module.py')['inspect']
result = {'status': 'started', 'hardware_tested': False,
          'kernel_release': '6.12.113-tabor-modular'}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

try:
    assert sha(out / '.config') == '7effb33413cbb4ab6dcda93563c2600f1948f9764387df70cd016883892fdaec'
    cmd = ['make', '-C', str(src), 'O=' + str(out), 'ARCH=powerpc',
           'CROSS_COMPILE=powerpc-linux-gnu-', '-j4', 'modules']
    result['command'] = cmd
    with (w / 'build.log').open('w') as log:
        proc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
    result['exit'] = proc.returncode
    if proc.returncode:
        raise RuntimeError('Kbuild modules failed')
    module = out / 'drivers/gpu/drm/amd/amdgpu/amdgpu.ko'
    result['verification'] = inspect(module, result['kernel_release'], reference,
                                     '/qualification/installed-reference-amdgpu.ko')
    result['config_sha256'] = sha(out / '.config')
    result['patches'] = {p.name: sha(p) for p in w.glob('*.patch')}
    result['tools'] = {x: subprocess.check_output([x, '--version'], text=True).splitlines()[0] for x in ['powerpc-linux-gnu-gcc', 'powerpc-linux-gnu-ld']}
    result['tools_image'] = 'sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0'
    result['status'] = 'compiled-crcs-verified-not-deployed'
except BaseException as exc:
    result['status'] = 'failed'
    result['error'] = str(exc)
    raise
finally:
    (w / 'build.json').write_text(json.dumps(result, indent=2) + '\n')
