# Explicit-LE userspace GFX IB fetch control — 2026-11-09

Candidate013 adds a default-off diagnostic parameterpolaris11_le_user_ib.
It is read-only after module load and selects ib->is_le only for BE Polaris11
userspace GFX jobs. It does not convert command bytes or change other engines,
ASICs or the normal default. ExplicitLE callers are mandatory when enabled.

Why this test: the kernel GFX self-test that advanced past its payload gate in
011 uses LE IB data and fetchswap0. Userspace native and LE controls both used
legacy fetchswap2. Live source/VM/VRAM/ring checks now verify the mapping, root
register, memory contents and encoded fetchmode, but do not prove swap2 works
for this userspace path. We have not tested the kernel self-test's passing
byte-and-fetch combination in a userspace allocation.

The exact selector block passes24cases perarchitecture: disabled default,
otherASIC/engine isolation, existingLE selection preservation and BE target
selection. This validates selection logic only. It does not simulate hardware
fetch or prove hardware swapping is defective.

The complete pinned6.12.113 kernel build uses two CPUs/4GiB, existing GCC14
image/source/config and private reflink source/output. No SDK/userland drift.
A separate boot is required to load this new complete matching module set.
No live unload/reload or runtime register patching is planned.

First-bind harness first-bind-013.py preserves installed-set preflight/hash
checks and offboard capture, then runs normalmodprobe with the explicit option
polaris11_le_user_ib=1 and verifies its exported valueY. Default boot is not
silently changed to enable this option.

Acceptance order: verified013 kernel/module; firstbind optionY; explicitLE
allocated-buffer write; inspect ring IB lowaddress bits0 rather than2; require
actual marker bytes and completed fence. On failure retain evidence and stop.
Existing Mesa native PM4 must NOT run with this option enabled: it still has
its old native-IB contract. Only after the diagnostic passes may a separately
reviewed paired producer-side Mesa implementation be tested. This candidate is
an experiment, not a distribution release or a claim of acceleration fixed.

## Build and USB checkpoint

Complete013 kernel/43modules accepted with687matching imported CRCs; AMDGPU
SHAa50eb602944186f8186e633da8b687d208434af601b1afed67efcb5b7ad1cfb6.
Cruzer serial03007431041721021451/rootPARTUUIDa1221108-02 checked. All staged
files and U-Boot script verified, boot.scr selects013, exact012rollback
retained asboot-012-rollback.scr. FAT unmounted/rootRO. No reboot requested;
012 is still running. The boot image does NOT enable the diagnostic parameter.

run-explicit-le-013.py refuses any kernel/option except013/Y, verifiesROroot
and copied helper/tool hashes, submits only explicitLE GFX words, captures
kernel logs, then checks the latest matching CPU ring IB address has swapbits0.
PayloadPASS is separate from fetch-selectorPASS. This test has not run yet.
Do not start existing native-PM4 Mesa while the option is enabled.

## First physical 013 boot and loader correction

Physical boot confirmed `6.12.113-tabor-e2e-013`, taint zero, no modules loaded.
First bind returned with `amdgpudrmfb`, but the diagnostic parameter read `N`.
The harness stopped before submitting any explicit-LE commands. This run does
not test the new fetch contract. See `hardware-013-001/receipt.json`.

Source/config review found `CONFIG_FEATURE_CMDLINE_MODULE_OPTIONS` disabled
in the installed full BusyBox modprobe build. `do_modprobe()` conditionally
omits command-line options when this feature is disabled. This is a loader
configuration defect, not evidence against the GPU hypothesis.

Rebuilt the same pinned BusyBox source/SDK with that feature enabled, using
a private output and bounded R730 Docker build. On-board `modprobe -D` proves
the original drops `polaris11_le_user_ib=1` and the replacement preserves it.
No modules are inserted by these dry runs. Installed replacement SHA256
`1270d14ab490b0a2b2b663dd6c78181151159930325f816bf8b8fca3ca322932`,
retaining `/sbin/busybox-modules.before-options-013`. Root returned read-only;
GPU was not unloaded or reloaded. The first-bind harness now checks argument
preservation before loading any module, and reports a useful error on `N`.

A further fresh boot is required before repeating first bind with this fixed
loader. Kernel 013 itself needs no rebuild. No GPU payload or hardware GL
success is claimed from this boot.
