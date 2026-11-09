# Mesa explicit-LE GFX publication — 2026-11-09

Target: A1222 PPC32 BE SPE, RX560/Polaris11, kernel 6.12.113-e2e-013
with diagnostic `polaris11_le_user_ib=1`. Prior allocated GFX WRITE_DATA
physically wrote the expected LE marker with fetch swap0. This directory
pairs Mesa's producer with that kernel fetch contract. It is a private
runtime experiment, not a package-managed desktop or release.

## Shared producer boundary

Pinned Mesa 25.0.7 source/build from radeonsi-aco-20261109-002, including
previous executable-only ACO upload serialization and GBM native formats.
Private R730 reflink at work/radeonsi-le-ib-20261109-001; same accepted SPE
C++ SDK8.5 read-only, 2 CPUs/4GiB, no network. Kernel remains GCC14-built.
No SDK promotion or version refresh. Source and patch hashes are retained.

Patch0003 is default-off (`TABOR_POLARIS11_LE_IB=1`), BE/Polaris11/GFX-only.
It leaves CPU PM4 construction and chain-size fixups native, then serializes
all completed main/chained chunks before asynchronous submission. Preambles
are serialized once after padding; reset NOP header likewise before unmap.
Kernel ioctl metadata, descriptors, constants, shader uploads and other
engines retain their separate byte contracts. Existing descriptor and
constant uploads already use Mesa's CPU-to-LE helpers and must not be
converted again. Existing unmodified Mesa must not run with kernel diagnostic
fetch0. Pair both opt-ins; scripts verify exact kernel/parameter/taint first.

Actual extracted selector/serializer checks pass 18 selection cases and128
buffer cases per x86/PPC architecture, 12,800 identical serialized bytes.
OldBE output differs, unchangedLE output matches. Static call-site checks
cover final-size ordering, chains and preamble publication. Queue lifecycle,
fetch and GPU behavior are modeled, not simulated hardware. Full Mesa rebuild
and QEMU loader resolution pass. Private /opt/tabor-mesa-le-ib-20261109 bundle
verified file-for-file on the A1222; original runtime retained, rootRO.

## First physical clear result

Initial clear failed pixel acceptance: actual RadeonSI/ACO ES2 context,
complete framebuffer/no GL errors, but `TABOR_RED_CLEAR rgba=0,0,0,0` and
exit255. Console restoredVT1; SSH/taint0 remain. User saw black VT2 and return
to console via VLC. Render-only testing does not scan out the rendered image.

Patch0004 adds CPU-side publication and clear-route diagnostics. Captured
312DW and160DW GFX chunks start native c0012800 and store native002801c0,
confirming actual LE serialization. Clear mask4 survives both fast-clear and
compute-clear attempts, so this operation proceeds through graphics drawing.
One `AMD_DEBUG=nodmashaders` control bypasses shader-upload DMA; same black
readback. These exclude neither shader execution nor readback defects. No
cube trial, GPU reset, reload, or success claim follows these failures.

## Response-side shared fence decode

Source walk found `amdgpu_fence_wait` compared raw mapped GPU LE64 memory
against native sequence numbers. Kernel amdgpu_ib_schedule emits uf_sequence
through GFX8 EVENT_WRITE_EOP DATA_SEL64; Mesa must decode the mapped value.
A completed old sequence1 can appear as0x0100000000000000 on BE and falsely
satisfy a later wait. Patch0005 uses util_le64_to_cpu at the shared comparison
and virtio assertion. This does not reinterpret native ioctl results.

The actual extracted wait function passes4096 pending +4096 completed
scenarios per arch with corrected decoding. OldBE reproduces false pending
completion; LE behavior and actual completed cases remain correct. Mapped
memory/readiness modeled and ioctl timeout stubbed; hardware causality remains
separate. Userqueue direct-fence consumers exist but are outside this legacy
kernel-queue trial; do not claim every Mesa engine/response fixed.

## Final physical checkpoint

After0005, red-clear still returns exit255/zeroRGBA; SSH, VT1 and taint0
remain. This is a negative rendering result, not proof of fence-fix causality.
Actual post-Mesa GFX ring retained before another workload. The independent
explicitLE buffer test then passes again: marker addefeca, remap identical,
fence complete, swap0, taint0. The command processor/memory-write path remains
working after Mesa trials; accelerated rendering remains unaccepted.

No driver/kernel reload or reboot occurred. Final private libgallium SHA256
42967d7ea468d65db463134c2d112c4f6af28e348a7d0d1b09c145b16a10ec3d.
Original runtime and pre-trace/pre-fence copies retained. Diagnostic trace
patch is retained for review, not proposed as production logging. Next source
work must distinguish actual shader execution, render-target writes and
readback; do not repeat an unchanged black-frame trial or claim global driver
coverage. No cube run while the red-clear gate remains failed.
