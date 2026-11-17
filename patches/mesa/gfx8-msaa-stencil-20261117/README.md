# GFX7-8 MSAA stencil sampled with the wrong bank layout

`0001-ac-surface-gfx8-stencil-macro-mode-via-db-copy.patch`, against Debian
mesa 25.0.7 with `debian/patches/series` applied. Apply with `patch -p1` from
the source root. Mesa MIT licence; this does not relicense anything.

This one is not a big-endian bug. It is in radeonsi's GFX7-8 surface setup
and should show on any host with a Polaris card.

## The bug

On GFX7-8 the DB applies the depth plane's macro tile mode (bank width, bank
height, macro tile aspect, from `DB_DEPTH_INFO`) to both depth and stencil.
The texture unit gets only a tiling index and derives the stencil plane's
macro tile mode from it.

- `gfx6_compute_surface` (`src/amd/common/ac_surface.c`) keeps the two equal
  (`matchStencilTileCfg`) only for mipmapped Z/S and Stoney.
- With TC-compatible HTILE on an MSAA surface, depth takes a large tile split.
  On Polaris11, 4x Z24S8:
  - depth: tiling index 4, macro mode 4 (bank height 1, aspect 2);
  - stencil: tiling index 1, macro mode 1 (bank height 4, aspect 4).
- No stencil tiling index can reach depth's macro mode here. If addrlib is
  asked to match the two, it turns TC-compatible HTILE off instead.
- So when stencil is sampled, for example by the stencil resolve in
  `glBlitFramebuffer`, the texture unit reads with different bank parameters
  than the DB wrote with, and the stencil comes back scrambled.

The patch sets `stencil_adjusted` when the two macro tile modes differ. That
clears radeonsi's `can_sample_s`, so stencil sampling goes through the DB->CB
copy, which reads the stencil with the DB's own parameters. TC-compatible
HTILE and the surface layout are unchanged. The same code is in Mesa 26.2.3.

## Evidence

**25.0.7, compile only.** The patch applies to the replica's 25.0.7 tree and
builds incrementally with the GCC14 SPE SDK (tabor2) with no warnings, and
`libgallium-25.0.7.so` changes. It was not run on hardware: 25.0.7 on this
board offers no EGL config with `EGL_OPENGL_ES3_BIT`, so dEQP GLES3 does not
start.

**Same change on a Mesa 26.2.3-based big-endian Linux tree, A1222.** Setup:
Polaris11 RX 550, kernel 019 (#49) with `polaris11_le_user_ib=1`, tabor3 SPE
userland, dEQP GLES3 with pbuffer 256x256 and `rgba8888d24s8ms0`, all on one
boot. Results:
- The 13 failing cases pass:
  `fbo.msaa.{2,4,8}_samples.{depth24_stencil8,depth32f_stencil8,stencil_index8}`
  and `fbo.invalidate.{whole,sub}.unbind_blit_msaa_{color,depth}`.
- `AMD_DEBUG=tex` still shows `tc_compatible_htile=1` on the MSAA surface.
- The 866 `fbo.{msaa,invalidate,blit,depth,stencil}` cases: 841 Pass, 13 Fail,
  12 NotSupported before; 854 Pass, 0 Fail, 12 NotSupported after.
- 1523 other GLES3 depth/stencil cases (`fragment_ops.depth_stencil`,
  `texture.shadow`, the depth/stencil formats and others) give identical
  per-case results before and after.
- Kernel taint stayed 0.

How it was narrowed:
- Turning TC-compatible HTILE off on MSAA fixes all 13.
- Decompressing before sampling fixes only the 4 invalidate cases.
- The `ac_compute_surface` layout is identical between an x86 build and the
  big-endian SPE build, fed the board's tile registers.
- The live `GB_TILE_MODE`/`GB_MACROTILE_MODE` registers match the tables the
  kernel reports.
