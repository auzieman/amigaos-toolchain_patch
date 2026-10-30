# E-Trixie image follow-up

User expressed interest in an E-Trixie build after the initial kernel/emulator
work. This is a follow-up proposal, not a working image or an active full distro
build. Establish the intended E desktop/package set before an image release.

The current kernel source is already Debian trixie security linux 6.12.113-1;
selected libc source is glibc 2.41-12+deb13u4. That source baseline does not imply
Debian supplies an official trixie powerpcspe binary distribution. Do not install
ordinary PowerPC hard-float packages into an SPE root filesystem or label a
soft-float bootstrap as accepted SPE hard-float support.

Suggested gates:

1. Retain full Tabor kernel build and separate QEMU e500v2 boot evidence.
2. Establish a reference SPE toolchain/sysroot; restore modern GCC and glibc,
   then verify float/double, ABI, libm/fenv, signals, threads/TLS and unwinding.
3. Build a minimal serial rescue rootfs with explicit ABI and package/source
   manifest. Keep generic QEMU and real Tabor device-tree/boot profiles separate.
4. Verify actual A1222 serial boot and board/storage/network requirements.
5. Bring up headless guest-side Mesa rendering and correctness checks, followed
   by the chosen E desktop and actual GPU/DRM support as a separate milestone.
6. Package an image only after reviewing licenses, firmware and boot layout;
   writing a physical thumbdrive remains separately authorized work.

No rootfs image, desktop build, GPU passthrough or physical-media write is
claimed by this follow-up note. The kernel-only CLI boot does not exercise
modern glibc, SPE arithmetic or OpenGL.

## SDL and graphics acceptance

User requested an SDL test and AMD hardware / QEMU graphics coverage.
Keep identical scenes and numerical workloads where possible:

- Direct SPE instruction/ABI tests establish CPU correctness independently.
- Guest-side SDL software rendering checks the rebuilt application/runtime and
  deterministic pixels without depending on a physical GPU. Record SDL version,
  selected video/render driver and result checksum; a dummy video driver alone
  does not establish graphics output.
- SDL with an OpenGL context exercises the selected guest Mesa path. Record
  GL_VENDOR, GL_RENDERER, GL_VERSION, extensions and scene output. Explicitly
  reject a silent renderer fallback when checking an accelerated path.
- QEMU virtual GPU acceleration is a separate feasibility task: verify ppce500,
  guest DRM/Mesa, graphics transport and host renderer support. A host NVIDIA
  GPU is not automatically exposed as an NVIDIA device in the PPC guest.
- Real A1222 AMD graphics acceptance requires the exact card/PCI ID, kernel
  DRM driver and firmware, userspace Mesa driver and real display output.
  Retain serial/kernel logs and compare the SDL/GL scene with the software run.

Report rendering correctness separately from timing. QEMU TCG timings are not
A1222 performance measurements. Neither an accelerated GL result nor a passing
SDL test alone establishes that the compiler emitted or executed SPE arithmetic.
SDL allows explicit renderer selection and runtime enumeration:
https://wiki.libsdl.org/SDL3/SDL_CreateRenderer . API/version selection for the
actual build is still pending; this reference is not a claim SDL3 already builds
or runs on our target. No graphics stack has yet been built in this lane.
QEMU's virtual GPU backends and host rendering transport are documented at
https://www.qemu.org/docs/master/system/devices/virtio/virtio-gpu.html .
Availability there does not establish working accelerated graphics with our
PPC32 big-endian SPE guest or the installed edge NVIDIA driver.

The requested image should resemble the laptop's main E desktop: review a
package/desktop/theme manifest, rebuild for the selected A1222 ABI and keep
personal configuration, credentials and private wallpaper licensing separate.
A laptop filesystem clone is not a target-compatible image. First deliver a
minimal bootable rescue environment; then expand toward that desktop manifest.
