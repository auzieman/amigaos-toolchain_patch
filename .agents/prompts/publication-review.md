Review public-source readiness without changing repository visibility or rewriting
history. Read AGENTS.md and docs/publication-readiness.md. Confirm actual refs,
working changes and the intended export before scanning.

Use Gitleaks with the repository configuration, full reachable history
(--log-opts='--all --full-history') and a separate publication-candidate directory
scan. Keep full redaction enabled and reports outside the repository. Review
password assignments, private keys, tokens and password hashes; report paths,
commits and rule classifications without printing values. Check tracked sensitive
filenames as well. Ignored local private/build directories are not publishable
inputs; report that scope limitation instead of claiming all disk files clean.

Treat a historical credential as a real exposure until classified; removing it
from the working tree does not remove it from Git history. Prepare a concrete
remediation plan and preserve evidence. Do not force-push or change visibility
without explicit authorization. Preserve original licensing notices and distinguish
source publication approval from passing compiler/image/hardware qualification.

Refresh README, review-start, active task and relevant skills/prompts so current
GCC14-only/base-image priorities are clear and dated historical claims remain
recognizable. Verify local links, JSON, patch hashes and relevant tests; avoid new
compilation during this documentation/security pass. Include the skills/prompts
in reviewed exports and publish only what was actually inspected.
