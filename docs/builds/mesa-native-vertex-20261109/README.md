# Native vertex data and legacy streamout conversion candidate

2026-11-09. Implemented, built and offline-qualified. Default off. Not deployed
to the A1222; no physical test, driver reload, reset or boot change in this pass.

## Shared conversion implementation

Patch0012 covers eight source files. On big-endian GFX8,
TABOR_NATIVE_VERTEX_DATA=1 enables a native CPU vertex-buffer contract:

* Vertex element creation retains complete format metadata and puts it in the
  shader key even for formats that normally need no fetch workaround.
* All enabled vertex input formats use the existing open-coded lowering path.
  Scalar channels load separately. A shared NIR helper reverses each16/32-bit
  scalar before numeric conversion; byte channels remain unchanged. Double
  inputs decode two32-bit words and reorder halves before the existing64-bit
  reconstruction. Packed word formats decode their scalar container before
  existing field extraction, scaling and swizzling.
* The same scalar helper encodes legacy streamout values at the external-buffer
  store boundary. VS/TES and GS-copy callers pass gfx_level to the shared writer.
  CPU-only output state and GPU-internal GS rings remain unchanged.
* The optional draw_vertex_state/display-list fast-path capability is withheld
  only for this opt-in. Its upstream implementation asserts fix_fetch_always==0;
  the normal draw path carries the format key needed by decoding. This preserves
  normal rendering rather than bypassing the conversion in a second entrypoint.

The patch preserves CPU vertex bytes in place. GPU instructions interpret those
native-format API bytes correctly instead of indiscriminately modifying an
untyped buffer. It does not convert command metadata, already-LE descriptors,
ordinary constant uploads, or arbitrary raw byte arrays again.

## Verification

Both SPE and native Mesa builds/install pass with the frozen source baseline,
accepted SPE C++SDK8.5 and pinned native Trixie environment. R730 jobs are capped
at2 CPUs/4GiB. SDK and dependency stage remain shared read-only. Native reference
is compiler-output qualification, not another target archive.

| Check | Result | Actual scope |
| --- | --- | --- |
| Scalar encode/decode | 20,480 cases per x86/SPE host pass | Actual helper extracted; integer builder operations mocked;8/16/32/64 and double-word pairing; old BE model mismatches12,275 cases |
| Actual NIR helper | 128 cases pass | Mesa NIR builder and constant folder, no GPU |
| Actual vertex-format lowering | 190 cases pass | Extracted opencoded_load_format, ufN_to_float and actual fix_fetch union; real NIR builder/folder; scalar/packed/reversed formats; modeled LE memory reader and controlled native predicate |
| Actual legacy streamout lowering | 16 cases pass | Extracted whole writer and get_output_and_type; real NIR builder/folder;32-bit components,1–4 channels, dense/gapped stores; controlled native predicate |
| x86 standard RGB regression | Unchanged | All four executable uploads and scalar metadata byte-identical to prior reference, even with option requested |
| SPE option-off RGB regression | Unchanged | All four uploads/configurations byte-identical |
| SPE option-on RGB | Vertex shader changes52 ->160 bytes | Real driver/compiler emits scalar-load/decode code; fragment and compute uploads/configs remain identical |
| SPE attribute-free point | Unchanged | All three uploads/configurations byte-identical with option enabled; **this does not fix that hang** |

No-op runs deliberately fail pixel probes because no GPU commands execute.
Their upstream Polaris12 profile is a GFX8 sibling, not physical Polaris11.
Kernel013 LE-IB pairing is not exercised by that profile; previous physical
command controls and publication traces remain separate acceptance evidence.
Actual NIR checks are more than an arithmetic mock, but memory endpoints are
still modeled, and constant folding does not validate GPU instruction execution.

## Preflight caught an incomplete first draft

The initial forced fetch path read default/omitted format metadata for ordinary
formats. Its compiled vertex shader lost its buffer load. Full-upload inspection
caught this before any deployment. The completed patch fixes the producer/key
path too; final option-on shader contains the loads and decoding instructions.
The later entrypoint audit found the incompatible display-list fast path and
added the opt-in capability guard. Final source/artifact hashes, builds and
regressions include both corrections. Initial captures010/011 remain on R730;
final qualified runs are015 (off RGB),016 (on RGB),017 (on point).

Private build isolation initially requested unsupported reflinks. The incomplete
task-owned copy was removed, and only source/build state was ordinarily copied;
the large dependency stage and SDK were shared read-only. No shared source, SDK,
board runtime or user data was overwritten.

## Remaining limits / hardware scope

This is a diagnostic candidate for native CPU vertex input plus legacy32-bit
streamout interoperability. Arbitrary SSBO/image/compute-generated vertex
buffers are not covered: their producers still need an explicit compatible
contract. Lowered64-bit transform-feedback ordering and physical8/16/packed/
64-bit fetches are unqualified. NGG is outside this GFX8 gate. Do not enable it
as a universal GPU-buffer translator or claim every3D interface is converted.

MESA_SHADER_CACHE_DISABLE=true is required for this diagnostic: the environment
option is not a production cache identity for every streamout variant. The
existing TABOR_POLARIS11_LE_IB=1 and kernel013 polaris11_le_user_ib=Y contract
remain required for a real Polaris11 GFX trial. Do not deploy the offline DRM
shim or its time64 adapter to the board.

The previously stalled standard point draw has no vertex inputs, and its code
is unchanged. Its timeout remains a separate unresolved execution boundary;
this patch is not offered as its root-cause fix. Before any physical trial,
retain the clean-boot/module/root/hash preflight and off-board logging. No
hardware trial was launched merely because compilation or no-op capture passed.

## Reproduction and retained evidence

Private candidate:
/srv/data1/tabor-build/linux-live-001/work/native-vertex-contract-20261109-001.
Parent: mesa-3d-contracts-20261109-001 with preceding patches through0011.
Preparation order is prepare.py, finish-metadata.py, guard-fastpath.py; then
bounded SPE/native builds, checks and final offline runs. Existing scripts use
historical container mount paths consistently and share the old dependency
stage read-only. The canonical patch is evidence/0012-*.patch.

Evidence includes final patch, all modified source hashes, libgallium hash,
immutable build images/mounts, build exits/logs, actual helper/format/streamout
checks, regression manifest and complete tiny final shader uploads. Earlier
intermediate run scripts/receipts are kept for traceability, not acceptance.

## Stage-only deployment authorized and verified

User explicitly requested staging and no actual onscreen renders. Candidate is
installed separately at /opt/tabor-native-vertex-20261109 on A1222 kernel013.
All28 regular files match the qualified assembly manifest; the native dynamic
loader's --list mode resolves the standard shader runner's dependencies without
running its main function or shared-library initializers. No EGL context, shader
compile, DRM ioctl or render workload was launched on the board.

No runtime device/proc/sys/run interfaces were mounted. The no-op DRM shims and
offline time64 adapter are excluded. Existing runtime, module, boot script and
default environment are untouched. Root was briefly remounted writable for the
new directory, then synced and restored read-only. Final boot ID matches the
preflight (178dae6d-2771-4fa4-8709-a91f770b0712), taint0, amdgpudrmfb registered.
Staging is not rendering acceptance. User's no-render instruction remains in
force until they authorize a later trial.

See staging/ for source/runtime receipt, all target hashes, loader listing,
mount restoration and final state. assemble-live.py and stage-live.py reproduce
the stage-only process; they never bind devices or execute the graphics tests.
