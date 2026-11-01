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
