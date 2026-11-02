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


## 2026-10-31 — software E session filesystem build underway

User requests another filesystem and QEMU boot into E. Added locked session
source chain and separate native generators, target dependency/EFL runners,
and runtime staging/startup preparation. Expat/font/image/shaping libraries
build; missing GCC8 libatomic now builds and passes threaded64-bit guest test.
Fresh OpenSSL/curl/D-Bus build succeeds; Lua's Debian generated-header step is
included, with keyboard/font/Xvfb/VNC compilation continuing. Retain prior
failures and issue4. No target E/X server boot yet; software-e-session.md records
scope, exact tools image and remaining runtime acceptance.


## 2026-10-31 — SPE target X server boots; EFL builds

Software-session source dependencies and EFL1.28.1 now build. Fixed CMake target
library directory, specified real font path, added mandatory minimal sndfile/GIF
APIs. Separate x11-root001 reaches shell/SSH; target Xvfb/VNC and target client
pixel/protocol tests pass, with Fontconfig font discovery and OpenSSL execution.
No E desktop yet. E 0.27.1 source needs optional-Eeze configure and ACPI watcher
guards; ordered hash-checked patches are building in fresh e-session003. Retain
all prior failures and runtime proofs; issues4/5/6 expose current corrections.


## 2026-10-31 — Separate filesystem boots into E; rendering fault retained

Completed EFL1.28.1, E0.27.1 and Terminology1.14 target SPE builds. Three
minimal no-Eeze source guards are hash-pinned; source iterations and failures
remain retained. New root002 contains the selected four themes/still wallpapers,
without the stock400MiB gallery or held-back Fire Strong Animated. Compressed
archive round-trip/hash verification passes; launch now rejects incomplete roots.

Software-e003 boots the new root using ramfs to avoid the minimal kernel's tmpfs
size limit. Shell/key-only SSH, target Xvfb/VNC and interactive E wizard run;
standard profile reaches wallpaper, shelf, icons and window frames. Client
interiors are black, so this is a partial graphical boot, not clean desktop
acceptance. Screenshot, runtime/serial logs and exact receipts are retained in
docs/builds/r730-software-session-20261031. Desktop4 noVNC6089 shows this guest.
Issues7/8 track integration omissions and rendering respectively; issue3 remains
open. No physical A1222, Radeon, OpenGL or full SPE ABI acceptance is implied.
Next: isolate non-SHM compositor readback versus direct client drawing, then
repair and repeat the graphical test before preparing hardware USB media.


2026-10-31 E log review: read actual ~/.e-log.log and rotated log, not just
launcher output. Confirmed four disabled-module/profile mismatches, unprivileged
system-helper error, missing system D-Bus/UPower, Xvfb DPMS polling noise and
kernel inotify omission. Retain non-finite-number, Eo object and thread/font
warnings without assuming their cause. No OOM/crash event found in sampled
serial log. See builds/r730-software-session-20261031/log-review. Guest unchanged;
issues7/8 remain open for integration and rendering.


2026-10-31 package/hardware increment: actual private powerpcspe .deb bundles
install into a fresh offline root with recorded ownership/modes. Native dpkg
1.22.22 + libmd build and query/audit the installed guest. Fresh qemu-live007
adds HIGHMEM/SYSVIPC/inotify; 8GiB guest reports8248388KiB and CPUs0–1 online.
Both pinned-core SPE arithmetic/64MiB page-pattern checks pass. Physical kernel
already has SMP/MMU/HIGHMEM/PHYS_64BIT/PTE_64BIT/SPE/SWIOTLB; firmware memory map
and real-board execution remain unvalidated. Board age/link suggests Plus, not
an exact revision measurement. Version0.3 root fixes service boot ordering:
mount /dev before system D-Bus. Messagebus and E root helper run; black client
interiors persist, so issue8 remains open. 6089 now points at software-e007.
See package-hardware-readiness.md and builds/r730-packaged-session-20261031.
Mesa/libdrm sources are pinned/audited; no GL/Radeon runtime pass claimed.


2026-11-01 reconnect: R730 restarted, artifacts intact; reverified accepted
kernel/root and launched software-e008. Package audit clean, ~7.87GiB usable and
two online guest cores. E starts from fresh RAM-root state. Moved noVNC proxy to
a bounded loopback-only R730 service; kept6089 local entry via SSH, removed local
proxy and three retired test forwards. No local builds/VMs or extra viewer
windows started. Laptop resource policy is now in AGENTS.md; no crash cause is
inferred from current memory snapshots. See reconnect-resource-policy.md and
builds/r730-reconnect-20261101. Rendering/GL/physical tests remain outstanding.


2026-11-01: Fresh0.4 installed-image QEMU test passes key SSH,8GiB/SMP,
software GL readback and matched SPE fractal visualization. Added an explicit
Debian installation-state gate: FAIL because only lab bundles are installed.
Do not confuse dpkg audit success with native package setup. USB unchanged;
normal Debian binary-package/configuration integration is next. Evidence:
builds/r730-installation-round-20261101/README.md.


2026-11-01 live VM132 correction: inspected running reference via guest agent.
Confirmed broader omissions than package records: PAM/logind/udev, normal
Xsession/user-bus activation, packaged EFL engines/loaders, polkit/UPower/udisks
and Xorg libinput/EGL/GBM integration. Existing minimal build disables features
that reference packages depend on. Added VM132 session baseline seed profile;
resolve full target dependency closure and restore normal Debian session setup
before E acceptance. Retain lean profiles as diagnostics. See
builds/vm132-comparison-20261101/README.md. USB unchanged; causal rendering
fix and target package builds remain pending.


2026-11-01 browser/archive scope: user requests compact browser and considers
Gitea/simple HTTP package hosting for our custom compile. Added NetSurf GTK as
an unvalidated candidate (limited modern JS), plus signed lab HTTP APT archive
plan with normal package metadata/source provenance and one common SPE archive
for QEMU/A1222. Added apt bootstrap to baseline. No browser build, server
deployment or signing key creation claimed. See package-repository-plan.md.


2026-11-01 private media inspection: located FTP ISO/Enhancer, streamed six
selected documents read-only with 7z (no mount/install/execution). A1222 onboard
video notes describe early U-Boot display/keyboard limitations; keep installed
PCIe Radeon for boot trial. Enhancer RadeonRX history explicitly mentions
A1222 SPE copy/blitter/compositing optimizations, useful future workload clues
but not Linux graphics validation or source reuse. Recorded selected hashes
and factual summary only; media remains private. No USB/firmware changes. See
builds/os4-media-review-20261101/README.md.


2026-11-01 automated native-package increment: no active package job; built
pinned native debhelper tools image, added fresh hash-locked Debian package
runner and single-job R730 submit command (4CPU/6GiB, network off). Real libmd
SPE packages built via normal debian/rules with dependency checks enabled.
Recorded cross-sysroot shlibdeps fix and gzip bootstrap packaging adjustment;
retained six success/failure iterations. Actual library MD5/SHA256 vectors pass
in guest010. Target extraction exposed missing GNU tar (BusyBox lacks required
option), reinforcing need for full Debian Essential dependency closure. No
forced package installation or USB write. See debian-package-build.md and
builds/debian-libmd-20261101. E/graphics/fenv/hardware gates remain open.


2026-11-01 actual Trixie transition: pinned seven bootstrap source packages;
built normal Debian attr/libattr and dash packages. Fixed dash native-generator
LDFLAGS/sysroot contamination at source level; target shell smoke passes.
Glibc Debian powerpcspe registration/reference-compiler patch applies and actual
control generation succeeds; full libc packaging remains pending. Effective
QEMU config lacks cgroups/ACL/virtio-block; started bounded qemu-live008 rebuild
with corrected seeds/assertions. Full root becomes ext4 disk-backed with normal
Debian Essential/PAM/init/session/package state. No USB write or full Trixie
acceptance claimed. See builds/trixie-bootstrap-20261101 and the new
profiles/images/trixie-bootstrap.json for exact progress and remaining gates.


2026-11-01 status check: qemu-live008 kernel build exited0; receipt reports compiled. Cgroups/ACL/virtio-block config checks passed. New kernel and normal disk-root boot remain untested. No package job currently running; full libc package/Essential root bootstrap remains next.


2026-11-01 libc Debian bootstrap: packaged real native-host GCC8.5 SPE compiler
and installed it in pinned libc build image. Corrected architecture-specific
compiler dependency selection and supported stage2 dependency cycle; preflight
checks remain enabled. Iteration002 reaches libc link then native objcopy cannot
read PPC; explicit cross OBJCOPY export fixes selection. Fresh003 compiling
with ~stage2 version. Full-feature rebuild, installed root and runtime gates
remain pending; no forced dependency/status records. Six following library
sources pinned for normal SELinux/audit closure. See builds/glibc-debian-20261101.


2026-11-01 target policy (user clarification): preserve Debian behavior while
compiling/configuring for the A1222 SPE CPU, real memory/SMP and Radeon. Prove
this baseline on physical hardware, then measure/tune, then port AlpinE tooling
as native Debian packages. Flatpak excluded. Avoid importing Alpine/musl
binaries or porting tooling ahead of hardware validation. Current libc C++
unwinding regression remains the active prerequisite; do not stop that work.

2026-11-01 iteration003 runtime gate: seven real Debian glibc stage2 artifacts
built successfully. Candidate loader/libc/libm hashes match the .deb payload.
A dynamically linked C probe passes eight basic ABI checks; fenv rounding
remains failing. C++ exception unwinding crashes with SIGSEGV, unlike the
existing baseline. Offline core analysis locates the fault in dl_iterate_phdr
while obtaining the caller address; generated code reads an uninitialized
stack slot. Compiler/SPE frame handling is a hypothesis requiring a reduced
reproducer, not yet an established fix. Initial static-C loader attempts are
explicitly excluded from shared-libc acceptance. No target installation or USB
write. Next: isolate the return-address regression before iteration004.

2026-11-01 Hyperion handoff and compiler isolation: opened unwind issue #9 and
roadmap #10; updated fenv #3 with actual dynamic probe evidence. Added
docs/hyperion-roadmap.md separating Linux reference, portable probes and
OS4 SDK/runtime/kernel obligations. Reduced GCC8.5 probe reproduces SIGSEGV
with -fpic plus strong stack protection under both libc runtimes; ordinary
PIC without protection and non-PIC variants pass. Retaining frame pointers
does not fix it. Experimental SPE/ABI_V4 return-address patch keeps hardening;
fresh gcc-unwind-002 compilation running remotely, 4CPUs/6GiB. Candidate
runtime acceptance pending. No accepted artifacts, target root or USB changed.

2026-11-01 QEMU retest of rebuilt gcc-unwind-002: completed six modes against
both libc runtimes. Protected PIC and protected PIC+frame-pointer still exit139;
other modes pass. First candidate modified inactive rs6000 backend: actual
gnuspe uses config/powerpcspe/powerpcspe.c. Retained failed evidence; did not
promote compiler or rebuild libc. New0002 mirrors the depth-zero real-SP
correction from the same GCC8.5 rs6000 source into active powerpcspe; fresh
gcc-unwind-003 build submitted,4CPU/6GiB. Updated #9. Future build receipts
record selected backend; probe receipts hash cc1 as well as compiler driver.

2026-11-01 active-backend correction verified: gcc-unwind-003 rebuild passed.
All18 existing-QEMU return-address tests pass (nine modes, two libc runtimes),
including protected PIC, frame pointers and -O0. Guest uploaded bytes verified
by readback hashes. Package new compiler as8.5.0+tabor2 and require it in
Debian libc source metadata; fresh libc rebuild remains prerequisite for
original C++ unwind acceptance. Keep #9 open until that passes; fenv #3 and
hardware gates remain open. Evidence: builds/glibc-debian-20261101/006-*.

2026-11-01 libc004 runtime acceptance: seven real Debian stage2 artifacts
built; library hashes match .deb payload and guest readback. Original C++
exception/RAII unwind, LD128, thread/TLS and atomics now PASS, versus003
SIGSEGV. New compiler/new libgcc_s/libstdc++ combination also passes all4.
Dynamic C eight basic ABI checks pass; directed rounding remains FAIL (#3),
not suppressed. #9 original regression gate satisfied. Evidence007-*.
Desktop4 monitors and shell updated; bounded remote log rendering limits
laptop impact. noVNC waits for a new graphical image. No installed target
runtime/root replacement, full-feature libc or physical acceptance yet.

2026-11-01 next dependency increment: libcap-ng002 built five artifacts with
normal Debian nopython profile; libsepol001 built four artifacts. Package-
matched libraries pass read-back-hash-verified QEMU smokes with private libc004
(capability query/local clear/reload, policydb create/free). No privilege-
changing capability apply or policy enforcement attempted. Initial cap-ng001
failed shlibs metadata for ld.so.1; map loader to its actual libc6 owner and
retain failure. Checks stay enabled. Preserve package hardening flags while
appending SPE ABI. Fresh pcre2-001 building next, existing JIT-disabled target
configuration preserved. Desktop4 follows it. No target installation/USB write.

2026-11-01 dependency batch completed: PCRE2 also built and passed ASCII,
nonmatch and UTF-8 matching in system-QEMU; JIT disabled as Debian specifies
for powerpcspe. All three package-library smokes use verified .deb payloads,
guest readback hashes and actual libc004 mappings. Build frontend identity now
recorded. Evidence: builds/bootstrap-libraries-20261101. Continue genuine
dev-dependency closure for libselinux/audit/libcap2, then full-feature libc and
Essential root. No installed Debian root or graphical-image acceptance claimed.

2026-11-01 user build-policy clarification: Debian Trixie powerpcspe rebuild
above patched compiler/runtime/board foundations. Debian source Build-Depends
and profiles govern readiness; binary Depends/Pre-Depends govern installation.
Recipe allowlist is not an ordering/dependency solver. Added authoritative
docs/debian-port-build-contract.md and AGENTS instruction. Do not extend
ad hoc sysroot/shlibs accommodations across the archive indefinitely: prepare
real repository/build-root package state and use normal apt/sbuild mechanisms.
Our tools enter as packages with real dependencies. Native/target roles and
bootstrap/full-feature phases remain explicit; normal setup/scripts preserved.
Fresh source --check-dependencies-only invokes dpkg-checkbuilddeps before
compilation; blocked inputs stay blocked. Current runner is not yet an apt/
sbuild dependency service. Auditing the next real source dependency gates and
a known-ready bootstrap source; no new compilation/target installation claimed.

2026-11-01 Debian preflight verification complete: libselinux/audit/libcap2
correctly dependency-blocked; known-ready libcap-ng nopython profile passes
without building. Exact source requirements and Debian exits retained under
builds/debian-dependency-preflight-20261101. Next gate is genuine repository/
build-root dependency state, not another hand-sorted list or disabled check.
Desktop4 displays that gate; no new compilation or root configuration occurred.

## 2026-11-01 — keep package builds powerpcspe only

User corrected the attempted native-library expansion. Stopped the isolated
`tabor-debian-glibc-amd64-003` container (exited 137) and removed the uncommitted
amd64 package-build route and native package overrides. Existing Debian host
utilities remain build tools; no native libc rebuild is part of the plan.
The pending target archive manifest now lists powerpcspe only and excludes the
separate host cross-compiler package. Earlier mixed-architecture archive/solver
receipts remain historical experiments, not an accepted installation route.

The signed archive experiment authenticated package indexes, but foreign libc
coinstallation hit Debian's matching-version requirement. Building native libc
counterparts was the wrong scope; the next step is a target-only package-managed
root/dependency closure, retaining normal Debian installation semantics.
No new target root or QEMU boot acceptance and no SanDisk write are claimed.

## 2026-11-01 — SPE-only archive, kernel/storage proof and live filming session

Built genuine SPE-only linux-libc-dev via Debian's UAPI packaging rules and
rebuilt gzip with preserved explicit ABI flags. Compiler defaults independently
remain8548/SPE/double-GPR/LD128; no architecture switch was observed. Packaged
gzip payload passes a hash-verified compression roundtrip under private libc004.
Signed archive005 now contains30 target .debs; target-only apt development
closure resolves. Essential installation closure remains incomplete and is
retained explicitly, with seven more source inputs cached/hash-locked.

Kernel008 boots with two CPUs,8240288kB usable RAM, cgroup2 controllers and
virtio/ext4 write/unmount/remount proof. New software-e011 runs that kernel
with the earlier diagnostic RAM root, verified equal fractals and Mesa25.0.7
softpipe GL pixel readback. Desktop4's existing noVNC6089 now shows that live
recording loop; guest shell/monitors updated individually. E compositor remains
issue8; fenv issue3 and physical Radeon/board acceptance remain open.
Physical tabor-live002 kernel rebuilding on R7304CPU/6GiB, briefly paused while
bringing up the viewer and then resumed. No new complete Debian root or USB
write is claimed. Next: finish board-kernel build, preflight/build base-files
and Debianutils, then close actual Essential dependencies and run normal target
package configuration before assembling the new disk-root image.
Evidence: builds/boot-candidate-20261101/README.md.

2026-11-01 Molten Steel profile: conservative standard-derived E configuration
prepared and tested on isolated display2/private HOME. Molten theme precaches,
E reaches shelf/startup, but final screenshot remains black even with software
rendering/no DRI swap/no SHM/C locale. Test stopped and loopback5925 removed;
working display1 recording stays live. Missing diagnostic dbus-send also noted;
no package state fabricated. Keep rendering #8 open. Board tabor-live002 kernel
compiled successfully; base-files001 genuine Debian SPE package built normally.
Neither is hardware/installed-root acceptance. Evidence: builds/e-molten-safe-20261101.

2026-11-01 session-base audit: diagnostic guest lacks /dev/shm and /run/user;
PID1 is a shell, despite mounted proc/sys/dev/devpts. E logs show animator
delays/DPMS warnings, not a decisive render failure. Retain incomplete Debian
session setup as an open cause; see builds/e-molten-safe-20261101/session-base-audit.md.

2026-11-01 complete desktop gate: full selected application closure with normal
APT recommendations is required, beyond Essential/development subsets. Actual
signed-archive desktop simulation008 fails as expected. Infra006 adds host
po4a; Debianutils002 compiles but shlibdeps cannot locate target libc. Essential
preflights retained (diffutils ready; findutils/grep/sed/mawk dependencies missing).
Next correction is a shared genuine package-aware build environment, not more
per-package shlibs overrides. See builds/debian-desktop-closure-20261101/README.md.

2026-11-01 shared cross-libc packaging repair: receipt-pinned Debian dpkg-cross
conversion plus normal host cross-runtime package installation fixes library
discovery without new per-package shlibs patches. Debianutils003, Diffutils002
and Mawk002 build genuine SPE packages. Corrected pure scripting/data -A mode
removes target CC/sysroot and permits normal tests; no amd64 binary packages
are emitted. Debconf003 builds; init-system-helpers005 passes8 suites/1064 TAP
checks after restoring host Perl files excluded by the slim image. Signed
archive007 contains42 artifacts; full Essential/desktop closure still blocked.
Next: actual target development dependency closure for dpkg/base-passwd and
normal Essential configuration, not RAM-root patching. Evidence: builds/cross-development-20261101/README.md.

2026-11-02 scope/fail-forward correction: VM132 functional application collection
is the target; the66-seed desktop is an intermediate gate. R730 core queue001
attempts17 pinned sources from a frozen snapshot, one constrained container at
a time, independent of laptop/editor lifetime. Debian preflights remain enabled;
failures/blocked items are retained in deferred.json while later sources run.
Observed base-passwd blocked followed by a successful media-types build.
See builds/core-queue-20261102/README.md; this is not a completed target root.

Core queue001 finished17 attempts: media-types/adduser built,15 deferred.
Installed real host tools in infra012 and retry queue002 built keyring,
ca-certificates and tzdata with tests enabled. Combined:5 new source builds,
12 still dependency-blocked; normal target dependency/root acceptance pending.
Both complete/deferred receipts retained in builds/core-queue-20261102.

Reviewed successful queue artifacts added to signed archive008: 48 artifacts;
signature/selected-library check passes, full Essential/desktop still blocked.

2026-11-02 coverage correction:17 was only the selected queue. Audit verified
93 distinct pinned cached sources,19 with some archived build evidence plus
separate Linux route;73 remaining sources entered broad dependency readiness
queue001. All12 old failures are pre-compilation dependency blocks, including
already-built dev packages not installed in the effective build environment.
No new compiler regression demonstrated. See builds/source-coverage-20261102.

Broad readiness completed73 sources:70 dependency-blocked,3 ready. Actual
ready-source builds pass for libpthread-stubs/libxcvt; zlib exposes missing
minizip --build/--host tuples. Added pinned source-level packaging fix and
started fresh203 retry. Cached8 previously missing dependency sources; total
pinned cache inventory now101 sources. Dedicated9-source retry/dependency build
pass runs on R730 with failures deferred; full target root still not accepted.

Evaluation update: dependency203 pass finishes7 dependency blocks, GMP C/C++
compile followed by missing target libstdc++ package metadata, and zlib internal
link failure after corrected cross configure. Added minizip-style -lz linkage
to miniunzip and started fresh204 retry. Genuine GCC runtime/development
packages plus installed target dev state are the highest-leverage next gate.

Final zlib205 packaging passes with3 observed cross-build fixes; no target
self-tests are attempted on the host with requested nocheck. Target runtime
remains untested. libpthread-stubs202/libxcvt202 also built. GMP203 remains
blocked after compilation by unowned target libstdc++ dependency metadata.

Reviewed actual new build receipts indexed in signed archive009: 57 artifacts;
signature/development subset check passes, full Essential/desktop still blocked.

2026-11-02 runtime packaging: created genuine target libgcc-s1/libstdc++6
packages from the provenance-checked recorded GCC8.5 build, with debhelper
shlibs/Depends and upstream notices. Converted those real artifacts only for
host cross-development metadata. Cleaned four bootstrap libtool archives from
the relocated host SDK; original tools tree unchanged. Offline environment
installed all3 packages normally and passed dpkg audit. Fresh GMP301 runs with
the installed SDK on R730 (4CPU/6GiB). No target execution in the build stage;
73 sources is working scope, not dependency/boot acceptance by count. Details:
builds/runtime-packaging-20261102. Full target root and graphical gates remain.

GMP301 finishes normal Debian packaging:5 packages, with target library
RUNPATH checks clean of /tools, /work and compiler SDK prefixes. This resolves
the demonstrated GMP203 metadata/build-path blockers; target runtime tests are
still pending. Signed archive010 now contains64 artifacts (was57). Its
signature/update and selected dependency checks pass; full Essential/desktop
closure remains blocked. No new accepted root, graphical boot or USB write.
Next: install genuine already-built target development packages and close the
remaining core dependency source chain. See runtime-packaging-20261102.

2026-11-02 managed build-root transition: ordinary target development package
state remains missing despite archived binaries. Added explicit preserved-Debian-
version and package-managed-root recipe modes: keep upstream changelog/version
for normal library coinstallation, retain patch/compiler provenance in receipts,
and retire TABOR_SYSROOT/TABOR_SHLIBS transport overrides in that mode. No
installed version/status rewriting or native source counterpart rebuild.
Fresh libc401 uses corrected SDK, six patches and existing stage2/nobiarch
profiles as build-root-only bootstrap input; compiling/packaging on R730.
Pinned missing pkgconf1.8.1-4 source (native executable is a separate foreign
package; target package supplies cross scripts). Next: normal apt installation,
then real attr development package state and ACL retry. See
builds/managed-build-root-20261102. Final target root/graphics remain unaccepted.

Managed-root checkpoint: libc401 produced7 packages; libc6/libc6-dev install
and configure normally beside native tools with clean dpkg audit. Header401
retains Debian universal UAPI data/metadata and adds the gnuspe include tuple
via source patch, with no extra executable target compilation. Pkgconf401
exposes that missing path; pkgconf402 then compiles but reveals libc401's
OUTPUT_FORMAT(elf32-big) linker-script defect. Native/cross objdump comparison
confirms the producer cause. Seven-patch fresh libc402 now selects the cross
objdump; installation/fresh pkgconf acceptance pending. GitHub issues12/13
retain separate gates. Future manual submissions freeze recipe snapshots; the
serial queue launcher retains failures and continues independent sources.

2026-11-02 verified managed-root checkpoint: libc402/header401 and real target
library development packages install normally with clean dpkg audit. Pkgconf,
attr, libxcrypt, fribidi, pixman, mtdev and ACL source builds pass; subsequent
libmd/libcap-ng builds also pass. Remaining65 are dependency-blocked. Libsepol
and PCRE2 reveal the common SDK default /sysroot when normal Debian rules reset
CFLAGS. Issue14 tracks a fresh GCC8.5 rebuild with installed sysroot / and a
separate read-only build sysroot, running on R730 at 4CPU/6GiB; acceptance and
consumer retries pending. Archive011 has83 artifacts with bad old libc6-dev
explicitly excluded; full dependency closure remains blocked. No new graphical
image or USB write. See builds/managed-build-root-20261102 for retained evidence.

2026-11-02 compiler-default correction verified: fresh GCC8.5 source build
system-root001 and native SDK5 install pass. The installed compiler selects /
and the SPE/no-FPR/IBM128 big-endian ABI by default. C/C++ header/compile/link
checks pass without injected target flags; all9 tool lookups select cross
binutils. Libsepol502 and PCRE2-502 then complete normal Debian packaging.
Managed recipes now validate those defaults and leave maintainer flags to
Debian. Retained evidence: builds/sdk-defaults-20261102. Native build-tool
installation is running; reviewed +b1 binary rebuild support and a20-source
core/X11 dependency wave are prepared but not yet accepted. Full target root,
normal-feature libc, graphical/runtime and physical gates remain pending.

2026-11-02 dependency-wave result:15/20 sources pass, xz fails independent-doc
packaging,4 sources defer on actual Build-Depends. Normal target -B versus
independent -A selection fixes xz without a source patch; fresh504 passes and
its real development package installs. Reviewed binary-NMU versions allow normal
ACL/libmd/libcap-ng coinstallation. Native generators stay native; libjpeg
compiles but needs a help2man source-recipe correction (issue16). GPM/LZ4/xxHash
sources are pinned with authenticated apt metadata and preserved licenses.

Actual development-root installation exposes GCC8/host-GCC14 runtime identity
collision. Real build-root-only runtime providers contain canonical target ELF
bytes, truthful8.5 versions/Provides, normal shlibs and apt configuration. GMP
and other library development packages now install with clean audit; native14
remains present. Static packaged-byte and canonical dependency-generation checks
pass; no target execution. Providers are barred from the final target archive.
A queue accidentally submitted against an earlier root is retained separately;
verified-root retries follow checked validation. See sdk-defaults-20261102.
Full target configuration, normal-feature libc, ABI/runtime and graphics remain.

2026-11-02 follow-up checkpoint:507 retries pass GPM/JPEG/PCI/font encoding;
GMP506 and PNG506 also build in the real runtime-managed root. JPEG's ordered
native-generator/help2man/SPE-symbol-registration patches preserve strict ABI
symbol checks. GPM +b2 normal coinstallation passes after generating exactly one
well-separated binary-only changelog stanza; source header bytes are preserved.
Source outputs from15 selected latest builds pass static inspection:67 package
artifacts,69 ELF files, all ELF32 big-endian PowerPC. JPEG/PNG/PCI/font target
development packages install normally. Next serial queue builds ncurses/LZ4
against actual installed GPM/xxHash. This is still a cross-build root; complete
target setup, full-feature libc, runtime/graphics and bare-metal gates remain.

Latest follow-up: LZ4-508 source compilation/packaging and normal development
package installation pass. Ncurses508 exposes missing linux-gnuspe in its
GNU/Linux feature-test case; wide C lacks wcwidth declaration. Version/hash-
pinned source patch registers the tuple in existing GNU handling, preserving
wide support and error checks. Fresh ncurses509 then zstd509 queue runs against
the verified LZ4-managed root, constrained4CPU/6GiB. Issue18 retains that gate;
new desktop target image remains unaccepted.


2026-11-02 accepted follow-up: ncurses509/zstd509 packaging and normal target
runtime/development installation pass; LZ4/ncurses/zstd static payload evidence
adds21 artifacts/117 ELF. Current constrained70-source iteration510 queue runs
on the R730; some core sources are dependency-blocked while independent builds
continue. Full target installation/configuration, full-feature libc and fresh
QEMU/physical image acceptance remain pending. See
[accepted dependency evidence](builds/sdk-defaults-20261102/README.md).


2026-11-02 cumulative dependency correction: real apt installs of SPE libxcvt,
SELinux C development/runtime, libbsd and readline now update subsequent build
roots. Grep520, libselinux520 (supported library bootstrap), libbsd/readline540
and previously blocked findutils/sed540 package successfully. Queue history
retains the local-apt option failure and metadata/workload guard failure; later
entries marked attempt-failed are infrastructure skips, not compiler failures.
Three scheduler regression tests pass. Native prerequisites now derive from
Debian build-dep across the source scope; missing target-source intake remains
explicit. OpenSSL's compiler path is fixed; its GCC8 register-clearing flag
limitation has a source patch pending full packaging. See
[cumulative evidence](builds/cumulative-dependencies-20261102/README.md).
Full target configuration, required binding/libc rebuilds and new boot acceptance
remain pending; no USB/image changes are claimed.
