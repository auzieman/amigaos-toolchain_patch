# Systemic Mesa/ACO boundary review — 2026-11-09

This pass broadens the review from the last failing command to shared producers
and consumers across RadeonSI, ACO, GPU command memory and CPU response reads.
Target remains A1222 PPC32 BE SPE / Polaris11, pinned Mesa25.0.7 and6.12.113.
No base refresh, ABI change, SDK promotion, global memory swap or driver reload.

`boundary-ledger.json` pins source hashes and owning code for PM4 construction,
main/chained/preamble publication, executable upload, compiler mode packing,
descriptors, constant buffers, general vertex buffers, blitter user-SGPR data,
color-format endian policy, image staging, raw mappings and completion reads.
It is an audit ledger, not a claim every path has hardware coverage. Existing
shared typed conversions must be retained; source anchors alone do not prove
that every caller supplies the right representation. Inactive userqueue fence
reads remain separately unresolved. Compute/video contracts are not accepted
by a GFX-only test.

## ACO shared packed-mode mismatch reproduced

`aco::float_mode` says it matches the GPU MODE register, but its native C++
bitfield declaration and overlaid uint8_t are little-endian-layout dependent.
The same fields produce a different numeric value on BE before any byte upload.
For example, rounding nearest and preserving denorms for both widths should
produce0xf0, but the old PPC type produces0x0f. This is a packed scalar layout
defect, not a request to byte-swap all shader data.

`check-float-mode.py` extracts the actual enums/type from pinned aco_ir.h,
compiles old/candidate for native x86 and actual SPE C++ SDK8.5, and runs PPC
under QEMU e500v2. All256 combinations exercise field->val and val->field plus
round/denorm nibble aliases. OldBE differs; candidateBE matches unchangedx86.
Patch0006 reverses declaration order only on BE, including the nibble alias,
using the existing endian abstraction. Other CPU-only compiler bitfields are
not blindly reversed: numeric mask/shift helpers and opaque object state have
different contracts.

Source connects this type to seven ACO config.float_mode producer sites and
RadeonSI shader resource-register packers (including PS S_00B128_FLOAT_MODE).
The correction therefore covers the common mode type across shader stages;
it is not one per-shader instruction substitution. This test does not compare
complete compiled shaders or establish the black-frame cause.

## Isolated build and physical outcome

Private reflink from the previous corrected Mesa candidate preserves IB
serialization, ACO executable upload, GBM formats and LE64 fence decoding.
R730 build:2CPUs/4GiB, SDK/sysroot read-only, network disabled; all41 compile/link
steps and install pass. Source/patch/build receipts retained. No laptop build.
Final private libgallium SHA256:
08e0249311adcc3cf3e59d231ff22c7695fa3814030509cde8c72ae12abe2104.
Copied and hash-verified on the running013 board; pre-mode library retained.

Physical clear still fails: RadeonSI/ACO renderer, correct native float API
bits, complete framebuffer, serialized312/160DW GFX IBs, but zeroRGBA/exit255.
Fast-clear and compute-clear leave the mask for graphics drawing. VT1 restored,
SSH and taint0 preserved. User's VLC view is running; render-only VT switching
shows black rather than directly scanning out the render target. No cube,
GPU reset/reload or claim of hardware GL success.

The systemic hypothesis remains productive, but source-proven fixes are not
by themselves proof of the remaining fault's cause. Next qualification should
compare complete shader/config/descriptor output and GPU render-target versus
staging/readback contents as a connected path. Preserve correct existing LE
helpers and the physically working explicitLE+fetch0 command contract.
