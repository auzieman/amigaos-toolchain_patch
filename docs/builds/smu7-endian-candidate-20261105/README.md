# SMU7 firmware word endian candidate

Status: source-reviewed experiment; compilation and physical acceptance pending.
Baseline Linux6.12.113-1, exact accepted modular configuration, retained tools
image sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0.

The audited chain is amdgpu_cgs_get_firmware_info -> raw firmware payload
info.kptr -> smu7_upload_smu_firmware_image -> smu7_upload_smc_firmware_data.
Firmware header fields are decoded with le32_to_cpu, but the upload loop
currently dereferences uint32_t directly. CGS write_register calls WREG32,
then amdgpu_device_wreg, then writel for the direct MMIO path. Thus identical
file bytes produce different register values on big- and little-endian hosts.

Candidate patch changes the raw word type to const __le32 and uses
le32_to_cpu at the upload write. This preserves the existing little-endian-host
numerical register stream without changing reset sequencing, firmware selection,
PCI configuration, power tables or timeout handling. A byte-vector equivalence
check passed: 01 23 45 67 produces0x67452301 both on current LE and corrected BE,
whereas current BE produces0x01234567. This establishes transformation behavior,
not that it resolves hardware startup. Other endian defects may remain.

Patch is isolated under patches/linux/experiments and is not in the default
Linux series. Fresh R730 build work/tabor-smu7-endian-20261105-001 uses both
board patches followed by the candidate, exact modular .config and4 CPUs/6GiB,
network disabled and cached source. Build container tabor-smu7-endian-build-001.
Working USB/kernel/modules remain unchanged during compilation.

Next: verify compilation and module ABI, preserve original amdgpu.ko, stage the
candidate with hashes, capture /dev/kmsg before one controlled load, check
binding/framebuffer/SSH and the earliest SMU message. A clean reboot may be
required after the already failed original probe; do not repeatedly rebind.
No generic graphics or GL acceptance until actual output is verified.

## Actual result

Build completed successfully. Exact .config and Module.symvers compare equal
with the running modular kernel. Candidate module SHA256:
`ee4f5f3fe96af564fb54ba79703b3eb111fe124bd16f570f0b6e6a94a06f2d02`.
Vermagic:6.12.113-tabor-modular SMP mod_unload modversions relocatable.
Native transfer hash verified; old module unloaded normally and candidate
inserted once. Module insertion returned0, but the GPU device still failed
SMU firmware startup and probe-22. No driver bound, no framebuffer; SSH remains
available. Complete /dev/kmsg stream started before removal/loading and stopped
afterward, preserving the earliest messages despite cleanup warnings.

This is a negative warm-state trial, not a confirmed remedy. Original failed
probe had already touched hardware; no cold-power-cycle candidate comparison
has been performed. Installed kernel/module tree remains original, so reboot
restores the original driver file. Experimental patch stays outside default
series. Next inspect protection-mode startup status, firmware selection and
upload/readback semantics before another change; avoid repeated blind reloads.
