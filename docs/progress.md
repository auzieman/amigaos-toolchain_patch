# Engineering progress

This log records evidence rather than treating a successful source import as a
working toolchain. Raw generated source/build trees remain outside Git; patch
origins, source pins, run IDs and artifact hashes provide the replay path.

## 2026-10-31 — R730 larger-build host prepared

Verified the reinstalled Debian 13 R730 against retained chassis/root UUID
records. Forty logical CPUs, 128 GB RAM and about 1.77 TB available on the
selected existing data filesystem remove edge's 1.5 GB free-space bottleneck.
Workspace: `/srv/data1/tabor-build`, initially four CPUs/8 GiB per build.

QEMU 10.0.13, libvirt, Docker and build dependencies installed. Initial host
preparation stopped at its final Docker CLI check; explicitly adding Debian's
separate docker-cli package and replaying the corrected script passed. A pinned
Debian container verified two CPUs, 4 GiB and network-none enforcement.

Diskless x86 ROM executed under KVM and observed guest VMX. Nested host setting
is Y; actual L2 guest boot remains untested. The existing e500v2 Linux kernel
and source-built shell passed command execution under PPC TCG on this host.
RTX 3060 Ti and audio share isolated IOMMU group 28; assignment remains untested
and the host driver remains attached. No disk/boot/BIOS configuration changed.
Larger image compilation has not started. Scripts, package versions, raw serial
and hashed receipts: [R730 preparation](r730-build-host.md),
[evidence](builds/r730-20261031/receipt.json).

## 2026-10-31 — AmigaGCConDocker review for Steven

[Pinned integration review](amigagccondocker-integration.md) traces the linked
development image to AmigaGCConDocker-base and AmigaLabs/adtools. Its docs
advertise GCC6 SPE support; its target runtimes differ from Linux glibc.
Our workflow/test design can inform that work, but modern GCC restoration is
not implemented yet and Linux libc/board patches are not direct AmigaOS fixes.
Exact failing image/runtime/reproducer remains to establish before a patch is
selected. No upstream changes or AmigaOS build acceptance claimed.

## 2026-10-30 — first Debian iterations

Target sources: Debian linux 6.12.113-1 and glibc 2.41-12+deb13u4.
Host/build environment: Debian trixie container on BKC lab-edge; PowerPC cross
compiler, 2 CPU / 4 GiB runtime. AmigaOS SDK integration remains a separate
contract; the current results concern Linux/SPE on A1222.

| Revision / run | Change and reason | Verified result / remaining work |
| --- | --- | --- |
| `5314411` | Pin Debian sources, add fresh extraction/re-patching runner and first component patches | Tabor machine/DTS patch plus preparatory 36-file glibc import. Neither patch initially proved a complete build. |
| `0fce93d7-aeb9-4fdf-9165-5a7b6834c10c` | First BKC attempt, unpacking on shared NFS | Tools image built. Unpack was I/O-bound and intentionally stopped; no compiler failure inferred. |
| `12c10c7` | Move active work to local disk with free-space guards | Preserve diagnostics and use fresh work for retries. |
| `23fa71a4-4dbb-49a3-9249-8333c3312e4b` | Apply patches to real Debian sources and cross-compile board targets | Tabor object and DTB passed; object is 32-bit big-endian PowerPC ELF. Full kernel interrupted because olddefconfig re-enabled DWARF. glibc patch applied but compiler rejected SPE flags. |
| `02cf5eb` | Select DEBUG_INFO_NONE explicitly and retain evidence before deleting disposable trees | Seven tests passed. Exact scoped artifact hashes: [first iteration receipt](builds/20261030-first-debian-iteration.json). |
| `4c8d17fa-5380-402a-ab11-42e9a528e19f` | Fresh retry with corrected config | Initial 4 GiB free-space guard stopped kernel extraction because duplicate staged archives consumed space. This is infrastructure, not a patch failure. |
| `b57b3f7b-cc3c-43b4-95a7-31b11186478b` | Replay from the canonical verified archive cache using a 150 KB project bundle | Fresh Debian extraction, local patches, DEBUG_INFO_NONE assertion and scoped board/DTB checks passed. Full vmlinux/modules/dtbs compile passed; collected artifact hashes verified. glibc compiler preflight remains failed. No board boot/ABI acceptance. |

The archive cache is now deduplicated independently of small project/patch
bundles. Cached archives remain hash-checked and read-only in containers;
every source/object workspace is newly created and re-patched. Completed-run
duplicate cache copies were compared before removal; the canonical cache and
local downloaded originals remain. An attempted bulk archival copy to NFS timed
out; no partially copied file is used as a verified cache entry.

## What reviewers can assess now

- Actual Tabor platform/DTS source changes and retained upstream notices.
- The recovered e500-only glibc files and their exact removal-history origin.
- Fresh-run logic, source/patch checksums and explicit failure handling.
- The compiler prerequisite: current Debian GCC rejects `-mabi=spe`, `-mspe`
  and `-mfloat-gprs=double`; modern SPE userspace is not working yet.

Full compile evidence: [Debian kernel receipt](builds/20261030-full-debian-kernel.json).

Next: QEMU e500v2 boot smoke test, then GCC SPE restoration
and the remaining glibc shared-state/configuration work. Kernel boot wrapping,
real A1222 serial boot, audio/power controls and runtime ABI tests remain pending.

## 2026-10-30 — QEMU boot accepted

Full Tabor kernel compilation passed independently. The initial minimal QEMU
profile required configuration dependency fixes; its first linked kernel was
silent because PHYS_64BIT/SERIAL_OF_PLATFORM were missing. Fresh attempt-005
with both enabled booted Linux 6.12.113 under QEMU 10.0.13/e500v2, brought up
two CPUs and reached freestanding PPC32 init. No panic during 60 seconds.
[Boot receipt](builds/20261030-qemu-boot.json) and
[serial proof](builds/20261030-qemu-serial.log) retain exact evidence. Artifact
manifest, kernel/config/init hashes verified; seven workflow tests pass.

Two desktop-4 capture windows show build/serial and an ANSI edge CPU/RAM
monitor. Guest metrics are explicitly pending. [E-Trixie follow-up](e-trixie-follow-up.md)
records the laptop-style live USB intent and direct SPE → SDL software →
SDL/GL → real A1222 AMD validation gates. No distribution image is built yet.

## 2026-10-30 — direct SPE arithmetic and graphics limits

The same booted QEMU kernel now runs a libc-free init executing known-result
single/double SPE additions and register load/store. Exact results passed;
serial/initramfs/source hashes verified and disassembly retained. See
[arithmetic receipt](builds/20261030-qemu-spe-arithmetic.json). Full ABI, glibc
and GL are still unvalidated. Desktop-4 monitor shows the narrower PASS.

[Minimal E/gears work](minimal-e-gears.md) records the unavailable edge GPU,
stock VirGL little-endian limitation, physical USB preference and a verified
staging bundle. No compatible rootfs/reference firmware packaging is currently
available, so no boot-ready USB or E/gears execution is claimed.

## 2026-10-30 — matched fractal timing demo

[ASCII report](builds/fractal-20261030/results-ascii.txt) and
[comparison graphic](builds/fractal-20261030/comparison.png): software FP
median 446.341 ms, explicit SPE median 173.063 ms (2.58x in this QEMU run).
Three timed trials per path after warmup; identical escape-count images.
Raw evidence, helper provenance and [replay recipe](../bench/README.md) retained.
This is a freestanding CPU demo, not a restored C ABI/glibc or GL/physical
A1222 performance result. Initial failed timing probe is documented separately.

## 2026-10-30 — minimal live-image package plan

[Incremental seeds](minimal-package-plan.md): serial rescue -> E/Xorg ->
GL/DRM tests, with Firefox as an optional final increment. One normal console
login, startx and no greeter; mandatory dependencies retained, optional
services excluded by default. Machine-readable JSON validated. All target
runtime code requires our restored SPE compiler/glibc; source pins/dependency
closure, RAM/firmware and exact Radeon identity remain execution gates.

## 2026-10-30 — fresh SPE libc retry and media check

Ported historical fenv syscall calls to glibc2.41 interfaces (patch3). Fresh
Debian preparation passed; edge libc attempt3 is running, not ABI-accepted.
Retained failed iteration evidence and reclaimed generated trees. Seven
workflow tests passed. Read-only A1222 ISO probe reached Sam460 firmware only;
[receipt](builds/20261030-os4-iso-probe.json) records limits and media hashes.

## 2026-10-30 — graphical AmigaOS probe and libc tool selection

Nested QEMU under existing Proxmox VM127 loaded A1222 ISO Kickstart modules,
then remained at launching Kickstart; no Workbench. Local browser console
verified connected; [receipt](builds/20261030-os4-display-probe.json) distinguishes
bootloader progress from OS boot. SPE libc retry reached target object cleanup
but selected host objcopy. Fixed target OBJCOPY/STRIP; fresh005 retry started.

## 2026-10-30 — QEMU ATI experiment prepared; USB still gated

Signature-verified QEMU 11.1.3 source build running, with bounded ATI probe
queued. [Private overlay/configuration](qemu-ati-test.md) pins driver0.1 and
keeps non-redistributable content outside Git. Actual accelerated OS test needs
matching machine media. [USB first-boot gates](usb-first-boot.md) retain the
rear-port preference; no stick write yet. Libc006/stage5 retries with host C++
discovery disabled for the C-only bootstrap. Seven workflow tests passed.

## 2026-10-30 — fresh SPE libc and interactive shell passed

Experimental glibc2.41 compiled/installed, then static BusyBox plus native init
booted on the accepted e500v2 kernel. Commands returned ppc and real proc memory
values without panic. [Raw evidence and receipts](builds/shell-20261030/receipt.json)
retain exact hashes. Fixed BusyBox configuration/flags and removed the script
init dependency. Full SPE ABI and real-board boot remain unvalidated. QEMU11
replay is queued behind its corrected internal-libfdt build; old ISO guest stopped.

## 2026-10-30 — updated emulator pass and physical-image gates

QEMU11.1.3 now builds and [boots the fresh Linux shell](builds/qemu11-20261030/linux-receipt.json),
with real commands and no panic. Shared terminal editing, Ctrl-C and line endings
are fixed. Basic C ABI results are partial: arithmetic/formatting/context pass,
fenv rounding fails in both emulator versions and pthread needs kernel futex.
[ABI evidence](builds/abi-20261030/receipt.json) stays below full acceptance.
The bounded updated OS4/ATI probe did not show Workbench.

Source-built live image plan now includes SSH and physical-display VNC.
Standard U-Boot board payloads pass CRC/decompression checks, but HDMI
controller/driver and USB keyboard module inclusion still need resolution
before writing the authorized SanDisk. User has Elgato; device is detected,
frame reads failed. R730 is booting its expected Trixie image; changed old-address
SSH key means OS identity is not yet verified, and no work was deployed there.

## 2026-10-31 — larger rescue image built on R730

[Workflow and VM132 target](r730-live-image.md), implementation `4fe159f`.
R730 now builds fresh Linux iterations; board kernel, richer RAM rescue image,
Polaris firmware and static key-only OpenSSH are assembled into a verified
2 GiB FAT32 boot image. This is the shell-first increment toward the E desktop.

[Native SSH/QEMU evidence](builds/r730-live-20261031/network-probe-003/receipt.json)
passes key login, uid1000/home permissions, PTY and matched CLI fractal execution.
[ASCII results](builds/r730-live-20261031/results-ascii.txt) record identical
pixels and emulator-only timings. Eight basic ABI checks pass, including
pthread/TLS; fenv rounding still fails. No complete ABI or physical/GPU claim.
Early network failures and exact final config are retained alongside successes.

The authorized SanDisk write is complete: [full-image readback receipt](builds/r730-live-20261031/usb-write-receipt.json)
matches the file image SHA256. [Temporary boot commands](builds/r730-live-20261031/BOOT-README.txt)
are ready for the real-board trial; saved firmware settings remain unchanged.

## 2026-10-31 — larger desktop prerequisites: split the fenv failure

[Detailed diagnostic](fenv-rounding.md) separates working mode/exception APIs
from failed directed-rounding arithmetic in QEMU. Exact register values, fresh
probe receipt and source-review hashes are retained. This narrows the failure
to an emulator-state hypothesis; no workaround or relaxed ABI acceptance.
R730 is separately building an isolated historical SPE C++ compiler/runtime,
which the prior C-only bootstrap lacked, before graphical-source builds.

## 2026-10-31 — reference C++ runtime and shared-library execution

[R730 desktop foundation](desktop-foundation.md): fresh GCC8 C/C++/libgcc/
libstdc++ build completes after correcting target binutils aliases. Static and
shared C++ probes pass 128-bit long-double size, exception/RAII unwind, thread
TLS and uint32 atomics. The shared probe executes through native SSH into QEMU;
prior fractal/C tests still pass except the unchanged fenv failure. Failed
archiver and weak-static-pthread checkpoints remain in the evidence trail.

Exact EFL/E/Terminology sources from VM132 are cached, hash-pinned and inspected
for licensing/build options. A lean software-X11 candidate is recorded, with
native code generators and target dependency closure still to resolve. A new
shared-runtime boot image passes file-image packaging/readback on R730; the
written SanDisk is unchanged. E/Xorg/Mesa and physical boot are not accepted.


## 2026-10-31 — software desktop prerequisites execute in the SPE guest

[Source build and evidence](desktop-base.md): fresh R730 iteration 002 builds
Debian zlib, security-updated libpng and Pixman using the reference SPE compiler
and isolated restored libc. Explicit target flags, AltiVec disabled, no generic
PowerPC binary substitution. Three shared-library CLI checks pass through SSH
in the existing QEMU guest: compression round-trip, PNG RGBA round-trip, ARGB
compositing copy. Existing desktop 4 guest remains running. Failed iteration001
and its libpng CPPFLAGS correction are retained. Sources/licenses/hash locks,
native image/package identity, recipes and runtime receipts are captured.

This completes only the first software prerequisites. X11/font dependencies,
native EFL generators, cross EFL/E/Terminology/Xorg remain. The known fenv
failure, Mesa/GPU gate and physical/U-Boot/HDMI validation remain unchanged.


## 2026-10-31 — four-theme A1222 desktop selection

User requests Fire, Molten Steel, Frosty and Minty in the future E image.
Recorded exact local theme/still-wallpaper reference hashes and target selector/
rendering gates in profiles/images/a1222-theme-selection.json. No target install
or asset publication yet; held-back Fire Strong Animated remains excluded.


## 2026-10-31 — restart source-built X11 dependency jobs

[Active workflow](x11-build-cycle.md): pinned 22 Debian source packages and
launched detached, constrained offline R730 X11 client builds. Fresh iteration001
built protocol/transport headers, then rejected an unexpected license filename.
Corrected notice handling; fresh002 compiles against the accepted read-only SPE
compiler/libc and source-built software prerequisites. Live receipts expose
active component/status; desktop4 log view now follows the latest iteration
with explicit state. No Xorg/E session or full ABI acceptance claimed.


## 2026-10-31 — X11 cross-build blockers fixed and protocol tests pass

Fresh004 builds all 22 X11 client components and checks 48 target ELF files.
Fixed stale installed public-library libtool metadata; measured Xorg allocation
configure predicate on the SPE guest before setting scoped cache answer. Failed
002/003 receipts and output remain. No upstream ABI/source patch required.
SPE QEMU client passes pixel readback, Render/RandR/XFixes queries and XCB
request/reply against a separate native Xvfb server, now stopped. See
[x11-build-cycle.md](x11-build-cycle.md) and its raw evidence links.

GitHub issues1/2 track these corrections; issue3 retains unresolved fenv failure.
Continue source-built fonts, native EFL generators and Xorg/E stages; no target
server, physical GPU/HDMI or complete ABI acceptance follows from client proof.
