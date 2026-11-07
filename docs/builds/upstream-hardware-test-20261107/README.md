# Clean upstream kernel hardware test preparation

2026-11-07: corrected GCC14 libgcc/glibc rebuilds completed exit0 on R730.
The live A1222 was still running6.12.113-tabor-modular, no loaded modules.
All21 installed firmware hashes match the pinned new-module requirements.
The staged archive and every payload file passed SHA256 checks. USB serial
03001919041721081205 was checked before writes.

Installed the separate42-module7.3.0-rc6-tabor-upstream-001 directory without
replacing old modules. Backed up old kernel on FAT at
boot/uImage-modular.rollback-6.12 and under
/root/upstream-clean-20261107-001/rollback/uImage-modular; both verified against
6c289f999b9cc707d519489d417d00d68a3e722c81c0abad1a05685271ac12c9.
Activated new boot/uImage-modular by staged copy, hash check, rename, sync and
readback. New SHA7377e17e308cbe6902aed0747cf8cb3870c8672d1d45e27e7cf7856b9a1b0270.
boot.scr, DTB and uRamdisk-fw hashes remain unchanged. FAT unmounted cleanly.
Raw command/result and manifest evidence are adjacent. No reboot or driver bind
has happened in this preparation step.

The user requested the new kernel/GPU hardware test before desktop image work.
The unresolved7.3 QEMU two-core startup limitation was disclosed before
activation; this is a physical experiment, not passed SMP validation. Boot
using the existing saved Linux entry. If it fails, restore the verified old
kernel file from the FAT rollback copy (same old loader/script/load addresses).
No U-Boot environment or firmware flashing was performed.

Next: verify new release/CPU count/network/root and SSH; hold AMDGPU until an
off-board log capture is ready and USB root can be protected read-only. One
bounded first bind; no repeated unload/reload after a failed initialization.
Kernel boot, local console, DRM scanout and GPU acceleration remain separate gates.
