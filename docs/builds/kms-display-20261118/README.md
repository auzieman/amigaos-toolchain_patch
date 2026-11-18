# Polaris11 big-endian KMS/GBM display path on kernel 020 (#35) - 2026-11-18

A1222 (P1022, e500v2), RX 550 (Polaris11) on HDMI-A-1, kernel 6.12.113-tabor-e2e-020 (019 +
0038; the display patch is #49's 0037), amdgpu loaded with `polaris11_le_user_ib=1`.
Userspace: the tabor3 SPE bundle `/opt/a1222-gl-spe3` with the linux-be Mesa 26.2.3 libraries,
including the big-endian XRGB8888/ARGB8888 GBM visuals (libEGL `e0ae05ae...`, libgallium
`b0b38d56...`). The monitor's preferred mode is 1920x2160@60.

## The client

`kmstest3.c` is the #49 `kmstest` with options set through the environment. It takes the
connected connector, renders with radeonsi into a GBM scanout surface, and registers each BO
with ADDFB2 in the BO's own format. It shows four quadrants drawn with scissored clears, then
page-flips a depth-tested cube.

- `KMS_FORMAT`: the surface format, taken from the EGL window configs with that visual.
- `KMS_MODE=WxH@R`: the mode to set.
- `KMS_NORESTORE=1`: exit without restoring the CRTC.

It prints the GL readback and the scanout BO's raw bytes for each quadrant, the cube's frame
rate and flip errors, and the result of `DRM_CLIENT_CAP_UNIVERSAL_PLANES` and
`DRM_CLIENT_CAP_ATOMIC`. It is built by `build-kmsprobe.sh` with the GCC14 SPE SDK; binary
`939f5c75...`.

## Results

**Plane and capabilities** (`hw/modetest-020.txt`, `hw/kms3-xr24-020.txt`). The primary plane
lists `BX24 BA24 XR24 AR24`. Universal planes is accepted. `DRM_CLIENT_CAP_ATOMIC` returns
EOPNOTSUPP: `dce_v11_0` (the non-DC display path this board uses) has legacy modesetting only.
A client that requires atomic KMS cannot drive this display. Xorg modesetting and clients with
a legacy fallback can.

**Formats and modes** (`kms-matrix.sh`, `hw/kms-matrix-020.txt`). Each run is 1 s of bars and
120 cube frames:

| mode | XR24 | BX24 | AR24 | BA24 |
|---|---|---|---|---|
| 1920x2160@60 | 59.31 | 59.27 | 59.31 | 59.29 |
| 1920x1080@60 | 59.37 | 59.31 | 59.34 | 59.31 |
| 3840x2160@30 | 29.83 | 29.83 | 29.83 | 29.83 |
| 1280x720@60 | 59.32 | 59.32 | 59.30 | 59.32 |
| 1920x1080@120 | 116.58 | 116.62 | 116.55 | 116.62 |

- The values are fps. Every run had 0 flip errors, and taint stayed 0 throughout.
- Each run carries a fixed start-up cost of about 30 ms, which shows in the short 120 Hz runs.
  1200 frames at 1920x1080@120 give 119.63 fps.
- Raw bytes of the red quadrant: XR24 `00 00 ff 00` and AR24 `00 00 ff ff` (little-endian
  B,G,R,X/A); BX24 `00 ff 00 00` and BA24 `ff ff 00 00` (host order X/A,R,G,B).
- XB24 does not start: Mesa offers no XBGR8888 window config on GBM, and the plane does not
  list it either.

**On screen** (`hw/kms-eye-020.txt`). XR24, AR24 and BX24 each showed the quadrants for 15 s,
then the cube. In all three the user saw red top-left, green top-right, blue bottom-left, white
bottom-right, and normal cube colours. So the GL-rendered little-endian XRGB8888/ARGB8888 path is
correct on screen, not only the CPU-filled buffers that #49 checked.

**Console handoff** (`kms-handoff.sh`, `hw/kms-handoff-020.txt`). Before any client ran, the CRTC
showed fbcon's framebuffer 57 at 1920x2160. It showed the same after each of these:

- a client exited without restoring the CRTC;
- a client was killed with SIGKILL while page flipping;
- a client exited without restoring after setting 1280x720.

Taint stayed 0.

## Not covered

- Xorg modesetting/glamor, a Wayland compositor, and a VT switch through `VT_SETMODE`. The
  rescue root has no X server, compositor or getty.
- 16 bpp formats (see #49: the legacy 16 bpp host format is not in the plane list).
