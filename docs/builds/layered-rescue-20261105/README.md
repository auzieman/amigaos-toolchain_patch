# Layered A1222 rescue USB — 2026-11-05

User requested replacing the RAM-root trial with the legacy-style layered disk
layout and retaining the observed `mem=3500M` baseline. This is a historical
GCC8/SPE diagnostic root; it is not the full Debian Trixie desktop or GCC14 SDK.

The repeatable builder verifies retained kernel/DTB/rescue archive hashes,
extracts the rescue root preserving ownership, modes, symlinks and device nodes,
and creates a 2GiB MBR image with 128MiB FAT32 and 1919MiB ext4. Built-in USB
storage, SCSI disk, ext4 and partition support are checked. No target executable
is run during assembly. Existing SSH public key/account/config and licenses
remain; no private client key or preset host key is bundled. Normal Debian
package installation is not fabricated: this root is explicitly a rescue root.

The kernel directly mounts the ext4 PARTUUID, using `init=/init` and no
initramfs. Its first-stage root does not mount internal disks. Writable ext4
retains runtime host keys and logs, unlike the old RAM root. Boot script stages
the unchanged board kernel at 0x04000000 and DTB at 0x08000000. Launch it after
USB enumeration with `fatload usb 0:1 0x09000000 /boot.scr` then
`source 0x09000000`. Firmware `source` support remains to verify on hardware;
manual fallback is in BOOT-README. No saved firmware settings are modified.

Validation: FAT files read back and hashed, ext4 e2fsck passed, complete image
partition regions compared to source files. A snapshot QEMU ppce500/e500v2 guest
with the separate qemu-live-008 kernel and virtio disk booted directly from
PARTUUID, mounted ext4, reached SHELL_READY and NETWORK_SSH_READY. Native client
key login, uid/home permissions, PTY and matched fractal pixels passed. Existing
fenv failure persists. QEMU uses serial and virtio; this does not validate the
physical board kernel, USB, Radeon, memory map, 8GiB RAM or filesystem drivers
for local Amiga volumes. Board kernel and DTB remain unchanged from the first
physical trial; the new layout and memory cap are a controlled next experiment,
not an asserted fix for the missing Linux output.

All heavy assembly and QEMU ran on R730. Assembly was limited to 2 CPUs/4GiB
(initial 2GiB cgroup incurred page-cache pressure); QEMU 2 CPUs/6GiB. An initial
unprivileged probe could not create an output under root-owned /work; the
corrected probe writes under /home/owner without changing shared permissions.
QEMU runs as owner and uses snapshot writes, loopback SSH forwarding only.
Physical write/boot acceptance must be recorded separately.
