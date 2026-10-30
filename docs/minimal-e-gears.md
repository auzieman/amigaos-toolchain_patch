# Minimal E/gears target and physical USB staging

Scope requested: E, a terminal and glxgears; a simultaneous ANSI evidence panel
and remote graphics view. Reuse the application/rootfs workload for QEMU and
A1222, while keeping their kernel/device-tree/GPU profiles distinct. No full
laptop clone, desktop suite, browser or new distro release is needed.

## Verified prerequisites and actual limits — 2026-10-30

- The patched Debian 6.12.113-1 kernel boots the QEMU e500v2 profile; its full
  Tabor board profile also compiles separately.
- A libc-free init now directly executes efsadd and efdadd on 1.5 + 2.25,
  checks exact 3.75 results, and exercises evldd/evstdd. It passed in QEMU.
  This is selected SPE instruction arithmetic, not a full ABI/fenv/glibc test.
  See [receipt](builds/20261030-qemu-spe-arithmetic.json) and
  [raw serial log](builds/20261030-qemu-spe-serial.log).
- Edge 192.168.1.15 is itself a VM. PCI inventory exposes 1234:1111 virtual
  VGA, no NVIDIA device; /dev/dri has card0 but no render node. The installed
  QEMU tools image has none/curses display backends and unaccelerated
  virtio-gpu-pci, with no virtio-gpu-gl device. No GPU was detached or assigned.
- More fundamentally, Linux 6.12 virtgpu_kms.c sets has_virgl_3d only inside
  __LITTLE_ENDIAN. Our e500v2 Linux guest is big-endian. Stock VirGL therefore
  does not provide the intended accelerated path, even if host GL is added.
  Source: https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/virtio/virtgpu_kms.c#L149 .
- VirtIO 2D plus guest software Mesa is a possible first graphics lane, pending
  compatible userspace; it is not GPU passthrough. QEMU reference:
  https://www.qemu.org/docs/master/system/devices/virtio/virtio-gpu.html .
- The known historical Tabor Debian 8 SPE image is described in the separate
  board workbench, but its recorded mount is gone. No matching image found in
  the bounded Downloads/project search. Seagate is not in current local block
  inventory. An existing Cruzer USB was observed but neither mounted nor written.

User steered toward a physical USB test if GPU assignment is unsuitable.
The useful next physical path is the A1222's actual AMD card, after identifying
its PCI ID, firmware and supported Mesa/DRM driver. No unsupported claim that
ordinary PowerPC hard-float packages work on SPE is acceptable.

## Prepared artifacts, not a boot-ready disk image

scripts/stage-physical-test.py verifies the full board kernel/DTB/config against
its compile receipt and the shared SPE initramfs against its passing receipt.
It copies them into a fresh ordinary directory and records remaining blockers.
It never opens a block device, formats disks or invents a firmware header.

Initial output: work/physical-test-001. The manifest is retained in
[staging evidence](builds/20261030-physical-staging.json). This bundle has no
interactive rootfs, E, Mesa or gears yet and is explicitly not firmware-boot-ready.
The vendor firmware wrapper/load addresses must be verified from reference
media first. The existing board workbench's zero-padding wrapper is a historical
experiment, not proof of the real firmware format; do not ship it as validated.

## Smallest intended desktop payload

Use an existing qualified SPE rootfs/toolchain when available. Add only Xorg
with the selected modesetting/input drivers, E/EFL and necessary dependencies,
a terminal, Mesa/libdrm/libGL, glxinfo and glxgears. Keep serial access and the
ANSI panel. Explicitly record ABI, versions, packages, driver and firmware hashes.
A working older reference userspace can test the modern kernel; label it as such
rather than calling it modern trixie SPE/glibc. A soft-float alternative requires
its own explicitly reviewed sysroot; do not silently mix ABIs.

For remote capture, use a LAN-only VNC view/tunnel after the graphics guest is
usable. QEMU's virtual display view and a physical machine's captured desktop
are separate paths. Record GL_VENDOR/GL_RENDERER/GL_VERSION, actual scene output
and timing. Show selected SPE arithmetic PASS independently from GL status.
Neither gears animation nor FPS establishes that CPU arithmetic used SPE.

Remaining inputs: accessible reference SPE image/sysroot, actual firmware boot
contract and A1222 GPU identity. E/gears execution, accelerated graphics and
physical boot remain untested; no bootable USB image has been produced.
