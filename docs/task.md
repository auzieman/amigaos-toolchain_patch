# Active task — private Tabor SPE toolchain intake

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

Pending clarification: Linux/SPE userspace first versus a Linux-hosted compiler
targeting AmigaOS first. Independent first action: baseline kernel provenance.
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
