# Commit and review notes

Keep each commit focused on one patch, build-workflow correction or evidence
update. Give the subject a concrete component and outcome. In the body explain:

- Why the change is needed and what changed.
- Exact source/toolchain baseline and patch origin when relevant.
- Checks actually run, with BKC run IDs or retained evidence links.
- Failures, untested behavior and the bounded next action.

Separate patch application, compilation, emulator execution, actual A1222 boot
and SPE ABI/runtime acceptance. Record infrastructure interruptions as such.
Keep component patches ordered and attributable; preserve upstream notices.
Do not amend published shared history to improve old messages. Backfill context
in docs/progress.md and link the relevant commit/run instead.

Use docs/progress.md as the concise review trail, docs/builds for structured
results and docs/task.md for detailed active work. Update review-start.md when
acceptance changes. Cached source, SDK/media and generated build trees stay out
of commits. Submission and retention scripts are lab-specific; the generic
Docker/iteration runners should remain inspectable independently.

Track reproducible build/runtime failures in this private repository's GitHub
issues as work proceeds. Include the failing iteration, exact component/ABI,
observed error, evidence, proposed correction and a bounded validation gate.
Link correction commits and raw results; close only after that gate passes.
Keep unresolved ABI failures open even when later application builds succeed.
