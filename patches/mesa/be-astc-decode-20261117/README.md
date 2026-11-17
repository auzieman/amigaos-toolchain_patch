# ASTC decode on big-endian hosts

`0001-astc-decode-le-words-on-big-endian.patch`, against Debian mesa 25.0.7
with `debian/patches/series` applied. Apply with `patch -p1` from the source root.
Mesa MIT licence; this does not relicense anything.

## The bug

Polaris has no ASTC sampler, so the state tracker decodes every ASTC upload on
the CPU through `_mesa_unpack_astc_2d_ldr` (`src/mesa/main/texcompress_astc.cpp`).

- `Decoder::decode` copies the 16-byte block into `uint32_t data[4]`.
- `InputBitVector::get_bits()` then takes bit n from `data[n / 32]` bit `n % 32`.
- So the block is read as a little-endian 128-bit number, and on a big-endian
  host every word is byte-reversed. Every block decodes wrong.
- The output side writes bytes and is correct.

The patch loads each word with `util_le32_to_cpu` after the copy, which is a
no-op on little-endian hosts. The same code is in Mesa 26.2.3.

## Evidence

**25.0.7, compile only.** The patch applies to the replica's 25.0.7 tree and
builds incrementally with the GCC14 SPE SDK (tabor2) with no warnings, and
`libgallium-25.0.7.so` changes. It was not run on hardware: an unpatched 25.0.7
radeonsi does not run on this kernel without the Polaris BE series.

**Same change on a Mesa 26.2.3-based big-endian Linux tree, A1222.** Setup:
Polaris11 RX 550, kernel 019 (#49) with `polaris11_le_user_ib=1`, tabor3 SPE
userland. Results:
- dEQP GLES3: all 1288 ASTC fails pass (`texture.wrap.astc_*` and others).
- The 44 ASTC API and upload cases that already passed still pass.
- Full GLES3 mustpass, without `builtin_functions.precision`: 43312 Pass, 21 Fail.
  Before this and the other two fixes it was 1321 Fail. The 21 are 8 `fract`
  (#48) and 13 MSAA depth/stencil cases, a separate HTILE issue.
- Kernel taint stayed 0.
