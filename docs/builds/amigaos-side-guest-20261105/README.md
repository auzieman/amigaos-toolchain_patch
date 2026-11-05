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
