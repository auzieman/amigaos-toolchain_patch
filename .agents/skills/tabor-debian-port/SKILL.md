---
name: tabor-debian-port
description: Build and validate the frozen Trixie powerpcspe Debian port for A1222 using standard Debian package, dependency and cross-build mechanics after toolchain bootstrap.
---
Read AGENTS.md, docs/debian-port-build-contract.md, the latest task/progress
entries and profiles/trixie-spe-base.lock.json. Use profiles/port-build-scope.json
for the selected workstation closure. Keep the frozen baseline, powerpcspe ABI
and remote resource limits; native amd64 tools stay native. Debian's maintained
PowerPC ports are references for packaging mechanics, not ABI substitutes.
Route demonstrated compiler/runtime defects to tabor-spe-forward-port and
board/kernel work to tabor-kernel-build.

Current compiler requirement (user, 2026-11-11): GCC14 throughout the target
SDK/runtimes, build roots and final compiled packages. Consult
profiles/compiler-policy.json; keep consumer compilation stopped until that
foundation is qualified. GCC8 receipts are retained bootstrap history, not
acceptable final distribution outputs. Current GCC14 C++ runtime failure belongs
to tabor-spe-forward-port; do not resume GCC8 packaging to work around it.

Target is powerpcspe / powerpc-linux-gnuspe, P1022 e500v2, ELF32 big endian.
Preserve the qualified ABI flags: -mcpu=8548 -mabi=spe -mspe
-mfloat-gprs=double, and the qualified long-double ABI. Verify compiler defaults
and resulting instructions; do not introduce AltiVec or classic FPR instructions.
Do not apply userspace flags blindly to kernel compilation. Kernel SPE/context
configuration belongs to the kernel workflow and its qualified configuration.

Use Debian metadata and tooling as the authority: source Build-Depends,
Build-Conflicts, architecture restrictions and profiles; dpkg architecture
registration; dose installability; sbuild/apt installation and dpkg-buildpackage.
Our scripts retain reviewed sources, patches, real artifacts, bounds and logs.
Do not add a competing dependency solver or override package state. Cross
builds execute native tools/generators, not newly built SPE programs; runtime
validation belongs in separately recorded QEMU/physical tests.

Keep the server's broad tool/download provisioning separate from each build
root. Persistent source archives, apt downloads and accepted target artifacts
accumulate; disposable roots start from a qualified frozen buildd base with
necessary native cross-build infrastructure, including apt-utils. Let sbuild
install each source's actual dependencies and honor Build-Conflicts. Do not
clone a universally preinstalled dependency superset into every job. Consult
docs/port-build-pipeline.md for scripts and current qualification limits.

Before a broad retry, review the latest completed fallout as a whole. Group
unique sources by failure stage and shared prerequisite; repeated entries in
multiple phases are not independent failures. Distinguish acquisition, root
setup, dependency coinstallation, source compilation, packaging and runtime.
Use the actual logs to identify the earliest shared blocker. Supported Debian
bootstrap profiles may break cycles; record required full rebuilds and omitted
outputs. Intake missing producers from authenticated frozen metadata rather
than shrinking the workstation closure to reach a package count.

Qualify changes at the boundary they affect before widening the batch. For
root/cache changes, exercise the same sbuild user, UID/GID mapping, bind mounts,
apt configuration and cross-resolver as real jobs. An apt check or host-root
nspawn probe alone does not qualify a cross-build root. Cache qualification
includes network-disabled reuse and recovery of completed archives after
failure. Representative package builds must cover the observed dependency
conflict and SDK/compiler path, not just the easiest successful source.
Retain failing/passing receipts and exact input hashes; distinguish a narrow
regression pass from completed integration acceptance.

When infrastructure is qualified, use scripts/submit-port-build.py for up to
four independent dependency-ready R730 jobs within AGENTS.md limits. Continue
unrelated ready work after a package failure. Retry a deterministic failure
only after relevant inputs change; acquisition retries can reuse verified
caches without source changes. If a round adds no accepted outputs, inspect
its shared blockers before submitting another equivalent round. Changed run
IDs, queued jobs and metadata readiness are not progress in accepted packages.

Fix repeated compiler/header failures in their demonstrated SDK/foundation
cause before consumer edits. Preserve genuine Debian control/version/profile
semantics; register explicit reviewed patch and binary rebuild requests in
profiles/port-package-overrides.json. Do not force coinstallation, fabricate
shlibs/installed records or strip unrelated features to make a queue pass.

Assemble target filesystems with apt/dpkg, preserving maintainer scripts,
triggers, permissions and service/session setup. Acceptance is the selected
X11/E workstation with terminal/editor, browser, SSH/VNC and GL/SPE demos plus
its dependency closure; QEMU client painting and physical CPU/RAM/Radeon tests
are separate gates. Report new accepted source/binary outputs, root provenance,
active jobs, grouped blockers and the next image/runtime gate. Never describe
a submitted correction as deployed or a build as target-runtime validated.

Cross-build failure checklist (adapted from the supplied pipeline example):
- Start with sbuild --build=amd64 --host=powerpcspe --profiles=cross,nocheck.
  Add nobiarch, nopython or pkg.<source>.* only when the selected source actually
  implements the profile; record omitted outputs and required full rebuilds.
- Distinguish executable build tools from target headers/libraries before
  changing architecture qualifiers. Native generators run on amd64; target
  development libraries stay SPE. In particular, Python generators and target
  libpython development headers are separate requirements. Follow actual
  Build-Depends/Multi-Arch semantics, not a blanket :native rewrite.
- Publish inspected .deb outputs to the signed local archive, refresh apt
  metadata in the appropriate build root, and let sbuild/apt install them.
  Preserve the existing qualified archive/root mechanism; no parallel reprepro
  service or sbuild-update requirement without an actual need.
- For configure runtime tests or Meson introspection, use measured target cache
  answers/properties or package-supported cross mechanisms. Never invent
  ac_cv_* values just to pass configuration. Where target execution is needed
  to establish an answer, retain separate QEMU/board evidence. Keep source,
  toolchain and ABI provenance with the answer.
