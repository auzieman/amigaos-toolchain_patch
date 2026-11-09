# A1222 console live USB — 2026-11-08

File-backed 4.25GiB diagnostic image assembled on R730 from the existing rescue
root and verified artifacts. Target is the previously wiped 14.3GiB Cruzer Glide,
serial03007431041721021451. The original working007 SanDisk is not a write target.

Includes matched6.12.113-tabor-e2e-008 kernel/43modules/Polaris11 firmware and
007 kernel/modules as a selectable rollback. Both derive from retained complete
build receipts. Early firmware archive remains the previously accepted payload.
Native rescue init and root filesystem layout are preserved; module utilities,
verified static Bash from its actual .deb, the tested framebuffer presenters
and measured SPE fractal counts are included. This is not a normally installed
Debian X/E desktop or a GCC14 userspace/accelerated GL acceptance claim.

Wired DHCP and public-key-only tabor/root SSH remain enabled. A unique host key
was generated for this image; only its public key is in the image receipt and
has been added to the operator's existing board known-hosts file. Private keys
remain in the protected server image/root and are not committed. SSH logs move
to tmpfs /run, avoiding a persistent root write-open during the later RO gate.

AMDGPU is not auto-loaded. After boot/SSH identity checks, use the existing
protected off-board first-bind procedure against the exact008 installed module.
Do not reload after a failed bind. The console/SPE demos follow a healthy bind;
008 remains physically untested until that gate. Candidate007 scanout acceptance
does not automatically establish008 acceptance.

Existing saved U-Boot Linux entry should continue to load /boot.scr. Manual:

```
usb reset
fatload usb 0:1 0x09000000 /boot.scr
source 0x09000000
```

Same-drive007 rollback:

```
fatload usb 0:1 0x09000000 /boot-007-rollback.scr
source 0x09000000
```

Both scripts use the new image PARTUUIDa1221108-02, verified load addresses,
consoletty0 and the existing conservative mem=3500M limit. No saveenv, internal
disk installation or claim of full8GiB memory qualification is made here.

After healthy framebuffer initialization, local commands:

```
bash
fractal-screen
cube-screen
```

The cube runs240CPU-rendered frames and restores the covered rectangle. Its
backup stays in /run. Restore the fractal rectangle explicitly with:

```
/bin/fb-fractal --restore /run/fractal-console.backup
```

build.py performs source/bundle hash and U-Boot CRC checks, FAT file readback,
normal ext4 population with preserved metadata, and read-only FAT/ext4 checks.
write.py waits for a passing image receipt, then invokes the existing serial-
guarded media writer with full-image SHA256 readback. It never selects by a
remembered /dev/sdX letter. Physical write results belong in usb-write.json;
a file-backed image receipt alone is not a ready-to-boot USB confirmation.

Remaining capacity is unallocated for later desktop expansion. All image
assembly, hashing and writing take place on the R730 with explicit resource
limits. Reboot and physical acceptance are separate from media preparation.

Media acceptance: full4,564,451,328-byte USB write/readback SHA256 matches image
`e63f263d9475b7f693d97ffeee5edee811d7431891eb7df3f598cfa9927ef586`.
Partition table refresh succeeds; both256MiB FAT and4GiB ext4 partitions are
unmounted and buffers flushed. Cruzer serial03007431041721021451 is ready to
move. Actual008 physical boot and GPU bind remain pending. See usb-write.json.

Post-boot correction: the001 image selected an older BusyBox with empty module
paths. It was corrected persistently on the Cruzer, preserving the old binary.
First failed launcher call did not initialize hardware; one subsequent normal
GPU bind returned0.008 reaches SSH, taint0 and1920x1080fbdev; visual confirmation
is pending. GFX IB still times out with payloadcafedead/fence0, so the comparison
fix does not solve the earlier execution/completion failure. See
hardware-summary-008.json and ../module-tools-20261108/. Fresh file-backed
image002 is being assembled;001 full-image hash describes the pre-correction
media state, not the current modified stick. No second physical flash.
