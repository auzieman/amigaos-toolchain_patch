# Matched boot-set installation — 2026-11-08

The SanDisk now selects a complete rebuilt Linux **6.12.113-tabor-e2e-001** kernel, its own43-module directory, a rebuilt Tabor DTB, and verified Polaris11 firmware. The distinct kernel release prevents normal modprobe from choosing a previous build's AMDGPU. This is a new complete build of the proven6.12 hardware branch, not activation of the separate7.3 experiment or a new Debian userspace image.

## Provenance and checks

Canonical source: atom-channel-20261108-002, parent of commit826ca35's hardware-tested module. It includes the ATOM complete-clock-word correction, all AVFS calibration endian corrections, mandatory DPM error propagation and request/gate tracing. The complete source/output were copied without hardlinks into fresh R730 storage; the parent is preserved. Only LOCALVERSION changes in .config; olddefconfig is checked against the expected exact configuration. Kbuild vmlinux/modules/dtbs and modules_install/depmod ran normally in the pinned image2781e118,4CPU/6GiB/networknone. Cached compiler tooling was mounted, with no download.

- Complete build/package receipt: receipt.json; commands: build.py and launch.json.
- Kernel physical memory end0x24c158c stays below the unchanged0x04000000 compressed-image staging address.
- U-Boot image header/data CRC, gzip-to-kernel roundtrip, script CRC/text, module release/import CRCs and all firmware hashes verified.
- AMDGPU SHA256 `ad5fc87d5b92fde72a1bb4fca2460f5c4dea0a273212c67d6aefecf673f70959`;687 imports checked against this build's complete Module.symvers.
- Bundle24,156,160 bytes; SHA256 `e15ebba63af9b060860ceb6b51d62edba4bb5e7251822eea6776907021c52cd6`.
- This exact physical-board config disables PPC_QEMU_E500/SERIAL_OF_PLATFORM. It was not mislabeled as a successful ppce500 boot. No extra config variant was substituted for the USB artifacts.

## Identified media and installation

SanDisk Cruzer Glide serial03001919041721081205, FAT128MiB A1222_BOOT and ext4 A1222_ROOT/PARTUUIDa1221105-02. No partitioning or formatting. Initial boot hashes match the recorded known selection. Read-only filesystem checks passed; ext4 noted board-clock timestamps within a day of host time, with no structural failure reported.

The file updater verifies the bundle and target identity, retains host-side rollback copies, installs the new versioned payload and module directory, verifies firmware contents, and switches /boot.scr only after payload readback. Existing firmware aliases are preserved when contents match. A pre-activation pause exposed the initial regular-file-only assumption; all57 staged files were hash-checked before resuming, and no boot activation had occurred. The final readback verifies all80 bundle files,43 modules, seven preserved firmware symlinks and exact script text. See usb-install.json, usb-readback.json and fsck.json. Both partitions were unmounted after final checks.

Changed selection:

- `/boot.scr` now loads `/boot/e2e/uImage` and `/boot/e2e/tabor.dtb`.
- `/boot/uRamdisk-fw` remains the verified early-firmware image; root firmware matches the bundle. The small early ramdisk remains separate from the ext4 root.
- `/lib/modules/6.12.113-tabor-e2e-001/` contains the complete installed module/dependency set.
- `/etc/tabor/e2e-boot.json` records the selected artifact identities.

Rollback: `/boot-before-e2e.scr` and matching .cmd preserve the exact previous script, referencing retained old kernel/DTB/early-firmware filenames. The existing6.12 and7.3 module trees remain. Host backup is work/e2e-usb-20261108/usb-backup. Firmware saveenv/boot defaults were not altered.

## First physical boot, without serial

Use the saved USB startup command that sources `/boot.scr`, with the SanDisk in the previously working top-right rear port. Manual fallback if needed:

```
usb reset
fatload usb 0:1 0x09000000 /boot.scr
source 0x09000000
```

For rollback, substitute `/boot-before-e2e.scr` in the fatload line. No saveenv is needed for either script.

The existing native rescue /init and network/sshd setup are retained. SSH must come up before graphics loading, allowing off-board logs even without a nine-pin serial cable. Initial acceptance: uname reports the complete new release and normal modprobe resolves the installed driver. The capture script now has --installed-release mode: it checks the installed .ko hash and kernel release, verifies read-only root before normal modprobe, and uses no driver override, rmmod or RAM insmod. Its fake-endpoint tests prove the load follows the read-only gate and a failed gate prevents the load; they do not claim hardware success. Move the running sshd log to RAM before remounting root for the physical test, as in the existing capture procedure.

The prior matched-driver trial passed DPM, PowerPlay and DCE initialization but faulted in UVD ring testing. The full boot set retains UVD and does not claim that fault fixed. No video-block masking or permanent feature removal was applied. Do not repeat initialization after a bus fault; preserve capture and use a fresh boot. DCE success is not scanout/console or accelerated desktop acceptance.

This update preserves the existing rescue userspace, account keys and /init byte-for-byte. A full package-managed Trixie workstation remains a separate open milestone. The new complete kernel/modules set has not yet physically booted.


## Complete physical boot and installed-driver result

The A1222 booted6.12.113-tabor-e2e-001 from the updated USB, reached SSH with taint0/no GPU module, and exposed the expected installed driver SHA and all21 matching firmware hashes. The existing BusyBox module loader does not support -n; its dependency file was inspected instead of substituting a module or loader. The next load used ordinary modprobe with no override, rmmod or RAM module replacement. Root was verified read-only and SSH logging moved to RAM before that load.

DPM_Enable acknowledged1 in6087us; PowerPlay and DCE hw_init returned0. The first PCIe fault occurred46172us after entry to the UVD ring test. SSH dropped; no second initialization or diagnostic MMIO retry was made. This independently confirms that the ATOM/AVFS candidate's prior DPM advancement survives a coherent kernel/module/firmware boot. It does not establish an individual fix's causality, working scanout, decoder operation or a desktop. The new UVD failure is reproduced without a mixed-release module explanation.

Evidence: hardware-boot-001/ (boot identity, firmware, dependency metadata and boot dmesg), hardware-installed-001/ (normal module-load stages and off-board kmsg), hardware-summary.json. The absence of a serial cable limits visibility before networking; this boot did reach SSH. Further hardware tests need a fresh boot following this failed initialization.
