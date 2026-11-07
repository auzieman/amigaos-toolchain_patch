# Targeted Polaris11 BE command-ring candidate

User explicitly authorizes hardware-specific changes for the A1222/Polaris pair.
Experiment0007 selects software-LE only for BE Polaris11 GFX rings. It changes
single-word, bulk-copy, clear/NOP and conditional-packet patch writes together;
pointer shadows are encoded/decoded consistently, and CP_RB0 hardware swap is off.
The common helper predicate lives in amdgpu_ring.c (full device definition),
avoiding a new ring-structure ABI field. Other ring types retain their contracts.
IB buffers remain native with the existing separate IB swap request; this is not
an assertion that the entire accelerated userspace stack is now endian-correct.
The first acceptance gate is the normal gfx ring scratch self-test, not a bypass.

Audited direct ring writes in gfx8, amdgpu_gfx and amdgpu_ring: gfx8 has only
snapshot reads; common writers are covered. Other direct stores found in JPEG
and gfx9 belong to different engines. Existing debugfs raw reads remain raw.

Fresh isolated R730 gfx-software-le-20261106-001,4CPU/6GiB/network-none,
unchanged6.12.113 modular config and cached source. Existing SMU and TOC fixes
and temporary instrumentation retained. Build/physical outcomes pending.

Exact writer-helper validation passed on native x86 and emulated BE PPC: NOP fill, single write, wrapping bulk copy, conditional patch, condition shadow and accounting produce the same expected36bytes. First harness001 failed to declare bool; corrected harness002 passes. This tests encoding helpers, not GPU execution.

Build completed exit0. Config and Module.symvers compare exactly with accepted modular003. Module SHA2567b06066034650fd44a6b01284665bc86b905ebb7540ce7e261d3be55b03b4d0d. Target test uses temporary in-memory module, original disk module preserved.

## Physical result

GFX ring self-test passes: cp_test_all_rings calls GFX and immediately returns
on its error; this execution reaches and fails the subsequent KIQ self-test.
The timeout snapshot now belongs to native-encoded kiq_0.2.1.0, not GFX.
Thus the new graphics-ring producer contract executes on real hardware.
No framebuffer yet. Failed-init cleanup emits repeated amdgpu_irq_put and
amdgpu_i2c_destroy warnings; SSH/uptime remain healthy after capture.
Do not claim complete driver or userspace acceptance.

Follow-up0008 extends the same contract to KIQ/compute: native CPU MQD setup
and register commits/backups are retained, then the GPU-visible MQD allocation
is serialized to LE once; HQD hardware swap off, pointer shadows consistent.
This keeps CPU register values separate from GPU-memory wire values.
