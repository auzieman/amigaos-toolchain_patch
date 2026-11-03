---
name: tabor-debian-port
description: Operate the frozen Trixie powerpcspe package port and A1222 desktop build service after toolchain bootstrap; resolve dependency closure, provision build environments, batch builds and assemble package-managed images.
---
Read AGENTS.md, docs/debian-port-build-contract.md, the latest entries in
docs/task.md and docs/progress.md, and profiles/trixie-spe-base.lock.json.
Use profiles/port-build-scope.json to distinguish the selected base/desktop
closure from metadata-only candidates. The source inventory is not a request
to build a web server, new language runtime or compiler suite. Use existing
native helpers for native jobs; target builds need a traceable selected binary
or necessary target build-library consumer. Prefer supported source profiles
such as stage1 to break bootstrap cycles before the full services are built.
Use this workflow for ongoing Debian userspace work. Use tabor-spe-forward-port
only for a demonstrated compiler/runtime ABI defect, and tabor-kernel-build
for kernel/board work. Do not restart toolchain investigation for an ordinary
missing Build-Depends or a broken build-server configuration.

Use scripts/submit-port-build.py and docs/port-build-pipeline.md for normal
build rounds. Evaluate retained fallout, commit reviewed source fixes/profile
choices in profiles/port-package-overrides.json, and rerun the pipeline when
inputs change. One-off package commands are bounded diagnostics, not the
default workflow. The pipeline prepares source metadata, uses Debian's solver
and package builder, and reports failures; it must not invent another resolver.

Provision the R730 for the whole selected source scope up front. Keep a broad
native build-tool/dependency template and downloaded package cache on the
server. scripts/prepare-port-build-server.py installs the original pinned
DSCs' build dependencies with apt, including independent build tools. Preserve
the frozen snapshot and native foundation versions. Incompatible dependency
sets need separate prepared templates, not repeated removal/reinstallation
in one shared mutable root. Existing native binaries supply native tools;
do not rebuild an amd64 distribution. All heavy work stays remote.

Large templates unpack on the data filesystem through sbuild's documented
unshare_tmpdir_template; /tmp is tmpfs on this server and counts against worker
memory. The temporary path must be traversable by the mapped user without
relaxing private source-directory permissions. Build Architecture:all data and
helpers separately with native tools and normal -A dependency semantics;
their acceptance excludes ELF payloads and native architecture packages.

The source list is an intake inventory, not a closed port. Use Debian's
architecture/profile-aware dependency reports and authenticated Sources and
Packages metadata to identify missing producers, including virtual Provides.
Intake the missing target sources and their prerequisites from the same frozen
snapshot before retrying consumers. Distinguish a native generator from a SPE
library using actual package/control metadata; do not infer its role from its
name. Review cross annotations and supported bootstrap profiles for cycles.
Keep omitted outputs and required full-feature rebuilds explicit.

Use dose-builddebcheck for readiness and normal sbuild/apt for dependency
installation in disposable build roots. Accumulate real accepted artifacts
in the port pool; the prepared native template is a cache, not evidence that
SPE development libraries are installed. Keep build-root-only runtime
providers out of the final target archive. Use up to four dependency-ready
R730 jobs within AGENTS.md resource bounds and re-evaluate after new artifacts.
When there is no ready work, advance dependency-source closure or resolve the
shared infrastructure fault; do not resubmit the unchanged blocked batch.

Separate missing archive inputs, dependency conflicts, infrastructure errors,
source compilation failures and target runtime failures. Fix shared causes
before creating per-package patches. Retain failed logs and give a source back
after its dependencies or reviewed fix change. Target programs do not execute
as part of cross compilation. Avoid per-package feature stripping, fabricated
package state or shlibs substitutions to make a queue appear successful.

Assemble with apt/dpkg, preserving Debian maintainer scripts, triggers,
permissions and service/session setup. The deliverable is X11, Enlightenment,
a terminal/editor, the selected compact browser, SSH/VNC and GL/SPE demos with
their actual dependency closure, not a source-count target. QEMU validates
normal configuration and client painting separately from compilation;
physical A1222 CPU/RAM/Radeon acceptance follows. Report accepted packages,
shared blockers, active workers and next image gate without equating partial
bootstrap outputs or metadata readiness with a working desktop.
