# Native MQD staging and GPU memory publication

Follow-up to physically passing GFX and pre-map KIQ self-tests; compute mapping
still hangs. Off-board trace also contains PowerPC alignment exception at mapped
MEC HPD/EOP memset during sw_init. This experiment uses memset_io for the BE
Polaris11 HPD BO when placed in VRAM. Other domains/platforms retain normal clear.

Build MQD in normal CPU memory, keep native register commits and reset backups,
then publish all2064bytes once: writel per word for VRAM, explicit cpu_to_le32
stores for GTT, followed by mb before MAP_QUEUES. Restore mapped pointer before
caller unmap. Log native descriptor header/base/control/domain before mapping.
This removes ordinary memset/memcpy/normal in-place serializer reads on mapped
VRAM MQDs; it does not claim these accesses caused the mapping hang.

Candidate001 compiled but uses a2064byte stack temporary; retained as build-only,
never deployed. Candidate002 moves staging to kzalloc/free and propagates KIQ
allocation error through its existing resume caller; avoids large kernel frames.
Fresh isolated R7306.12.113/4CPU/6GiB/network-none builds, same reference config.
002 build and hardware outcomes pending.

Exact allocation header and publication helper produce expected identical4128bytes
(two domain branches) on native x86 and emulated BE PPC. Models writel semantics,
not real PCIe ordering or consumer correctness. Wire SHA256:
664d3b95c8b5604587829e6ab41c7ff121de6d8385a40aadf594406f1b12c78e.

002 completed exit0, .config and Module.symvers exactly match modular003. SHA256f6475b61ef7affae8fff7cbd008ef2a70090f96327f3c7a0cd8d2d9adb5e2e49. Retrieved ignored local artifact amdgpu-gfx-mqd-host-002.ko; ready for next cold physical boot. Not deployed, hardware unverified.

## Physical002 result

Fresh boot/no modules, verified module transfer, rootro/off-board logger confirmed.
No PowerPC alignment WARNING appears in saved stream; earlier mapped clear warning
is removed in this run. MQD publication logs control descriptor in VRAM at
f400382000; eight compute descriptors in GTT atff0071c000..ff00723000.
Headersc0310800; compute PQcontrolc031890a and GPU ring bases retained in logs.
Pre-map KIQ scratch test returns0. Mapping-submit entry/return logged, then
PCIe00800000/23 storm and SSH loss. Still no display or compute acceptance.
CPU-side publication values do not establish GPU consumer bytes/coherency.
Next bounded experiment changes compute MQD placement to required VRAM for BE
Polaris11; maintains packet/wire encodings and all tests. This isolates the
translated system-memory descriptor-fetch path without inventing new packets.
