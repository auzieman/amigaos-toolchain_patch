# Polaris PowerPlay handoff — 2026-11-08

The protected first bind of candidate080f5493 reached a more specific failure
boundary. Graphics, KIQ, all eight compute scratch tests, GUI-idle interrupt
enable, and both SDMA scratch tests returned0. GFX and SDMA hw_init returned0.
The next marker was powerplay hw_init entry. The first captured PCIe error
followed55,771 microseconds later, with ERR_DR00800000/ERR_CAP_STAT23.
PowerPlay never returned in the retained capture. Bind timed out; a subsequent
SSH connection timed out during banner exchange. No GPU retry/reset followed.

Evidence is in ../gfx-postmap-review-20261108/hardware-offboard-002/. The root
was verified read-only before any driver operations. Attempt001 stopped before
GPU work because the sshd log held the root writable. A temporary8MiB /run tmpfs
and replacement sshd listener writing its log there resolved this; SSH config,
keys, installed modules and saved boot files were unchanged. Those changes are
volatile and reset at reboot. The off-board capture is retained independently.

This establishes completion of these scratch tests, not IB/fence, display or
application acceptance. It moves the observed endpoint failure into the
PowerPlay interval; an earlier asynchronous operation is not excluded solely
by the last log line. Do not keep describing the compute-map stage as the
established failing operation.

## Source correction

The6.12 smu7_send_msg_to_smc helper reports success unconditionally, even for
an unsupported command, failed command, or inaccessible-device responseffff.
The cached upstream snapshot5349075eac146ae0511d8929fc24451e4d9a4b7e has a
corrected helper that returns0 only for response1, -EOPNOTSUPP forfe, -ENXIO
forffff, and -EIO otherwise. Patch0016 copies that exact function, without
importing a newer kernel or overwriting the existing BE firmware/TOC fixes.
The shallow checkout identifies a snapshot, not the original change's commit.

An executable regression uses the actual original and corrected function
bodies with a simulated register endpoint. All five response cases must return
the expected status, send the same1234 command and perform exactly two writes.
The legacy function acts as a negative control: it falsely succeeds for all
four error cases. Native execution and a freestanding PPC32 BE executable are
separate checks; neither simulates actual PCIe/MMIO timing or GPU recovery.

Patch0017 records the PowerPlay lifecycle calls, SMU message ID/parameter/raw
response and ATOM command calls. It retains existing conversions, return values,
conditionals and ordering; it performs no new register reads. Logging is scoped
to Polaris11 and can affect timing. These are diagnostic markers, not a repair
of the initiating bus fault. The new status handling can expose earlier ignored
errors but cannot guarantee recovery once PCIe has stopped responding.

Relevant producer/consumer contracts:

* ATOM ROM and command parameters use LE; the interpreter already uses
  get_unaligned_le32 and cpu_to_le32. Existing callers' conversions are retained.
* SMU7 DPM SRAM structures use BE fields, with PP_HOST_TO_SMC conversions and
  explicit MSB-first byte packing in smu7_copy_bytes_to_smc. They must not be
  treated like the separate LE GPU transfer TOC or raw firmware container.
* SMU mailbox command/argument values are native integers passed through normal
  LE MMIO accessors. No blanket CPU-to-GPU data conversion is introduced.

The source review also noticed native DWORD casts in the AC timing parser and
a raw SVI2 load-line read. These merit separate BE audit. They are not silently
folded into this candidate or claimed as this hang's cause; the Polaris MC table
has no further consumer in this exact polaris10_smumgr.c path.

## Reproduction and remaining gate

prepare.py copies a qualified parent source/output into a private R730 workspace,
extracts the upstream helper, emits both patches and builds the response test.
build.py uses normal Kbuild with the full copied output and checks the resulting
module against the accepted export table and installed-reference full vermagic.
The original source, SDK and output remain read-only. Containers are limited to
4 CPUs/6GiB with networking disabled. Launch receipts pin their image/mounts.

Prepare001 exposed absent PPC libc development headers in the build-only image;
the integer-only regression was changed to freestanding Linux syscall exit.
Prepare002 exposed an incomplete errno include;003 uses the full kernel UAPI
errno header. These are test-build setup failures, not driver failures. Failed
workspaces remain separate; no package install or source-version drift occurred.

Physical acceptance still requires a fresh boot, exact candidate verification,
RAM-backed SSH logging, protected USB root and a single off-board captured bind.
Do not retry the GPU from the failed state. A visible terminal, DRM scanout and
accelerated rendering remain open gates.

## Qualified artifact

Normal Kbuild completed exit0; all687 imported CRCs and full vermagic match the
accepted6.12.113-tabor-modular kernel/reference module. Result module SHA256:
7067488b2b42329c262c8e6d65ae2c63c47c13a9370bfd88a84e302fa19db247.
It remains on R730 at
/srv/data1/tabor-build/linux-live-001/work/polaris-powerplay-20261108-003/output/drivers/gpu/drm/amd/amdgpu/amdgpu.ko.
No deployment or new physical bind has happened.

Five response cases passed natively and in the PPC32 BE executable under QEMU.
The first standalone PPC test launcher omitted the exit syscall number because
a C fixed-register variable crossed a function call; disassembly confirmed the
missing li0,1. The corrected assembly entry calls main then issues exit; the
bounded QEMU run exits0. This was a test-launcher defect, not a driver/ABI claim.
The final prepare.py reproduces the corrected entry. The old test source/log
remains on the server as negative setup evidence.
