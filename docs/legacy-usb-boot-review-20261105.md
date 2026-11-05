# Legacy Tabor USB boot comparison — 2026-11-05

Primary references checked:
- https://wiki.amiga.org/index.php/AmigaOne_Linux
- https://eliyahu.org/tabor/data/Linux_installation_instructions_A1222_Tabor_v0.9.4.pdf (public search extraction; full PDF fetch timed out)
- https://www.mail-archive.com/dri-devel@lists.freedesktop.org/msg142018.html (Julian Margetson, 2016-04-01, firsthand Tabor boot log)

The Debian 8 USB recipe boots uImage.sdk17.2 plus tabor2.dtb with root=/dev/sda2 rootdelay=5 and no separate ramdisk. This matches the older stick's FAT16 boot and ext4 root layout. It differs from our RAM rescue initramfs; do not copy its disk-root arguments into our rescue image.

The public installation-guide extract documents serial-first installation and warns DIU cannot be used with an installed Radeon in that historical configuration. This contextualizes the onboard DVI test but does not prove the behavior of our modern kernel.

The firsthand kernel 4.6 Tabor log shows kernel load/entry zero, the same available-memory 0x30000000 warning, serial plus tty0 console arguments, then Linux machine initialization, two CPUs and Radeon SI hardware. These are reference observations, not proof our load ranges, DTB, Polaris GPU or modern kernel are correct. Older successful graphics used a different GPU generation and required board/graphics fixes.

Current physical trial: USB enumerated after moving stick to top-right port with mouse disconnected. Kernel and ramdisk CRCs passed, DTB loaded, decompression and relocation reported OK. No Linux output or SSH confirmed. The claim that console naming or zero image entry alone explains failure is unsupported. No root cause established.

Next bounded diagnostic: compare exact current board DTS/memory/PCI ranges and early boot initialization with known working source; verify actual Polaris firmware requirements and initial console path. Preserve hashes and source baseline. Do not blindly reuse legacy addresses: our decompressed kernel extends beyond the older DTB staging address. No media edits performed in this review. The specific remembered painfully-slow claim was not independently located.
