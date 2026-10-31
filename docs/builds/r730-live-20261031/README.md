# R730 linux-live-001 evidence

Implementation: `4fe159f`. All target execution here is QEMU e500v2 under TCG;
physical A1222 boot and GPU/GL remain untested. Full logs/source/object trees
are retained on R730, not committed as generated build artifacts.

| Evidence | Outcome |
|---|---|
| tabor-live-001 | Compiled board vmlinux/modules/dtbs; exact config/seed retained |
| rescue-005 | Static BusyBox/native init, console selection and background network hook |
| abi-live-002 | Eight PASS; fenv FAIL; legacy time32 enables pthread/TLS |
| libxcrypt-001 | Static libcrypt installed into disposable sysroot overlay |
| openssh-004 | Static reduced OpenSSH 10.0p1 client/server/helpers compiled |
| live-payload-001 | CLI benchmark/ABI + pinned Polaris10/11 firmware |
| combined-payload-003 | Verified merged payload, accounts, operator public key, licenses |
| rescue-full-001 | Hash-checked initramfs overlay, explicit uid/modes |
| qemu-live-005 | Compiled final live QEMU kernel with resolved networking dependencies |
| network-probe-001 / 002 | Failed: no network interface in reduced kernel |
| network-probe-003 | Native laptop SSH, ordinary uid/home, PTY, CLI execution passed |
| native-ssh | Raw command output/stderr and receipt; ABI failure remains recorded |
| board-boot-001 | ELF/layout, U-Boot CRC and decompression checks passed |
| usb-image-002 | 2 GiB MBR/FAT32 file image and boot-file readback verified |
| usb-write-receipt.json | SanDisk written; entire 2 GiB image readback SHA256 matches |

`results-ascii.txt` summarizes measured emulated timings. The two PGM images
come directly from the measured 128x96 iteration bytes (grayscale = min(255,
iteration*4)); equality checks use the original bytes in `fractal.stdout`.
The benchmark is freestanding software FP versus explicit SPE, not GL.

`tools-lineage.json` distinguishes imported OCI manifest identity from classic
Docker config identity while checking identical rootfs layers. This was not a
compiler rebuild. OpenSSH's tooling image adds only build-system dependencies.
`index.json` hashes retained evidence; component receipts separately hash inputs,
outputs and selected logs. Build logs on R730 also retain unsuccessful
configuration/link iterations; failures were not converted to successes.

The board seed reconstructed from its exact initial fragment hash is retained.
The current source fragment additionally spells out settings already enabled
in that board config. Test and image receipts never imply full ABI acceptance,
a native speedup, physical HDMI output or an installed E desktop.
