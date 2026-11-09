# Submitted GPU buffer boundary audit

2026-11-09. Follows the source path beyond individually checked words. Canonical
Mesa25.0.7 candidate and pinned Trixie/SDK environments from the preceding
command comparison. No new board access, deployment, render, reset or reboot.

## New measured payload gap

Upstream standard Piglit sanity.shader_test (RGB) uploads rectangle coordinates
(-1,-1),(1,-1),(1,1),(-1,1). The submitted storage contains native CPU float32
bytes: x86 LE and SPE BE. All eight words are reversed. Under a GPU LE float32
load, the SPE bytes produce values near zero rather than +/-1. This is separate
from the now-LE vertex-descriptor metadata.

The source path is si_buffer_transfer_map / native byte copy / unmap, then
si_nir_lower_vs_inputs::load_vs_input_from_vertex_buffer and
opencoded_load_format. For dword input formats the latter issues
nir_load_buffer_amd, splits channels and interprets floats without an explicit
BE scalar decode. The four compiled RGB shader uploads have identical executable
bytes and matching scalar configuration across hosts; differences are confined
to the previously classified five UMR markers. No observed RGB shader
instruction differences implement a CPU-specific decoder.

This reproduces a missing-contract problem for native CPU vertex input under
these load semantics. It does not establish the cause of the attribute-free
point hang: that draw has no such inputs. No hardware RGB or point test followed.

## Broad capture and scope

A default-off TABOR_BO_CAPTURE_DIR hook lives exclusively in the upstream no-op
DRM backend, not in the installed board driver. At CS submission it snapshots
up to65536 bytes per active GEM handle from the backend's backing memfd. It adds
no GPU execution or format conversion. The capture includes live buffer prefixes
and may include unused allocation padding; differences are not automatically
consumed fields. All raw bounded snapshots, IBs and shader captures are retained
in evidence/bounded-captures.tar.gz, with per-prefix hashes and comparisons in
buffer-comparison.json.

| Workload | Allocation snapshots | Identical prefixes |
| --- | ---: | ---: |
| Standard constant point | 11 | 8 |
| Standard RGB sanity | 60 over5 submissions | 47 |

Other differing prefixes include native-PM4 words, expected because the upstream
Polaris12 profile leaves the Polaris11-only LE selector inactive; UMR markers;
and point BO9 offsets0x98/0x9c whose consumed meaning is not yet classified.
The latter may be unused/uninitialized data: it is explicitly unresolved, not
masked out as harmless or asserted to be the hang cause. Handles are checked
for equality across runs; no address or allocation remapping is performed.

The no-op backend cannot execute draws or DMA. Zero pixel probes are expected,
not test acceptance. Prefix snapshots do not validate later pages, GPU-side
copies, coherence, shader fetch, draw execution or image readback. Polaris12 is
a GFX8 sibling profile, not physical boardPolaris11.

## Connected producer/consumer ledger

| Object | Producer/publication | Consumer | State |
| --- | --- | --- | --- |
| Main/chained/preamble GFX IB | native construction, shared final serializer | kernel013 LE+swap0 CP fetch | Existing opt-in fix; physical8DW passes, finalized400DW construction comparison retained |
| Executable shader | ACO native words, fixups, shared LE upload | instruction fetch | Point and all4 RGB executable captures match x86; hardware fetch not proven |
| Ordinary constants | si_upload_const_buffer -> util_memcpy_cpu_to_le32 | scalar buffer loads | Existing conversion; preserve |
| Generic descriptors | si_upload_descriptors -> util_memcpy_cpu_to_le32 | descriptor fetch | Existing conversion; preserve |
| Vertex descriptor tail/divisors | shared tail and divisor publications | vertex fetch metadata | New0008 fix built/offline-checked, not deployed |
| CPU vertex payload | raw native byte copy | raw/typed NIR input loads | Measured RGB32-bit input contract gap |
| GPU-generated vertex payload | legacy streamout values -> nir_store_buffer_amd | future vertex input/readback | Must be coupled to any shared fetch change |
| Surface state | ac_colorformat_endian_swap -> CB_COLOR_INFO.ENDIAN | colour export/layout | Existing BE hardware mode; sole finalized400DW state difference |
| Query responses | GPU status/counters -> mapped decode | CPU arithmetic | New0007 built/offline-checked; no physical query acceptance |
| Completion | GPU LE64 fence -> util_le64_to_cpu | CPU wait | Existing fix, separate from native ioctl results |
| CPU image readback | texture transfer/layout staging | native GL pixels | Still requires format/layout tracing; no blanket buffer swap justified |

## Fix constraints from following the complete path

Changing every input-fetch word would also affect GPU-generated buffers.
ac_nir_prerast_utils::ac_nir_emit_streamout gathers output values and publishes
raw nir_store_buffer_amd vectors; those writers must share the intended buffer
contract. Scalar32, scalar16/64, byte attributes, packed formats, and arbitrary
shader-storage data cannot receive the same blind whole-word swap. GPU internal
rings and already-LE constant/descriptor storage must remain distinct.

No speculative vertex decoder was committed in this pass. The next conversion
candidate must explicitly pair typed vertex reads with affected producer paths,
preserve byte attributes/packed formats, and qualify transform-feedback reuse.
The measured native32 CPU-input case supplies a concrete byte oracle. It cannot
be offered as a fix for the no-attribute point hang.

Kernel review also confirms GFX8 clear-state-buffer words already use upstream
cpu_to_le32, RLC firmware list entries decode through le32_to_cpu before MMIO,
and MQD publication uses the existing LE helper. The raw VGPR/SGPR initialization
shader arrays in gfx_v8_0_do_edc_gpr_workarounds are guarded for CARRIZO and are
inactive on Polaris11; do not patch an inactive path as a claimed fix.

## Validation/provenance

Both full incremental builds pass in the existing isolated2CPU/4GiB R730 jobs.
A first instrumentation build lacked util/u_atomic.h and failed; its log is
retained. The explicit include corrected it before successful SPE/native builds.
Standard tests and compiler settings were unchanged. Offline shim time64 adapter
is the previously documented qualification-only adapter, never board-deployed.
Source before/after hashes, patch, launch/build/run receipts and complete bounded
capture prefixes are retained. Python scripts pass syntax validation.

This is an audit/evidence checkpoint, not a new accepted GL candidate. The real
A1222 remains at the prior passing cached/USWC control checkpoint. Its previously
working2D console and fractal are not treated as hardware3D acceptance.
