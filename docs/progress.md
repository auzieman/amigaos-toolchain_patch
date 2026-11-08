## 6.12 GPU review checkpoint —2026-11-08

The next6.12 candidate compiles and passes all687 imported CRC checks against
the accepted kernel export table, with matching ELF32 BE and full vermagic.
It includes upstream ring-test ordering/error-propagation fixes and post-map
boundary markers. NXP's P1022 documentation identifies the captured ERR_DR bit
as an outbound completion timeout; the initiating GPU failure remains unproven.
See builds/gfx-postmap-review-20261108/README.md for source exclusions, evidence
and next controlled test. Candidate is staged inactive; live6.12 remains
healthy/dual-core with GPU unloaded. No boot/kernel/firmware changes this pass.

## Native GCC14/glibc milestone — 2026-11-07

The original SPE C ABI probe, compiled with GCC14 plus candidate patch17,
passes all9 top-level checks on the physical A1222, including varargs and
floating-point rounding, exit0 and kernel taint0. Fresh GCC14-built glibc2.41
loader/libc/libm were copied to a private /tmp directory and invoked explicitly;
no system libraries, kernel, USB boot files or accepted SDK were replaced.
Exact uploaded SHA256 and output: builds/gcc14-runtime-20261107/hardware-runtime-001.json.
QEMU user-mode still fails rounding with the same candidate executable/libraries;
do not weaken native libc semantics to accommodate that emulator result.

Patch17 restricts SPE subreg conversions to register operands, avoiding a
miscompiled spilled double-return conversion. Original ABI test passes varargs
at O0/O2 in QEMU. This checkpoint used libraries built before patch17: a fresh
bounded regression/libgcc/glibc rebuild is now launched on the R730 as
`tabor-gcc14-runtime-rebuild-002`. Full C++/unwinding/long-double and broader
cross-version/generic PPC regression acceptance, Debian packages and image
assembly remain open. Native Trixie workstation remains the end goal.

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


2026-11-02 workflow correction after user review: the custom cumulative-root
queue is bootstrap infrastructure, not a substitute for Debian's resolver/build
service. Freeze further custom solver expansion. The standard sbuild proof now uses
a clean mmdebstrap buildd root and genuine bootstrap packages as extra-package
inputs, with build=amd64/host=powerpcspe. Native build-dep superset completion is
not target readiness. See [source-backed workflow audit](debian-workflow-audit-20261102.md).
Continue remaining-source closure through the standard path after the proof;
retain resolver, infrastructure and source failures separately.


2026-11-02 validation direction: once the base load is package-managed, run a
separate serial QEMU validation stage for package batches, including normal apt
configuration, package tests/smoke tests and a final desktop/session gate.
Cross-building stays separate from target execution. QEMU and physical A1222
acceptance remain distinct. See [validation gates](qemu-package-validation.md).


2026-11-02 frozen baseline established: native buildd root002 passes exact
Linux headers6.12.115-2/glibc2.41-12+deb13u4 checks against snapshot20261102T220000Z.
Base lock and root hashes gate subsequent builds; no rolling-mirror fallback.
SPE UAPI009 rebuild is running on that root. Standard SPE libxdmcp acceptance,
remaining desktop closure and QEMU validation are pending. See
[standard-builder evidence](builds/debian-standard-builder-20261102/README.md).


2026-11-02 current fixed-path spot check: UAPI009 and libxdmcp006 pass standard
sbuild/apt in frozen root002. Historical resolver/source preparation failures
are retained as history, not asserted against these successful rebuilt outputs.
Libxcb001 continues the X11 dependency chain. User requests letting the build
finish, then launching the newly assembled image in QEMU; this remains pending
image assembly and normal package-install/configuration checks. No replacement
of the image by an older diagnostic boot is authorized by that request.


2026-11-02 dependency-first correction: libx11-002 passes using the previously
measured SPE configure answer. A real dependency-only crossbuild-essential SPE
port package now connects standard Debian dependency tooling to the genuine
frozen SDK/libc/UAPI inputs. Audit005 checks108 reviewed source groups:66 have
installable cross-build dependency sets,42 are blocked with full explanations.
Of49 still missing successful package receipts,12 are dependency-ready (data-only
work remains separate). Parallel batch002 runs up to4 jobs x4 compiler jobs/6GiB,
with apt installing native tools and SPE development packages before compilation.
The initial mixed-old-libc pool was rejected by apt and stopped; corrected inputs
pin libc402 and use Debian solver installation sets. All first4 jobs now pass
preinstallation and architecture checks. Full target image/QEMU acceptance stays
pending; see [current evidence](builds/debian-standard-builder-20261102/README.md).


2026-11-02 broad dependency coverage: control-center/Firefox ESR metadata from
the frozen snapshot yields99 individual relation probes,69 blocked. This expands
visibility, not the image selection. Parallel batch002 accepts16 source builds;
3 further attempts fail apt version selection and Lua fails shlibs packaging.
Exact Debian solver package/version/architecture/file identities now drive the
input set; cross-core metapackage2 includes real target compiler runtimes. Lua
passes in batch003. Dpkg/tar continue, while OpenSSL needs a retry with normalized
quilt patch line ranges. Earlier bootstrap source successes are preserved and
full-feature rebuild gates stay open. See current standard-builder evidence.


2026-11-02 verified follow-up: dpkg/tar/Lua now pass in batch003, bringing this
round to19 additional accepted source groups. The installed target compiler
runtime dependencies and exact solver-selected versions close those earlier
preinstall/shlibs failures. OpenSSL retry004 passes normal quilt --fuzz=0 and
source-package preparation, then proceeds to standard sbuild; final packaging
is pending. GNOME/control-center and Firefox remain dependency coverage probes,
not new image/application selections. Frozen kernel/glibc/compiler pins remain.


2026-11-02 libatomic/OpenSSL acceptance: the existing verified GCC8.5 SPE
libatomic build is now wrapped in normal Debian source packaging, with
canonical target runtime/development outputs and an explicitly build-root-only
runtime provider. This is recorded bootstrap assembly, not a fresh Debian GCC
source rebuild. Both packaging jobs pass static inspection and their shared
ELF payload hashes match. Cross-core metapackage3 installs the real atomic
runtime/development requirements. OpenSSL005 now produces six packages through
standard frozen-root sbuild; issue21's packaging gate passes. The source probe
explicitly records GCC8's unsupported register-clearing hardening flag.
A separate e500v2 QEMU-user threaded atomic64 add/CAS diagnostic passes in2.77s;
it is not installed-image or physical SMP acceptance. This round has20
additional successful source groups, including partial bootstrap outputs; it
is not a workstation completion percentage. Full-feature libc, ABI rounding,
normal target configuration, desktop paint and hardware gates remain open.


2026-11-02 Debian port service shift (user direction): ongoing desktop/package
work now routes to .agents/skills/tabor-debian-port, with a continuation prompt.
The R730 has roughly1.6TiB free and ample memory; stop minimal per-consumer
provisioning. port-build-server-001 preinstalls all available native build
dependencies for108 pinned source groups, including independent tools, in a
separate frozen Debian buildd template. Original DSC metadata drives apt;
package archives accumulate. Per-source sbuild roots remain disposable and
still install actual SPE dependencies normally. No native source rebuild.

The running provisioning pass has19 source groups successfully processed at
this checkpoint. An nspawn timezone bind initially blocked tzdata's ordinary
postinst; disabling that bind and normal dpkg configuration/retry fixed the
container issue without suppressing scripts. Prior attempts remain recorded.
Full template acceptance requires all selected dependency sets, clean apt/dpkg
and unchanged foundation versions. It has not passed that final gate yet.

port-dependency-intake-001 uses actual Debian dose failure relations and signed
frozen source/binary metadata to discover35 producer candidates outside the
old inventory. port-dependency-source-cache-001 is caching their archives with
source-index hashes. These candidates include native-helper/profile questions
and compiler-related producers requiring review, not35 required new target
ports or permission to change the frozen compiler. No candidate is declared
ready, built or installed by metadata discovery. Shared prerequisites now
advance before unchanged blocked consumers are submitted again. See
docs/builds/port-build-server-20261102 for retained discovery/checkpoint data.


2026-11-03 post-reboot: R730 retains the completed native provisioning root
(108 source dependency sets;1,278 installed native packages, clean audit and
frozen foundation). Cross batch005 accepted libICE, Oniguruma, libunistring,
db-defaults, libidn2, ruby-defaults and slang2. FUSE needs conditional libatomic
linkage in its C++ example (issue23); Java defaults lack an SPE runtime mapping.
Six further authenticated producer sources are cached; base/compiler unchanged.

The full template exposed a server infrastructure issue: /tmp tmpfs charged
its unpacked root against6GiB worker limits. A first disk path then failed
mapped-user traversal through the private source parent. Both remain failed
infrastructure attempts, not source regressions. The current disk temporary
area is outside that private parent; all four workers reached root extraction
without changing private source permissions or memory caps. Cross batch008
and independent-data batch003 are running. A native -A/dose mode builds only
universal script/data packages; static acceptance excludes ELF and amd64
binaries. See builds/port-restart-20261103 for evidence and remaining gates.


2026-11-03 scripted port cycle: scripts/submit-port-build.py now freezes and
submits the reviewed scope/recipes to one R730 controller. It prepares modified
DSCs before profile-aware Debian dependency checks, builds ready sources with
sbuild, reuses verified artifacts and records classified fallout. Deferred
metadata candidates are not a build-all list. A queued --after-run round waits
for its predecessor rather than overlapping package workers.

Verified packaging results: native dh-golang1.63+spe1 fixes C/SPE backend
discovery without enabling unsupported Go/SPE; four regression checks passed.
Popt/Tcl-defaults, corrected xorgproto, libtool/libltdl and the DB C library
built successfully. No SPE Fortran compiler was built: its libtool dependency
is qualified to the checks that already omit it in nocheck cross builds.
Receipts are retained under builds/port-pipeline-20261103.

The current round002 is building library prerequisites; round003 is queued
with corrected libffi symbol metadata. Dependency indexing excludes historical
source-version variants using actual package controls, keeping reviewed
foundation exceptions explicit. SQLite/Tcl/ICU producer sources are pinned to
the same authenticated frozen snapshot. Full patched glibc source registration,
remaining dependency closure, target installation and a new QEMU/image gate
remain pending. No USB write or physical Radeon/SMP acceptance occurred.


2026-11-03 pipeline003 evaluation: rounds002/003 completed-with-fallout;
no workers remain active. New accepted target package receipts: round002
libselinux, Tcl8.6, ICU and SQLite; round003 libffi. There is one observed
source-build failure (util-linux),45 unique dependency-blocked sources, and
a full patched-glibc source-registration gate. Counts describe selected
reports, not the complete final installation closure.

util-linux's first error shows both /usr/include/linux/mount.h and the SDK's
lib/gcc/powerpc-linux-gnuspe/8.5.0/include-fixed/sys/mount.h declaring
fsconfig_command; mount_attr also conflicts. Investigate stale GCC-fixed
header provenance/selection and reproduce with a minimal include probe before
patching util-linux. This is a demonstrated SDK/header integration suspect,
not evidence of a new util-linux algorithm defect.

Shared dependency chains require supported bootstrap review: libcap2 -> PAM
-> systemd -> libcap2; audit -> krb5 -> e2fsprogs -> util-linux -> audit;
DBus -> AppArmor -> Apache development dependency. Python/GIR-qualified
requirements also block Brotli/ALSA/newt/Harfbuzz/Avahi. Inspect original
profiles/native annotations rather than automatically adding language or
web-server ports. X/Mesa/E wait on these foundational libraries.

Controller review: util-linux retried the identical fingerprint in003 after
failing002. Current failure suppression spans stages within one run, not
completed predecessor rounds. Carry forward predecessor failure evidence
while allowing a changed recipe/dependency set to retry. Do not submit another
unchanged broad round. New target image/QEMU/physical tests remain pending.


2026-11-03 shared SDK correction: GCC8 fixincludes machine-name rewriting
corrupted five __has_include Linux path string operands. SDK revision
8.5.0+tabor6 repairs those generated strings centrally during packaging;
core adapter1.0+spe5 pins the correction. Compiler source/frontend, SPE ABI,
target runtimes and frozen Debian baseline are unchanged. All sbuild SDK
inputs explicitly identify the corrected packaging revision. The immutable
base lock continues to record its original SDK baseline.

Header regression003 reproduces original mount/rseq failures and passes all
five corrected header combinations with GNU feature declarations enabled.
It performs syntax-only checks against genuine extracted target development
and UAPI packages in the read-only native template. This is not runtime or
link acceptance. SDK/core receipts are retained under
builds/shared-sdk-headers-20261103; private issue24 tracks consumer validation.

Existing Debian profiles, verified in original control/rules: PAM/systemd
stage1 with full rebuilds required; Brotli/newt nopython for selected C
libraries; Avahi nogir/nopython/pkg.avahi.nogui for selected client libraries.
These are recipe choices, not per-consumer source edits. Round004 is running
util-linux/Brotli/newt using the corrected SDK. Controller failure suppression
now retains fingerprinted completed-round evidence as well as current-stage
failures. Changed recipes/SDK/dependency inputs can retry normally.

Bounded source intake identifies libtasn1/libxml2 and flex as necessary target
library producers; initial archive downloads failed HTTP503 from the pinned
Snapshot server. Background retries keep the same versions/hash verification.
No mirror substitution or new language/compiler target was introduced.
Debian cross-build/staged-bootstrap mechanics remain the authority, shared
with supported PowerPC ports; target ABI and the availability of prebuilt
target libraries differ from ppc64el.

Source-intake follow-up: pinned Snapshot retries succeeded for libtasn1-6,
libxml2 and flex. Their authenticated source locks are committed, and reviewed
round005 waits for004 before building them and their newly ready consumers.
libxml2 uses its existing nopython profile for the selected C library. All
remaining normal-feature and installed-target acceptance gates remain open.
With GNU feature macros enabled, regression003 reproduces four original header
failures (mount/rseq/sched/statx); all five corrected combinations pass.

2026-11-03 consumer evaluation: round004 accepted Brotli. The repaired SDK
removed util-linux's mount-header errors; compilation advanced to a PAM link
failure in the existing stage1 build. Broad native headers let configure
select su/runuser although stage1 omits target PAM dependencies. A minimal
Debian-rules patch now disables these tools only in stage1, retaining ordinary
full-feature builds. This is a demonstrated profile correction, not a SPE
consumer code workaround.

Newt was given back before compilation: native libslang2/dev2.3.3-5+b2 cannot
coinstall with target2.3.3-5 under Multi-Arch:same. The shared runner now derives
matching binNMU levels from authenticated frozen native package metadata and
uses standard sbuild --binNMU/--make-binNMU. It does not edit binary package
control fields. Verified metadata selects slang2+b2 and libXt+b2. An initial
binary-rebuild producer stage precedes library consumers; artifact reuse also
checks the requested binary rebuild level. Target compile/package acceptance
of this integration remains pending.

The final reviewed follow-up is round008, waiting for004. Earlier queued
005/006/007 snapshots were superseded before any package worker started as
new evidence changed the reviewed recipe; no running builds were interrupted.
It includes the cached libtasn1/libxml2/flex sources, binNMU producer stage,
existing Debian profile choices and the bounded util-linux stage1 fix.


2026-11-04 shared-runner evaluation: round008 finished with four accepted
sources: libtasn1-6, libxml2, p11-kit and Wayland. Forty sources remain
dependency-blocked in its selected reports. Flex/S-Lang never compiled: sbuild
required --maintainer for binNMUs and the runner omitted it. This shared
configuration mistake is now corrected; actual binary-rebuild acceptance
remains pending. It must not be described as a package/SPE compiler defect.

Util-linux's header errors remain resolved. Stage1 then tried the separately
auto-detected pam_lastlog2 module. The original configure.ac confirms
--disable-pam-lastlog2; the stage1-only patch now disables that module alongside
su/runuser, without changing full builds. Freetype dependency installation
failed through libX11/libxcb coinstallation; libxcb is added to the reviewed
producer/rebuild scope. Round port-pipeline-20261104-001 is submitted through
the same standard scripted cycle. No new image or runtime acceptance claimed.


2026-11-04 shared-input follow-up: round20261104-001 accepted flex, libxcb,
FreeType, libXfont and libxkbcommon. Observed remaining attempted failures are
before compilation: Snapshot HTTP503 blocked util-linux/PAM downloads; target
Oniguruma binary coinstallation blocked S-Lang and therefore newt. No new
compiler/header/ABI error has been demonstrated in those failures.

Round20261104-002 uses standard apt Acquire::Retries in the disposable sbuild
root setup hook and adds the demonstrated Oniguruma rebuild producer. Binary
rebuild levels are now explicit reviewed registry requests, passed to sbuild;
removed automatic native-index inference from orchestration. The comparison
helper remains diagnostic only. No consumer source patch or speculative SDK
change was added. Existing corrected SDK and immutable baseline remain in use.
Multi-consumer compile successes are evidence for that SDK, not full runtime
or restored-glibc acceptance. Full patched-libc source registration remains
an explicit gate. The new cycle is submitted; acceptance remains pending.


2026-11-04 round002 status: no new compiled packages. All five attempted
builds stopped at apt-get-update because sbuild expanded the retry hook's
printf %s token into its documented shell-command substitution. This was a
shared wrapper bug, not a Debian/SPE source failure. Replaced the hook with
plain echo containing no substitution tokens; remote shell output and native
apt-config parsing pass (work/apt-retry-hook-check-001). Round003 is submitted
with the corrected hook. A new image has not been assembled/booted, and no
qemu-system-ppc process was observed on R730 at this check. QEMU/light session
validation remains required after package-managed candidate assembly.


2026-11-04 closer round003 watch: Oniguruma6.9.9-1+b1 passed normal sbuild
and payload inspection. S-Lang's earlier dependency attempt still selected
old Oniguruma and was given back; the base stage is retrying with changed
inputs alongside util-linux/PAM/newt. These remain unaccepted at checkpoint.

Shared infrastructure finding: the broad native template lacks apt-utils,
so sbuild ResolverBase.pm1028-1036 explicitly falls back instead of passing
--solver sbuild-cross-resolver. This is an absent Debian prerequisite, not
a new reason to invent resolver rules or patch consumers. A versioned child
template installs native apt-utils through apt, checks ordinary dpkg/apt state
and unchanged frozen foundations, hashes the actual solver executable, and
archives separately. Parent template and active workers are unchanged.
The root recipes now include apt-utils for future builds. Actual invocation
of Debian cross resolver in a new package job remains the validation gate.

Nettle3.10.1-1 and Unbound1.26.2-0+deb13u1 source archives are authenticated
and cached for required Xorg/TLS dependencies. Unbound's existing Debian
pkg.unbound.libonly profile supplies the selected C library without requesting
a DNS daemon/Python package set. New sources and the qualified child root
will enter a reviewed follow-up after this active run. Full glibc registration,
remaining graph, normal target configuration and new QEMU validation remain
open; source readiness counts do not establish a bootable desktop.

Closer-watch acceptance update: native-cross-resolver-001 completed with
1,279 native packages, clean apt/dpkg, matching frozen foundations and a
hash-qualified Debian apt solver. Current sbuild specs pin its receipt;
round004 waits for003 and uses that child root plus Nettle/Unbound sources.
Issue25 remains open until a new package log verifies actual cross-resolver
use. The host infrastructure already included apt-utils; the omission was
inside the independently created build roots.

Round003 additionally accepted util-linux stage1 and S-Lang2.3.3-5+b2, with
normal packaging and payload checks. Util-linux provides the real UUID, blkid,
mount, fdisk and smartcols library packages; full utilities/service rebuild
remains required. New artifacts made libSM, Fontconfig and e2fsprogs ready,
and those sources started automatically. PAM was given back on Snapshot504
fetching native libfakeroot; newt's earlier attempt preceded accepted S-Lang.
No fresh image/boot validation is claimed. See builds/native-cross-resolver-20261104.


2026-11-04 common-failure evaluation: libSM, Fontconfig and e2fsprogs all
failed before compilation on the same uuid-dev shared man page. Native
uuid_generate_random.3 is expanded content, while stage1 uuid-dev ships a
one-line .so alias because its Debian override skips dh_installman. The
primary target page is already byte-identical to the native expanded alias
(SHA256:252d2959ef7abba24e6c74941174f5f85adf8533812bdbfaf2b7b8da6837eecb).
Normal native dh_installman restored exact native-compatible alias content in
regression002. The stage1 patch now retains that helper; full builds unchanged.
No force-overwrite, binary-file substitution or consumer patch is involved.

Artifact intake now rejects superseded source-patch hashes as well as wrong
source versions, so old UUID artifacts cannot silently re-enter the new pool.
Archive-acquisition failures are no longer treated as immutable source errors
for cross-round retry suppression. Improved diagnostics retain coinstallation
errors. These supply corrected real inputs to Debian apt/sbuild.

PAM log confirms five libfakeroot retries, followed by504. A bounded transport
probe checked the exact frozen libfakeroot file against authenticated-index
SHA256: primary Snapshot returned504 and snapshot-cloudflare returned403.
Neither is a verified usable fallback in this test. No live mirror/base
switch occurred; retained verified local archives remain necessary.

Round004 started during diagnosis and was left running. The revised runner
can use the free one of its two controller slots to wait after an active
follow-up. Round005 is queued after004 with the validated UUID helper fix and
artifact provenance guard. Full package rebuild/coinstallation remains
pending; the successful native regression alone does not close that gate.

2026-11-04: Persistent apt download cache corrected. Source intake already
reuses hash-pinned files; native binary downloads were lost with sbuild roots,
and sbuild explicitly defaulted retention off. Documented unshare bind mounts
and retention now connect per-worker apt caches to a shared archive pool,
including failed/interrupted workers. Seeded1,155 archives; native network-off
apt reinstall/download-only check passed, requesting0B. Round006 submitted
with the fix; actual sbuild bind/acquisition and target runtime remain pending.
Evidence: docs/builds/apt-archive-cache-20261104/README.md.

2026-11-04: Round006 uncovered cache namespace ownership failure; initial
nspawn diagnostic missed sbuild's mapped UID boundary. Fixed using sbuild's
own UID/GID mapping, then verified actual usernsexec/pivotroot/bind with
network disabled: writable cache, apt requests0B. Round005 had40 unique
deferred sources, predominantly shared dependency chains; no new success in006.

Shared review also found round005 util-linux blocked by native libedit-dev
already installed in the broad template versus its Build-Conflicts. A broad
archive cache is useful; a universally preinstalled dependency superset is not
necessarily coinstallable. Next root qualification must cover Build-Conflicts
and the actual sbuild cross-resolver path, not only apt check on the template.

2026-11-04: Revised the Debian-port skill and starter prompt; aligned AGENTS,
contract and pipeline documentation. Broad server caches/tools are distinct
from clean per-source installed state. Actual sbuild-boundary qualification,
shared-blocker grouping and evidence-driven retries now replace broad-template
wording that conflicted with standard Debian roots. Debian's ppc64el workflow
is a mechanics reference, not an SPE ABI replacement. Documentation only;
clean-root/build qualification remains pending. Diff and manual structure
checks passed; skill validator unavailable locally due to missing PyYAML.

2026-11-04: Clean buildd child created with125 native packages and apt-utils,
clean apt/dpkg checks and unchanged foundation; broad caches remain external.
Standard pipeline qualification now targets util-linux/PAM, the observed
conflict/cache boundary, before broader retries. Missing-producer source
intake for libevent/libtextwrap started separately; no new target pass claimed.

2026-11-04: Qualification001 passed prior cache/coinstallation boundaries,
then failed frozen archive acquisition before compilation. Same-origin
hash-verified apt-helper recovery cached3 missing native files, reused1;
5 still503/504. Qualification002 running with those cache additions. Missing
producer source intake also hit Snapshot; no unverified sources accepted.

2026-11-04 actual pass: PAM1.7.0-5 stage1 cross build succeeded in clean root002:
7 .debs (4 non-debug plus3 debug), payload hashes and ELF32BE PowerPC inspected.
Required full PAM rebuild/runtime acceptance remain open. Util-linux passed
old dependency conflict and recovered its downloads. Normal workstation round007
queued after qualification002, max4 dependency-ready jobs, no overlapping batch.

2026-11-04: util-linux stage1 passed too:14 inspected SPE .debs. Together with
PAM's7, both clean-root qualification sources now have accepted bootstrap
outputs. Round007 is active; full rebuild/runtime gates remain. Source-cache
fall-through fixed and3 injected-failure/reuse/integrity tests passed on R730;
live source acquisition is tracked independently from the fixture results.

2026-11-04 desktop4 log viewer: existing terminal had a stale SSH session and
old build.log-only selector. Reconnected only the task log terminal, restored
desk3,0/zone1 and original920x270 geometry. Server-side bounded viewer now
follows active pipeline sbuild.log files (up to4 jobs,3 lines each,4s refresh),
labels completed outputs, and reports audit-only periods. --once verified
current round007 data; live server process confirmed. No extra browser/views.

2026-11-04: round007 produced31 inspected .debs from5 additional normal-profile
sources (libcap2/e2fsprogs/fontconfig/libsm/libarchive).35 sources deferred.
Fixed viewer hiding completed progress. Standard noinsttest profile selection
for GLib/D-Bus/systemd removes test dependency edges; round008 dose report
confirms GLib progressed from DBus to libelf prerequisite. Full64-source batch
running; producer intake005 covers json-c/keyutils plus previous archive gaps.

2026-11-04: grouped remaining35 into producer chains, recorded in
remaining-closure-20261104.md. Existing elfutils nodebuginfod profile addresses
ELF/GLib prerequisites. AppArmor C-library stage1 packaging prepared; corrected
patch application,2-versus11 package selection and recipe dry-runs verified,
actual cross-build pending. Round010 queued after009; crypto producer intake006
running. Snapshot acquisition still blocks4 missing producers; no unverified
sources or new runtime acceptance claimed.

2026-11-04: elfutils now passes,11 inspected .debs. AppArmor blocked by native
archive504 before compilation. Selected supported GLib nogir to avoid target
GIR execution during the C-library bootstrap. Fixed classification losing apt
fetch errors beyond long summaries, including retrospective retry handling;
2 tests and real AppArmor-log reproduction passed. Round011 running. Snapshot
source/native acquisition remains a distinct unresolved external limitation.

2026-11-04: GLib is now dose-installable in011. Completed classifier regression
coverage also preserves original dependency conflicts when the later diagnostic
explainer hits a network failure;3 tests pass. Reporting follow-up is for future
snapshots; running011 remains immutable.

2026-11-04: mirror comparison confirmed the blocked json-c file is available
hash-identical from Debian CDN while Snapshot timed out. Explicit cache-only
CDN mode recovered all5 missing source sets without changing frozen metadata,
versions or apt sources.6 tests passed; round012 includes recovered producers.
Round011 also passed AppArmor bootstrap2 debs and GLib13, with payload inspection.
Full-feature and runtime acceptance remain separate. Results/probe receipts in
docs/builds/exact-file-cdn-20261104/.

### 2026-11-04 — Desktop log viewer heartbeat

Existing desktop 4 viewer now refreshes a server-clock heartbeat every four seconds, reports latest log-write age and shows controller output between compiler jobs. In-progress fallout is explicitly provisional. Deployed to the existing R730 viewer; Python compilation and server --once rendering passed. Round012 completed with six inspected source-build receipts / 22 debs and 32 unique deferred sources; no image/runtime acceptance implied.

2026-11-04 broader closure repair: reviewed round012 as shared dependency chains, not32 compiler defects. Registered13 additional frozen verified producers across crypto/netfilter/device management, SASL/LDAP, account setup, VNC and target Python. Added explicit reviewed intake manifest so first-error-only dose reporting does not force one prerequisite per round; actual readiness remains Debian-owned. Selected declared OpenLDAP client and SASL core profiles to break cycles; target Python/defaults now justified by ALSA. Three CLI regression tests pass on R730. Full-scope round013 submitted with qualified clean roots/max4 bounded jobs. GIR/full-glibc/image/runtime gates remain open. See docs/builds/closure-chain-repair-20261104/.

2026-11-04 audit performance repair: stages/waves previously reran all source/profile groups. Added bounded --sources requests without shrinking the verified binary pool; skip empty stages and omit attempted sources on later waves. Five-source dose equivalence and actual two-source CLI qualification passed. Added five reviewed target Python prerequisites; rpcsvc-proto cached only as native generator inspection. Eighteen new target producers registered total. Round013 has four real sbuild jobs; round014 queued after013 with scoped audits and Python prerequisites, no overlapping workers. Compilation/remaining-count acceptance still pending actual receipts.

2026-11-04 shared acquisition follow-through: round013 passed SASL8, libdebian-installer3 and architecture-properties3 inspected debs. Kmod stopped before compile on Snapshot503 scdoc. Added opt-in pre-wave native archive cache fill from actual dose installation sets, matching frozen NativePackages tuples/hashes, with exact-CDN then pinned-Snapshot fallback. Three native cache regressions pass; actual scdoc recovered into persistent cache. Round014 waiting-only cancelled/replaced (prior receipt retained);015 never started after safe submission rejection. Predecessor identity now matches --output, not an after-receipt substring. Round016 queued after013 with complete repairs; original worker jobs intact. Whole-wave integration/final remaining-count acceptance pending.

2026-11-04 next closure pass: completed013/016 delivered16 inspected source builds /60 debs. Original32 request set now29 deferred; total35 includes six new Python prerequisites. Native prefetch actual016 wave cached116/reused52 successfully. Round017 requests explicit libcap2 binNMU3 for observed systemd Multi-Arch coinstallation conflict; restores normal Python-defaults doc helper dependencies by removing nodoc; selects verified existing cdebconf text/client profile; registers five frozen source producers libxmu/xft/lmdb/libev/libverto. Unknown libxft source name was rejected at metadata intake, corrected to canonical xft; diagnostics improved and3 intake tests pass. Full selected round017 submitted with persistent caches/scoped audits/max4 bounded remote workers. Evidence docs/builds/closure-next-wave-20261104/. No new image/runtime acceptance.

2026-11-04 whole-fallout repair:017 delivered12 inspected source builds /66 debs. Reviewed all failed builds/chains together. Found shared epoch cache filename bug (real sbuild --nonet before126kB failure / after0B success), dose-selected archive trimming that constrained apt alternatives, and actual download choices missing from predictive prefetch. Fixed canonical verified cache names, complete verified SPE archive exposure and one bounded actual-native acquisition recovery with first logs retained. Nine targeted regressions pass; actual Tk/Kerberos/BLT logs validate recovery boundaries. Reviewed full Native Tk closure and rebuilt Xft4/Xext3/Xss3 in018 (six inspected debs). Reconciled14 ignored existing binary revision entries; all16 requests verified against frozen native metadata, with consistency guard. Native Python documentation tools qualified in control/template and source repack passed. Registered libxpm/libxxf86vm/libdaemon from frozen hashes.018 continues;019 queued after018 for remaining reviewed core alignment, no overlap. Evidence docs/builds/multi-failure-repair-20261104/. GIR/full-glibc/image/runtime gates remain open.

2026-11-04 follow-up:018 accepted6 sources/13 debs (Xft/Xext/Xss/Xpm/Xaw/libdaemon). Reviewed three actual source failures together: removed invalid :native from Multi-Arch:foreign Docutils, guarded Debian BLT C23 variadics for pinned GCC8, and extended existing measured Xorg malloc cache to libxxf86vm. Real GCC8 before/after, actual archive metadata + dpkg dependency evaluation, and both source repacks pass. Full builds pending. Waiting019 cancelled before workers, replaced by020 after active018 with previous core binNMUs retained. No new image/runtime acceptance. Evidence: docs/builds/multi-failure-repair-20261104/.

2026-11-04 desktop follow-through:018 completed7 accepted sources/15 inspected debs.020 now runs the broad reviewed core/desktop scope with max4 constrained R730 sbuild jobs. Kerberos reached a genuine Autoconf cross-runtime gate. Debian dpkg-cross already documents its constructor/destructor cache answer; static and dynamic target probes using hash-verified pinned glibc/GCC8 pass under e500v2 QEMU. Added target-restricted standard Debian rules cache input; source repack002 passes after correcting source-lock pointer rejected in001. No general stock PowerPC site import, target execution during builds, or new desktop/hardware acceptance. Evidence docs/builds/krb5-cross-configure-20261104/.

2026-11-04 workflow correction: user expects maintained Debian PowerPC build mechanics and a broad workstation archive. Current plan110 sources. Qualified shared real installed SDK root004 with a true read-only compiler mount (dpkg -V clean, EROFS write rejection, SPE assembly emission), plus standard sbuild extra-repository transport for730 verified artifacts (offline namespace apt/hash check). Two integrity/reuse regressions pass. Active020 unchanged; waiting021 replaced by022 after020 with full scope and all previous fixes. Full integration acceptance pending. Compiler baseline audit explicitly confirms GCC8.5/tabor6 remains, not Trixie GCC14.2.0-19; no modern SPE compiler completion claimed. Evidence shared-sdk-repository-20261104 and docs/sdk-baseline-audit-20261104.md.

2026-11-05 reconnect and side-guest review: R730 up, transient build services
inactive.020 completed13 sources/47 inspected debs;022 produced no new accepted
packages, with actual libatomic-dev unpack attempts under the RO SDK explaining
its install failures. Mainline GCC14 SPE restoration remains the user's main
baseline requirement, not completed by prior GCC8/tabor6 SDK repairs. Private
AmigaOS preflight found only A1222 ISO/Enhancer; read-only Kicklayout checks and
prior identical-media QEMU11 test do not support a Workbench/install claim.
Platform-matched AmigaOne/Pegasos media is the next prerequisite. No old-GCC
batch restart or new AmigaOS install. See amigaos-side-guest-20261105 evidence.

2026-11-05 correction to side-guest scope: our existing ppce500/e500v2/SPE Linux harness is a valid custom-emulation starting point; no stock A1222 name does not prove impossibility or require other media as the only path. Actual bounded R730 direct-entry probe of the unmodified uploaded AmigaOS A1222 kernel loaded at NIP0x010000d4 and reached NIP0x700 after2s, no serial/Workbench. Private kernel kept outside Git, no disk/network, QEMU stopped. Next isolate AmigaBoot/Kickstart handoff and P1022 MMIO requirements before emulator changes. Evidence e500-entry-receipt.json in amigaos-side-guest-20261105.

2026-11-05 separate OS4 control guest: prepared R730 Pegasos II/7457,512MiB,
8GiB sparse disk, SM501, reserved loopback VNC5912. Actual BBoot0.8/VOF probe
configured PCI devices and stopped at expected missing initrd. No OS install
or running guest claimed. Matching Pegasos media/Kickstart remain needed;
existing e500/SPE work unchanged. Scripts, artifact hashes and exact serial
receipt in docs/builds/amigaos-pegasos2-20261105/.

## Layered rescue USB — 2026-11-05

Built FAT/ext4 disk-root rescue image with mem=3500M and a temporary U-Boot script. QEMU disk-root boot, key SSH, PTY and matched fractal passed; known fenv failure remains. Unchanged physical kernel/DTB, hardware boot still unverified. See [build evidence](builds/layered-rescue-20261105/README.md). No full Trixie/GCC14 completion claimed.

## Tabor physical boot machine-match defect — 2026-11-05

Original-image/vendor review found our kernel matches fsl,tabor but shipped DTB uses varisys,TABOR. Exact source and Linux machine-selection loop verified. Added ordered correction and packaging identity guard; original pair rejected, corrected source passes. No corrected binary/hardware acceptance yet. See [audit](builds/tabor-machine-audit-20261105/README.md).

## Corrected physical kernel staged — 2026-11-05

Fresh Linux 6.12.113-1 board rebuild passed with the exact configuration from the actually shipped tabor-live-001. Machine identity matches unchanged vendor DTB. Corrected uImage installed on exact SanDisk, remount/readback verified; root, DTB and boot script preserved. Stick safely powered off; physical retry remains open in issue #26. See [build and write receipts](builds/tabor-match-rebuild-20261105/README.md).

## Real A1222 boot and SSH confirmed — 2026-11-05

Corrected kernel boots USB ext4; key SSH at 192.168.1.249 works. Both e500v2 CPUs visible; ~3.35GiB under intentional mem=3500M. All nine ABI CLI checks pass, including fenv. HDMI failure is now traced to missing polaris11_sdma.bin during early AMDGPU initialization. No full ABI/8GiB/GL acceptance. See [physical evidence](builds/a1222-first-ssh-20261105/README.md). Preserve working boot/root; next fix firmware completeness and early availability.

## Early Radeon firmware correction prepared — 2026-11-05

Native root contains polaris11_sdma.bin; built-in AMDGPU asks before ext4 mounts. Built pinned 1.49MiB firmware-only early archive, no init/OS root, and adapted temporary boot script. QEMU disk-root + SSH/PTY/fractal passed; physical GPU test pending. USB remains on running A1222 and has not been updated. ROM interfaces inspected read-only by metadata; no ROM dumps/flash performed. See [evidence](builds/early-polaris-firmware-20261105/README.md).

## Display/admin USB update ready — 2026-11-05

Exact SanDisk updated with early firmware, root key-only SSH and read-only QEMU inventory. Kernel/DTB preserved. QEMU root/tabor SSH tests passed; both USB partitions remount/readback verified and powered off. Physical Radeon retry pending. See [evidence](builds/display-admin-usb-20261105/README.md).

## Native SMU graphics failure isolated — 2026-11-05

Root key SSH works. Live log/reprobe reaches VRAM/GART and firmware discovery, then SMU startup fails (-22); HDMI still stale. Private live-DTB/PCI inventory retrieved by SFTP, no ROM reads/flash. Audit SMU upload endianness and PCI windows before choosing a patch. See [evidence](builds/native-gpu-smu-20261105/README.md).

2026-11-05: Modular kernel compiled; matching modules/static module tools and separate boot payload installed on live SanDisk over SSH/SFTP. Transfer/readback and machine identity checks passed; old kernel and boot-known-good.scr retained. Reboot sent, physical new-kernel acceptance pending. See builds/modular-usb-update-20261105/.

2026-11-05 physical modular acceptance:6.12.113-tabor-modular boots USB, SSH works, all9 ABI checks pass. Corrected static module-loader defaults /lib/modules/modules.dep; dependency resolution and insertion work, but AMDGPU device probe still fails-22, no framebuffer. See modular-usb-update-20261105 evidence.

2026-11-05: Audited SMU7 raw firmware words -> CGS -> WREG32/writel; native u32 upload differs by host endian. Isolated LE-decode candidate prepared (not default series), numerical stream equivalence checked, fresh constrained exact-config R730 build started. Physical fix remains unproven. See builds/smu7-endian-candidate-20261105/.

2026-11-05: SMU7 endian candidate compiled, exact .config/Module.symvers match. One controlled physical module test with continuous kmsg: insertion succeeds but SMU startup still fails and device probe-22, no framebuffer. SSH healthy; installed module tree unchanged. Negative warm-state test, no cold-cycle result or fix claimed. Evidence: builds/smu7-endian-candidate-20261105/.

2026-11-05: AMDGPU requirements audit: all13 dependency modules match accepted kernel; all42 existing Polaris10/11 firmware files already matched pinned firmware-amd-graphics20250410-2. Installed complete892-file firmware payload/licenses to USB over SSH, all892 native hash readbacks pass; original subset and .deb retained. No missing Polaris file found, no GPU reload or graphics-fix claim. Evidence: builds/full-amd-firmware-20261105/.

2026-11-05: Source-level SMU startup audit identifies ignored firmware lookup and handshake results; no proven root cause. Isolated logging/error-propagation candidate builds targeted AMDGPU on R730 with original upload behavior and exact physical modular config. Logs selected firmware and PC/status/response stages; no reset changes. See builds/smu-startup-diagnostics-20261105/.

2026-11-05: Diagnostic module physical test confirms polaris11_k_smc.bin version0x1800 loads successfully; protected/security mode1, SMU response/status0 around startup, low sampled PC. Still no framebuffer, SSH healthy. Combined LE+logging build prepared but untested. Read-only OS4 disk header probe finds three NGF1 volumes; no compatible mount/read driver established, no disk writes. Uploaded Enhancer RadeonRX documentation supplies PCI/revision/DPM leads, not installed-version proof. See smu-startup-diagnostics-20261105 and aos-readonly-intake-20261105 evidence.

2026-11-06: Completed bounded source walk and full selected-firmware word model on R730. Confirmed baseline native-load divergence and complete modeled equivalence with explicit LE decode; prior physical failure remains. Reviewed existing PPC barriers and indirect locking; identified discarded handshake results. Evidence in builds/smu-source-walk-20261106/. No boot changes or additional build started.

2026-11-06: Physical upload-readback trial completed, not a display fix. All32493 comparisons differ, firstaaaa5555 versus35771e80; protected SRAM visibility/index state now needs qualification. Build/config/Module.symvers passed; SSH healthy, installed module tree unchanged. Evidence: builds/smu-readback-20261106/.

2026-11-06: Exact Radeon runs on ASUS x86 with matching firmware. Captured running SMC/debugfs and no-loss register trace. Rebind skips firmware upload; must measure first cold Linux bind before comparing bootstrap paths. Alternate held-driver boot prepared, normal default preserved. See x86-radeon-hardware-20261106.

2026-11-06: Held-driver x86 boot verifies full protected SMU startup, not just reuse. Real upload matches LE model completely; measured mailbox sequence succeeds. This narrows PPC comparison to initial readiness and delivery/handshake, without claiming hardware readback or root cause. Framebuffer/SSH healthy.

2026-11-06 physical milestone: after fresh power-on, corrected LE firmware upload and SMU protected startup succeed on A1222, with complete x86-equivalent upload and matching~53ms handshake. Remaining failure is secondary GPU firmware loading/TOC stage. Graphics still unavailable; no universal-fix claim.

2026-11-06: Shared SMU7 transfer-table encoder candidate built, x86/BE byte-equivalence passed. Warm hardware state remains wedged after prior load failure; clean candidate boot pending, no display acceptance.

2026-11-06 physical TOC milestone: fresh candidate passes SMU startup and reaches graphics ring test beyond former firmware-load timeout. Ring completion-110 and PCIe error require next review; graphics output not yet accepted.

2026-11-06: Producer-boundary snapshot reveals requested ring byte-swap versus sampled effective setting mismatch, plus native pointer-shadow encoding. Focus shifted to coherent ring producer/consumer contract; blanket conversion not applied.

2026-11-06 immediate swap proof: fresh diagnostic build/config/symbol checks pass. Physical CP_RB0_CNTL swap bit17 reads0 immediately after all3 writes requesting1; pointer-enable bit31 reads correctly. NativeBE packets plus inactive swap strongly identify GFX8 encoding boundary; gfx test still-110/no display. Latest pinned upstream and100 path commit subjects retain native/swap contract, no applicable fix found in bounded review. See builds/gfx-swap-readback-20261106/.

2026-11-06 targeted Polaris11 SW-LE graphics-ring candidate compiled/config/symbol checks pass. Actual GFX scratch self-test now passes; next KIQ ring times out with nativeBE packet bytes. No display; failed-init cleanup warns, SSH remains healthy. Writer wrap/NOP/patch tests match native x86 and emulated BE PPC. Extending coherent ring/MQD boundary to KIQ/compute in fresh candidate; see builds/gfx-software-le-20261106/.

2026-11-06 KIQ/compute+MQD LE candidate builds/config/symbols pass, but warm hardware unload/load command timed out and SSH became unresponsive; stage unknown, no acceptance. Candidate/hash/attempt retained in builds/gfx-queues-le-20261106/. Fresh physical power-cycle required before first-load validation; disk module and boot defaults unchanged.

2026-11-06 SanDisk laptop check: no read errors, FAT/boot.scr intact; ext4 journal recovered after metadata/log backup, final read-only checks clean. VLC fatload command lacked usb. Verified queue candidate and first-load-only capture script staged; USB unmounted, boot defaults unchanged. See builds/sandisk-recovery-20261106/.

2026-11-06 fresh boot first-load candidate attempt: initial SSH/uptime34s/no modules confirmed, then test timed out60s; SSH/ICMP lost, user reports green screen. No successful GPU acceptance or phase evidence. Added explicit launcher stage output; next test requires off-board kmsg and another cold boot. See builds/gfx-queues-le-20261106/.

2026-11-06 off-board capture: SSH log moved off USB at runtime, root verified read-only. Dependencies and held candidate insertion pass; explicit bind locks board. Saved kernel stream shows SMU success, CP start, then PCIe00800000/23 storm; earlier mapped-memset alignment warning retained. No GPU acceptance. Adding pre-map KIQ self-test to isolate command/descriptor boundary; see builds/polaris-offboard-20261106/.

2026-11-06 KIQ gate physical pass: pre-map control self-test returns0; hang after compute mapping submission, PCIe storm saved off-board. Native CPU MQD staging/IO-safe VRAM publication candidate in progress; exact wire-helper x86/PPC tests pass. No display acceptance. See builds/gfx-kiq-gate-20261106/ and gfx-mqd-host-20261106/.

2026-11-06 native MQD staging candidate002 compiled; config/symbol parity pass; SHA f6475b61ef7affae8fff7cbd008ef2a70090f96327f3c7a0cd8d2d9adb5e2e49. IO-safe VRAM clear/publish, heap-native construction and KIQ error propagation; ready locally for cold test, no new hardware acceptance.

2026-11-06 MQD staging002 physical test removes mapped memset warning; KIQ still passes, compute mapping still hangs. Logs expose compute descriptors in GTT vs KIQ in VRAM. Single-placement BE Polaris11 VRAM candidate building; no display acceptance. See builds/gfx-mqd-host-20261106/ and gfx-mqd-vram-20261106/.

2026-11-06 VRAM placement physical negative: all compute descriptors confirmedVRAM, same post-map PCIe hang. Do not accept placement as fix. GPU COPY_DATA calibration+MQD readback diagnostic building on staging002 without placement override; AMD PAL packet source pinned. See builds/gfx-mqd-vram-20261106/ and gfx-mqd-read-20261106/.

2026-11-06 historical comparison confirms older Radeon Evergreen hardware-swap path;2018 Polaris BE report explicitly passes ring test with software LE and finds hardware swap ineffective. Clarified history doc. GPU MQD readback candidate compiled/config/symbol checks pass, SHAed5b746997cdaab551ac75d8cfc323391708ea9305a386f8e0d4ebe9bce57169; physical pending.

2026-11-07 lab resumed: A1222 modular kernel/no modules, R730 healthy. Off-board006 GPU calibration and22/22MQD sampled words pass; remaining hang after combined resource/map submission. IH and CSB helpers already correct. Stage-gated normal KIQ tests between resource assignment/individual mapping building; no new conversion guessed. See builds/gfx-map-stage-20261107/.

2026-11-07 staged hardware run: GPU samples, SET_RESOURCES, all8MAP_QUEUES/control checks pass; later init hangs. This narrows previous mapping-failure wording. Toolchain remains authoritative; preparing public forge kernel-build snapshot on wip/polaris-be with source/patch/config/module hashes and explicit acceptance limits.

2026-11-07 console isolation: native-MQD candidate002 loaded with upstream num_kcq=0 on fresh A1222 boot, USB rootro and off-board capture verified. KIQ pre-map test passes; resource submission followed by same PCIe storm/SSH loss. No framebuffer acceptance; compute mapping alone is not sufficient explanation. Recorded in builds/polaris-console-zero-kcq-20261107/. Await contributor patches or targeted post-resource stage instrumentation before another physical retry.

2026-11-07 investigation reset: added tabor-amdgpu-investigate skill and continuation prompt. Require init-order reconstruction and producer/consumer contract ownership before more encoding changes; distinguish PPC32BE from POWER64LE/BE controls. Zero-kcq trial used older002, so not a single-variable comparison to latest diagnostic. Derfs patch content remains pending. No hardware load or claimed GPU fix in this reset.

2026-11-07 AMDGPU source intake: cached mainline d487237 and AMD development5349075 on R730, official drm/amdgpu/kernel drm-amdgpu-next ref verified equal. Retained hashes/licenses and three-way init/test/pointer source comparison. New compute-test error propagation and still-native IB producer are review leads, not established PCIe fixes. Hardware/baseline unchanged. See builds/amdgpu-upstream-intake-20261107/.

2026-11-07 source correction: both original/patched and AMD-next GFX8 IB emitters retain explicit BE packet swap controls; SDMA has ring/writeback/IB swap settings. Native IB stores alone are not a defect. Retained exact contexts in amdgpu-upstream-intake-20261107/existing-be-controls.json. No global conversion or physical retry; audit patch interaction and first failing operation.

2026-11-07 user authorizes updating glibc/SDK components if required. Version audit: frozen Trixie target already pins glibc2.41-12+deb13u4; complete patched-libc/package/runtime acceptance remains open. SPE userspace compiler remains GCC8.5/tabor6, distinct from ordinary PowerPC GCC14.2 used for the freestanding kernel experiment. Finish clean upstream kernel control without introducing a libc change; subsequent SDK update must retain SPE ABI/fenv and standard Debian packaging, pin reviewed versions and validate runtime. No floating source refresh or current glibc completion is claimed.

2026-11-07 clean upstream control compiled: GitLab AMDGPU5349075 / Linux7.3-rc6, only two board patches, fresh detached source and output, no GPU diff or experimental GPU patches. Kbuild vmlinux/modules/dtbs exit0, version7.3.0-rc6-tabor-upstream-001 and artifact/config hashes retained. R7304CPU/6GiB, no USB update or hardware test. No glibc change required for kernel; SDK gaps remain separately authorized. See builds/amdgpu-upstream-clean-20261107/.

2026-11-07 upstream QEMU control: configuration variant compiled;2CPU startup stalls before shell,1CPU boots new7.3 kernel with8/9 ABI passes/fenvFAIL and identical SPE/software fractals;2CPU nosmap control also stalls. Snapshot disk unchanged. User requests existing boot.scr reuse; hardware bundle with42 modules/U-Boot CRC+load checks staged inactive on reachable A1222 and hash verified. Active boot/script/firmware unchanged, FAT unmounted, no reboot. Gate: secondary CPU startup before USB activation. See builds/upstream-qemu-20261107/ and upstream-usb-staging-20261107/.

2026-11-07 fresh userspace direction: candidate profile trixie-spe-sdk-candidate.json selects GCC14.2.0-19 + patched glibc2.41 with full SPE ABI gates. Cached source hashes/size pass; fresh Debian wrapper extraction completed without downloads. Verified legacy8.5 source pin and inventoried162 backend/runtime files. Actual ordinary PowerPC GCC14 probe rejects -mabi=spe/-mspe/-mfloat-gprs=double; no modern SPE compiler or package-wide rebuild accepted. Next implementation is backend/libgcc forward port before libc/C++/Debian package closure. See builds/gcc14-spe-foundation-20261107/.

2026-11-07 user confirms kernel-up graphical shell with basic display fallback before acceleration. Added graphical-shell candidate profile/contract linked from fresh SDK candidate: real fbcon/getty, verified firmware simpledrm handoff if available, working KMS without glamor or fbdev X path, software E/Mesa and independent SSH recovery. Pinned source confirms FB_VESA requires X86 and simpledrm requires actual initialized scanout. No fabricated framebuffer or claimed universal PPC VESA mode, no new kernel build or device change.

## 2026-11-07 — GCC14 SPE backend restoration starts

Imported147 hash-checked GCC8.5 SPE backend files into disposable GCC14.2.0 sources on R730. Candidate target selection, GCC14 option metadata, removed debug interfaces and machine-mode iterator syntax are recorded as ordered source patches. Used Debian’s existing DFSG documentation build patch. Pass005 now reaches compiler translation units; modern backend API adaptations remain. Accepted SDK and active USB kernel unchanged. See [checkpoint](builds/gcc14-spe-port-20261107/README.md).

## 2026-11-07 — GCC14 SPE C bootstrap and native selected tests pass

Completed coherent candidate backend/API migration on the pinned GCC14.2.0 DFSG
source:16 ordered patches,94 option-record preservation checks, eight tuning
defaults carried through modern option state, modern ABI/asm/attribute/alignment
interfaces, and per-analysis vector costing. Actual `-O3` testing found and fixed
a stale vector-analysis context; the optimized loop emits SPE evfsadd and runs.
Full `all-gcc` stage010 exits0; serialized source replay matches compiled source.
20 automated compiler checks pass. The final freestanding C probe passes in
QEMU/e500v2 and on the A1222 under6.12.113 with exit0 and taint0. An initial
hardware exit-status failure was our incomplete syscall clobber list, corrected
against glibc2.41 and retained in evidence. No libgcc/libc was linked.

See [evidence](builds/gcc14-spe-interface-20261107/README.md). Accepted SDK/base
lock/USB remain unchanged. libgcc, glibc/fenv/context/TLS/atomics, long double,
C++ unwinding and cross-version/general PowerPC regression gates remain open.

Compiler checkpoint committed as `2047b47`; remaining runtime promotion gates
are tracked in [issue27](https://github.com/auzieman/amigaos-toolchain_patch/issues/27), kept open.

2026-11-08 PowerPlay checkpoint: protected6.12 bind passes GFX/KIQ/all8 compute and both SDMA scratch tests, then PCIe/SSH fail after powerplay hw_init entry. No retry; reboot requested. Backported upstream SMU response status correction (legacy helper always succeeded), added scoped lifecycle/ATOM/mailbox markers. Native and PPC32BE/QEMU five-case response checks pass; fresh Kbuild exits0 and all687 imported CRCs/full vermagic match. Candidate7067488b remains on R730, not deployed/physically accepted. Evidence: builds/polaris-powerplay-20261108/.

2026-11-08 physical PowerPlay candidate7067488b: protected single bind again passes GFX/compute/SDMA scratch tests; first PCIe error follows SMU DPM_Enable0x14e entry by45,333us inside smu7_start_dpm. Bind timed out; no retry or boot changes. See builds/polaris-powerplay-20261108/hardware-offboard-001/. Next: audit DPM transition/table producer contracts; command causation not proven.

2026-11-08 historical graphics intake: retained A-EON5.4 config enables radeon, disables amdgpu; retained vendor patch changes board/audio only. May2025 firsthand report loses Linux after Polaris replacement. Archive web indexes502; package recovery not yet accepted. See builds/historical-tabor-graphics-20261108/.

2026-11-08 derfsss U-Boot review pinned9bfbc801: VBIOS POST/bridge forwarding and framebuffer bus-to-CPU conversion documented; RX560 graphics testing cited on X5000, A1222 console unverified. PCIE1 outbound windows match our captured Linux boot, so no gross address-map fix found. Six-file intake/hashes in builds/derfsss-uboot-review-20261108/. No firmware/hardware change.

2026-11-08 derfsss/qemu isolated sparse checkout on R730 pinned91b22ec (g5-amigaone, VERSION11.0.50). Latest delta changes Teron AmigaOne CPU/interrupt model to970fx, not A1222/SPE. Generic ppce500/e500v2 remains. No build/replacement/test; same-image SPE comparison is the bounded next experiment. See builds/derfsss-qemu-review-20261108/.

2026-11-08 DPM rereview: narrowed first failing command to SCLK enable, not subsequent MCLK/PCIe enable. Prepared mandatory-table/start error-propagation experiment0018 and passed extracted-routine native fault injection; source apply-check0. Not built or physically tested; no root-cause claim. Linked graphics/PCIe state producer and actual SRAM contract remain next review boundary.


2026-11-08 fresh SMU7 review: confirmed pre-swapped native AVFS calibration literals violate the BE upload byte contract; optional hardware gate remains unrecorded, so causality is unproven. Display-voltage fix already present. Reproducible audit and next complete typed serialization step: docs/builds/smu7-fresh-review-20261108/README.md. No physical retry or deployed fix.


2026-11-08 clock-channel implementation and physical trial: patches0019/0020 correct complete AVFS wire constants and ATOM clock/flag words (native24-bit bitfield truncation onBE). Compiled full calibration objects and native/PPC input fixtures pass. Candidate44823d09 builds with687matching importCRCs. Physical first bind on the EXISTING6.12.113-tabor-modular kernel confirms AVFS calibration ran, DPM_Enable ack1, smu7_start_dpm/PowerPlay/DCE init0. First fault now duringUVD ring test; SSH drops, no console acceptance, no rebind. Newer kernel NOT booted; no boot/default files changed. Both fixes tested together, individual causality unisolated. See builds/atom-channel-review-20261108/README.md and hardware-summary.json.


2026-11-08 user requests coherent USB boot rather than RAM-module split. Complete rebuilt6.12.113-tabor-e2e-001 kernel/43modules/DTB/Polaris firmware bundled on R730, installed to identified SanDisk serial03001919041721081205. All80bundle files/readback/scriptCRC pass; both filesystem checks pass; partitions unmounted. /boot.scr selects versioned e2e payload, exact prior script retained as /boot-before-e2e.scr. Existing rescue/init/SSH keys unchanged, no firmware saveenv. Test capture supports normal installed modprobe mode; simulated RO-gate tests pass. Actual new boot and UVD/display acceptance pending. See builds/e2e-usb-20261108/README.md. No serial cable available; SSH-first/off-board capture remains necessary.


2026-11-08 complete USB boot VERIFIED: physical6.12.113-tabor-e2e-001 reached SSH, taint0/no AMDGPU, installed modulead5fc87d/all21firmware hashes match. Normal installed modprobe with off-board capture/rootRO reproduces DPM ack1 and PowerPlay/DCE success, then first PCIe fault46172us after UVD ring-test entry. SSH drops; no retry. This is the complete new boot, not a RAM driver split test. Display/UVD remain unaccepted. See builds/e2e-usb-20261108/hardware-summary.json.

2026-11-08 standalone codec gate: eight actual candidate driver functions extracted into freestanding userspace with simulated MMIO/device consumer. 32 policy/wrap cases per x86/PPC architecture plus bulk/conditional checks pass; missing/double conversion detected on BE. Exact PPC binary also passes on physical A1222 CPU without module load or GPU access. Earlier ATOM56-case physical gate remains separate. Full e2e-002 build/43modules/687importCRCs pass, not deployed. No actual GPU swap, DMA or display acceptance. See builds/standalone-gpu-codec-20261108/ and shared-kernel-boundary-20261108/.

2026-11-08 e2e-002 physical trial: matched kernel/module verified, rootRO/offboard capture, normal installed modprobe. UVD decoder ring now returns0; encoder uvd_enc0 times out-110. Full GPU initialization fails; no fbcon. First recorded PCIe error occurs about6.33seconds after encoder timeout during failure unwind, followed by NULL-pointer oops. SSH survived to capture device state; no rebind/reload. This is progress versus e2e-001 decoder-stage fault, not full hardware acceptance or isolated proof of clock-fix causality. Next review the encoder-specific command-memory contract in standalone interpreter before another physical trial. See builds/shared-kernel-boundary-20261108/hardware-summary-e2e002.json.

2026-11-08 UVD encoder codec: candidate0023 extends shared Polaris11 ring encoding to UVD_ENC, leaving decoder/MMIO/other ASIC paths unchanged. Actual14-function extracted simulation runs512old/candidate x86/PPC ring cases plus wrapped IB/fence/END/NOP and predicate checks; correctedPPC matches unchangedx86 under explicit LE/no-hardware-swap model. Physical encoder fetch contract remains unverified. Full constrained e2e-003 build started; no A1222 access/deployment/reboot. See builds/uvd-encoder-codec-20261108/.

2026-11-08 fresh e2e-002 boot reached SSH, taint0/no AMDGPU. Installed complete e2e-003 candidate over SSH after USB serial and old boot hash checks; all staged/installed payloads verified, firmware aliases preserved. /boot.scr now selects /boot/e2e-003; exact e2e-002 selection retained as /boot-e2e002-rollback.scr. FAT synced/unmounted. Running kernel remains e2e-002, no GPU load, no reboot. Candidate physical boot/encoder acceptance pending. See live-deploy.json.

2026-11-08 e2e-003 physical trial: fresh untainted complete boot and module hash verified, rootRO/offboard capture, normal installed modprobe. UVD decoder and BOTH encoder ring tests now return0; all logged hw_init blocks including VCE return0. Later SMU SCLKDPM_SetEnabledMask0x145/parameter0x80 is followed by first PCIe fault47,539us after entry; responseffff after fault is not accepted firmware ack. SSH lost, no display acceptance, no rebind. Candidate shared encoder routing passes its targeted physical ring gate; actual packet bytes not captured, full IB/fence/encoder workload unvalidated. Source identifies command from smu7_ppsmc.h. Next review clock-level mask/table transition producer contract, not another UVD encoder retry. See builds/uvd-encoder-codec-20261108/hardware-summary.json.

2026-11-08 whole-flow reset: retained85-function direct source map plus Polaris callback table across VBIOS parsing, ATOM, table population/upload, state transitions, enable masks and SMU responses. Actual three-function common transport test passes1788cases per x86/BE-PPC architecture (all masks/responses, SRAM byte/tail preservation, invalid transfers). This validates given encoded inputs only. Full table/dependency/divider state parity remains open; no arbitrary swap of0x145argument, no patch/deployment/hardware retry. Source exposes ignored mailbox errors and continuation after state-step errors, treated as recovery issues not proven first-fault causes. See builds/smu-flow-review-20261108/.

2026-11-08 capture-backed preflight: parsed190962x86register events into75SMUtransactions, all observed responses retained. Actual common sender replay outputs match native x86/BE-PPC. Combined ATOM/ring/encoder/transport/replay suites allPASS under1CPU/6GiB but aggregate gateBLOCKED(exit2), deployment disallowed due missing complete tables/ATOM buffers/trace-loss coverage. Captured x86SCLKmask0xff differs from PPC0x80; input/state divergence must be resolved before another endian patch. No new kernel/hardware action. See builds/trace-replay-20261108/.

2026-11-08 upstream state-clock defect found: captured e2e-003 ATOM input2555576320/98530000 equals byte reversal of21400/5398 and returns zeroFCW. Actual V1 raw-state constructor omits LE decoding at six MCLK/SCLK loads across both revisions; separate dependency parser decodes correctly. Connected constructor->DPMupdate->trim regression reproduces exact reversed-clock/highest-entry-overwrite/mask80signature on oldPPC. Candidate0024decodes all six boundary fields; candidatePPC matches unchangedx86 across288version/archcases including both memory/engine/masks. Separate five-function complete-level pipeline passes256cases perarch/20480identicalbytes using partial captured ATOM fields. Seven aggregate suitesPASS but full gateBLOCKED; raw physical state/complete table capture and hardware causality remain open. No0024kernelbuild/deploy/GPUaccess. See builds/state-clock-decode-20261108/ and clock-table-pipeline-20261108/.

2026-11-08 SanDisk moved to R730: serial/partition identity verified, root/FAT read-only checks pass, e2e-003 boot/kernel/module hashes unchanged. Recovered six old PPC traces to server with source/cache hashes,3665760filtered register events; limited scope/polling not full coverage. Adjacent state audit confirms V1offset/class/caps decoding already present, boot FirmwareInfo clocks/voltages decoded, candidate0024covers six V1clockloads; separate legacyV0raw16clockloads remain follow-up. Full e2e-004 build started under4CPU/6GiB for compilequalification only. USB unmounted/unchanged; no physical retry. See builds/usb-audit-20261108/ and state-clock-decode-20261108/adjacent-input-audit.json.

2026-11-08 e2e-004 compile qualification complete: fullkernel/43modules/DTB/U-Boot bundle pass,687AMDGPU importCRCs checked, moduleSHAd96f5e51ed01079c889c670110fb1205cccc6b4cca0c307b34c82350d4303340. No USB installation; selected e2e-003 preserved, partitions unmounted after read-only forensic audit. Seven-suite overall hardware gate remainsBLOCKED; no assertion of completeinterfacefix.

2026-11-08 connected qualification: replaced independent test inputs with one actual-source constructor->DPM update/trim->ATOM/PLL->graphics/memory object->SRAM->SCLK mask/response flow. Ten driver functions,72cases/build; fixed x86/PPC and oldx86 produce53,883identicalbytes,432mailbox checks/arch. OldPPC rejected before upload/message in all72cases by offline fixture-domain guard. Eight aggregate suitesPASS; complete hardware gate remainsBLOCKED. Raw states/voltage/fulltables/timing remain partly modeled; no USB/GPU activity or new driver patch. See builds/connected-gpu-flow-20261108/.

2026-11-08 interface closure scope expanded: pinned-source ledger tracks22contracts through MMIO, firmware, state, rings, IBs, page tables, interrupts, DMA/cache and scanout. Searchable AMD-tree inventory retained offboard (686candidatefiles; counts are not coverage). Actual fence writer/reader, CPU PTE writer and Polaris IHdecoder pass1,024checks/arch with47,616identicalbytes. Existing GFX/compute IB-fetch BEbits and SDMA separate swaps preserved; UVDencoder IB pairing and upstream IHshadow BE TODO remain review items, not fabricated defects. Nine aggregate suitesPASS, hardware gateBLOCKED; no new patch/deployment/GPUaccess. See builds/interface-closure-20261108/.

2026-11-08 UVD included end-to-end in qualification scope: actual decoder create/destroy message and firmware-resume functions pass288message+5resume scenarios/arch with1,048,960matching emittedbytes. Actual encoder create/destroy IB producers pass768scenarios/arch including allocation/submission errors and fence ownership; modeled LEvsbyteswapped fetch demonstrates nativePPCpayload requires matching fetch/serialization contract. Actual encoder firmware fetch remainsUNRESOLVED, no conversion inferred solely from model. Eleven aggregate suitesPASS; no physical video/IB/firmware execution acceptance or new patch/install. See interface-closure-20261108 UVD receipts.

2026-11-08 PowerPlay error chain repaired in source:0025propagates voltage/mask request failures and stops the eleven-step SMU7 state transition at first error;0026carries it through PSM, avoiding false current-state publication and downstream display/force/profile requests. Actual-source negative-control regressions pass1,488transition+256PSM scenarios on old/fixed x86/PPC, preserving successful behavior. hwmgr runtime callers return errors; teardown still attempts cleanup. These are verified error-handling defects, not proof of initial PCIe-fault cause or recovery from a wedged transaction. Isolated005/006build qualification underway; no USB/hardware action. See powerplay-fail-stop-20261108/.

2026-11-08 combined fail-stop candidate006compile qualification complete:6.12.113-tabor-e2e-006/43modules/687AMDGPU importCRCs pass, moduleSHA39cb3f14c248af27a10ac04d970308c669f18b710deb7633c4380cab130a7a90. Candidate contains0024native-clock correction plus0025SMUtransition/mask error propagation and0026PSM failure propagation. Both005/006receipts retained; no SanDisk install or physical GPU trial. Hardware acceptance and unresolved interface contracts remain open.

2026-11-08 console-specific qualification: actual DCE10surface programmer and generic TTMdamage copy pass64success+4error scenarios/arch across16formats,3,200modeledpixelwords/arch. Kernel VT/fbcon/fonts/fbdev requirements verified. Read-only SanDisk audit shows003active,consoletty0present,nativebootstrap/init rather than getty. Staleboot.cmd/banner identified but notmodified. DIUcompiledbutnoTaborpixelclockhook,soactualDIUinitreturnsENODEV;noonboardfallbackclaimed. Fourteenoffline suitesPASS; physical framebuffer registration/modeset/scanout remainsopen. See console-path-20261108/.

2026-11-08 selected-display correction: physical003andvi.c selectDCE11.2/sharedDCE11callbacks,notDCE10. Historicalneighbor tests reclassified;actualnineIPdescriptor order/callbacks pinned. DCE11surface/TTMcopy passes64success+4errorcases/arch;actualdisplayATOMPLL/DCEclock/DTDhelpers pass392cases/arch withmatchingrequestbytes. ConfirmedDCE11mode_set discarded surface errors;0027propagates them and prevents falsehw_mode update,160old/fixed/archcases pass. Full007build/43modules/687importCRCs qualified;16aggregateoffline suitesPASS. VoidATOMerrorAPIs,physicalHPD/EDID/PLL/link/VRAM/scanout and delayedIBwork remain explicit gaps. Cached-state collector prepared;SanDiskunchanged/nohardwaretrial. See console-selected-path-20261108/.
