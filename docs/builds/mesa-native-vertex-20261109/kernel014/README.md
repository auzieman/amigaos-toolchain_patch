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
