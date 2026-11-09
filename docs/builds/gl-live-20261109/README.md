# Physical OpenGL cube, kernel011

An isolated32,129,482-byte X/GL runtime assembled from the prior source-pinned hardware-x-002 stage, accepted Trixie libc6 runtime, and accepted GCC8.5 SPE C++/libgcc runtime packages. ELF dependency closure, source ELF hashes, and39 binary/module/config board readback hashes checked. The existing frozen SPE sysroot supplies any remaining runtime dependency. This test bundle is not a dpkg-installed desktop rootfs.

Stored at /opt/tabor-gl-20261109, root returned read-only before X. Bind mounts expose dev/proc/sys/run inside the test root; tmp and var/lib/xkb are separate small tmpfs mounts. A separate rebuilt BusyBox1.37 test utility enables standard chroot, setsid, timeout applets; boot/module BusyBoxes remain unchanged. Its executable basename must start with busybox for dispatcher recognition.

Xorg1.21.1.16 runs on VT2, AMDGPU KMS modesetting at1920x1080, AccelMethod none, shadow framebuffer, software cursor, no input devices configured. It uses no GLAMOR/Radeon DRI driver. Missing default mouse/kbd/libinput modules are logged; this timed demonstration is not an interactive desktop acceptance.

Existing gl-spe-demo creates a384x288 coloured rotating cube. Renderer reports Mesa25.0.7 softpipe/OpenGL3.3 compatibility. It reads pixels and checks glGetError on every frame. The run requests3600frames and has a180second process timeout; upon exit the launcher terminates Xorg to restore the prior text console. It requests a final PPM at /run/gl-cube.ppm. Completion/readback and user visual acceptance must be recorded separately.

No GPU reset, driver unload/reload, boot selection change, persistent service or full package installation. Acceleration status1 from the prior DRM query does not make this software renderer accelerated.

## Physical result

All3600frames completed in176.951seconds, exit0. GL_PIXEL_CHECK=PASS with5070 coloured pixels; no GL error return. Final PPM converted losslessly to PNG using standard PNG/zlib framing and visually inspected: coloured cube on dark background. Xorg terminated and VT1 was restored; SSH alive, kernel taint0. This is physical software OpenGL acceptance, not Radeon shader acceleration. User visual confirmation remains separately pending.
