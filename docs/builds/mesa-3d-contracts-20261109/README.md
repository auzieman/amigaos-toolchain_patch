# Mesa 25.0.7: 3D publication and response contracts

2026-11-09. Private source candidate; not deployed or hardware accepted.

This pass follows producers, publication boundaries and consumers rather than
adding conversions to individual GPU commands. The accepted SDK remains the
SPE C++ reference 8.5, not the unqualified GCC 14 userspace SDK. Native x86
compiler-output qualification uses the frozen Trixie snapshot
20261102T220000Z, libc 2.41-12+deb13u4. No target archive version drift.

## Implemented fixes

`evidence/0007-radeonsi-query-memory-byte-contract.patch`:

* Publish unused render-backend status markers as LE32.
* Decode mapped LE32 query counters before native arithmetic.
* Decode mapped LE64 timestamp and performance-counter results.

`evidence/0008-radeonsi-publish-vertex-metadata-le.patch`:

* Publish memory-resident vertex descriptor tails as LE32 after both normal
  draw construction and draw_vertex_state copying converge.
* Publish instance-divisor factor tables with the existing CPU-to-LE helper.
* Keep inline SGPR words native until existing PM4 publication; preserve native
  CPU caches and allocation padding. No blanket swapping of arbitrary payloads.

Both changes preserve the existing x86 paths. They cover shared publication and
response paths, but cannot explain a point draw that has no vertex attributes
and no application queries.

## Verification

The full SPE Mesa candidate compiled and installed successfully (28 incremental
steps). `3d-build.exit` is 0. This validates compilation, not GPU behavior.

Query fixtures execute extracted source functions: 48 preparation cases and
4096 response scenarios per architecture. Vertex fixtures exercise the actual
publication block and existing helper: 198 descriptor-count/inline combinations
and 32 divisor table sizes per architecture. Old BE negative controls fail the
known LE-byte oracle; unchanged x86 and corrected BE pass. GPU writers/readers
are modeled. The full draw function is not executed by the vertex fixture.

## Complete shader publication comparison

The same upstream Piglit constant-point shader was compiled with this candidate
on native x86 and QEMU e500v2 SPE, using upstream Mesa's no-op DRM backend and
its Polaris12 profile. This is a GFX8 sibling profile, **not the actual
Polaris11 board**. The backend executes no GPU commands; both pixel probes
therefore fail, as expected. These failures are not rendering acceptance.

Actual complete uploaded buffers and native scalar metadata are retained under
`evidence/offline-*-captures*`; comparison is in
`evidence/shader-upload-comparison.json`.

* Vertex upload: 52 bytes; executable bytes match.
* Fragment upload: 68 bytes; complete upload matches byte for byte.
* Compute upload: 108 bytes; executable bytes match.
* SGPR/VGPR counts, float_mode (192), LDS and scratch metadata match.
* Vertex and compute tails differ in exactly five native UMR disassembler end
  markers (`0xbf9f0000`). `aco_assembler.cpp::emit_program` records exec_size
  before appending these markers. There are no constants or scratch in these
  shaders. This mismatch is retained explicitly; complete hashes do not match.
  It is **not established as the GPU hang cause**, and no speculative marker
  rewrite was applied.

The diagnostic capture hook is default off (`TABOR_SHADER_CAPTURE_DIR`). It
copies upload bytes on the CPU before DMA/unmapping. It is instrumentation,
not a GPU conversion fix. Existing post-relocation executable serialization
and the ACO float-mode correction remain in the candidate.

The upstream no-op shim needed an offline-only Trixie 32-bit time64 ABI adapter:
libdrm calls `__stat64_time64`, `__fstat64_time64`, `__ioctl_time64` and
`__fcntl_time64`, which otherwise bypass shim intercepts. The adapter bridges
stat layouts through typed scalar fields and routes DRM ioctl/descriptor
operations to existing shim hooks. Do not deploy it to the board or use it for
arbitrary time-bearing ioctl payloads. Failed setup attempts are not GPU tests.
The successful SPE run is 006. PrivateDevices prevented real device access.

## Reviewed boundaries and unresolved work

* Kernel GFX8 clear-state-buffer construction already uses upstream
  cpu_to_le32. Do not convert twice.
* The existing MQD publication patch already writes LE words before queue
  mapping. Do not add a second conversion.
* Generic descriptors/constants already have LE publication paths. Bindless
  updates use WRITE_DATA through shared IB serialization.
* Arbitrary vertex payloads need a producer-aware contract: CPU uploads and
  GPU-generated/transform-feedback buffers cannot blindly receive the same
  byte swap. No such speculative patch was added here.
* The physical explicit-LE allocated-buffer write passed with USWC mapping.
  Cached LE+swap0 has not yet been equivalently qualified. Thus cache visibility
  and address/queue publication remain open alongside encoding, not excluded.
* This comparison does not validate PM4 stream equivalence, DMA visibility,
  actual shader fetch, texture layout, or hardware GL execution.

No board render command, module reload, manual reset, boot change, or deployment
was performed in this pass. The prior standard point test triggered GPU
watchdog recovery and VRAM loss; a clean boot is required before the next
qualified hardware trial. 2D success remains established, hardware GL remains
unresolved. These new query/vertex metadata fixes alone do not justify repeating
that same attribute-free point test as though its cause were fixed.

## Reproduction

Scripts use the private R730 work directory
`/srv/data1/tabor-build/linux-live-001/work/mesa-3d-contracts-20261109-001`.
Run preparation/check/build scripts in their recorded order, not against the
shared SDK or a running board. Heavy builds are bounded to 2 CPUs / 4 GiB.
Native build is a compiler-output reference only, not an amd64 target archive.
`launch-*.json` records immutable image and mount arguments; native package
versions and successful build exits are retained. The native run image is a
private commit of the completed, pinned native qualification environment.
