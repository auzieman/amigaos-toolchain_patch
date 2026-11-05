# Private AmigaOS side guest preflight

User authorized a separate AmigaOS boot/possible installation experiment while
keeping Trixie/SPE and modern compiler work as the main project. R730 reconnect
succeeded after reboot. Its installed qemu-system-ppc is10.0.13; documented
machines include amigaone, pegasos2, sam460ex and generic ppce500, not A1222.
No prior transient Tabor pipeline or QEMU service was running after reboot.

Uploads on edge contain AmigaOneA1222InstallCD-53.37.iso613640192 bytes and
Enhancer2.2 archive220291490 bytes. Read-only7z inspection confirms both root
and System Kicklayouts identify AmigaOneA1222. Enhancer's Kickstart directory
contains graphics/filesystem modules, with no alternate A1/Pegasos kernel found
in its listing. Neither original payload was changed or added to Git.

Retained actual QEMU11.1.3 device test at work/qemu-next/ati-probe-002 used the
same ISO SHA256 aaf22a514b8a7c416d01fe18965af492ea8d445d726c02eb2df1e860045b3623.
It did not verify an AmigaOS boot or a new guest driver. Earlier edge10.0.13
serial/display probe loaded Kickstart modules, then stopped at launch; no
Workbench observed. These are existing results, not a newly successful test.
The old device-probe receipt is retained; no equivalent trial was rerun merely
to produce fresh activity, and no new empty installation disk was created.

Primary references rechecked2026-11-05:
- https://qemu-project.gitlab.io/qemu/system/ppc/amigang.html
- https://zero.eik.bme.hu/~balaton/qemu/amiga/aos_bboot.html

The BBoot recipe requires the platform-matched AmigaOne/Pegasos edition and
appropriate official kernel update plus emulated graphics driver. Generic
e500 CPU support does not emulate the A1222 board/firmware/devices. Hardware
RadeonHD/RX drivers in Enhancer are not QEMU ati-vga drivers. Do not relabel or
force the A1222 kernel as a different supported board.

Bounded next step: user is checking whether matching AmigaOne XE/Pegasos II
media is available. Once supplied, hash/private-readonly media intake, isolated
machine-matched boot overlay, new guest disk, bounded R730 TCG/VNC trial, and
only then installer/Workbench acceptance. Keep VNC loopback/LAN-only and ISO
unchanged. This side guest cannot validate Linux SPE/glibc or physical A1222
GPU/SMP behavior. No purchase, account changes, OS installation or firmware
modification was performed.

Main build findings recovered during reconnect:020 completed13 source builds
and47 inspected binaries.022 completed without new accepted binaries: actual
apt/dpkg failures show tabor-spe-libatomic-dev tries to create a link under
/usr/lib/tabor-spe-toolchain, which is now mounted read-only. This is a package
ownership/layout integration defect, not evidence of compiler inability.
Do not silently make the shared compiler writable or claim full shared-root
integration acceptance. Preserve these logs and address runtime/development
package ownership against the user-selected GCC14 migration. No old-GCC batch
was restarted during this side investigation.


## Follow-up: use our existing e500 platform as the experiment

The user correctly noted our existing emulation work. Lack of a stock named
A1222 machine is not proof that a custom platform/boot adapter cannot work.
The standard AmigaOne/Pegasos media recipe is an alternative, not the only
possible project direction. Existing tracked Linux launchers use generic
ppce500/e500v2 with our patched Linux support; QEMU supplies its generated DT.
No named A1222 board model or P1022 code was found in the reviewed QEMU11.1.3
hw/ppc and hw/pci-host source directories. This is a scoped finding, not a
claim that no such work exists elsewhere.

Read-only ISO extraction identifies System/Kickstart/kernel as807744-byte
32-bit big-endian PowerPC ELF. Copied only that private kernel to R730, outside
Git, and performed a two-second bounded direct-entry test using existing
ppce500/e500v2 (1CPU/1GiB service;512MiB guest; no network or disk). This is an
entry diagnostic, deliberately not a complete ISO boot or AmigaBoot/Kickstart
handoff. No user kernel patching, boot-image relabeling or installed disk.

QEMU loaded the kernel with initial NIP0x010000d4; after two seconds NIP was
0x00000700, LR0x01018ca8. Serial output remained empty. These samples demonstrate
kernel entry/execution and an early failure state; they do not identify its
precise cause, prove an unsupported CPU instruction, or show Workbench. QEMU
was terminated after capture. Inputs, commands, registers and bounds are in
e500-entry-receipt.json; no proprietary executable is committed.

Next bounded experiment is the actual AmigaBoot/Kickstart handoff contract and
A1222/P1022 peripheral/address-map requirements against the generic e500 model.
Use read-only media documentation and trace the first failing entry operation
before changing the emulator. Firmware, DT/boot arguments, MMIO and required
modules are separate hypotheses. Do not mistake a generic ePAPR Linux direct
entry for the AmigaOS bootloader contract. A working Linux guest is useful
infrastructure but not proof of a completed A1222 board emulation.
