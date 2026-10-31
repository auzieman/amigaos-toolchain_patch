# Package installation and A1222 hardware audit — 2026-10-31

The user reports the board is about a year old and identifies
https://amigang.com/hardware-amigaone-a1222/ (titled A1222 Plus). This supports a
Plus working hypothesis, not an exact PCB/firmware revision measurement. Retain
P1022 dual e500v2 SPE, PPC32 big-endian and requested8GiB; confirm identity, DIMM
size and U-Boot version on the board. NXP's primary P1022 fact sheet describes
two cores, MMUs, SPE/double-precision support and36-bit physical addresses:
https://www.nxp.com/docs/en/fact-sheet/QP1022FS.pdf .

## Kernel memory and CPU gates

Actual compiled tabor-live001 config already enables SMP, MMU, HIGHMEM,
PHYS_64BIT, PTE_64BIT, SPE, INOTIFY_USER, SYSVIPC, SWIOTLB and coherent64-bit
DMA-address types. NR_CPUS24 is a maximum supported CPU count, not a claim of
24 physical cores. The target is two online cores. The board DTS memory node
intentionally lacks a hardcoded memory reg; firmware must supply the actual
memory map. Adding mem=8G cannot substitute for correct firmware/DT ranges.

The old qemu-live005 tiny config lacked HIGHMEM/SYSVIPC/inotify and only managed
768MiB, irrespective of its configured2GiB. qemu-live007 freshly rebuilds the
same locked Debian6.12.113-1 + ordered Tabor patch with those options enabled.
The runner now enforces physical memory/SMP prerequisites and a CPU-count floor.
Iteration006 retained an infrastructure failure: wrong read-only cache mount;
007 uses the correct source cache, freshly extracts and rebuilds.

Software-e004 boots a package-installed root with8192MiB QEMU RAM:
MemTotal8248388KiB (~7.87GiB), CPUs0–1 online. Two workers each pinned to a
different CPU pass64MiB page-pattern and exact binary-fraction arithmetic checks.
The target disassembly contains efdadd. This is a CPU-affinity/arithmetic smoke
check, not proof of all SPE context, signal, fenv, MMU or physical8GiB behavior.
Issue3's directed-rounding failure remains open. Required physical proof is two
online CPUs, expected usable memory after reservations, correct DT/boot log,
repeat arithmetic/memory checks and DMA/graphics stability.

## Actual .deb installation

Direct staging flattened every executable to0755. Debian e17 0.27.1-1 rules
explicitly restore4755 on enlightenment_sys/system/ckpasswd after dh_fixperms.
The new private powerpcspe bootstrap/session bundles are built with dpkg-deb
and actually installed using builder dpkg --root into a fresh offline root.
No arbitrary foreign maintainer scripts run on the host. These lab bundles have
no maintainer scripts and are not mislabeled official Debian binary packages;
they are a transition to individual rebuilt packages, not full dependency closure.
Original source stages, source/license notices and failure receipts stay retained.
Package data, installed status and archive hashes are recorded; ownership/modes
are verified before archiving, and newc preserves them. No USB media is written.
First packaging failure rejected unsupported console device nodes; iteration002
explicitly handles only the known console/null nodes. Ordinary user ownership
is preserved rather than applying root-owner-group to the whole bootstrap.

libmd1.1.0-2 and dpkg1.22.22 are locked, freshly source-built with GCC8.5 SPE,
restored glibc2.41 and explicit long-double128. Target dpkg prints powerpcspe,
queries both installed bundles and produces a clean audit in software-e005.
This minimal dpkg supports gzip packages; bz2/xz/zstd, apt, Perl development tools
and normal distro-wide dependency/service management remain separate work.
Do not install generic PowerPC hard-float Debian binaries into this runtime.

Version0.2 bundles add a locked messagebus service account and desktop video/input
group membership, plus root-started system D-Bus. This addresses actual missing
setup instead of treating setuid bits as the entire problem. Xvfb uses MIT-SHM
when the kernel exposes SysV IPC, retaining the old kernel's explicit fallback.
UPower and other optional service packages, locales/keyboards and matching E
module profile remain tracked under issue7. Black-client rendering is issue8.

## GL versus SPE

The compiled physical kernel enables amdgpu for the recorded1002:67FF Polaris/
Baffin-family card; generic old radeon kernel driver is not selected. Existing
Polaris10/11 firmware selection is hash-locked separately. Exact physical PCI
revision, firmware load, connector output and DMA behavior still require board
proof. Xvfb and kernel compilation do not demonstrate hardware OpenGL.

New graphics source lock pins libdrm2.4.124-2 and Mesa25.0.7-2+deb13u1 from
Debian trixie. Inspecting the pinned upstream meson.build shows RadeonSI requires
libdrm_amdgpu and LLVM; merely compiling a GL client with -mspe does not provide
these. CPU-side code and all libraries must preserve the SPE ABI. GPU shader
compilation targets AMD GPU instructions, separate from CPU SPE instructions.
LLVM used for GPU shaders must not be confused with enabling a CPU llvmpipe JIT
that emits unsupported conventional PowerPC FP instructions. Mesa's softpipe
interpreter is a separate bounded software-GL path, not GPU acceleration:
https://docs.mesa3d.org/systems.html .

Next GL acceptance: finish/pin the target libdrm/Mesa/LLVM dependency and ABI
recipe, build Xorg/GLX userspace, run a small client, record glxinfo renderer and
actual gears image, then repeat on the physical amdgpu device. FPS alone cannot
prove either GPU acceleration or correct SPE execution. No GL pass is claimed.

## Final observed package checkpoint

Version0.2/software-e006 exposed a real boot ordering defect: system D-Bus
could not open /dev/null before the native rescue init mounted devtmpfs.
Version0.3/deb-root005 mounts devices first and software-e007 starts the system
bus successfully as messagebus. E's helper runs as root with the intended
video/input memberships; no E_SUID_ERR is observed in this test. Native dpkg
reports powerpcspe, both0.3 bundles installed, and audit returns0 with no output.
The completed lab E profile is copied into this runtime test only (hashes in
evidence); a fresh image still starts with the wizard. Black client interiors
persist even with SysV IPC/MIT-SHM available. This narrows hypotheses but is not
a rendering fix. The same6089 viewer now uses this guest; original rescue/E
checkpoints are preserved, and only our transient004/005/006 guests were stopped.
No physical USB write or firmware/default changes have occurred.
