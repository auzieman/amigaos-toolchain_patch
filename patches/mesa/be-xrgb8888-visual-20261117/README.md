# XRGB8888 GBM visual on big-endian hosts (#35, Mesa side)

`0001-egl-gbm-xrgb8888-visual-on-big-endian.patch`, against Debian mesa 25.0.7
with `debian/patches/series` applied. Apply with `patch -p1` from the source root.
Mesa MIT licence; this does not relicense anything.

The base is the published 25.0.7 source. The earlier GBM/KMS format changes in
your tree are not in this repository, so I have not checked this patch against them.

## The bug

- **Word-order aliases.** On a big-endian host, `PIPE_FORMAT_BGRA8888_UNORM` and
  `BGRX8888_UNORM` in the `dri_fill_in_modes` list are aliases for A8R8G8B8 and
  X8R8G8B8 (memory A,R,G,B). GBM calls these BGRA8888/BGRX8888.
- **Missing order.** `GBM_FORMAT_ARGB8888`/`XRGB8888` map to B8G8R8A8/B8G8R8X8
  in `gbm_dri_visuals_table`. No config has that memory order, so EGL on GBM
  offers no XRGB8888 visual.

The patch makes two changes, both under `UTIL_ARCH_BIG_ENDIAN`:
- **`dri_screen.c`:** appends `PIPE_FORMAT_B8G8R8A8_UNORM` and `B8G8R8X8_UNORM`
  after every existing format, so no existing config changes place.
- **`egl_dri2.c`:** `dri2_match_config` keeps DRM-platform configs apart by
  native visual. The two channel orders have identical EGL attributes, so
  without this the second is merged into the first and dropped.

Scanning out the little-endian XRGB8888 framebuffer also needs the kernel to
accept it through ADDFB2: amdgpu patch 0037 in #49. On a kernel without it,
ADDFB2 refuses the format. The legacy ADDFB fallback is host-order, so it
would show swapped colours.

The same code is in Mesa 26.2.3.

## Evidence

**25.0.7, compile only.**
- The patch applies to the replica's 25.0.7 tree and builds incrementally with
  the GCC14 SPE SDK (tabor2), with no warnings.
- `libgallium-25.0.7.so` and `libEGL.so.1.0.0` change.
- **Runtime not tested on 25.0.7.** I tried a softpipe run on the A1222 with
  `GBM_ALWAYS_SOFTWARE=1`. It crashed with a NULL call inside 25.0.7's GBM before
  any config was listed, and it crashed the same way unpatched, so the crash is
  not from this patch. I have not investigated it.

**Same change on a Mesa 26.2.3-based big-endian Linux tree, A1222.** Setup:
Polaris11 RX 550, radeonsi, kernel 019 (#49), tabor3 SPE userland.
- **Configs:** GBM EGL configs went from 200 to 256 and now include XR24.
- **Scanout:** a GBM XRGB8888 surface renders and is registered through ADDFB2
  as XR24.
  - The BO bytes are little-endian: red is `00 00 ff 00`.
  - Colour bars were checked by eye on the monitor and were correct.
  - The cube ran 600 flips at 59.68 fps with no flip errors.
- **Regression check:** dEQP GLES2 (surfaceless) gave 17041 Pass and 0 Fail,
  the same per case as without the patch.

**Not tested:** X11 and Wayland. The `dri_screen.c` change adds the two configs
on every platform, but the `egl_dri2.c` separation applies only to
`_EGL_PLATFORM_DRM`. On X11, `dri2_match_config` already compares native visuals
for configs with alpha.
