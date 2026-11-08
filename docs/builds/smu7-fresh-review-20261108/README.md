# SMU7 fresh cross-architecture review — 2026-11-08

Scope: pinned 6.12 candidate source on R730; no driver loads, board writes or boot-file changes.
Source hashes and reproducible checks are in audit.json and audit.py. Run the latter on R730 against its explicit source path.

## Findings

1. The upstream display-clock voltage dependency implementation is already present. A duplicate backport is unjustified. The initial physical failure remains PPSMC_MSG_DPM_Enable (0x14e), before later MCLK/PCIe enable messages.
2. The optional AVFS calibration producer has a distinct endian contract defect. polaris10_setup_graphics_level_structure copies native vr_config and static avfs_graphics_level_polaris10 / avfs_memory_level_polaris10 structures directly to smu7_copy_bytes_to_smc. Its constants are pre-swapped for little-endian host memory. The helper explicitly assembles src[0..3] MSB-first, preserving the supplied bytes; it does not normalize native objects.
3. Reproduced examples: frequency literal 0x30750000 yields device bytes 00007530 (30000) on x86, but 30750000 on BE PPC. ActivityLevel 0x3200 yields 0032 (50) versus 3200 (12800). VRConfig has the same discrepancy. BootMVdd, by contrast, is explicitly converted before upload. This is a producer defect, not evidence that the common upload/MMIO helper should globally swap all callers.
4. The actual AVFS gate is hardware-dependent: polaris10_is_hw_avfs_present reads bit 0 of SMC efuse index SMU_EFUSE_0 + 49*4; smu7_init additionally requires PP_AVFS_MASK. The event manager is called during cold SMU startup only when firmware was not already running and not_vf is true. Existing populate_avfs_parameters success logs do not prove this earlier calibration upload executed. No recorded gate value establishes causality for this board.
5. polaris10_start_smu ignores the event manager return. Separately, experiment 0018 already demonstrates mandatory DPM failures being swallowed in startup. Neither correcting error propagation nor showing a serialization defect proves the observed PCIe fault repaired.

## Next bounded implementation

Correct the optional producer as a complete typed serialization change, covering every 16/32-bit member of both calibration structures and VRConfig while retaining byte fields. Preserve the known x86 payload byte-for-byte; use standard Linux endian conversions rather than changing the byte-copy helper or swapping entire mixed-width structures. Compare the complete native and cross-compiled BE objects, not only three sample fields. Add one calibration-entry/gate receipt to the same candidate so a cold first-bind can establish whether this correction is relevant. Keep experiment 0018 error propagation separate and reviewable.

Hardware test acceptance remains: first bind completes without PCIe faults, SSH survives, then readable fbcon/DRM scanout. Ring scratch tests alone do not satisfy GPU execution or display acceptance. The current failed board must not be repeatedly rebound.

## Limits

The audit uses Python integer packing to model the three demonstrated field contracts; it is not a cross-compiled complete-structure test. No kernel rebuilt in this review, no driver fix deployed, no display recovery claimed. AVFS execution and root cause remain unproven.
