Private Tabor SPE toolchain project. Read README.md and docs/task.md before changes. Keep Linux target, host tools and AmigaOS target ABIs separate. Preserve upstream license notices; vendor sample availability is not permission to relicense. Never import unreleased Hyperion source into a public repository. Pin exact source revisions and patch hashes before builds. Use isolated constrained lab jobs; retain source/toolchain/config/artifact hashes and logs. Build, emulator execution and real A1222 boot are separate acceptance gates. Do not overwrite existing Tabor sources, images or SDKs. No automatic remote publication or deployment.

Project workflows: .agents/skills/tabor-source-intake, tabor-kernel-build and tabor-spe-forward-port. Reusable task starters live in .agents/prompts. Read only the skill for the current slice. docs/kernel-build.md owns the executable kernel recipe.

Write reviewable commit bodies per CONTRIBUTING.md: motivation, concrete change, validation/evidence and remaining limits. Keep docs/progress.md current for Hyperion collaborators. Preserve published history; add follow-up context rather than rewriting it.


Laptop resource policy (user request, 2026-11-01): this workstation has about
12GiB RAM and no swap. Keep heavy compilation, source extraction, image assembly,
compression and QEMU on the R730/build server, never start local fallback builds
without a new user request. Use one heavy remote job at a time by default, with
explicit CPU/memory limits (normally4 CPUs/6GiB; justify larger jobs). Keep local
commands short and output bounded; summarize logs on the server instead of
streaming whole logs or repeated full build trees into the editor. Reuse one
existing viewer and do not automatically reopen batches of terminals/browsers.
Use one-thread limits for local BLAS/OpenMP/FFmpeg work if unavoidable. Check
available laptop memory and own process/thread impact at substantial job starts
and after symptoms; do not kill user apps, change swap, or tune services merely
from a snapshot. Remove only identified obsolete task-owned processes/tunnels.
Prefer a server-hosted noVNC proxy with loopback SSH forwarding.

Debian-first build policy (user clarification, 2026-11-01): read
`docs/debian-port-build-contract.md`. Patched compiler/runtime/board support
forms the foundation; Debian source dependency/profile semantics determine
build readiness and binary Depends/Pre-Depends determine installation order.
The recipe allowlist is not a dependency solver. Progress toward clean,
package-managed apt/sbuild build roots and repository-driven dependency
resolution; do not perpetually extend ad hoc sysroot/shlibs patches across
ordinary packages. Preserve normal Debian feature/setup behavior and close
bootstrap cycles with appropriate profiles and subsequent required full builds.
Our tooling must use real packages and dependencies in that same process.

Target architecture scope (user correction, 2026-11-01): source/package builds
are powerpcspe only. Use existing Debian host binaries for scripting and build
orchestration; do not expand target dependency work into rebuilding amd64 libc
or other native counterparts. Keep host compiler tooling outside the target
archive. Cross-compilation has a host and a target, but this is not a multi-target
archive rebuild. Resolve target dependencies in the target environment.
