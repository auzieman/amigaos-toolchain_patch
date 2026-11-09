"""R730-only: extract selected GFX8 IB/fence paths and test their byte contracts."""
from pathlib import Path
import difflib, hashlib, json, os, resource, subprocess
os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
# QEMU PPC reserves the 4 GiB guest address space; this bounds virtual, not resident, memory.
resource.setrlimit(resource.RLIMIT_AS, (6 * 1024**3, 6 * 1024**3))
S = Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-007/source')
W = Path('/home/owner/gfx-ib-flow-20261108')
D = S / 'drivers/gpu/drm/amd/amdgpu'

def function(text, signature):
    a = text.index(signature); i = text.index('{', a) + 1; depth = 1
    while depth:
        depth += (text[i] == '{') - (text[i] == '}'); i += 1
    return text[a:i]

gfx = (D / 'gfx_v8_0.c').read_text()
original = function(gfx, 'static int gfx_v8_0_ring_test_ib(')
assert original.count('tmp = adev->wb.wb[index];') == 1
fixed = original.replace('tmp = adev->wb.wb[index];',
                        'tmp = le32_to_cpu(READ_ONCE(adev->wb.wb[index]));')
needle = '\tif (r == 0) {\n\t\tr = -ETIMEDOUT;'
assert fixed.count(needle) == 1
fixed = fixed.replace(needle, '''\tif (r == 0) {
\t\t/* CPU-visible state only: no register reads or recovery submission. */
\t\tdev_err(adev->dev,
\t\t\t"IB_CONTRACT ring=%s payload=%08x fence=%08x emitted=%08x signaled=%08x ib_lo=%08x ib_hi=%08x length=%u\\n",
\t\t\tring->name, le32_to_cpu(READ_ONCE(adev->wb.wb[index])),
\t\t\tring->fence_drv.cpu_addr ?
\t\t\t\tle32_to_cpu(READ_ONCE(*ring->fence_drv.cpu_addr)) : 0,
\t\t\tREAD_ONCE(ring->fence_drv.sync_seq),
\t\t\tatomic_read(&ring->fence_drv.last_seq),
\t\t\tlower_32_bits(ib.gpu_addr), upper_32_bits(ib.gpu_addr),
\t\t\tib.length_dw);
\t\tr = -ETIMEDOUT;''')
candidate = gfx.replace(original, fixed)
(W / 'gfx_v8_0.c.fixed').write_text(candidate)
patch = ''.join(difflib.unified_diff(gfx.splitlines(True), candidate.splitlines(True),
                fromfile='a/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c',
                tofile='b/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c'))
(W / '0028-gfx8-decode-ib-test-writeback-and-record-completion.patch').write_text(patch)
ring = (D / 'amdgpu_ring.h').read_text()
fence = (D / 'amdgpu_fence.c').read_text()
functions = [function(ring, 'static inline u32 amdgpu_ring_encode_dw('),
             function(ring, 'static inline void amdgpu_ring_write(')]
for name in ['gfx_v8_0_ring_emit_ib_gfx', 'gfx_v8_0_ring_emit_ib_compute',
             'gfx_v8_0_ring_emit_fence_gfx', 'gfx_v8_0_ring_emit_fence_compute']:
    functions.append(function(gfx, 'static void ' + name + '('))
functions.append(function(fence, 'static u32 amdgpu_fence_read('))
pre = (W / 'fixture-prefix.c').read_text().replace('@VID@', str(D / 'vid.h'))
pre = pre.replace('@GFXENUM@', str(S / 'drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_enum.h'))
for name, value in [('64BIT', '(1 << 0)'), ('INT', '(1 << 1)'), ('EXEC', '(1 << 3)')]:
    line = next(x for x in ring.splitlines() if x.startswith('#define AMDGPU_FENCE_FLAG_' + name + ' '))
    assert value in line, line
post = (W / 'fixture-model.c').read_text()
main = (W / 'fixture-main.c').read_text()
# Preserve the original source notice with the extracted driver routines.
notice = gfx[:gfx.index('#include')]
code = notice + pre + '\n'.join(functions) + post
code += original.replace('gfx_v8_0_ring_test_ib(', 'test_original(')
code += fixed.replace('gfx_v8_0_ring_test_ib(', 'test_candidate(') + main
(W / 'connected-gfx-ib.c').write_text(code)
outputs = {}
for arch, cc, runner in [('x86', 'gcc', []), ('ppc', 'powerpc-linux-gnu-gcc', ['qemu-ppc'])]:
    exe = W / ('connected-' + arch)
    cmd = [cc] + (['-mstackrealign'] if arch == 'x86' else [])
    cmd += ['-O2', '-ffreestanding', '-nostdlib', '-fno-stack-protector',
            '-fno-builtin', '-fno-pie', '-no-pie', '-static', str(W / 'connected-gfx-ib.c'), '-o', str(exe)]
    p = subprocess.run(cmd, capture_output=True)
    (W / (arch + '-compile.log')).write_bytes(p.stderr); p.check_returncode()
    p = subprocess.run(runner + [str(exe)], capture_output=True, timeout=20)
    (W / (arch + '.bin')).write_bytes(p.stdout)
    assert p.returncode == 0, (arch, p.returncode, p.stderr.decode(errors='replace'))
    outputs[arch] = p.stdout
assert outputs['x86'] == outputs['ppc']
receipt = {'status': 'PASS', 'hardware_accessed': False,
    'source_candidate': str(S), 'source_sha256': hashlib.sha256(code.encode()).hexdigest(),
    'patch_sha256': hashlib.sha256(patch.encode()).hexdigest(),
    'source_inputs_sha256': {str(p.relative_to(S)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [D/'gfx_v8_0.c', D/'amdgpu_ring.h', D/'amdgpu_fence.c', D/'vid.h', S/'drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_enum.h']},
    'cases_per_architecture': 2 * 2 * 4 * 8 * 4,
    'coverage': ['actual shared GFX/compute test caller', 'actual primary-ring word encoder/writer',
                 'actual GFX and compute IB descriptors', 'actual EOP/RELEASE_MEM fence packets',
                 'actual CPU fence LE decoder', 'original/corrected payload comparison',
                 'CPU-only timeout classification: no completion vs completed without signal'],
    'negative_controls': ['original BE test rejects completed LE payload; x86 passes',
                          'modeled missing IB fetch swap fails BE without changing x86',
                          'pre-swapping a native IB while leaving fetch swap active fails BE'],
    'matching_normalized_output_bytes': len(outputs['ppc']),
    'limitations': ['allocation, scheduler dispatch, GPU execution and fence wakeup are modeled',
                    'IB fetch swap is a selectable model, not a hardware observation',
                    'does not establish physical DMA/cache/IRQ completion or fix the timeout']}
(W / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt, indent=2))
