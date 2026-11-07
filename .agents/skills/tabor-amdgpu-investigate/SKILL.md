---
name: tabor-amdgpu-investigate
description: Investigate A1222 AMDGPU initialization and rendering failures through cross-architecture source tracing and measured device contracts, using working x86 or POWER systems as controls.
---

Read AGENTS.md, docs/task.md and the latest relevant hardware receipt. Work as a
GPU driver engineer: derive a falsifiable source-level explanation, implement the
smallest justified boundary fix, and establish console/render acceptance. A role
prompt grants no AMD employment, internal documentation or additional access.
The canonical toolchain repository owns fixes; forge receives pinned exports.

## Establish the actual target and control

Pin ASIC/PCI IDs, kernel source and complete patch order, config, compiler,
firmware hashes, CPU ABI/endian mode, PCI host bridge and boot state for each
comparison. POWER8/9 CPU generation does not determine userspace/kernel endian
mode; inspect it. A1222 PPC32 BE/e500v2 and POWER64 LE/BE are different hosts.
Use shared driver functions as comparisons, not proof of identical DMA/coherency,
address widths, firmware handoff or platform behavior. Preserve the working x86
capture; distinguish warm rebind from a real cold firmware upload.

## Reconstruct execution before choosing a fix

Trace the pinned driver's IP-block setup and actual hw_init/late_init order,
including error returns and asynchronous work. Identify the last measured
success, first measured failure, and every intervening unobserved call. A log
printed after command submission proves CPU progress, not GPU completion.
A passing KIQ packet test does not prove graphics/compute IBs, fences, SDMA or
scanout. A solid screen colour does not identify a particular failure.

Build a producer-to-consumer ledger for the suspected common boundary:

- native CPU data and backups versus GPU-visible serialized structures;
- register/MMIO accessors, indexed registers and doorbell writes;
- GPU command rings versus indirect buffers, shader code and writeback;
- firmware container metadata versus raw microcode and transfer tables;
- VRAM I/O mappings versus coherent/system-memory mappings and DMA addresses.

For each relevant object record the owning writer/helper, width, address units,
required byte order, mapping API, publication ordering and consuming reader.
Inspect all writers of that object before proposing a shared conversion. Keep
existing Linux endian/MMIO/DMA abstractions; fix the violated contract once at
its owning boundary. Do not globally swap AMDGPU data, serialize native register
values, or assume a CPU ABI/compiler change repairs GPU wire encoding.

## Test the explanation

Prefer host-side native/BE byte-contract checks and reviewed source differences
before another physical trial. Such checks validate their model, not hardware
ordering or GPU execution. Compare applicable upstream and contributor patches
against the exact target; inspect rather than assume a newer version fixes it.
When testing hardware, mark the remaining unobserved call boundaries and retain
parameter values plus before/after status. Keep the change discriminating:
state which competing causes the result can actually exclude. Do not infer a
root cause from the last log or an interrupt storm alone. Decode vendor PCIe
registers using that host's documentation, not unrelated generic bit masks.

Use existing bounded first-bind tooling, verified candidate/config hashes,
off-board logs and verified read-only USB root. No repeated unload/reload after
failed initialization. If access is lost, retain the negative result and stop
hardware retries until a materially different, reviewed test or fix is ready.
Timeouts cannot guarantee recovery from a bus/kernel hang. Preserve the user's
saved boot setup. Use R730 for builds under the existing resource policy.

## Report useful acceptance

Deliver the narrowed source path, evidence for/against the hypothesis, proposed
shared fix or explicit remaining gap, and the next bounded test. Separate kernel
build, physical boot/SSH, readable local fbcon, DRM/KMS scanout, GPU execution,
Mesa/Xorg and E/compositing acceptance. User goal here starts with a visible
terminal; do not require a full accelerated desktop to acknowledge console
success. Record failures and commit provenance as carefully as successful gates.

For the current stalled Polaris trial, read
[the investigation reset](references/polaris-20261107.md). Keep that dated
checkpoint separate from reusable engineering rules.
