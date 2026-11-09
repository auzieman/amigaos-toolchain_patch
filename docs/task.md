## Native vertex candidate staged; no rendering authorized — 2026-11-09

User-authorized isolated stage at /opt/tabor-native-vertex-20261109. All28 file
hashes match, native loader dependency listing passes, root restoredRO, boot ID
unchanged,taint0. No runtime device mounts, EGL/DRM workload, render or reboot.
Existing runtime/module/boot/default flags remain. User explicitly defers actual
onscreen rendering; do not launch a graphics validation until later authorized.
See [staging receipt](builds/mesa-native-vertex-20261109/staging/staging-result.json).

## Implemented native vertex / legacy streamout candidate — 2026-11-09

Opt-in BE GFX8 patch now pairs typed vertex decoding with native-format legacy
streamout stores, complete producer format/key metadata, and a guard routing
unsupported fast display-list draws through the normal path. SPE/native builds
pass. Actual NIR checks:128 scalar,190 full format-lowering,16 legacy-store
cases; extracted helper model20,480cases/arch. x86/off unchanged; enabled RGB
changes onlyVS52->160bytes. Attribute-free point code remains unchanged: its
hang is not fixed by this patch. Defaultoff, no board deployment/test. Arbitrary
SSBO-generated vertices and lowered64 XFB remain unqualified. See
[native vertex candidate](builds/mesa-native-vertex-20261109/README.md).

## Submitted buffer audit: native32 vertex payload gap — 2026-11-09

Offline unchanged standard point/RGB tests snapshot11/60 allocation prefixes;
8/47 are byte-identical across x86/SPE. RGB rectangle coordinates reach storage
as nativeBE float32, while all4 RGB executable shader captures matchx86 and
source vertex-load paths show no explicit BE scalar decode. This is a concrete
CPU vertex-input contract gap, separate from descriptors and the no-attribute
point hang. Streamout GPU producers must be paired with any shared fetch change;
no blind decoder or speculative GL fix committed. Both instrumented builds pass.
No board access/deployment/test. Full bounded captures and connected ledger:
[buffer audit](builds/mesa-buffer-boundaries-20261109/README.md).

## Physical LE command visibility control: cached and USWC PASS — 2026-11-09

Fresh013 boot, verified installed-module first bind, rootRO, explicitLE GFX
fetchswap0. Identical8DW allocated WRITE_DATA test passes USWCflags5 and
cachedflags1: actual markeraddefeca, ioctl fencecomplete, remapidentical. Final
bootunchanged,taint0,amdgpudrmfb,SSHresponsive. NoGL,resetorreload. This does not
justify a cache-policy patch or qualify larger/shader/render-target visibility.
See [hardware control](builds/mesa-command-compare-20261109/README.md).

## Complete GFX construction comparison — 2026-11-09

Offline standard Piglit point draw now compares finalized command streams across
native x86 and SPE: one400DW GFX IB,399 identical numeric words; sole difference
is upstream CB_COLOR0_INFO.ENDIAN8IN32 on BE, decoded from its owning packet.
Prior executable-shader comparison also matches for this workload. Profile is
upstream Polaris12 no-op, not boardPolaris11; no GPU execution or physical
LEpublication acceptance claimed. Both instrumented builds pass. No board test,
deployment or reboot. Remaining cached-vs-USWC publication/coherency control is
specified before another GL attempt; no speculative cache-policy fix added.
See [command comparison](builds/mesa-command-compare-20261109/README.md).

## Standard Piglit baseline; GPU reset checkpoint — 2026-11-09

Frozen standardPiglit/Waffle sources built unchanged forGLES2. Same standard
surfacelessEGL/FBO tests physicallypass onsoftpipe (minmax,constantpointnovertex
attributes,RGBdraw/readback). RadeonSI passesrendererquery/minmax;firstconstant
pointdraw timesout, GFXseq17/18watchdog causesautomaticGPUreset/VRAMloss. Stop:
no furtherphysicaldraws or manualreload/reset. SSHalive,taint0,rootRO;GPUclean
state notaccepted. Onezombietestprocess,noneactive. Freshbootneeded before
materiallydifferenttrial. See builds/piglit-standard-20261109/. Standardtests
now baseline; no driverpatch should rely solely oncustomkmscube readback.

## Systemic Mesa/ACO audit and packed-mode correction — 2026-11-09

Shared boundary ledger now covers compiler packing, executable/command upload,
descriptors/constants, vertex/blitter state, surface endian policy, staging and
completion responses. Actual ACO float_mode type encodes0xf0 as0x0f onoldBE;
all256 field/alias encode/decode cases match unchangedx86 after endian-aware
layout fix. Full isolated41step Mesa build passes. Physicalclear remainszero,
SSH/VT1/taint0 preserved. See builds/mesa-systemic-boundaries-20261109/. No
3Dacceptance or claim all paths translated. Next: connected compiledshader/
config/descriptor and render-target/readback validation, not further unchanged
blackframe trials or blanket BO swapping.

## Mesa paired GFX encoding and fence decode — 2026-11-09

Physical013 plus fixed module loader passes allocated userspace GFX WRITE_DATA:
actual cafedead LE payload and swap0 verified. Paired Mesa25.0.7 opt-in now
serializes complete GFX main/chained/preamble/reset-nop IBs after CPU fixups;
actual-source cross-arch byte checks and bounded full build pass. Actual Mesa
publication traces confirm the conversion ran, but red-clear readback stays
zero with normal and direct shader-upload controls. Shared user-fence LE64
decode defect independently reproduced/fixed/tested (8192cases/arch); physical
clear remains zero after correction. No hardwareGL/cube acceptance. Board
SSH/VT1/taint0 preserved; no reset/reload. See builds/mesa-le-ib-20261109/.
Next: shader execution/image readback contract, preserving paired command
encoding and decoded completion values; do not launch native-PM4 Mesa against
the enabled013 diagnostic or blanket-swap descriptors already serializedLE.

## PowerPlay failure narrowed and candidate built —2026-11-08

The protected physical bind of080f5493 passes GFX/KIQ/all8 compute/SDMA0/SDMA1
scratch tests and GFX/SDMA hw_init, then loses PCIe responses during PowerPlay
hw_init. Bind and a later SSH check time out. USB root was verified read-only;
logs are retained off-board. No retry/reset from the failed state. User was
asked to power-cycle and boot the normal Linux entry; recovery remains unverified.

Backported the exact newer upstream smu7_send_msg_to_smc response-status helper:
legacy6.12 falsely returns success for all response errors. Added scoped
PowerPlay/ATOM/mailbox call markers without extra MMIO reads or endian changes.
Native and PPC32 BE/QEMU simulated-response regression passes all5 cases, with
the old helper as a false-success control. Fresh normal Kbuild completes and
all687 imported CRCs/full vermagic match. New module7067488b is on the R730,
not deployed or physically tested. See builds/polaris-powerplay-20261108/README.md.
No GPU/display fix is claimed; the initiating PowerPlay operation remains open.

## 6.12 GPU review checkpoint —2026-11-08

The next6.12 candidate compiles and passes all687 imported CRC checks against
the accepted kernel export table, with matching ELF32 BE and full vermagic.
It includes upstream ring-test ordering/error-propagation fixes and post-map
boundary markers. NXP's P1022 documentation identifies the captured ERR_DR bit
as an outbound completion timeout; the initiating GPU failure remains unproven.
See builds/gfx-postmap-review-20261108/README.md for source exclusions, evidence
and next controlled test. Candidate is staged inactive; live6.12 remains
healthy/dual-core with GPU unloaded. No boot/kernel/firmware changes this pass.

## Errand breakpoint —6.12 driver review,2026-11-07

See builds/gfx-postmap-review-20261107/README.md. Fresh source comparison found
upstream scratch posted-write ordering and compute-test error-propagation fixes;
0014 backports them,0015 adds precise ring/IP/GUI-idle initialization markers.
No hardware load/reset or boot/USB change. Isolated R730 build container
`tabor-gfx-postmap-review-002` may finish and exit while user is away; it cannot
deploy or launch hardware tests. First invocation had a relative M= build-path
error, corrected to in-tree amdgpu.ko target. Inspect build-002.json/log before
continuing. No claimed GPU fix or console/acceleration acceptance.

## Clean upstream hardware test prepared — 2026-11-07

Corrected GCC14 libgcc/glibc rebuilds finished exit0. New clean upstream7.3
kernel and matching modules are activated on the verified SanDisk with two
verified old-kernel rollback copies. Existing /boot.scr, DTB and early firmware
are unchanged. FAT is unmounted; A1222 remains on the old running kernel until
the next physical reboot. See builds/upstream-hardware-test-20261107/README.md.
Next gate: saved Linux boot entry, SSH/new release/SMP verification, then a
logged first AMDGPU bind. QEMU two-core startup remains a disclosed limitation.

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

## Runtime/harness increment — 2026-11-07

The GCC14 C bootstrap now builds static libgcc/libgcov and startup objects
successfully on the R730 (attempt003 exit0). The initial runtime attempt
exposed missing SPE-prefixed binutils lookup; passing native PowerPC
AR_FOR_TARGET/RANLIB_FOR_TARGET/NM_FOR_TARGET explicitly resolves it without
changing generated target code. No accepted SDK or boot media was changed.

Evidence: `work/gcc14-spe-port-20261107-001/libgcc-bootstrap-00{2,3}.log`
on the R730; final libgcc.a SHA256:
`417be053abbf416042db1c7ebc939887bed3d00199e2bb64ffcb0bb5d9597475`.
Container image remains the pinned GCC14 tools image, network disabled,
4 CPUs/6GiB. Reproduction from the existing configured build-stage1:

```
make -j4 AR_FOR_TARGET=/usr/bin/powerpc-linux-gnu-ar \
  RANLIB_FOR_TARGET=/usr/bin/powerpc-linux-gnu-ranlib \
  NM_FOR_TARGET=/usr/bin/powerpc-linux-gnu-nm all-target-libgcc
```

Static library build acceptance is not runtime ABI acceptance. Next: fresh
patched glibc2.41 with this compiler/runtime, final C/C++ libraries and ABI
checks, then the package-managed test root. Reproduce the existing harness
with X/E and a visual GL test, keeping QEMU software rendering and physical
Radeon acceleration separate. `scripts/visual-gl-smoke.sh` captures installed
packages, PCI binding, actual GL renderer and a bounded20-second gears window
inside an existing X session. Shell syntax checked; graphical execution is
pending. It never loads a GPU module or changes boot/session configuration.

## Current checkpoint — 2026-11-07, GCC14 SPE C bootstrap

User requested coherent compiler/SDK fixes and an audit of obsolete options.
The16-patch GCC14.2.0 candidate builds its C-only headerless compiler. Source
replay passes, all94 Report-marked option definitions retain their functional
properties, eight tuning defaults are migrated, and actual target option/override
checks pass. Retired vector-cost callbacks are adapted to GCC14, including a
real optimized-loop regression correction. The final selected freestanding C
probe passes under QEMU/e500v2 and native A1222 SSH execution with exit0/taint0.

See [full evidence and limits](builds/gcc14-spe-interface-20261107/README.md).
This does not complete libgcc/libc/C++ or full ABI support and does not replace
the accepted SDK. Next bounded action: bootstrap/qualify libgcc with this compiler,
then patched glibc2.41 and C++ runtimes, retaining normal Debian package semantics.
The original firmware/kernel and existing userspace stay intact. Historical
intake and earlier stages below remain review history, not current status.

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


2026-11-04 architecture clarification: user reaffirmed that the harness feeds
Debian cross-build logic; it must not replace it. Current execution does invoke
Debian dose/sbuild/apt/dpkg, but custom source inventories, phase lists and
native-version inference are local policy, not Debian authority. Audit those
boundaries before further orchestration growth. In particular, a native
binary revision is diagnostic coinstallation evidence, not a universal target
version policy. Preserve current immutable running inputs; no active build
was interrupted for this clarification.


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

2026-11-04 cache correction: retain apt binary downloads outside disposable
sbuild roots using documented unshare bind mounts/retention. Per-worker locks
and partial directories avoid concurrent apt lock conflicts; complete files
accumulate in a hard-linked shared pool, including recovery from retained
failed/interrupted workers. Source archives already use hash-checked reuse.
Offline native apt regression passed with1,155 seeded archives and0B requested.
Round006 submitted. Next gate is actual sbuild bind/acquisition acceptance,
then continue package closure and image/QEMU validation. Frozen archive misses
remain network-dependent; no live mirror fallback was added.

2026-11-04 pulse check: round005 completed with40 distinct deferred sources;
54 dependency-blocked entries repeat sources between phases. Round006's two
attempts, PAM/util-linux, failed before compilation on cache directory access.
Host owner1000 is not namespace root100000. Corrected ownership now comes from
sbuild's own mapping function, validated by real usernsexec/pivotroot/bind and
network-off apt reuse (apt-cache-namespace-003). No new package success yet.
Do not treat host-root-only diagnostics as namespace integration acceptance.
User requests broader shared-cause review before further narrow batch fixes.

Further shared-cause finding: round005 util-linux failed dependency resolution
because its dummy package Conflicts:libedit-dev while the broad native template
already has libedit-dev3.1-20250104-1 installed. This predates the cache failure.
Keep cached native dependency archives broad, but qualify a clean buildd template
with apt-utils and let sbuild install each source's dependencies normally; the
installed native tool superset is not universally compatible with Build-Conflicts.
Do not submit another unchanged broad-template round as a cure. Preserve the
existing template and receipts while qualifying an isolated child/base.

2026-11-04 workflow/prompt review: reconciled the Debian-port skill, continuation
prompt, AGENTS provisioning paragraph, build contract and pipeline guide. They
had conflated broad server dependency provisioning with each disposable root's
installed state. Current instructions retain broad caches/tools but require
clean source roots, normal Build-Conflicts handling and qualification through
the actual sbuild namespace/resolver before widening a batch. Repeated failure
entries must be grouped by unique source/shared cause; a zero-progress round
requires diagnosis rather than another equivalent submission.

Reviewed against Debian Trixie sbuild(1), Debian CrossCompiling and Trixie
architecture documentation. ppc64el is maintained, but its ABI is not SPE; use
its packaging mechanics without substituting target binaries/flags. Reviewed
behavior for the observed libedit-dev conflict, cache namespace mismatch and
blocked consumers: qualify the environment/producers, not consumer workarounds.
No builder/profile/patch changes, build submission or new acceptance claimed.
Diff/frontmatter/reference checks passed. Skill quick_validate could not run
because both local Python interpreters lack PyYAML; no environment changes were
made merely to validate a documentation edit.

2026-11-04 resumed closure: created clean-cross-buildd-002 from frozen-buildd002
plus native apt-utils,125 installed packages, native foundation unchanged,
clean apt/dpkg checks. Explicit parent/metadata receipts and persistent apt
cache now supported by the existing child-root recipe. Root001 was stopped
during repeated Snapshot index timeouts; root002 reused retained same-baseline
indexes and cached apt-utils. Profiles pin the qualified creation receipt.
Submitted port-qualification-20261104-001 with reviewed util-linux/PAM-only
plan through the standard pipeline, before widening the workstation batch.
Cross-build/SDK/package acceptance still pending. Separately started bounded
frozen source intake for libevent/libtextwrap, directly reported missing
producers for Unbound/GnuTLS and cdebconf/base-passwd dependency chains.

Qualification001: no cache permission recurrence; util-linux passed the old
libedit-dev conflict and PAM configured actual dependencies. Both stopped on
Snapshot503/504 acquisition, not compilation. Bounded exact-version native
cache fill via Debian apt-helper and same frozen URL with download query
verified/cached fakeroot, python3-ruyaml and strip-nondeterminism; dose-distcheck
reused. Five native files remain unavailable. Receipts retained. Libevent
source intake also failed Snapshot .dsc acquisition; no source lock registered.
Qualification002 now running with the recovered verified cache inputs. The
query transport is partial recovery, not a universally working fallback.

Qualification002 actual compiler result: PAM stage1 succeeded,7 .debs including
3 debug packages. Payload inspection SHA256 recorded in committed
pam-qualification.json; ELF32BE PowerPC and artifact hashes verified. No target
installation/execution claimed, required full PAM rebuild remains. Util-linux
is progressing after native helper downloads recovered. Queued normal
port-pipeline-20261104-007 after qualification002, using the now exercised clean
root and accumulating real artifacts. Debian metadata decides newly ready work
(e.g. PAM development output for libcap2); do not count queued sources as passes.

2026-11-04 follow-up: util-linux bootstrap qualification002 succeeded with14
.debs and verified payload inspection, including real libuuid/libblkid/libmount
development outputs. PAM7 + util-linux14 are bootstrap binary outputs, not21
completed source ports. Required full builds and runtime remain open. Wider
round007 is active with the clean root and these inputs. No new compiler or
consumer patch indicated by current evidence.

Source cache correction retains per-producer download failures and continues
independent sources. Same frozen origin/query recovery remains size/SHA256
checked; incomplete components never enter the lock. Three native fault tests
passed (fall-through, cache reuse, corrupt-file rejection). Live closure-cache004
is retrying the existing bounded libevent/libtextwrap intake; do not claim
sources cached until its receipt and hashes qualify them.

2026-11-04 round007 completed with5 new normal-profile source passes: libcap2,
e2fsprogs, fontconfig, libsm, libarchive,31 .debs total. All payload inspections
passed.35 unique sources remain deferred; not35 independent compiler defects.
Desktop log viewer now retains completed summaries and blockers, rather than
blanking when the pipeline stops or presenting only3 previous tails.

Reviewed frozen Sources show test relations with separate <!nocheck>
<!noinsttest> restrictions in GLib/D-Bus/systemd. Selected their supported
cross,nocheck,noinsttest profiles (plus stage1 where already required for
systemd). Round008 audit confirms GLib now needs libelf-dev, removing its old
DBus test edge; full D-Bus/systemd still correctly require AppArmor libraries.
Round008 is the normal64-source request plan, not another3-package test.
Bounded source intake005 adds json-c/keyutils and retries libevent/libtextwrap
from frozen metadata; acquisition is still pending, no new lock registered.

2026-11-04 solid closure pass: round008 completed without new outputs; remaining
fallout is dependency/foundation, not35 source compiler failures. Added explicit
chain map docs/remaining-closure-20261104.md. Selected existing elfutils
pkg.elfutils.nodebuginfod for required ELF/DWARF libraries without the unselected
HTTP debug service. Added explicit AppArmor stage1 library bootstrap packaging;
normal profile still selects11 packages, stage1 selects2 C-library packages.
Full AppArmor rebuild remains required. Initial draft009 failed source patch
parsing; corrected patch passes git apply --check, native dh_listpackages and
stage1 recipe dry-runs. Actual cross build pending round010, queued after009.
Crypto producer intake006 is bounded to libgcrypt20/libgpg-error/kmod discovery.
Earlier4-producer cache005 remained incomplete due Snapshot failures; no lock
registered. Target Python/GIR and full restored-glibc source gates remain open.

2026-11-04 round010: elfutils passed with11 inspected .debs using the existing
nodebuginfod profile. AppArmor did not compile: native autoconf-archive download
504, not a bootstrap compiler error. Native-cache-fill002 query recovery also
timed out; original archive remains unavailable. No newer source selected.

GLib's next blocker is cross-exe-wrapper from GIR Build-Depends-Arch, not an
ordinary missing compiler tool. The actual frozen control/Package-List support
nogir; selected cross,nocheck,noinsttest,nogir for the C-library slice, retaining
GIR typelibs as an explicit later requirement. Harfbuzz does not declare that
profile, so it was not blindly assigned nogir.

Found shared failure-retention defect: an apt error outside the last700 log
lines was classified as permanent dependency-installation. New bounded archive
scan retains transport evidence across the entire log; controller also examines
raw logs before importing historical deterministic install failures.2 regression
tests passed (long summary hides fetch error; real source error stays separate),
and the scanner reproduced the actual AppArmor504. Round011 submitted with
GLib profile and corrected retry classification. Crypto source intake006 still
failed Snapshot acquisition; no unverified lock registered.

Classifier completeness follow-up: do not let a download failure while sbuild
installs its optional dose explainer replace an earlier real coinstallation
failure. Archive scanning stops at the first package-installation failure;
classification uses that primary acquisition evidence rather than secondary
summary text. A third regression verifies original dependency conflicts remain
separate. All3 focused tests pass. These follow-up reporting guards apply to
future submitted snapshots; running011 retains its immutable initial inputs.
Actual011 dose report now marks GLib installable with the supported nogir profile.

2026-11-04 mirror investigation: bounded R730 probes of exact pinned files show
Snapshot json-c DSC timeout18s versus Debian CDN0.07s with identical expected
SHA256; Cloudflare route403. Autoconf archive verified through Snapshot0.33s and
CDN0.24s after previous failures. Added explicit --exact-file-cdn to cache tools
and intake CLI. This fetches only immutable hash-pinned pool files; no live apt
repository, metadata, version or baseline change.3 transport tests +3 existing
source-cache tests passed. Recovered/verified all4 previously missing source
sets plus libgcrypt20, registered in closure-prerequisite-sources.lock.json.
Round012 running with those5 producers added. Round011 actually passed
AppArmor stage1(2 debs) and GLib nogir(13), both payload-inspected; full AppArmor,
GIR and runtime gates remain open. Evidence: exact-file-cdn-20261104.

2026-11-04 broader closure repair: reviewed round012 as shared dependency chains, not32 compiler defects. Registered13 additional frozen verified producers across crypto/netfilter/device management, SASL/LDAP, account setup, VNC and target Python. Added explicit reviewed intake manifest so first-error-only dose reporting does not force one prerequisite per round; actual readiness remains Debian-owned. Selected declared OpenLDAP client and SASL core profiles to break cycles; target Python/defaults now justified by ALSA. Three CLI regression tests pass on R730. Full-scope round013 submitted with qualified clean roots/max4 bounded jobs. GIR/full-glibc/image/runtime gates remain open. See docs/builds/closure-chain-repair-20261104/.

2026-11-04 audit performance repair: stages/waves previously reran all source/profile groups. Added bounded --sources requests without shrinking the verified binary pool; skip empty stages and omit attempted sources on later waves. Five-source dose equivalence and actual two-source CLI qualification passed. Added five reviewed target Python prerequisites; rpcsvc-proto cached only as native generator inspection. Eighteen new target producers registered total. Round013 has four real sbuild jobs; round014 queued after013 with scoped audits and Python prerequisites, no overlapping workers. Compilation/remaining-count acceptance still pending actual receipts.

2026-11-04 shared acquisition follow-through: round013 passed SASL8, libdebian-installer3 and architecture-properties3 inspected debs. Kmod stopped before compile on Snapshot503 scdoc. Added opt-in pre-wave native archive cache fill from actual dose installation sets, matching frozen NativePackages tuples/hashes, with exact-CDN then pinned-Snapshot fallback. Three native cache regressions pass; actual scdoc recovered into persistent cache. Round014 waiting-only cancelled/replaced (prior receipt retained);015 never started after safe submission rejection. Predecessor identity now matches --output, not an after-receipt substring. Round016 queued after013 with complete repairs; original worker jobs intact. Whole-wave integration/final remaining-count acceptance pending.

2026-11-04 next closure pass: completed013/016 delivered16 inspected source builds /60 debs. Original32 request set now29 deferred; total35 includes six new Python prerequisites. Native prefetch actual016 wave cached116/reused52 successfully. Round017 requests explicit libcap2 binNMU3 for observed systemd Multi-Arch coinstallation conflict; restores normal Python-defaults doc helper dependencies by removing nodoc; selects verified existing cdebconf text/client profile; registers five frozen source producers libxmu/xft/lmdb/libev/libverto. Unknown libxft source name was rejected at metadata intake, corrected to canonical xft; diagnostics improved and3 intake tests pass. Full selected round017 submitted with persistent caches/scoped audits/max4 bounded remote workers. Evidence docs/builds/closure-next-wave-20261104/. No new image/runtime acceptance.

2026-11-04 whole-fallout repair:017 delivered12 inspected source builds /66 debs. Reviewed all failed builds/chains together. Found shared epoch cache filename bug (real sbuild --nonet before126kB failure / after0B success), dose-selected archive trimming that constrained apt alternatives, and actual download choices missing from predictive prefetch. Fixed canonical verified cache names, complete verified SPE archive exposure and one bounded actual-native acquisition recovery with first logs retained. Nine targeted regressions pass; actual Tk/Kerberos/BLT logs validate recovery boundaries. Reviewed full Native Tk closure and rebuilt Xft4/Xext3/Xss3 in018 (six inspected debs). Reconciled14 ignored existing binary revision entries; all16 requests verified against frozen native metadata, with consistency guard. Native Python documentation tools qualified in control/template and source repack passed. Registered libxpm/libxxf86vm/libdaemon from frozen hashes.018 continues;019 queued after018 for remaining reviewed core alignment, no overlap. Evidence docs/builds/multi-failure-repair-20261104/. GIR/full-glibc/image/runtime gates remain open.

2026-11-04 follow-up:018 accepted6 sources/13 debs (Xft/Xext/Xss/Xpm/Xaw/libdaemon). Reviewed three actual source failures together: removed invalid :native from Multi-Arch:foreign Docutils, guarded Debian BLT C23 variadics for pinned GCC8, and extended existing measured Xorg malloc cache to libxxf86vm. Real GCC8 before/after, actual archive metadata + dpkg dependency evaluation, and both source repacks pass. Full builds pending. Waiting019 cancelled before workers, replaced by020 after active018 with previous core binNMUs retained. No new image/runtime acceptance. Evidence: docs/builds/multi-failure-repair-20261104/.

2026-11-04 desktop follow-through:018 completed7 accepted sources/15 inspected debs.020 now runs the broad reviewed core/desktop scope with max4 constrained R730 sbuild jobs. Kerberos reached a genuine Autoconf cross-runtime gate. Debian dpkg-cross already documents its constructor/destructor cache answer; static and dynamic target probes using hash-verified pinned glibc/GCC8 pass under e500v2 QEMU. Added target-restricted standard Debian rules cache input; source repack002 passes after correcting source-lock pointer rejected in001. No general stock PowerPC site import, target execution during builds, or new desktop/hardware acceptance. Evidence docs/builds/krb5-cross-configure-20261104/.

2026-11-04 workflow correction: user expects maintained Debian PowerPC build mechanics and a broad workstation archive. Current plan110 sources. Qualified shared real installed SDK root004 with a true read-only compiler mount (dpkg -V clean, EROFS write rejection, SPE assembly emission), plus standard sbuild extra-repository transport for730 verified artifacts (offline namespace apt/hash check). Two integrity/reuse regressions pass. Active020 unchanged; waiting021 replaced by022 after020 with full scope and all previous fixes. Full integration acceptance pending. Compiler baseline audit explicitly confirms GCC8.5/tabor6 remains, not Trixie GCC14.2.0-19; no modern SPE compiler completion claimed. Evidence shared-sdk-repository-20261104 and docs/sdk-baseline-audit-20261104.md.

2026-11-05 user clarified that our own workstation target must bring the SPE
compiler forward to the selected Trixie GCC14.2.0-19 baseline, beyond Steven's
separate SDK ask. Treat GCC8/tabor6 as historical bootstrap/reference only;
retain the frozen accepted artifacts while qualifying a separate GCC14 SPE
candidate. No GCC14 SPE restoration or acceptance is complete. Do not mistake
existing gcc-14 native/ordinary-PowerPC binaries for a working SPE backend.

2026-11-05 separate AmigaOS guest preflight: R730 reachable after reboot,
transient pipelines inactive. Uploaded ISO is A1222-specific, as both actual
Kicklayouts confirm; QEMU10.0.13 machine list has no A1222 board. Existing11.1.3
probe with identical media also did not verify OS boot. Enhancer listing did
not supply alternate A1/Pegasos kernel. Await platform-matched media for a valid
boot/install trial rather than repeat the known incompatible setup. No fresh
OS boot or installation claimed. Main020 recovered13 accepted sources/47debs;
022 had no new outputs because libatomic-dev attempts to write into shared RO
SDK. Preserve failure; do not restart old-GCC batch or weaken RO. Evidence:
docs/builds/amigaos-side-guest-20261105/.

2026-11-05 correction to side-guest scope: our existing ppce500/e500v2/SPE Linux harness is a valid custom-emulation starting point; no stock A1222 name does not prove impossibility or require other media as the only path. Actual bounded R730 direct-entry probe of the unmodified uploaded AmigaOS A1222 kernel loaded at NIP0x010000d4 and reached NIP0x700 after2s, no serial/Workbench. Private kernel kept outside Git, no disk/network, QEMU stopped. Next isolate AmigaBoot/Kickstart handoff and P1022 MMIO requirements before emulator changes. Evidence e500-entry-receipt.json in amigaos-side-guest-20261105.

2026-11-05 second guest authorized/prepared: independent Pegasos II/7457
AmigaOS side VM on R730 with8GiB sparse raw disk,512MiB RAM, SM501, loopback
VNC5912 for future run, no guest networking. BBoot0.8 author release hash-pinned,
source/license inspected. Actual bounded VOF/BBoot probe enumerated/configured
PCI and reached expected missing-initrd message; stopped afterward, no OS boot
or installation. Waiting for matching Pegasos ISO/prepared Kickstart; Linux/SPE
images untouched. Launcher/source scripts and exact receipts retained in
amigaos-pegasos2-20261105 evidence. This validates the side loader setup only.

2026-11-05 media follow-through: uploaded A1222 ISO/Enhancer listings do not
provide Pegasos alternate boot files. Found Hyperion's official digital Pegasos
ISO and registered-user update sources; opened product page in existing Opera
session per user preference. No purchase/account access/download of commercial
ISO. Prefer existing registration/media access where applicable; do not assume
cross-edition entitlement. Guest remains prepared, awaiting matched boot files.

## OS4 SSH side option — 2026-11-05

Prepared a public-key/read-only diagnostic ZIP in LAN FTP downloads. Server installation remains unqualified: native OS4 OpenSSH listing provides clients; BebboSSH m68k source has classic MMIO and its Linux reference connection timed out. See [evidence and bundle](amigaos-ssh-preflight-20261105.md). No server, startup or existing Amiga config changed. Next: inspect the device report and qualify a native server or reviewed OS4 port before installation.

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

## Live display power/handoff probe — 2026-11-05

Read-only native probe: Radeon D0/runtime-active, driver unbound after failure; no registered framebuffer. DT stdout points to onboard DIU with no bound driver; initial board patch lacks DIU hooks. No reset/register writes. See [probe](builds/native-gpu-smu-20261105/live-power-handoff.md). SMU root cause remains unconfirmed.

## Modular graphics kernel candidate — 2026-11-05

User requests flexibility for alternative cards. Added separate tabor-modular profile and module-valued fragment support. R730 fresh candidate003 launched with 4CPU/6GiB, cached source, both board patches and distinct release suffix. Compile/modules/deployment validation pending; USB unchanged. See docs/kernel-build.md.

2026-11-05 status check: modular candidate003 completed successfully (container exit0, receipt status compiled). vmlinux/modules/DTBs built. Packaging, module installation/dependency metadata and physical GPU validation remain pending. No USB deployment performed.

2026-11-05: Modular kernel compiled; matching modules/static module tools and separate boot payload installed on live SanDisk over SSH/SFTP. Transfer/readback and machine identity checks passed; old kernel and boot-known-good.scr retained. Reboot sent, physical new-kernel acceptance pending. See builds/modular-usb-update-20261105/.

2026-11-05 physical modular acceptance:6.12.113-tabor-modular boots USB, SSH works, all9 ABI checks pass. Corrected static module-loader defaults /lib/modules/modules.dep; dependency resolution and insertion work, but AMDGPU device probe still fails-22, no framebuffer. See modular-usb-update-20261105 evidence.

2026-11-05: Audited SMU7 raw firmware words -> CGS -> WREG32/writel; native u32 upload differs by host endian. Isolated LE-decode candidate prepared (not default series), numerical stream equivalence checked, fresh constrained exact-config R730 build started. Physical fix remains unproven. See builds/smu7-endian-candidate-20261105/.

2026-11-05: SMU7 endian candidate compiled, exact .config/Module.symvers match. One controlled physical module test with continuous kmsg: insertion succeeds but SMU startup still fails and device probe-22, no framebuffer. SSH healthy; installed module tree unchanged. Negative warm-state test, no cold-cycle result or fix claimed. Evidence: builds/smu7-endian-candidate-20261105/.

2026-11-05: AMDGPU requirements audit: all13 dependency modules match accepted kernel; all42 existing Polaris10/11 firmware files already matched pinned firmware-amd-graphics20250410-2. Installed complete892-file firmware payload/licenses to USB over SSH, all892 native hash readbacks pass; original subset and .deb retained. No missing Polaris file found, no GPU reload or graphics-fix claim. Evidence: builds/full-amd-firmware-20261105/.

2026-11-05: Source-level SMU startup audit identifies ignored firmware lookup and handshake results; no proven root cause. Isolated logging/error-propagation candidate builds targeted AMDGPU on R730 with original upload behavior and exact physical modular config. Logs selected firmware and PC/status/response stages; no reset changes. See builds/smu-startup-diagnostics-20261105/.

2026-11-05: Diagnostic module physical test confirms polaris11_k_smc.bin version0x1800 loads successfully; protected/security mode1, SMU response/status0 around startup, low sampled PC. Still no framebuffer, SSH healthy. Combined LE+logging build prepared but untested. Read-only OS4 disk header probe finds three NGF1 volumes; no compatible mount/read driver established, no disk writes. Uploaded Enhancer RadeonRX documentation supplies PCI/revision/DPM leads, not installed-version proof. See smu-startup-diagnostics-20261105 and aos-readonly-intake-20261105 evidence.

2026-11-05 historical GPU source intake: located Marcus Comstedt2018 primary RX550 BE report and author patch; reports working SMU/firmware startup but unfinished gfx ring. Cached/hash-pinned; initial6.12.113 comparison finds mixed upstreamed/remaining changes. No complete older BE distro proof or imported patch acceptance. See polaris-big-endian-history-20261105.md.

2026-11-06: Combined LE upload + diagnostics compiled with baseline config/symbols and tested on physical A1222. Firmware is found, but protected SMU status/response remain zero and probe fails -22; no framebuffer. Installed module tree unchanged. Historical hunk audit 13 old/7 already-new/18 evolved; current Atom interpreter has explicit LE buffer accesses, so old swaps require semantic review. Evidence: builds/smu-diag-le-20261106/.

2026-11-06: User-requested local SDK inspection located Projects/SDK. PCI interface documents endian conversion; Radeon resource exposes volatile MMIO with sync/eieio barriers. No Polaris startup source found in bounded SDK search. I/O-interface mode is not proof of mapped-MMIO behavior or RadeonRX implementation. See sdk-pci-reference-20261106.md.

2026-11-06 cross-platform walk: traced CGS firmware metadata, SMU native upload, VI index/data access, PPC LE MMIO/barriers and protected startup. Full payload model confirms 28649/32493 baseline BE words differ from x86; explicit LE matches all. Linux already has ordering; ignored handshake results obscure failure. No new hardware fix claimed; next SRAM readback instrumentation requires reviewed helper semantics. See builds/smu-source-walk-20261106/.

2026-11-06 follow-up: upstream selected polaris11_k_smc.bin equals installed SHA256 exactly; no newer selected blob found at current upstream path. Established BE table helpers differ from firmware upload semantics. Prepared isolated 0003 register-readback diagnostic, not compiled/deployed; serialization/protected-read/timing review remains.

2026-11-06 physical readback test: constrained modules build passed, config/symbols match. 32493/32493 SRAM register comparisons mismatch, first expected35771e80 actualaaaa5555. Warm protected-mode readback not validated as readable; cannot conclude transfer corruption. SMU startup still fails, no framebuffer, SSH healthy; boot/module tree unchanged. See builds/smu-readback-20261106/.

2026-11-06: Prepared user-mounted x86 Debian SanDisk as stock control. Repaired dpkg, added AMD firmware/X/Mesa/Openbox and BIOS GRUB; configured DHCP/public-key SSH/automatic log capture. Initramfs module+selected firmware verified, matching firmware hash; clean unmount. Legacy boot only, tower runtime pending. See builds/x86-usb-reference-20261106/.

2026-11-06: Reinserted x86 USB recovers full capacity on direct port. Added512MiB ESP after checked root shrink, installed signed removable UEFI GRUB/shim without NVRAM changes, verified packaged hashes/config/audit; retained BIOS and root UUID. Cleanly unmounted; ASUS boot pending. See x86-usb-reference-20261106/uefi-receipt.json.

2026-11-06: x86 control UEFI boots ASUS; USB Ethernet DHCP192.168.1.253 and SSH work. Exact transplanted GPU IDs match. Stock AMDGPU initializes with framebuffer and DRM/render nodes, no SMU startup failure. Hardware logs retained; matched readback and GL execution not yet tested. See builds/x86-radeon-hardware-20261106/.

2026-11-06 x86 source-path qualification: running SMC status3/flags1/PC20564; some SRAM reads alsoaaaa5555, so pattern not corruption proof. Stock PCI rebind works,256862 trace events/no losses, but no firmware upload occurs (running SMU reused). Prepared separate held-driver initramfs/menu and first-bind tracing script; cold physical startup pending user. Normal boot remains default.

2026-11-06 held x86 first bind succeeds with real SMU upload:32493/32493 words match explicitLE model, no trace loss. Pre-Test response1; command100/argument20000 returns1 after~53ms, status3. PPC had response/status0. Evidence preserved, no PPC fix yet. See first-bind-* evidence in x86-radeon-hardware-20261106/.

2026-11-06 boot environment comparison: x86 early console measured via efifb0.34s while AMDGPU held until~41s. Both kernels have VT/fbcon; PPC lacks established firmware framebuffer handoff, DIU unbound. DC and full Debian initramfs/systemd/udev differ too, but no evidence userland packages cause SMU failure. Read-only configs saved in boot-environment-comparison-20261106/.

2026-11-06 user-directed environment parity: captured493-package healthy x86 reference, added a1222-debian-parity profile and linked existing scope. Latest R730 pipeline022 is not running and retains libatomic/coinstallation plus patched-glibc-source gates. No unchanged batch restarted; complete Debian PPC root not yet built/accepted.

2026-11-06: Verified PPC kernel already includes ftrace/debugfs/events, PCI/MSI and VT/fbcon. Prepared hash-gated shell first-bind trace with PCI resources/mailbox/index-data capture for real A1222; syntax checked, not hardware-executed. x86 BAR5/D0/MSI/command-state reference captured. No speculative VESA/DC toggles or raw SMU writes.

2026-11-06 gather-data pass: x86 still reachable/card bound; A1222 offline. Preserved full successful first-bind trace on R730 with matching SHA; added current PCI/SMC/platform snapshot and VBIOS hash. Paired PPC trace script ready with pre/post PCI config snapshots; physical run awaits A1222.

2026-11-06 A1222 return/capture: broad traces004/005 overflow and perturb timeout polling, rejected as complete traces. Narrow006 no loss but warm state skips upload; later SMU commands no nonzero responses, probe-22/no framebuffer, SSH healthy. HDMI signal changes reported. Prepared narrow+continuous-kmsg007 for cold-power capture; physical restart pending. See ppc-smu-trace-20261106/.

2026-11-06 fresh-power narrow007: zero lost events, full32493-word PPC upload matches x86 SHA. Protected SMU Test succeeds~53ms, status3/response1. Failure moves to secondary firmware load from VRAM via TOC commands252/253/250/251/254. No framebuffer/probe-22; SSH healthy. Review historical BE transfer-table fix next; warm-state reliability unresolved. Evidence ppc-smu-cold-trace-20261106/.

2026-11-06 TOC candidate: local wire-serialization boundary implemented; actual helper emits identical344bytes on native x86 and emulated BE PPC. Constrained modules build/config/symbol checks pass. Warm physical test reuses unresponsive SMU and fails secondary load; no new primary bootstrap or framebuffer. Fresh-power candidate trial required. See smu-toc-boundary-20261106/.

2026-11-06 fresh TOC candidate: SMU startup succeeds and previous secondary-firmware-load error is gone; next failure gfx_v8_0 ring self-test-110. PCIe error capture retained. BE ring path already enables hardware BUF_SWAP, so generic extra swaps are not justified without ring/mapping/error audit. No framebuffer; SSH healthy. See smu-toc-cold-20261106/.

2026-11-06 live pre-build ring capture: A1222 SSH healthy;108007 events/no loss using existing tracepoints. Ring control/base/writeback programmed, scratchcafedead read100000times with no deadbeef completion. No CP_RPTR or doorbell readback/packet contents available from existing trace; next targeted snapshot narrowed accordingly. See ppc-gfx-registers-20261106/.

2026-11-06 producer-first audit: generated CPU_BIG_ENDIAN and compiled BUF_SWAP branch confirmed. Snapshot-only module built/tested, ring bytes nativeBE while requested BUF_SWAP1 reads0 at timeout; native wptr500 decodesLE50000. Identified concrete ring contract lead, not a new swap fix. Pointer/GART/doorbell state retained; no display. See gfx-producer-contract-20261106/.

2026-11-06 immediate swap proof: fresh diagnostic build/config/symbol checks pass. Physical CP_RB0_CNTL swap bit17 reads0 immediately after all3 writes requesting1; pointer-enable bit31 reads correctly. NativeBE packets plus inactive swap strongly identify GFX8 encoding boundary; gfx test still-110/no display. Latest pinned upstream and100 path commit subjects retain native/swap contract, no applicable fix found in bounded review. See builds/gfx-swap-readback-20261106/.

2026-11-06 targeted Polaris11 SW-LE graphics-ring candidate compiled/config/symbol checks pass. Actual GFX scratch self-test now passes; next KIQ ring times out with nativeBE packet bytes. No display; failed-init cleanup warns, SSH remains healthy. Writer wrap/NOP/patch tests match native x86 and emulated BE PPC. Extending coherent ring/MQD boundary to KIQ/compute in fresh candidate; see builds/gfx-software-le-20261106/.

2026-11-06 KIQ/compute+MQD LE candidate builds/config/symbols pass, but warm hardware unload/load command timed out and SSH became unresponsive; stage unknown, no acceptance. Candidate/hash/attempt retained in builds/gfx-queues-le-20261106/. Fresh physical power-cycle required before first-load validation; disk module and boot defaults unchanged.

2026-11-06 SanDisk laptop check: no read errors, FAT/boot.scr intact; ext4 journal recovered after metadata/log backup, final read-only checks clean. VLC fatload command lacked usb. Verified queue candidate and first-load-only capture script staged; USB unmounted, boot defaults unchanged. See builds/sandisk-recovery-20261106/.

2026-11-06 fresh boot first-load candidate attempt: initial SSH/uptime34s/no modules confirmed, then test timed out60s; SSH/ICMP lost, user reports green screen. No successful GPU acceptance or phase evidence. Added explicit launcher stage output; next test requires off-board kmsg and another cold boot. See builds/gfx-queues-le-20261106/.

2026-11-06 off-board capture: SSH log moved off USB at runtime, root verified read-only. Dependencies and held candidate insertion pass; explicit bind locks board. Saved kernel stream shows SMU success, CP start, then PCIe00800000/23 storm; earlier mapped-memset alignment warning retained. No GPU acceptance. Adding pre-map KIQ self-test to isolate command/descriptor boundary; see builds/polaris-offboard-20261106/.

2026-11-06 pre-map KIQ diagnostic compiled/config/symbol checks pass, SHA449ecd7d979904dfb619cea9e4f8dd530bf1ce237a0983ad426d37fd466420fb. Ready locally/R730; physical first-load pending cold reboot. Existing self-tests retained; no hardware fix claimed. See builds/gfx-kiq-gate-20261106/.

2026-11-06 KIQ gate physical pass: pre-map control self-test returns0; hang after compute mapping submission, PCIe storm saved off-board. Native CPU MQD staging/IO-safe VRAM publication candidate in progress; exact wire-helper x86/PPC tests pass. No display acceptance. See builds/gfx-kiq-gate-20261106/ and gfx-mqd-host-20261106/.

2026-11-06 native MQD staging candidate002 compiled; config/symbol parity pass; SHA f6475b61ef7affae8fff7cbd008ef2a70090f96327f3c7a0cd8d2d9adb5e2e49. IO-safe VRAM clear/publish, heap-native construction and KIQ error propagation; ready locally for cold test, no new hardware acceptance.

2026-11-06 MQD staging002 physical test removes mapped memset warning; KIQ still passes, compute mapping still hangs. Logs expose compute descriptors in GTT vs KIQ in VRAM. Single-placement BE Polaris11 VRAM candidate building; no display acceptance. See builds/gfx-mqd-host-20261106/ and gfx-mqd-vram-20261106/.

2026-11-06 VRAM compute-MQD placement candidate builds/config/symbol checks pass, SHA49e956e9a0655da97ea2db7458c572a8626b4c89fd6180fcf22572a33cd86b99. Artifact ready locally/R730; next cold first-bind pending, not deployed.

2026-11-06 VRAM placement physical negative: all compute descriptors confirmedVRAM, same post-map PCIe hang. Do not accept placement as fix. GPU COPY_DATA calibration+MQD readback diagnostic building on staging002 without placement override; AMD PAL packet source pinned. See builds/gfx-mqd-vram-20261106/ and gfx-mqd-read-20261106/.

2026-11-06 historical comparison confirms older Radeon Evergreen hardware-swap path;2018 Polaris BE report explicitly passes ring test with software LE and finds hardware swap ineffective. Clarified history doc. GPU MQD readback candidate compiled/config/symbol checks pass, SHAed5b746997cdaab551ac75d8cfc323391708ea9305a386f8e0d4ebe9bce57169; physical pending.

2026-11-07 lab resumed: A1222 modular kernel/no modules, R730 healthy. Off-board006 GPU calibration and22/22MQD sampled words pass; remaining hang after combined resource/map submission. IH and CSB helpers already correct. Stage-gated normal KIQ tests between resource assignment/individual mapping building; no new conversion guessed. See builds/gfx-map-stage-20261107/.

2026-11-07 console isolation: native-MQD candidate002 loaded with upstream num_kcq=0 on fresh A1222 boot, USB rootro and off-board capture verified. KIQ pre-map test passes; resource submission followed by same PCIe storm/SSH loss. No framebuffer acceptance; compute mapping alone is not sufficient explanation. Recorded in builds/polaris-console-zero-kcq-20261107/. Await contributor patches or targeted post-resource stage instrumentation before another physical retry.

2026-11-07 investigation reset: added tabor-amdgpu-investigate skill and continuation prompt. Require init-order reconstruction and producer/consumer contract ownership before more encoding changes; distinguish PPC32BE from POWER64LE/BE controls. Zero-kcq trial used older002, so not a single-variable comparison to latest diagnostic. Derfs patch content remains pending. No hardware load or claimed GPU fix in this reset.

2026-11-07 AMDGPU source intake: cached mainline d487237 and AMD development5349075 on R730, official drm/amdgpu/kernel drm-amdgpu-next ref verified equal. Retained hashes/licenses and three-way init/test/pointer source comparison. New compute-test error propagation and still-native IB producer are review leads, not established PCIe fixes. Hardware/baseline unchanged. See builds/amdgpu-upstream-intake-20261107/.

2026-11-07 source correction: both original/patched and AMD-next GFX8 IB emitters retain explicit BE packet swap controls; SDMA has ring/writeback/IB swap settings. Native IB stores alone are not a defect. Retained exact contexts in amdgpu-upstream-intake-20261107/existing-be-controls.json. No global conversion or physical retry; audit patch interaction and first failing operation.

2026-11-07 user authorizes updating glibc/SDK components if required. Version audit: frozen Trixie target already pins glibc2.41-12+deb13u4; complete patched-libc/package/runtime acceptance remains open. SPE userspace compiler remains GCC8.5/tabor6, distinct from ordinary PowerPC GCC14.2 used for the freestanding kernel experiment. Finish clean upstream kernel control without introducing a libc change; subsequent SDK update must retain SPE ABI/fenv and standard Debian packaging, pin reviewed versions and validate runtime. No floating source refresh or current glibc completion is claimed.

2026-11-07 clean upstream control compiled: GitLab AMDGPU5349075 / Linux7.3-rc6, only two board patches, fresh detached source and output, no GPU diff or experimental GPU patches. Kbuild vmlinux/modules/dtbs exit0, version7.3.0-rc6-tabor-upstream-001 and artifact/config hashes retained. R7304CPU/6GiB, no USB update or hardware test. No glibc change required for kernel; SDK gaps remain separately authorized. See builds/amdgpu-upstream-clean-20261107/.

2026-11-07 upstream QEMU control: configuration variant compiled;2CPU startup stalls before shell,1CPU boots new7.3 kernel with8/9 ABI passes/fenvFAIL and identical SPE/software fractals;2CPU nosmap control also stalls. Snapshot disk unchanged. User requests existing boot.scr reuse; hardware bundle with42 modules/U-Boot CRC+load checks staged inactive on reachable A1222 and hash verified. Active boot/script/firmware unchanged, FAT unmounted, no reboot. Gate: secondary CPU startup before USB activation. See builds/upstream-qemu-20261107/ and upstream-usb-staging-20261107/.

2026-11-07 fresh userspace direction: candidate profile trixie-spe-sdk-candidate.json selects GCC14.2.0-19 + patched glibc2.41 with full SPE ABI gates. Cached source hashes/size pass; fresh Debian wrapper extraction completed without downloads. Verified legacy8.5 source pin and inventoried162 backend/runtime files. Actual ordinary PowerPC GCC14 probe rejects -mabi=spe/-mspe/-mfloat-gprs=double; no modern SPE compiler or package-wide rebuild accepted. Next implementation is backend/libgcc forward port before libc/C++/Debian package closure. See builds/gcc14-spe-foundation-20261107/.

2026-11-07 user confirms kernel-up graphical shell with basic display fallback before acceleration. Added graphical-shell candidate profile/contract linked from fresh SDK candidate: real fbcon/getty, verified firmware simpledrm handoff if available, working KMS without glamor or fbdev X path, software E/Mesa and independent SSH recovery. Pinned source confirms FB_VESA requires X86 and simpledrm requires actual initialized scanout. No fabricated framebuffer or claimed universal PPC VESA mode, no new kernel build or device change.

2026-11-08 physical PowerPlay candidate7067488b: protected single bind again passes GFX/compute/SDMA scratch tests; first PCIe error follows SMU DPM_Enable0x14e entry by45,333us inside smu7_start_dpm. Bind timed out; no retry or boot changes. See builds/polaris-powerplay-20261108/hardware-offboard-001/. Next: audit DPM transition/table producer contracts; command causation not proven.

2026-11-08 historical graphics intake: retained A-EON5.4 config enables radeon, disables amdgpu; retained vendor patch changes board/audio only. May2025 firsthand report loses Linux after Polaris replacement. Archive web indexes502; package recovery not yet accepted. See builds/historical-tabor-graphics-20261108/.

2026-11-08 derfsss U-Boot review pinned9bfbc801: VBIOS POST/bridge forwarding and framebuffer bus-to-CPU conversion documented; RX560 graphics testing cited on X5000, A1222 console unverified. PCIE1 outbound windows match our captured Linux boot, so no gross address-map fix found. Six-file intake/hashes in builds/derfsss-uboot-review-20261108/. No firmware/hardware change.

2026-11-08 derfsss/qemu isolated sparse checkout on R730 pinned91b22ec (g5-amigaone, VERSION11.0.50). Latest delta changes Teron AmigaOne CPU/interrupt model to970fx, not A1222/SPE. Generic ppce500/e500v2 remains. No build/replacement/test; same-image SPE comparison is the bounded next experiment. See builds/derfsss-qemu-review-20261108/.

2026-11-08 DPM contract rereview: first failing command is SCLK DPM_Enable; MCLK/PCIe-DPM enable follows later. Graphics levels link PCIe states, so source/table coupling remains relevant. Retained experiment0018 propagates mandatory SMC-table/start errors instead of continuing then returning0. Native extracted-routine fault injection passes; apply-check passes. No kernel build/bind accepted. Rejected overwritten-clock-result lead after discovering intentional success fallback. See builds/dpm-contract-review-20261108/.


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
# 2026-11-08 candidate007 physical trial

User-authorized full007 installation verified all80 bundle files on the SanDisk,
with clean before/after root/FAT checks and unmounted partitions. Existing rescue
userspace/SSH/initrd and saved U-Boot startup preserved; boot.scr selects007,
exact003 rollback retained. Physical007 boot and visible console now PASS: user
confirms readable text, HDMI1920x1080/32bpp, fbcon bound, SSH survived, taint0/rootRO.
SCLK maskff/ack1; GFX indirect-buffer test still fails-110. User also requests
publication to canonical development and forge wip/polaris-be, preserving the
toolchain as authoritative. See builds/e2e007-usb-test-20261108/README.md.

2026-11-09 RadeonSI/ACO qualification: pinned Mesa25.0.7 builds with SDK8.5; raw ACO executable upload serialization fixture passes. Physical GBM native-format mismatch corrected, actual RadeonSI/Polaris11/ACO ES2.0 context reached. Scanout AddFB2 fails EOPNOTSUPP; separate draw/readback is all black, so accelerated rendering FAIL, not accepted. SSH/VT1/taint0 preserved without reload/reset. Frozen workstation dependency audit completed:7 metadata-ready/9 blocked sources; GCC14 C++ thunk failure still blocks SDK promotion and fresh workstation batch. See builds/radeonsi-aco-20261109/README.md.

2026-11-09 GPUVM boundary candidate012: corrected kmscube legacyADDFB fallback physically reaches framebuffer registration/modesetting. Native GL float API values verified, but red-clear/readback stayszero even withDCCdisabled and matching packagedlibdrm pair. Independent allocated-GTT WRITE_DATA fences complete without payload, native/LE andlowVA controls fail withoutcrash. Source reveals shared VM SDMA PTE array writtennative64 then byte-copied withswap0. Patch0032 serializes complete address|flags once asLE64.256cases perarch pass witholdBEnegativecontrol. Complete6.12.113-e2e012 kernel/43modules/687CRCs builds, USBhashes/scriptverified andselected with011rollback; running011unchanged, no reboot. Hardwarecausality/3D stillpending. See builds/vm-pte-contract-20261109/README.md.

2026-11-09 physical012: exact kernel/module boot and firstmodprobe accepted, SSH/fbcon/taint0 preserved; knownvce0timeout remains. Independent nativeBE andexplicitLE lowVA GFX WRITE_DATA still return completedfences withzeropayload. PTE sourcefix insufficient; noGLretry, unload/reset. Retained hardware-012-001 andphysical-012-summary.json in builds/vm-pte-contract-20261109/.

2026-11-09 full buffer-boundary audit: VRAM/nativeLE andGTT-USWC controls fail, remap/directVRAMread confirm actualzerotarget. LivePTE/PDE andVMID7baseregistermatchtraced nativeaddresses/flags; ringrptr=wptr, IBword lowbits2 confirmed. KernelselftestLE+swap0 differs from BOTHuserspace controls (native orLE +swap2). Scopeddefaultoff readonly polaris11_le_user_ib selector added incandidate013,24casesperarch pass, completekernel43modules/687CRCs accepted. USB013hash/scriptverifiedselected with012rollback, no reboot; running012taint0/SSH/VT1. Firstbind andexplicitLE test scripts prepared; no claimhardwarefetch0or3Dpass. See builds/gpu-memory-contract-20261109/ anduser-ib-fetch-20261109/.
