from pathlib import Path
import subprocess,runpy
s=runpy.run_path('tabor-spe-toolchain/work/modular-usb-update-20261105-001/board_access.py')['ssh'];p=Path('tabor-spe-toolchain/docs/builds/gpu-memory-contract-20261109')
names=['amdgpu_vm_flush','amdgpu_vm_set_ptes','amdgpu_vm_copy_ptes','amdgpu_cs_ioctl']
try:
 s('set -e; for n in '+' '.join(names)+'; do echo 1 > /sys/kernel/tracing/instances/tabor-vm012/events/amdgpu/$n/enable; done; echo 1 > /sys/kernel/tracing/instances/tabor-vm012/tracing_on')
 code=(p/'run-uswc.py').read_text().replace('/run/gfx-write uswc; r=$?','/run/gfx-write uswc le; r=$?').replace('uswc-native','uswc-le-traced');(p/'run-uswc-le-traced.py').write_text(code)
 subprocess.run(['python3',str(p/'run-uswc-le-traced.py')],check=True)
finally:
 s('echo 0 > /sys/kernel/tracing/instances/tabor-vm012/tracing_on')
 r=s('cat /sys/kernel/tracing/instances/tabor-vm012/trace; for f in /sys/kernel/tracing/instances/tabor-vm012/per_cpu/cpu*/stats; do cat "$f"; done',capture_output=True,text=True);(p/'vm-trace.txt').write_text(r.stdout)
 s('for n in '+' '.join(names)+'; do echo 0 > /sys/kernel/tracing/instances/tabor-vm012/events/amdgpu/$n/enable; done')
print((p/'vm-trace.txt').read_text()[-8000:])
