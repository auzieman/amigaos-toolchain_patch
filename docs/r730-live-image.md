# R730 Linux rescue image toward the VM132 desktop

The R730 is now the active larger-build host. Work is isolated under
`/srv/data1/tabor-build/linux-live-001`; sources are re-extracted and patches
reapplied each iteration. The known reference compiler remains GCC 8.5 SPE,
with restored experimental Debian glibc 2.41; this does not restore SPE in
modern GCC. Kernel input is pinned Debian Linux 6.12.113-1.

VM132 (`trixie-smoke-132`) is a functional reference, not a binary source:
it is amd64, systemd/LightDM with Enlightenment 0.27.1, Terminology 1.14.0,
Xorg 21.1.16 and Mesa 25.0.7, using approximately 12 GiB. Mesa-utils and
x11vnc were absent. Its binaries cannot populate the PPC/SPE filesystem.

## Current increment

A 2 GiB MBR/FAT32 image holds a legacy U-Boot kernel, board DTB and compressed
RAM rescue filesystem. The filesystem provides source-built BusyBox 1.37,
proc/network/USB tools, the CLI SPE ABI test and matched fractal benchmark,
OpenSSH 10.0p1 client/server, and Polaris10/11 firmware with license notices.
Both firmware families are retained until the board's exact Radeon revision
is checked. The board kernel includes built-in USB storage/HID, wired network,
amdgpu legacy DCE, framebuffer console and the relevant filesystems. Driver
configuration and successful compilation do not establish physical output.

The first console follows the last kernel `console=` setting: `tty0` becomes
`tty1` for the local root rescue shell. Wired DHCP and SSH start independently
in the background, logging to `/tmp/network-boot.log`. The `tabor` SSH account
is ordinary uid1000, accepts only the provisioned operator public key and has
no sudo. Private client keys stay on the operator laptop; unique Ed25519 host
keys are generated at each boot. Password and root SSH logins are disabled.
This rescue setup is for the lab and contains no internal-disk installation.

No E/Xorg/Mesa/systemd desktop is installed in this increment. The next stage
is a source-built PPC/SPE userspace matching the VM132 feature set after the
ABI and hardware gates. VNC belongs with that graphical stage. Firefox remains
optional. A larger FAT partition alone would not provide this software.

## Repeating the build

Scripts require fresh output directories and write receipts; consult their
`--help` for paths. Keep all input caches separate from work directories.

1. Use `debian-iterate.py --component linux --mode build --kernel-profile
   qemu-live` and separately `--kernel-profile tabor-live`. Limit jobs and
   container CPU/RAM; keep network disabled during cached builds. Verify the
   final `.config`, not just requested Kconfig settings.
2. Build `build-skinny-shell.py --variant rescue` using the reference compiler
   and sysroot. Its native init and libc-linked code explicitly use 128-bit
   long double. `build-linux-live-payload.py` adds the verified CLI ABI binary,
   original GNU soft-float inputs, matched SPE fractal and pinned firmware.
3. `build-rescue-libxcrypt.py` builds a disposable sysroot overlay. Then
   `build-rescue-openssh.py` uses the pinned Debian source, autoreconf and
   libxcrypt. The derived `Dockerfile.live-tools` adds autoconf/automake/libtool.
   OpenSSL, PAM and security keys are disabled; the tested key/cipher path is
   Ed25519/Curve25519/ChaCha20. The helper binaries include both `sshd-auth`
   and `sshd-session`. The seccomp sandbox requires matching kernel support.
4. `assemble-live-payload.py` verifies component manifests, adds accounts,
   network startup and licenses. `extend-rescue-initramfs.py` verifies the base
   archive and overlays regular files and explicit ownership/modes. It never
   includes client private keys or pre-generated host keys.
5. Run `qemu-live-network-probe.py` on R730 loopback. Forward that port through
   SSH, then use `probe-live-ssh-client.py` from the laptop. Return its receipt
   as `client-proof.json` to the probe directory. The probe tests key login,
   uid/home permissions, PTY, image equality/timings and the ABI CLI. Console
   debugging accepts a local `console-command.txt`; no LAN QEMU listener.
6. `package-board-boot.py` requires `--machine-source` pointing to the exact
   build's `arch/powerpc/platforms/85xx/tabor.c`; it rejects a machine/DTB
   compatible mismatch before producing boot images. It accepts compiled board artifacts and checks hashes,
   ELF layout, legacy-image CRCs and decompression. Its kernel input directory
   contains `linux-receipt.json`, `vmlinux` and `tabor-a1222.dtb` copied from the
   same iteration. `build-usb-fat-image.py` creates a regular file and verifies
   every boot file by FAT readback. Ensure `/usr/sbin` is on PATH for mkfs.fat.
7. Only after testing, `write-verified-usb.py` requires an explicit device,
   expected USB serial and image hash. It rejects mounted/non-USB targets,
   verifies the image first and checks the entire written image by readback.
   Retain its receipt. Never infer real-board boot from a write receipt.

The imported tools archive has OCI manifest digest
`14e54601943b132a398ace86e677dfe440305206f454bb951c5cdbbecdd0d2ad`.
Classic Docker on R730 reports its config identity
`2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0`;
archive blob/config hashes and rootfs layers were compared. These identify
the same retained image lineage, not a rebuilt compiler.

## Acceptance boundaries

The old tiny QEMU profile omitted futex. The live profile additionally needs
legacy 32-bit time syscalls for this userspace; enabling these makes pthread/TLS
pass. A network probe exposed Kconfig dropping virtio-net without NET_CORE and
the legacy transport needed by this QEMU device; these are now explicit checks.
The fenv rounding test still fails under emulation. This is not full SPE ABI
acceptance; exception/unwind, wider library use and native hardware remain.
The fractal compares software FP with explicit SPE instructions, not OpenGL or
GPU acceleration; emulator timings are not A1222 performance predictions.

Use the generated BOOT-README for temporary U-Boot loads. Verify `iminfo` and
actual USB enumeration before `bootm`; never `saveenv`. The operator recalls
rear/direct USB being preferable, which remains a practical trial rather than
a documented rear-only requirement. Capture real output with OBS/Elgato and
then native ABI/fractal logs. E/gears and native Radeon acceleration follow.

Firmware reference: the published [Tabor Technical Reference Manual 1.0.3,
Table 21](https://www.eliyahu.org/tabor/data/trm_tabor_1.0.3.pdf) lists USB keyboard
alongside serial input and VGA alongside serial output. This supports trying
the firmware console without a serial cable, but does not verify this board's
current environment, chosen Radeon output or firmware version. Do not change
those critical saved settings as part of this test.
