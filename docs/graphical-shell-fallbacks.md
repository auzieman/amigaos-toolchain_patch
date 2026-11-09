# A1222 graphical shell and recovery contract

The kernel-up target is a readable local login terminal, then an X11/E shell
that remains usable without GPU rendering acceleration, followed by accelerated
Radeon/Mesa/compositing. Profile: profiles/images/a1222-graphical-shell.json.
This is a required capability plan, not a claim the image currently has it.

2026-11-08: candidate007 now has user-confirmed readable HDMI fbcon and a correct
CPU/SPE framebuffer fractal. The user prioritizes software X11/E without waiting
for hardware GL. Actual kernel/input readiness and prepared unaccelerated Xorg
profiles are recorded in
[the desktop restart](builds/software-desktop-restart-20261108/README.md).
The configured Debian desktop root and X/E execution remain separate open gates.

## Display initialization and rendering are separate

The pinned upstream7.3 drivers/video/fbdev/Kconfig makes FB_VESA depend on X86.
The standard PC VESA BIOS path is therefore not our PPC fallback. The source
also contains DRM_SIMPLEDRM, whose help requires hardware initialized by the
bootloader plus a real device-tree framebuffer handoff. Do not fabricate a node
from guessed PCI BARs. Existing7.3 hardware config has DRM fbdev emulation,
VT/fbcon and AMDGPU, but simpledrm is disabled and no usable firmware framebuffer
has been accepted. Compiling a fallback driver alone does not establish one.

Useful paths to qualify:

1. A verified firmware framebuffer retained through simpledrm can supply fbcon
   before a native KMS handoff, when this board/firmware actually provides it.
2. Successful Radeon display initialization can provide KMS and fbcon even
   before accelerated rendering is accepted. Xorg modesetting without glamor
   is then a candidate software path; it still requires functional scanout,
   buffers, memory mappings and correct byte order.
3. Where a working /dev/fb0 exists, target-built Xorg fbdev is another candidate
   for a plain X terminal. It cannot create a missing framebuffer or revive a
   failed GPU by itself.

Select safe standard modes only from a verified connector/monitor mode list.
Neither nomodeset, a forced resolution nor software GL substitutes for display
initialization. Preserve SSH recovery independently. VNC/Xvfb may aid remote
recovery but do not satisfy the physical-screen acceptance gate.

## Build/install acceptance

Preserve normal Debian package installation, getty/service setup, PAM, udev,
D-Bus/session state, permissions, fonts and input dependencies. Candidate seeds
are resolved and rebuilt through the existing frozen apt/sbuild pipeline after
modern SPE compiler/runtime qualification; this is not a second dependency
solver or authorization to fetch arbitrary current package versions.

First show a login/getty on real hardware. Then run an X terminal and verify
text, moving/overlapping windows and repaint, followed by a software-rendered
Enlightenment session. Test Mesa software rendering separately and record the
actual renderer; softpipe is a candidate that does not require assuming LLVM
JIT support on SPE. Hardware GL/compositing and resource tuning are later gates.
QEMU's selected virtual display device gets its own test record; it is not an
RX560 hardware surrogate. Keep /boot.scr and a verified kernel rollback path.

Sources:
- https://www.kernel.org/doc/html/latest/fb/vesafb.html
- https://gitlab.freedesktop.org/drm/amdgpu/kernel/-/blob/5349075eac146ae0511d8929fc24451e4d9a4b7e/drivers/gpu/drm/sysfb/Kconfig
- https://gitlab.freedesktop.org/drm/amdgpu/kernel/-/blob/5349075eac146ae0511d8929fc24451e4d9a4b7e/Documentation/devicetree/bindings/display/simple-framebuffer.yaml
- https://packages.debian.org/trixie/xserver-xorg-video-fbdev
