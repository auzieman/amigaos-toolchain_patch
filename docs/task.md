# Active task — private Tabor SPE toolchain intake

User confirmed the restoration objective: derive missing SPE/e500v2 support
from legacy kernel/compiler/libc sources and forward-port the required A-EON
changes. docs/patch-set-plan.md defines separate component series, comparison
against still-present target support and acceptance. Do not describe generic
PowerPC support as removed or assume a newer kernel needs a wholesale CPU
restore. Exact modern target revisions remain to select; no accepted restoration
patch or modern build result is claimed. Existing A-EON multi-board changes
need review/splitting so this work stays focused on Tabor.

Current scope clarification: A1222/Tabor e500v2 SPE is the immediate focus.
User reports Steven and Trevor requested this investigation; no additional
source access or external communication authorization is inferred. Other A-EON
platforms and the user-described Marhi board are future scope, pending precise
hardware identification. Preserve board-profile separation without implementing
additional platforms now. Builds use constrained BKC lab-edge jobs; the R730
is optional and its power/cooling work is separate. After baseline/forward-port
and boot-wrapper verification, prepare a minimal USB/rescue image with an explicit
userspace ABI. No physical drive write, lab job or hardware trial has begun.

User requests a private project supporting modern GCC/glibc SPE, initially a
viable Linux kernel, followed by graphics and a future Hyperion SDK lane.
Created private local project, examined existing Tabor workbench and SDK paths,
verified vendor patch applies to exact v5.4-rc3 upstream commit with git apply
--check, and recorded input hashes. No kernel/toolchain build, patch restoration,
remote creation, SDK modification or hardware trial completed this turn.

Current execution is the Linux/SPE kernel and userspace lane selected by the
Debian-baseline request. The separate AmigaOS SDK host/target/runtime contract
remains to establish and does not block this Linux build.
Next bounded execution: resolve exact modern kernel/toolchain pins, prepare an
isolated constrained lab job, reproduce baseline kernel output and inspect
board boot packaging before changing kernel version. In parallel intake terms,
locate supplied Hyperion patches and exact NXP/Freescale sample package; record
licenses and affected compiler/runtime components before reuse.

Uncertainty: modern GCC/glibc restoration effort, actual target ABI, SDK contract,
boot-firmware format acceptance, graphics hardware and full board testing.
Rollback removes only this newly created project; existing sources unchanged.

## Skills, prompts and isolated build runner — 2026-10-30

User requested E-projects-style local skills/prompts and Docker kernel build
logic. Applied skill-creator. Added three focused project skills and four task
prompts, routing from AGENTS.md, a digest-input Dockerfile with build entrypoint,
reviewed exact vendor profile, and an isolated kernel runner. Runtime inputs
are mounted read-only; committed source is exported into new storage and patch
hashes/applicability are checked before modifying that copy. Profile selects
vmlinux/modules/dtbs, not unverified firmware/boot image targets. No changes to
existing Tabor repository, SDK, installed system or remotes.

Verification: all three skills passed bundled quick_validate on host Python
(the session Python lacks PyYAML). Three real-Git integration tests passed,
covering source isolation/committed bytes, refusal to reuse output, hash mismatch
failure receipts and patch conflicts. Existing verify-intake also passes.
No tooling image build, full kernel compile or hardware boot was executed.
Image package resolution is not snapshot-locked; retain resulting image digest
and package list before accepting a build. Next execution remains a constrained
lab baseline job, followed by review of actual compiler/boot-format failures.
Rollback this slice via its Git commit; it does not remove reference inputs.

## Deferred Kyvos environment — 2026-10-30

User supplied workshop notes about Kyvos v2 automated AmigaOS provisioning and existing ISOs on Seagate. Recorded author-page evidence and inaccessible workshop/video claims separately in docs/future-amigaos-provisioning.md. Pegasos 2 is a future SDK/application test environment, not A1222/SPE acceptance. No media inspection or provisioning requested/executed; current kernel/SPE work remains the active objective.

## Manufacturer source acquisition — 2026-10-30

Applied tabor-source-intake. Confirmed P1022/e500v2 against NXP product information and local board DTS. Bounded local filename inventory did not establish a complete prior vendor SDK; no unmounted Seagate search performed. Downloaded nine clean shallow repositories from the NXP-domain-verified nxp-qoriq-yocto-sdk organization: GCC4.9.2, EGLIBC2.19, SDK1.7 Linux/U-Boot, P1022 layer, historical toolchain layer, manifest reference, boot-format and flib. Verified concrete GCC SPE backend and libc e500/fenv/context implementations. flib is SEC/crypto reference, not an SPE runtime. Recorded exact revisions/tree IDs/inspected-file hashes and per-component licensing qualifications; all repositories passed connectivity fsck and the repeatable check-only command.

Vendor-source lock and docs/vendor-source-intake.md distinguish mixed historical references from a coherent SDK build. Complete binutils/Poky/recipe closure remains pending. Direct vendor PDF URLs returned 404; no downloaded manual is claimed. No compilation, reference-tree edits, bootloader execution, media writes or remote publication. Next: compare historical SPE/compiler/runtime code with last supported upstream and locate supplied Hyperion patch information before selecting restoration targets.

## Debian modern-source iteration — 2026-10-30

User selected recent Debian kernel/glibc and explicitly requested disposable
re-patching on each iteration. Pinned linux 6.12.113-1 (trixie security) and
glibc 2.41-12+deb13u4. Cache contains DSC/orig/Debian tar files with locked
sizes/SHA256; independent archive signature-chain verification remains explicit
as unimplemented rather than claimed. Added fresh-extraction dpkg-source runner,
ordered per-component patches, failure receipts, and canonical BKC CLI/core
submission/collection template. Tests prove independent re-patching and cache
rejection (using a small extraction fixture); all five local tests passed.

Initial Linux patch adds modern Tabor compatible matching and vendor-derived
DTS, with P1022 common init from modern upstream. Linux already retains e500/SPE;
no fake CPU restoration. Audio/DIU and board power controls remain outside the
first serial/PCI slice. Preparatory glibc patch restores 36 deleted-only e500
sysdeps files from upstream removal a053e878494080f7070cf92890e546057236c9c9;
configure rejection/shared state handling are not yet restored. Exact origin
inventories retained. Both patches pass selected upstream-file apply checks;
Debian-integrated and compile results must be recorded separately.

BKC initial run 0fce93d7-aeb9-4fdf-9165-5a7b6834c10c stages immutable bundle
f00d02cc4336dd3d4f3835101f301e1dad5b303259d260b5ff54583294815ea2.
This first bundle precedes the preparatory glibc source import and runner's
scoped board precheck; later bundles include those changes. First tooling image
built on lab-edge. Its fresh work directory was moved while empty onto existing
shared Tabor storage to avoid exhausting the 50 GiB lab-edge root filesystem;
canonical subsequent jobs now select shared storage directly. Runtime limited
to 2 CPU / 4 GiB, no network. No boot media, live board or desktop changes.

Initial run result: stopped the known build container during NFS extraction
because only about 15 MiB had been written after several minutes and the tar
process was I/O-blocked. No source-patch or compiler result was reached. BKC
marked the run failed and retained tooling logs. Original runner PID1 termination
did not create its receipt; collection is now conditional and SIGTERM records
an interrupted iteration when possible. This is an infrastructure failure,
not evidence against Tabor support. Subsequent runs use fresh local work,
require 4 GiB free before kernel extraction and stop running commands below
1 GiB free. Shared storage remains available for retained completed outputs.
Tooling image built successfully; apt package/toolchain versions are retained.

Private collaboration handoff — user created auzieman/amigaos-toolchain_patch and reports inviting Steven Solie, explicitly authorizing prompts/patch publication there. GitHub metadata verified private visibility and an empty remote. Publish the development history with review-start status, source pins, prompts, patches and build logic; exclude caches/generated artifacts/media. No collaborator messaging or additional access changes requested/performed.

BKC retry 23fa71a4-4dbb-49a3-9249-8333c3312e4b: local extraction and Debian
patches succeeded; local Tabor patch applied. Real tabor.o and tabor-a1222.dtb
compiled; tabor.o inspected as 32-bit big-endian PowerPC ELF. Full build was
intentionally interrupted after discovering olddefconfig had re-enabled DWARF
via its choice despite disabling the derived DEBUG_INFO symbol. Corrected the
runner to select DEBUG_INFO_NONE and assert it after olddefconfig. glibc's
36-file preparatory patch applied to the actual Debian source; its compiler
preflight failed because Debian GCC does not accept SPE ABI/ISA flags. This is
not a restored glibc result. Returned artifact hashes passed. Supplementary
board object/config/DTB copies retained with hashes; generated source and object
trees discarded only after evidence retention, leaving caches intact. New
retention helper rejects symlink cleanup and has dedicated safety tests; all
seven local tests pass. Review evidence is docs/builds/20261030-first-debian-iteration.json.

User requested useful commit notes for Hyperion reviewers. Added CONTRIBUTING.md, a local commit template and an engineering progress log backfilling the significant commits/runs without rewriting published history. The third run stopped at the initial disk guard because archive copies consumed local space; archive caches are now deduplicated and project bundles will exclude archives. No partially copied NFS file is treated as verified input.

Current BKC checkpoint: b57b3f7b-cc3c-43b4-95a7-31b11186478b successfully uses the canonical verified source cache and approximately 150 KB project bundle. Fresh Debian extraction, patch application, explicit DEBUG_INFO_NONE and scoped Tabor object/DTB checks passed; full vmlinux/modules/dtbs cross-compilation remains running at the checkpoint. Root-disk headroom is stable around 2.8 GiB during compilation. No new source patch or compiler error observed so far; collect final receipts before claiming a complete kernel build.

## Full kernel compile and edge emulator preparation — 2026-10-30

BKC b57b3f7b-cc3c-43b4-95a7-31b11186478b completed the full modern
vmlinux/modules/dtbs build. Collection verified SHA256SUMS; vmlinux is static
32-bit big-endian PowerPC ELF. Exact receipts are in
docs/builds/20261030-full-debian-kernel.json. glibc still fails its compiler
SPE flag prerequisite, so overall component pipeline failure does not negate
the kernel compile result.

User authorized pulling prerequisites and booting on edge. Applied
tabor-kernel-build. The full Tabor config disables PPC_QEMU_E500, requiring
a separate minimal emulator configuration from freshly extracted Debian
sources with the same patch. Initial configuration attempts stopped before
compilation: first missing FSL_SOC_BOOKE prevented board selections, then
DEBUG_KERNEL being disabled hid DEBUG_INFO_NONE. Both failure receipts and
configs retained on edge; neither was a kernel compiler or boot failure.
Corrected seed enables both dependencies. Each retry uses a new source/output
workspace. QEMU installed into a separate container-derived tools image; host
services, GPU, boot defaults and physical media unchanged.

User requested collaborator documentation during the emulator build and
expressed interest in E-Trixie. Added docs/e-trixie-follow-up.md with explicit
ABI, rootfs, real-board and graphics gates. No full distribution image build
is claimed or started; the active boot attempt continues. The third emulator
attempt hit the initial free-space guard; two dpkg-source-created duplicate
orig archives were compared against the canonical source cache and removed.
The fourth fresh extraction passed configuration checks and is compiling.

First emulator kernel compiled (attempt-004), but its bounded QEMU test returned
no kernel serial output or init marker. No panic text was observed; silence is
not a successful boot. Inspection found PHYS_64BIT and SERIAL_OF_PLATFORM
missing in the minimal seed: QEMU ppce500 places CCSR devices above 4 GiB.
Added both, verified resulting selections in a new fresh attempt-005, and
changed the harness to stream stdout directly to serial.log during execution.
Stable edge live.log follows the build and switches to the serial log.

User requested screenshot-ready terminals on desktop 4 and an ANSI monitor.
Opened two local Terminology windows, verified __E_WINDOW_DESK=(3,0) on external
monitor zone 1: build/serial tail and edge-dashboard.py. Metrics label edge host
and container CPU/RAM explicitly; guest metrics, SPE/glibc and physical GPU
acceptance remain pending. User also requested the eventual live USB reflect
the laptop's main E desktop: record it as a Trixie-based A1222 image intent,
requiring rebuilt target packages, reviewed appearance inputs and board boot
acceptance. No laptop rootfs clone, private-config export or media write done.

Final attempt-005 passed: serial log identifies Linux 6.12.113, QEMU e500v2,
two brought-up CPUs, initramfs unpack and /init marker. No panic observed during
the bounded 60-second run; VM stopped normally by the harness time limit.
Collected artifact manifest verified, boot kernel SHA matches compile receipt,
and repository init/config seed match receipt hashes. Retained build/log/boot
artifacts before discarding generated source/object trees. Evidence:
docs/builds/20261030-qemu-boot.json and 20261030-qemu-serial.log. Seven local
workflow tests pass. No SPE arithmetic, glibc ABI, graphics or physical board
acceptance. Desktop 4 console/dashboard windows intentionally remain open.
Next bounded action: reference SPE toolchain/runtime and direct ABI tests, then
headless SDL/Mesa tests; E-Trixie laptop-style live image remains a follow-up.

## Minimal E/gears intake and direct SPE proof — 2026-10-30

User requested the smallest E/glxgears guest reusable on A1222, with GPU
assignment and ANSI/remote graphics evidence. Read kernel-build and source
intake workflows. Edge PCI inventory exposes only virtual VGA 1234:1111; no
NVIDIA device/render node is visible, and current QEMU image has no GL display
backend. Linux 6.12 virtgpu_kms.c additionally enables VirGL 3D only for
little-endian guests; e500v2 here is big-endian. Do not promise that enabling
host NVIDIA support alone makes this stock accelerated path work. No GPU
assignment, driver unbinding or hypervisor change performed.

Implemented a libc-free SPE init: single/double 1.5+2.25 checked exactly as
3.75, using efsadd/efdadd and evldd/evstdd. Reused the verified QEMU kernel.
Bounded 60-second run passed and raw serial/initramfs/source hashes verified;
disassembly confirms the intended instructions. Evidence in docs/builds.
Selected arithmetic PASS is distinct from unvalidated full ABI/glibc/GL.
Updated dashboard in a replacement terminal on desktop 4; closed only the
previous owned monitor window. Serial tail remains open on the SPE result.

User suggested physical USB if GPU assignment is unsuitable. Seagate is not
currently visible in local block inventory; the recorded Tabor image mount is
absent, and a bounded image-name search did not find a reference. The existing
Cruzer was not mounted or written. Prepared a hash-verified regular-directory
bundle at work/physical-test-001 using the full board kernel/DTB/config and
shared SPE initramfs. It is NOT firmware-boot-ready and contains no E/rootfs.
Reference firmware header/load addresses and compatible userspace are still
required; the old zero-padding wrapper is not accepted boot packaging.

Docs/minimal-e-gears.md bounds the E/Xorg/Mesa/glxgears payload and remaining
inputs. No full distro build, media write or physical boot was performed.
Next: make the reference SPE image available, verify boot format, then construct
the minimal userspace; identify real A1222 AMD GPU before selecting its driver.

## SanDisk target inspection — 2026-10-30

User removed Seagate and inserted a Debian SanDisk for a possible bare-metal
trial. Read-only host inventory identifies a 14.32 GiB SanDisk Cruzer Glide
at the current /dev/sdb path. blkid/partition inspection shows a hybrid ISO9660
installer with a small EFI partition. A temporary ro,nodev,nosuid,noexec mount
confirmed .disk/info: Debian GNU/Linux 13.7.0 Trixie official amd64 NETINST
with firmware. install.amd contains vmlinuz/initrd.gz. This is x86-64 media,
not A1222 PowerPC/SPE boot media. Temporary mount was removed after inspection.
No formatting, image write, boot-setting change or alteration of contents.

The stick is a possible future target, not the reference Tabor image needed
for firmware-wrapper verification and compatible userspace. Physical staging
remains not boot-ready. Device paths are transient; re-identify before any
future authorized write and do not infer erase authorization from insertion.

## ASCII comparison and measured Mandelbrot demo — 2026-10-30

User requested an ASCII with/without comparison, then a fractal/timing graphic.
Initial boot results had no matched timings; added a hash-verified ASCII
correctness report without inventing performance data. Then implemented a
freestanding 128x96 Mandelbrot workload using the same FP32 bit-pattern API:
GNU software FP helpers from the pinned vendor GCC4.9.2 reference versus
explicit efsadd/efssub/efsmul. Both use the same kernel/CPU/grid/algorithm.
This is not restored compiler SPE ABI, glibc, GL or physical-board evidence.

Initial run failed timing probe; fixed clock_gettime64/timespec and syscall
clobbers, retained that lab attempt without accepting its measurements. Retry
run-002 passed three measured renders per backend after warmup, alternating
order. All 12,288 escape counts match exactly; all timed checksums abd5de74.
Medians: software 446341 us, SPE 173063 us (2.58x in this QEMU TCG run).
Timing excludes boot/serial transfer and host image/palette generation.
Disassembly audit confines SPE instructions to the three intended functions;
no classic FP arithmetic/load/store found. Software/input notices preserved.

Raw serial, receipt, disassembly, hashes, per-trial timings, ASCII, PNG/SVG
comparison and independent images retained under docs/builds/fractal-20261030.
Source/helper hashes and build flags in 20261030-fractal-inputs.json; replay
recipe in bench/README.md. Report generator rejects failed/incomplete/mismatched
runs before presenting results. Desktop live console switches to ASCII report.
The image is a CPU arithmetic demo, not GPU-rendered fractals or glxgears.

## Incremental minimal A1222 package seeds — 2026-10-30

User requested an ultra-trim build list with E, GL tests, optional Firefox and
one login, targeting an A1222 with 8 GiB and AMD Radeon. Created the canonical
profiles/images/a1222-minimal.json and docs/minimal-package-plan.md. Stages:
source-built minbase-equivalent serial rescue, E/Xorg/Terminology, GL/DRM tests
(first desktop target), optional Firefox ESR after architecture/toolchain review.
All runtime code must be freshly built against the restored SPE sysroot; no old
Tabor rootfs or generic PowerPC binary mix. Required dependency closure is not
yet solved, and this seed list is not a version/source lock or built image.

Default one human tabor account, password at provisioning, console login plus
startx, no greeter/autologin. One init/udev/logind/user-D-Bus stack. No-recommends
policy with required EFL/Mesa runtime assets retained. SSH/VNC/SDL are explicit
optional overlays. Target RAM/revision still require firmware/device-tree/
HIGHMEM validation; exact Radeon PCI ID determines DRM/Mesa/firmware and LLVM
needs. 8 GiB physical RAM does not change PPC32 per-process address limits.

Checked official Debian package pages and existing lab amd64 metadata for seed
names only; not SPE availability. mesa-utils-extra has no cached candidate and
is omitted; AMD firmware exists in non-free-firmware. Verified JSON syntax,
ordered inheritance, unique stage/package entries and optional browser policy.
No runtime build, service change, media write or hardware trial in this slice.
Updated older minimal-E notes to reflect fresh-build requirement explicitly.

## Shell-first edge cycle — 2026-10-30

Started isolated edge cycle-001 for a source-built serial shell. GCC8.5 is a
pinned historical SPE bootstrap/reference, not the completed modern compiler
port. Compiler build running; pinned Linux6.12.113 UAPI export passed. Corrected
experimental glibc patch2 changes fourteen intended selection/FPU/saved-state
files and passed fresh Debian preparation plus exact integrated-file hashes.
Scripts cover fetch, compiler, headers, libgcc, experimental static glibc,
minimal static BusyBox1.37 and real serial-shell commands. Runtime excludes
E, systemd, package management, docs and host build tools. Later stages are
queued to stop at failure; no libc/shell boot pass is claimed at this checkpoint.
Seven existing workflow tests, Python/shell syntax and cached source checks pass.

Shell-cycle checkpoint: reference GCC8.5 built and generated efsadd/efdadd from
C; pinned UAPI export and static libgcc passed. Fixed target binutils PATH and
retained the failed first libgcc receipt. glibc configured with e500 sysdeps;
static-only configure failed generated-header setup, so a fresh source replay
uses the normal library build (runtime still copies only a static shell).
Libc compilation is underway. New fixes and checkpoint receipt are committed;
no shell/ABI acceptance yet.

## SPE libc retry and OS4 media probe — 2026-10-30

Patch3 ports twelve restored e500 fenv files to current INTERNAL_SYSCALL_CALL
and one-argument error checks, preserving prctl flags/error behavior. Fresh
Debian glibc-004 preparation passed; stage attempt3 compiles against the SPE
reference compiler. Full libc/ABI/shell results remain pending. Retention now
accepts numbered component iterations; failed002/003 logs/config/receipts kept
before generated source/output cleanup recovered about700MiB. Seven workflow
tests and Python/shell syntax checks pass.

User-uploaded ISO and Enhancer LHA verified read-only; hashes and bounded QEMU
probe in builds/20261030-os4-iso-probe.json. A1222-specific Kicklayout confirmed.
Sam460 30-second firmware probe initialized DRAM/PCI/SM502, ended at VGA:NO CARDS;
no AmigaOS boot observed. No installed disk, media modification or runtime-code
import. scripts/os4-iso-probe.sh preserves the bounded reproduction. QEMU has
no A1222 machine here; Pegasos/Sam media/firmware compatibility is a separate
requirement. Proxmox normal guest architecture choices do not include PPC;
standalone PPC QEMU can provide VNC, including inside a managed Linux VM.

## Visible OS4 probe under Proxmox VM127 — 2026-10-30

Verified Proxmox192.168.1.9 inventory: running VM127 is swarm1.lab.auzietek.com,
our existing edge host192.168.1.15. Launched constrained nested standalone
QEMU Sam460,512MiB,one CPU,ISO read-only,no guest network or installed disk.
VNC binds edge loopback5907, SSH forwards local15907, ignored local noVNC
checkout/websockify venv serves localhost6087. Firefox view-only client connected.
Graphical capture advances beyond serial: Kickstart files load, then final
screen says Loading done, now launching kickstart. Repeated capture unchanged;
QMP running does not establish OS boot. No Workbench. Probe stops after20minutes.
This uses existing Proxmox inventory VM127, not a new native PPC inventory VM.
Receipt: builds/20261030-os4-display-probe.json; screenshot/media stay ignored.
Matching Sam/Pegasos/AmigaOne media is needed for a supported OS4 emulator test.

SPE glibc004 compiled past old syscall failures, then host objcopy could not
recognize PPC libc_pic.os. Explicitly select target OBJCOPY and STRIP alongside
other target binutils. Retained004 evidence, discarded only generated trees,
and started fresh005/stage4 detached on edge. Pipeline stops at first failure,
then builds static shell and boots it only if libc succeeds. No libc pass yet.

## New ATI emulator slice and USB preparation — 2026-10-30

Pinned QEMU 11.1.3 from upstream; detached signature matches the release
fingerprint published on qemu.org. Source compilation running locally with
Ninja -j2, ample local storage, no system install. A bounded 90-second ATI
Sam460 device/firmware probe is queued after compilation; not an OS/2D pass.
New driver 0.1 downloaded privately, SHA-verified and README reviewed. Personal
non-commercial use/no redistribution: neither driver nor proprietary media is
committed. The private overlay helper preserves source files and rejects an
A1222 Kicklayout for AmigaOne/Pegasos; actual matching media remains needed.
See docs/qemu-ati-test.md and profiles/qemu/amigaos-ati.json for reproducible
build/overlay/configuration, and the preparation receipt for actual status.
Seven workflow tests and Python syntax checks pass; emulator build pending.

User authorizes thumbdrive preparation when ready; USB-first-boot.md records
readiness gates and the user's rear-port recollection, not an independently
verified rear-only restriction. Manufacturer manual confirms USB boot and
critical firmware settings; no port-bank rule found. SanDisk still14.3GiB,
untouched. Physical wrapper/load ranges, shell runtime, local display/keyboard
remain readiness gates; no boot defaults or internal disks modified.

Libc005/stage4 progressed further but selected host g++ for a support program.
Explicit CXX=false lets configure disable unavailable target C++ for this
C-only bootstrap. C++ ABI acceptance remains a later gate. Retained005 evidence
before generated cleanup, fresh006/stage5 running on edge; pipeline still stops
at first failure before shell/boot. This is a tool-selection fix, not a new
source mutation or claimed libc pass.

## Updated emulator retry — 2026-10-30

Stopped previous tabor-os4-display-002 guest at user request. QEMU11.1.3 first
build exposed missing libfdt headers in Pegasos/VOF; auto configuration had
silently omitted FDT. Fetched the exact DTC revision from upstream dtc.wrap,
reviewed README.license, and require --enable-fdt=internal in the replay helper.
Configuration now includes libfdt and rebuild is running; the post-link ATI
probe and separate Linux shell check remain queued. No updated-emulator boot
result is claimed yet. Local browser viewer6088 waits for the new guest.

## Source-built glibc and shell acceptance — 2026-10-30

Fresh glibc006/stage5 compiled and installed experimental glibc2.41 against the
pinned SPE reference compiler. Captured core sysroot library/startup hashes.
BusyBox allnoconfig resets seeded booleans, so generate all-no first, overlay
our explicit seed and resolve with oldconfig. Use recognized CONFIG_EXTRA_*
flags plus explicit bootstrap sysroot headers/startup search. Retained failed
shell001/002 attempts. Shell003 built and reached fallback ash, but script
/init failed ENOEXEC because the smoke kernel lacks BINFMT_SCRIPT; that run was
not accepted. A native static init avoids changing the accepted kernel. One
intermediate004 staging attempt lacked the new source file; source staged
before fresh005 retry.

Shell005 plus native init passed on existing QEMU10.0.13/e500v2: SHELL_READY,
real commands, ppc from uname, /proc/meminfo, SHELL_DONE, no panic. Hash-verified
serial and libc/shell/boot receipts in docs/builds/shell-20261030. This is shell
runtime acceptance, not full SPE fenv/signals/threads/unwind ABI or physical USB
boot. New qemu-shell-smoke --qemu records executable hash/version for the queued
QEMU11 replay. Seven existing workflow tests, Python/shell syntax checks pass.

## Shared console terminal fix — 2026-10-30

User observed odd terminal behavior. Fixed doubled carriage returns by clearing
PTY output translation before QEMU starts (including ONLCR, because QEMU enables
OPOST). Use stdio chardev signal=off so Ctrl-C reaches the guest. Native init
acquires ttyS0 as controlling terminal; enabled BusyBox editing/history. Fresh
shell006 boot/commands passed. Shared container tabor-spe-shared-shell-002 now
runs that image; Up-arrow recalled a command, Ctrl-C preserved the guest, and
CONSOLE_FIXED returned with single CRLF. Existing old container had exited on
SIGINT; no user disks or host services changed. Seven workflow tests and Python
syntax checks pass. Console remains shared and isolated, not a network login.

## C ABI gate exposes remaining scope — 2026-10-30

Added source-built static C checks for float/double, varargs, formatting, fenv,
setjmp, signals, pthread/TLS and ucontext. Initial link rejected historical GCC
64-bit long-double default against glibc2.41's IBM128 objects. Explicit
-mlong-double-128 fixes the mismatch; the live package plan records this flag
for every future consumer. Never suppress the linker ABI check.

ABI003 on QEMU10 passes arithmetic/varargs/formatting/setjmp/signal/ucontext;
fenv upward rounding remains 1.0 instead of nextafter(1.0). The tiny kernel
has no FUTEX, so the pthread check is explicitly SKIP_KERNEL_FUTEX, not a libc
thread failure. Prior002 hit libc's futex abort as PID1 and panicked; retained
that failure in lab. ABI003 detects ENOSYS first, reaches DONE, no panic, but
overall ABI gate remains failed. Hash-verified raw evidence in builds/abi-20261030.
QEMU11 repetition shows identical basic results. QEMU SPE arithmetic uses
vec_status, while spr_write_spefscr only stores the register; this suggests an
emulator rounding limitation, not yet proof that the libc setter is wrong.
Physical fenv validation and a futex-enabled runtime kernel remain next gates;
C++ unwinding and broader ABI coverage are still untested.

## Live image remote tools and board payload preparation — 2026-10-30

User requested SSH client/server and VNC for live boot, then authorized the
larger image and SanDisk write once ready. Promoted openssh-client/server into
rescue and x11vnc into E/X11 in the source-package plan. Lab/LAN SSH uses the
normal tabor account with privately provisioned keys; physical-display VNC
binds loopback over SSH and waits for X. No target packages/listeners installed
by this planning change. Elgato HD60 S+ appears on laptop video4/5; format query
reports1080p. Two bounded frame reads failed I/O; no capture stream inspected
or existing capture application changed. User states HDMI output.

Packaged the full board kernel and tested shell as standard U-Boot PPC/Linux
gzip uImage/uRamdisk plus DTB. Verified header/data CRC and payload decompression,
using the Linux wrapper's objcopy/gzip/mkimage method rather than old zero-pad
wrapper. Derived physical kernel extent0x24be2cc from ELF; proposed source
buffers64/128/160MiB avoid it. Receipt builds/20261030-board-package.json is a
review payload, not claimed hardware boot. HDMI controller still unidentified;
initial board patch lacks DIU hooks and Radeon DRM is disabled. USB HID is a
module absent from the tiny rootfs. Those must be resolved for a usable local
boot before the authorized stick write. Real firmware iminfo remains an
on-board check. No drive writes or persistent boot-default changes performed.

R730 old address10.20.0.130 responds through edge, but SSH key differs. User
expects the resale Trixie image; no host identity inferred, known_hosts not
changed and no build load deployed until the new OS identity is verified.

## Updated QEMU result — 2026-10-30

QEMU11.1.3 build completed with pinned internal libfdt. The same accepted
kernel and fresh source-built shell passed real commands on the new emulator;
binary hash/version and raw serial retained in builds/qemu11-20261030. A C ABI
repeat reproduces old-emulator partial results, including fenv rounding fail
and missing-kernel-futex skip. No full ABI acceptance inferred.

Updated Sam460/ATI read-only ISO probe completed. Firmware reports VGA/VESA OK;
no AmigaOS desktop seen. Initial screenshot targeted built-in SM501 by default;
repeated with explicit ati0 device and ATI-head screendump, still black at60s.
Receipt records bounded observation and no replacement guest driver loaded.
The A1222-specific CD remains unmatched to this emulated board. No proprietary
media/driver or screenshot committed. The Linux result is independent of this
OS4 outcome. Seven workflow tests and Python syntax checks passed.

## OBS identifies physical GPU; native SSH follow-up — 2026-10-30

User opened control panels in OBS on desktop3. Captured only OBS window
0x4a00011 read-only; capture settings unchanged. Enlarged PCI panel identifies
1002:67FF graphics and1002:AAE0 HDMI audio. Initial digit reading677F was
corrected before selection. Linux6.12.113 amdgpu table matches67FF to
CHIP_POLARIS11, so select amdgpu/radeonsi and family firmware rather than
legacy radeon or an assumed RX550 retail variant. Revision overrides and
required firmware still need source review. Receipt builds/20261030-a1222-gpu.json;
OBS screenshots remain ignored. This resolves the display-controller question,
not actual Linux graphics validation.

User floated native AmigaOS SSH/sshd/AmiSSL remote access. Checked AmiSSL
upstream and archived OS4 OpenSSH4.5p1-1 author readme from Aminet mirror:
that port explicitly provides clients only. No incoming daemon established;
AmiSSL update is not assumed to supply sshd. Next native step is identify
installed versions and errors before selecting any server/crypto fix. This
remains separate from Linux live-image OpenSSH; no OS4 software/accounts
installed or changed. Source: https://ftp.fau.de/aminet/comm/tcp/openssh-bin.readme
and https://github.com/jens-maus/amissl .

## R730 build capacity prepared — 2026-10-31

User authorized remote preparation of the resale Debian R730 for QEMU/KVM.
Found the final installed owner credential in a later private record, distinct
from the initially linked earlier installer credential. Completed mandatory
first-login rotation; new note remains mode0600 outside Git. Verified chassis
4XC6282 and root UUID against October5 installation evidence. Installed existing
BKC public key for owner, retaining password-authenticated sudo and scoped SSH
host-key tracking rather than replacing the old global host record.

Prepared QEMU10.0.13 x86/PPC, libvirt, Docker and native/cross build tools.
Docker CLI is a separate Debian package: initial recipe stopped at final version
check, fixed dependency and full replay passed. No partitions, firmware settings,
PCI binding or boot defaults changed. Existing `/srv/data1` has about1.77TB free;
owner workspace `/srv/data1/tabor-build` has cache/work/results directories and
four-CPU/8GiB initial policy. No bulk source/toolchain transfer or larger image
build started yet. Existing suspect data2 is not the selected workspace.

KVM guest ROM executed and observed VMX; host nested=Y,61 IOMMU groups. Actual
nested L2 boot untested. RTX3060Ti plus audio occupy group28 alone; nouveau stays
attached, no passthrough claim. Build-disk SMART reports OK and current boot log
shows no disk I/O errors; this is not a full media-health certification.
PPC e500v2 TCG boot of the previously accepted kernel/shell passed real commands.
Pinned Debian container passed 2CPU/4GiB/network-none check. Evidence retained
under builds/r730-20261031. Next: stage verified source/toolchain inputs and
resume fresh board-kernel/rootfs iterations, including amdgpu/local console/HID
requirements. No physical A1222 acceptance or full SPE ABI acceptance inferred.

User clarified current native AmigaSSH comes from OS4Depot, so the older Aminet
readme is reference only and does not identify their installed package. Native
SSH repair is deferred while the larger Linux build remains priority.

## AmigaGCConDocker integration intake — 2026-10-31

User reports Steven may want our work for walkero-gr/AmigaGCConDocker. Reviewed
the linked target docs, packaging Dockerfile/Makefile/changelog/license and
separate AmigaGCConDocker-base compiler/dependency recipes through GitHub tools.
Pinned inspected commits in docs/amigagccondocker-integration.md. Compiler base
builds AmigaLabs/adtools; target runtime choices are newlib/clib2/clib4, not our
Linux glibc. Explicitly recorded that our modern GCC patch series is still empty
and the present Linux ABI gate remains partial. No AmigaOS compatibility inferred.

Bounded next action: obtain exact image/GCC/runtime and failing command from
Steven, pin adtools/GCC inputs, reproduce smallest failure on R730, then select
an independently validated compiler patch if needed. Modern SPE support is a
working hypothesis only. No upstream writes, proprietary SDK imports or extra
container/toolchain builds performed for this review. Larger Linux build remains
the active implementation track.

## 2026-10-31 — R730 larger Linux image / VM132 reference

Returned to Linux `development`; kept the separate AmigaOS Docker/SPE work on
its own branch. Inspected live VM132 read-only: amd64 E 0.27.1/Terminology
1.14/Xorg/Mesa/LightDM, about 12 GiB used. Added a functional target profile;
no x86 packages or VM disk were copied into the target rootfs.

R730 `linux-live-001` now contains the retained reference tools/sysroot,
verified Debian source caches and fresh constrained build iterations. Board
kernel `tabor-live-001` compiled vmlinux/modules/dtbs with built-in USB keyboard,
USB storage, wired network and amdgpu legacy DCE/framebuffer support. The
original seed fragment is retained with its exact receipt hash; the newer
fragment makes already-selected time32/multiuser/PTY/seccomp choices explicit.

Built richer BusyBox/native init, Linux CLI fractal/ABI payload, pinned Polaris
firmware, isolated libxcrypt sysroot overlay and static OpenSSH 10.0p1 with its
auth/session helpers. New native init follows HDMI/serial console selection and
starts DHCP/SSH independently. Key-only ordinary uid1000 login uses the existing
operator public key; no client private key or baked-in SSH host key is included.

QEMU `network-probe-003`, kernel `qemu-live-005`, initramfs `rescue-full-001`:
background DHCP/SSH, native laptop key login, uid/home permissions, PTY and both
CLI tests pass their selected probe assertions. All 12,288 fractal pixels match;
three software and three explicit-SPE trials retained. Eight basic ABI checks
pass, including pthread/TLS after legacy time32 support; fenv rounding remains
FAIL. Probe PASS explicitly permits this known recorded ABI failure and does
not assert full ABI acceptance. Earlier failed network probes exposed missing
NET_CORE/legacy virtio transport in the reduced kernel; checked final settings
now prevent that omission. Source/config/receipts and raw CLI outputs are under
`docs/builds/r730-live-20261031`; full build trees/logs remain on R730.

Packaged standard U-Boot payloads with ELF/hash/CRC/decompression checks; created
a 2 GiB MBR/FAT32 file image and verified each boot file by filesystem readback.
The downloaded local image also matches its complete SHA256. The authorized SanDisk
write completed and the entire 2 GiB image readback matches SHA256
`7ac3e5d2aae9a6cb901a320fca42f18f406f2851dd65dc47816c8f06c3f613ff`. No actual A1222 boot, display/GPU output,
full floating ABI or E/Xorg/Mesa desktop is accepted. Native image is a hardware
rescue increment, not the completed VM132 desktop. Next: manual temporary U-Boot boot with OBS capture, retain real board/network/ABI logs, then
build graphical dependencies against the validated target ABI.

## 2026-10-31 — repeated larger-image request: R730 desktop prerequisite cycle

Kept Linux development separate from AmigaOS Docker work. Rebuilt the missing
reference C++ toolchain/runtime from pinned GCC8.5 with the restored read-only
SPE/glibc sysroot, 128-bit long double and bounded R730 resources. Iteration 001
failed on missing target ar; fresh iteration 002 adds private binutils aliases
and passes. Installed tree and binutils hashes retained. This is historical
reference tooling, not modern GCC restoration.

Static C++ probe 001 passed exception unwind but failed at a weak pthread_join
reference. Probe 002 explicitly retains pthread functions at static link and
passes all four selected checks. A separate shared payload resolves and checks
the full PPC32 DSO closure. network-probe-004 plus laptop native SSH executes
that shared C++ binary: long-double size, exception/RAII unwinding, thread TLS
and uint32 atomics PASS. Base C tests retain eight PASS/fenv FAIL and fractal
pixels remain identical. No full floating ABI or wider atomic claim.

Captured VM132's installed source versions, cached EFL1.28.1/e17 0.27.1/
Terminology1.14 Debian source packages, and reviewed copyright/build metadata
and exact Meson options. Added locked source inputs and a software-X11 EFL
candidate; no target build/configuration success or complete dependency closure
is implied. Keep native code generators distinct from PPC runtime libraries.

Packaged shared-runtime candidate usb-cxx-image-001 on R730; verified U-Boot
checks and FAT boot-file readback. It is not written to the existing SanDisk,
which still holds the previously verified rescue image. Still no E/Xorg/Mesa
installed or physical A1222 boot/HDMI/GPU validation. See desktop-foundation.md
and docs/builds/r730-desktop-prerequisites-20261031 for successes and failures.
Bounded next build: lock/build native EFL generators and software X11/font/
image/crypto/session dependencies, then E/Terminology/Xorg. Keep Mesa behind
ABI acceptance and run native board diagnostics when the USB trial is available.


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


## 2026-10-31 — requested A1222 desktop theme selection

Include Fire, Molten Steel, Frosty and Minty when E reaches the image. Exact
existing local preview archive hashes are in profiles/images/a1222-theme-selection.json;
these are references, not installed target binaries or a runtime compatibility
claim. Fire Strong Animated remains excluded per the earlier rejected flame
review. Start Fire/Molten wallpaper selection with still candidates; animated
Molten variants remain available for later target performance review. Frosty
and Minty use their recent corner candidates; no additional wallpaper has been
selected for them. Verify E/Elementary selector discovery and actual target
rendering before declaring integration. Preserve default E first boot. Full
inherited desktop assets retain their existing notice/distribution boundaries;
no third-party asset import or public release occurs in this selection change.


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


2026-11-01 installation-state correction (user instruction): preserve native
Debian package installation and configuration state throughout image assembly.
Current bootstrap/session .deb bundles are lab transport packages without
maintainer scripts; their installed status is not evidence of individual Debian
package configuration, dependency closure, triggers or service provisioning.
Do not describe these bundles as a completed Debian installation. Retain the
installed root, dpkg database, configuration, owners/modes and generated state
when archiving; do not replace it with another staged file overlay.
Before another E acceptance claim, inspect actual module failures, system and
session D-Bus, missing dependencies and helper permissions. Prefer target-ABI
source-package builds and their normal configure/install logic; execute target
maintainer scripts in the target environment, never as foreign host scripts.
New screenshot shot-2026-11-01_07-22-53.jpg shows an Error loading Module dialog
and black client interiors while E decorations and wallpaper draw. This does
not identify D-Bus or QEMU as the cause. New 0.4 installed-root archive completed
but has not booted; acceptance remains pending. User again reports editor UI
stall: keep local inspection bounded and heavy work on R730.


2026-11-01 scope clarification: no policy blocks Debian maintainer scripts or
triggers. Preserve normal Debian package installation, configuration, service
setup and general runtime behavior. Apply compatibility fixes at source-code
level rather than bypassing package setup. Execute target package scripts in
the appropriate target environment. The current lab bundles lack those scripts;
that is an incomplete packaging implementation, not a desired restriction.
Support exactly two configurations for this build: the QEMU validation machine
and the physical A1222. Keep machine-specific kernel, device and boot choices
in those configurations without replacing normal Debian package behavior.


2026-11-01 final-round gate: fresh actual installed root0.4 boots in bounded
R730 software-e010. Key-only SSH(uid1000),8GiB/two-core tests, installed
Mesa softpipe GL readback, matched fractal and direct redirected pixmaps pass.
Normal Debian configuration acceptance FAILS: only the two lab bundles are
registered, not the individual Debian packages. Added read-only installed-state
audit; configured/half-configured fixture checks pass on R730. Source review
confirms E profile/build mismatch for four disabled modules. Preserve normal
Debian maintainer scripts/triggers; build proper target packages with their
dependencies rather than transplanting raw maintainer-script templates.
SanDisk unchanged; E/Radeon/physical acceptance remains open. See
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

2026-11-01 safe Molten Steel follow-up: source profile, isolated launcher and
failed black-desktop evidence retained in profiles/e/recording-molten and
builds/e-molten-safe-20261101. Do not promote to recording view while #8 is open.
Next rendering gate: isolate Evas primitive output from compositor readback;
optional-module/locale/software/SHM configuration alone did not fix it.
Physical tabor-live002 compiled and base-files001 packaged; hardware boot and
normal Debian Essential root configuration still pending. User clip/still
located and sampled; original media remains local and was not published.

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
