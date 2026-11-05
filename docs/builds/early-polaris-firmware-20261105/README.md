# Early Polaris firmware availability — 2026-11-05

A1222 early Polaris firmware update - PREPARED, NOT HARDWARE VALIDATED

The current kernel and ext4 root boot and SSH works. Built-in AMDGPU probes
before root mounts, so firmware already on ext4 is unavailable at probe time.
This 1.49 MiB early archive contains 42 Polaris10/11 firmware files and their
copyright, no /init, shell, accounts or OS root. Linux retains ext4 disk-root.

Update requires the A1222 shut down and its serial-identified boot USB mounted
on the laptop. Do not remove the live Linux root USB while the A1222 runs.
Preserve current boot files as a rollback before changing anything.
Place uRamdisk-fw in /boot, and replace boot.cmd and boot.scr in FAT root.
Kernel, DTB and ext4 root remain unchanged. Do not flash board or GPU ROM.
Same temporary U-Boot launch: usb reset; fatload usb 0:1 0x09000000 /boot.scr;
source 0x09000000. Do not saveenv. Keep the known-working old script as rollback.

QEMU ext4-root boot + SSH/PTY/fractal passed with the firmware-only archive.
QEMU does not validate Radeon hardware or GPU acceleration. Real display
validation awaits USB update and physical retry. See receipt.json for hashes.

Source references: https://docs.kernel.org/filesystems/ramfs-rootfs-initramfs.html and https://docs.kernel.org/driver-api/firmware/fallback-mechanisms.html. Exact 6.12.113 source shows firmware loader waits for initramfs, and missing early /init falls through to prepare_namespace for disk-root.

Correction to initial graphics diagnosis: polaris11_sdma.bin is present on the running ext4 root. It is missing from the pre-root namespace during built-in AMDGPU initialization. Package contents were already sufficient for this first request; timing is the demonstrated problem. Further GPU failures remain possible after this is corrected.

ROM investigation: native sysfs exposes a root-only 131072-byte Radeon ROM interface and a root-only 12288-byte live FDT. Kernel log already confirms VBIOS read. /proc/mtd lists no mapped flash partitions. Current uid1000 session cannot dump those root-only files; no ROMs were read or flashed. A dump alone cannot implement absent QEMU P1022 peripheral models. Keep any future device firmware dumps private and hash/origin-qualified.
