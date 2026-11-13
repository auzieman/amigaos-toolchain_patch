# Public-source preparation

The owner reported Steven's clearance to make the toolchain public on
2026-11-13. This is source-publication clearance, not a claim that the SDK,
workstation image or all hardware paths have passed qualification. This review
does not itself change repository visibility or rewrite Git history.

## Secret review scope

The current sweep uses pinned Gitleaks 8.24.3 with its default rules plus the
repository's literal-password and Unix-password-hash checks. Scan all reachable
Git refs/history, then tracked and nonignored untracked publication candidates.
Retain redacted reports privately outside the repository. Ignored local private,
download, SDK/build and cache directories are outside the publication scope;
never include them in a later export without a separate review.

## Review results — 2026-11-13

Baseline: `development` at `b5d56fc`; 217 reachable commits. The initial
publication-candidate snapshot contained 2,865 files (60,408,946 bytes).
The refreshed working scan includes these documentation and rule changes.

- Default-rule history scan: 3,133 matches, all JSON checksum entries in build
  evidence; the 12 Sentry-rule matches are also checksum entries.
- Updated-rule full-history rerun: 3,135 matches; credential-rule matches
  cover the same package/checksum/provisioning descriptions.
- Working scan (3,138 matches): the same checksum matches plus public X.509 certificate
  fingerprints from a kernel log. Added credential rules also flag package names,
  file-checksum keys and the image profile's password-provisioning description.
- No private key, usable password, token or Unix password hash was identified
  in the reviewed findings. No broad checksum allowlist hides future matches.
- Four synthetic quoted/JSON/unquoted-password and password-hash cases were
  detected by the added rules. Private reports retain full redaction.

The pinned scanner archive was verified against its release checksum:
`9991e0b2903da4c8f6122b5c3186448b927a5da4deef1fe45271c3793f4ee29c`.
Reports and source snapshots remain in private audit storage outside the repo.
Repository visibility and history have not been changed.

## Limits

No finding's secret value belongs in a commit, issue, console output or report
published here. A clean pattern scan is evidence with limits, not proof that no
possible credential exists. GitHub account settings, issues, attachments and
external build storage are not scanned by this repository-file review.

If a credential occurs in history, a current-file edit is insufficient. Retain
the redacted location, arrange credential replacement with its owner and prepare
a reviewed history/export remediation. No automatic history rewrite or visibility
change follows from discovering a finding.

## Documentation and export checks

Keep README and review-start aligned with the actual GCC14-only checkpoint.
GCC8 builds remain historical bootstrap evidence. C++ thunk/runtime progress is
verified; directed rounding, SDK/root migration and the installed base image
remain separate open gates. Preserve historical records with clear date/context.

Include AGENTS.md, .agents/skills and .agents/prompts in reviewed source exports.
Keep lab authentication and private account configuration external. Retain source
licenses, patch attribution and provenance; do not add a blanket license that
purports to replace third-party notices. This pass does not reassess the owner's
licensing clearance or import additional vendor material.
