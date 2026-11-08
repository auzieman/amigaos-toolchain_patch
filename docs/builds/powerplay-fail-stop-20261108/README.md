# Preserve PowerPlay transition failures through the control path

The physical e2e-003 trace loses PCIe responses after SCLK mask submission.
Its initial fault remains unexplained; patch0024 addresses a separately proven
native state-clock decoding defect. This increment addresses a source-proven
failure-handling chain, not a claim that error returns prevent a bus hang.

Patch0025 changes three shared SMU7 functions:

- Return the voltage-request status instead of discarding it in a void helper.
- Stop mask upload at the first voltage/SCLK/MCLK command error.
- Return immediately at any failed state-transition step instead of recording
  the error and continuing through all later callbacks. Successful paths retain
  their existing order and optimized-state flag update.

Tracing that return outward found a second layer which swallowed it.
Patch0026 changes power_state_management and psm_adjust_power_state_dynamic to
propagate it. A failed transition no longer copies the requested state into
current_ps or continues into display notification, forced levels and profile
requests. Existing successful-state copy semantics are deliberately preserved.

These are common control-path corrections. No endian/MMIO accessor, command
constant, callback implementation or hardware feature is replaced or stubbed.
They do not resolve the UVD encoder indirect-fetch contract or DMA/scanout gaps.

## Verification

`test_transition.py` extracts the actual three functions from pinned6.12.113
sources. It injects three error classes at all eleven transition callbacks,
with/without PCIe requests and custom tables; tests all disabled/zero mask
combinations; and injects nested voltage/mask errors through the actual outer
transition. Original code is a negative control: it continues after errors and
nested requests falsely succeed. Fixed code retains the first error, sends no
later request and preserves the pending optimized-settings flag. Successful
control-flow output is unchanged across old/fixed x86/PPC32 BE.

372 scenarios/version/architecture,1,488 total, pass.

`test_psm.py` extracts the two actual PSM caller functions. Across64 scenarios
per version/architecture (256total), it checks failed transitions preserve the
old current state and forced-level setting, propagate the exact error, and issue
no downstream notification/force/profile call. Equal-state/no-change and
successful paths remain unchanged. Allocation and hardware callbacks are mocks;
these tests are not firmware execution or recovery validation.

Both tests and builds run only on the R730. The tests use oneCPU/6GiB; kernel
builds use the existing pinned Docker image under4CPU/6GiB. Candidate005 adds
0025 to004; candidate006 adds0026 to005 in a separate source/output copy. Neither
candidate writes USB or changes the selected e2e-003 boot entry. Receipts pin
patches, compiler/config/artifacts and full module CRC verification separately
from hardware acceptance.

## Caller and recovery limits

hardwaremanager.c returns the power_state_set callback status. The PSM layer
previously discarded it;0026 now preserves it. Reviewed hwmgr resume, suspend
and task-dispatch callers already collect/return psm_adjust_power_state_dynamic
status. hwmgr backend teardown still ignores that status and attempts cleanup;
this increment does not claim complete teardown fault containment.

A failure after DPM freeze can leave DPM frozen. The patch deliberately issues
no speculative unfreeze or recovery request after an error. A CPU trapped in a
failed PCIe/MMIO transaction cannot be rescued by an error check it has not yet
reached. A failed physical attempt still requires the existing cold-recovery
procedure. Kernel build and offline tests are distinct from a physical fix.

## Completed build qualification

Both005and006complete normal Kbuild, module installation/depmod, firmware and
U-Boot bundle packaging without errors. The combined006candidate is
6.12.113-tabor-e2e-006 with43modules,687AMDGPU imported symbol CRCs verified,
and module SHA256
39cb3f14c248af27a10ac04d970308c669f18b710deb7633c4380cab130a7a90.
The retained build receipts include source patch chain, config/compiler/tool
image, DTB/firmware/kernel hashes and bundle checksums. The existing boot script
and SanDisk remain unchanged. No physical boot, framebuffer or GPU acceptance
is inferred from this build.
