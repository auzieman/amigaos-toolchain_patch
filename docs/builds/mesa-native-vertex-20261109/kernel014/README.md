# Kernel014 pre-publication diagnostic candidate

Built from kernel013's accepted source/config/tooling in a fresh private R730
source/output tree. Single default-off bounded GFX envelope trace patch added;
CONFIG_LOCALVERSION changed to -tabor-e2e-014. No render fix claimed.

Build: GCC14.2.0-19/binutils2.44, pinned tools image,2CPUs/4GiB/networknone.
Complete vmlinux/modules/dtbs and firmware bundle accepted,43modules; AMDGPU
ELF32BE, correct vermagic,687 symbol CRCs verified. No compiler warning/error
lines. uImage CRC/compression and physical image-end checks pass. Receipts retain
hashes and commands. Firmware remains the pinned known pack.

Staged over surviving SSH on the kernel013 boot. All selected kernel/module
hashes verified. Existing /boot.scr now selects014; boot-013-rollback.scr/cmd
retained. Root returned read-only. No reboot or physical014 acceptance yet.
The current013 GPU remains post-timeout and must not receive another workload.

After manual fresh boot: verify014 release/module hash/options, rootRO, taint0,
no prior timeouts/reset. run-physical-rgb-014.py arms trace after boot and retains
offboard logging, renderer identity and one unchanged standard offscreen RGB
trial. No extra draws/reload/reset; timeout records a failure rather than retry.
Trace defaults off and is bounded16envelopes/512words each; can perturb timing.
Capture includes precommit words, excludes final commit-added alignmentNOPs.
decode-envelope.py correlates IB address/length and decodes waits/EOP fields.
Decoder checked for >32bit address, IB correlation and incomplete-log detection.

This is a diagnostic build/staging gate; physical boot, trace receipt and actual
GPU rendering remain pending. User reboot is the next required external step.

## Physical014 first bind and RGB trial

Fresh boot1eca6c54-6c4c-4419-b807-c7f6877bf366, kernel014, taint0. Initial
AMDGPU absent; exact installed module hash and loader options verified, rootRO
before first modprobe. First bind returned, LE-user-IB=Y. RAM BusyBox helper
restored and hash-verified after reboot. No repeated load/reload or VT change.

One standard RGB FBO trial reached actual Polaris11/ACO renderer and emitted
ACO errors: unsupported f2f32 in instruction selection, then undefined%8 used
by position export. Candidate still submitted408DW IB. GFX timed out1/2 and
automatic reset reported VRAM loss. No pixel pass, manual reset or retry.
Kernel envelope capture complete70DW: VMID7 IB0x218000,408DW,swap0 matches
logged IB metadata; kernel-fence wait reference1 and rawdecoded prior1;
completion packets request actual2. This is CPU-publication evidence, not GPU
progress. HDP operation1 has two separate register operands, not a combined
64-bit address; decoder corrected accordingly. No snapshot permits declaring
which wait/IB stage GPU reached.

This is newly retained compiler failure evidence, not a confirmed complete
explanation of older attribute-free failures. Native-vertex GPU fetch lowering
and compiler inputs need offline investigation before another hardware draw.
Actual source f2f32 selection accepts16/64-bit sources for VGPR; the logged error
means another source width reached it, leaving undefined output. Do not paper
over it with a fence timeout extension or submit further workloads.
