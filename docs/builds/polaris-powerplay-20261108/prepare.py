"""Run only in the bounded R730 container; preserve the qualified parent tree."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import subprocess

base = Path('/base/work')
parent = base / 'gfx-postmap-review-20261107-001'
upstream = base / 'amdgpu-upstream-clean-20261107-003/source'
work = Path('/candidate')
src = work / 'source'
out = work / 'output'
prefix = 'drivers/gpu/drm/amd/pm/powerplay/'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def function_span(text, name):
    match = re.search(r'^(?:static )?int ' + name + r'\([^;]*?\)\n\{', text, re.M)
    assert match, name
    start, pos = match.start(), match.end()
    depth = 1
    while depth:
        depth += (text[pos] == '{') - (text[pos] == '}')
        pos += 1
    return start, pos

def diff(path, before, after):
    return ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                      fromfile='a/' + path, tofile='b/' + path))

assert not src.exists() and not out.exists(), 'refuse to reuse a work tree'
assert sha(parent / 'output-matched/drivers/gpu/drm/amd/amdgpu/amdgpu.ko') == \
    '080f54935bb910a9bafa021b8e12ac8965aab34344cbb382067c2b18d032eb72'
for old, new in [(parent / 'source', src), (parent / 'output-matched', out)]:
    subprocess.run(['cp', '-a', '--reflink=auto', str(old), str(new)], check=True)

rel = prefix + 'smumgr/smu7_smumgr.c'
original = (src / rel).read_text()
fresh = (upstream / rel).read_text()
start, end = function_span(original, 'smu7_send_msg_to_smc')
us, ue = function_span(fresh, 'smu7_send_msg_to_smc')
corrected_function = fresh[us:ue]
fixed = original[:start] + corrected_function + original[end:]
(work / '0016-smu7-propagate-command-response.patch').write_text(diff(rel, original, fixed))
(src / rel).write_text(fixed)

# Execute the real old/new helper against a simulated register endpoint. This
# checks response semantics, not physical MMIO/endian/coherency or GPU recovery.
test_header = r'''
#ifdef FREESTANDING
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
#include "/base/work/gfx-postmap-review-20261107-001/source/include/uapi/asm-generic/errno.h"
#define printf(...) ((void)0)
#else
#include <stdint.h>
#include <errno.h>
#include <stdio.h>
#endif
struct amdgpu_device { void *dev; };
struct pp_hwmgr { struct amdgpu_device *adev; void *device; };
static int response, sent, writes;
#define PHM_WAIT_FIELD_UNEQUAL(...) 0
#define PHM_READ_FIELD(...) response
#define mmSMC_RESP_0 0
#define mmSMC_MESSAGE_0 1
#define dev_dbg(...) ((void)0)
#define dev_info(...) ((void)0)
static void cgs_write_register(void *dev, int reg, int value) {
    (void)dev; writes++; if (reg == mmSMC_MESSAGE_0) sent = value;
}
'''
old_function = original[start:end].replace('int smu7_send_msg_to_smc(',
                                           'int old_send_msg(')
test_main = r'''
int main(void) {
    struct amdgpu_device adev = {0};
    struct pp_hwmgr h = { &adev, 0 };
    const int values[] = {1, 0xfe, 0, 2, 0xffff};
    const int errors[] = {0, -EOPNOTSUPP, -EIO, -EIO, -ENXIO};
    for (unsigned i = 0; i < sizeof(values)/sizeof(values[0]); i++) {
        response = values[i]; writes = 0; sent = 0;
        int result = smu7_send_msg_to_smc(&h, 0x1234);
        if (result != errors[i] || writes != 2 || sent != 0x1234) return 1;
        int old = old_send_msg(&h, 0x1234);
        if (old != 0) return 2;
        printf("response=%#x legacy=%d corrected=%d PASS\n", response, old, result);
    }
    return 0;
}
#ifdef FREESTANDING
__asm__(".text\n.globl _start\n_start:\n"
        "bl main\nli 0,1\nsc\nb .\n");
#endif
'''
(work / 'smu-response-test.c').write_text(test_header + old_function + '\n' +
                                        corrected_function + '\n' + test_main)
with (work / 'smu-response-test.log').open('w') as log:
    for compiler, flags, name in [('gcc', [], 'native'),
                                 ('powerpc-linux-gnu-gcc', ['-DFREESTANDING',
                                  '-nostdlib', '-ffreestanding', '-msoft-float',
                                  '-Wl,-e,_start'], 'ppc-be')]:
        exe = work / ('smu-response-' + name)
        subprocess.run([compiler, *flags, '-O2', '-static', '-o', str(exe),
                        str(work / 'smu-response-test.c')], check=True, stdout=log, stderr=log)
        log.write(name + '\n'); log.flush()
        if name == 'native':
            subprocess.run([str(exe)], check=True, stdout=log, stderr=log)
        else:
            log.write('compiled; execute with R730 qemu-ppc before accepting\n')

changes = []
rel = prefix + 'inc/pp_debug.h'
text = (src / rel).read_text()
macro = r'''
/* Diagnostic: preserve the call's value and control flow; no additional MMIO. */
#define PP_INIT_CALL(hwmgr, call) ({ \
    int __pp_init_result; \
    if ((hwmgr)->chip_id == CHIP_POLARIS11) \
        pr_info("PWR_TRACE %s enter\n", #call); \
    __pp_init_result = (call); \
    if ((hwmgr)->chip_id == CHIP_POLARIS11) \
        pr_info("PWR_TRACE %s result=%d\n", #call, __pp_init_result); \
    __pp_init_result; \
})
'''
after = text.replace('#define PP_ASSERT_WITH_CODE', macro + '\n#define PP_ASSERT_WITH_CODE', 1)
assert after != text
changes.append(diff(rel, text, after)); (src / rel).write_text(after)

targets = {
    'hwmgr/hwmgr.c': ['hwmgr_hw_init'],
    'hwmgr/smu7_hwmgr.c': ['smu7_hwmgr_backend_init', 'smu7_setup_asic_task',
                           'smu7_enable_dpm_tasks'],
    'smumgr/polaris10_smumgr.c': ['polaris10_init_smc_table'],
}
call_counts = {}
for short, names in targets.items():
    rel = prefix + short
    text = (src / rel).read_text(); after = text
    for name in names:
        start, end = function_span(after, name)
        body = after[start:end]
        pattern = r'(\b(?:ret|result|tmp_result)\s*(?:=|\|=)\s*)([\w>.-]+\([^;]*?\));'
        body, count = re.subn(pattern, r'\1PP_INIT_CALL(hwmgr, \2);', body)
        assert count > 0, name
        call_counts[name] = count
        after = after[:start] + body + after[end:]
    changes.append(diff(rel, text, after)); (src / rel).write_text(after)

# ATOM callers supply LE parameter blocks. Capture which command table runs,
# retaining their existing conversions and interpreter contract unchanged.
rel = prefix + 'hwmgr/ppatomctrl.c'
text = (src / rel).read_text()
after, count = re.subn(r'(\bresult\s*=\s*)(amdgpu_atom_execute_table\([^;]*?\));',
                       r'\1PP_INIT_CALL(hwmgr, \2);', text)
assert count > 0
call_counts['ATOM command callers'] = count
changes.append(diff(rel, text, after)); (src / rel).write_text(after)

rel = prefix + 'smumgr/smu7_smumgr.c'
text = (src / rel).read_text()
start, end = function_span(text, 'smu7_send_msg_to_smc')
body = text[start:end]
body = body.replace('\tint ret;\n', '\tint ret;\n\n\tif (hwmgr->chip_id == CHIP_POLARIS11)\n'
                    '\t\tdev_info(adev->dev, "PWR_TRACE smu_msg=%#x enter\\n", msg);\n', 1)
body = body.replace('\tswitch (ret) {', '\tif (hwmgr->chip_id == CHIP_POLARIS11)\n'
                    '\t\tdev_info(adev->dev, "PWR_TRACE smu_msg=%#x response=%#x\\n", msg, ret);\n\n'
                    '\tswitch (ret) {', 1)
after = text[:start] + body + text[end:]
start, end = function_span(after, 'smu7_send_msg_to_smc_with_parameter')
body = after[start:end].replace('{\n', '{\n\tif (hwmgr->chip_id == CHIP_POLARIS11)\n'
    '\t\tpr_info("PWR_TRACE smu_msg=%#x parameter=%#x\\n", msg, parameter);\n\n', 1)
after = after[:start] + body + after[end:]
changes.append(diff(rel, text, after)); (src / rel).write_text(after)
(work / '0017-polaris-powerplay-call-boundaries.patch').write_text(''.join(changes))
(work / 'prepare.json').write_text(json.dumps({
    'parent_module_sha256': sha(parent / 'output-matched/drivers/gpu/drm/amd/amdgpu/amdgpu.ko'),
    'upstream_snapshot': '5349075eac146ae0511d8929fc24451e4d9a4b7e',
    'upstream_function_sha256': hashlib.sha256(corrected_function.encode()).hexdigest(),
    'call_counts': call_counts,
    'patches': {p.name: sha(p) for p in work.glob('*.patch')},
    'extra_mmio_reads': False, 'hardware_tested': False,
}, indent=2) + '\n')
