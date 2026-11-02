#!/usr/bin/env python3
"""Verify installed SPE compiler defaults in a configured cross-build root.

Compilation/linking only. No target executable or library is run on the host.
"""
import argparse, hashlib, json, subprocess
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--tools', type=Path, default=Path('/usr/lib/tabor-spe-toolchain'))
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
a.output.mkdir(exist_ok=False)
sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
r = {'status': 'running', 'target_execution': False, 'commands': []}
def run(cmd, **kwargs):
    r['commands'].append(list(map(str, cmd)))
    return subprocess.check_output(list(map(str, cmd)), text=True, stderr=subprocess.STDOUT, **kwargs)
try:
    cc = a.tools/'bin/powerpc-linux-gnuspe-gcc'
    cxx = a.tools/'bin/powerpc-linux-gnuspe-g++'
    r['compiler_sha256'] = sha(cc)
    r['sysroot'] = run([cc, '-print-sysroot']).strip()
    assert r['sysroot'] == '/'
    macros = run([cc, '-dM', '-E', '-'], input='')
    r['default_abi'] = [line for line in macros.splitlines() if any(s in line for s in
        ['__SPE__', '__NO_FPRS__', '__LONG_DOUBLE_128__', '__LONG_DOUBLE_IBM128__', '__BYTE_ORDER__'])]
    for macro in ['__SPE__ 1', '__NO_FPRS__ 1', '__LONG_DOUBLE_128__ 1',
                  '__LONG_DOUBLE_IBM128__ 1', '__BYTE_ORDER__ __ORDER_BIG_ENDIAN__']:
        assert '#define '+macro in macros, macro
    r['binutils'] = {}
    for name in ['ar', 'as', 'ld', 'nm', 'ranlib', 'readelf', 'objcopy', 'objdump', 'strip']:
        tool = Path(run([cc, '-print-prog-name='+name]).strip()).resolve()
        assert tool == Path('/usr/bin/powerpc-linux-gnu-'+name).resolve(), tool
        r['binutils'][name] = {'path': str(tool), 'sha256': sha(tool)}
    sources = {'c': '#include <stdio.h>\n#include <pthread.h>\nint main(void){printf("%zu\\n",sizeof(pthread_t));return 0;}\n',
               'cc': '#include <vector>\n#include <stdexcept>\nint main(){std::vector<int> a(2,3);try {throw std::runtime_error("probe");} catch(const std::exception&){return a[0]-3;}}\n'}
    r['linked_outputs'] = {}
    for ext, body in sources.items():
        source = a.output/('probe.'+ext); source.write_text(body)
        output = a.output/('probe-'+ext)
        run([cc if ext=='c' else cxx, '-O2', source, '-o', output])
        header = run([r['binutils']['readelf']['path'], '-h', output])
        assert all(s in header for s in ['ELF32', "big endian", 'PowerPC'])
        dynamic = run([r['binutils']['readelf']['path'], '-d', output])
        assert 'RPATH' not in dynamic and 'RUNPATH' not in dynamic
        r['linked_outputs'][ext] = {'sha256': sha(output), 'header': header, 'dynamic': dynamic}
    r['status'] = 'installed-defaults-compile-link-passed-not-executed'
except Exception as e:
    r.update(status='failed', error=str(e))
    raise
finally:
    (a.output/'receipt.json').write_text(json.dumps(r, indent=2)+'\n')
