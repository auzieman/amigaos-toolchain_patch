---
name: tabor-source-intake
description: Locate and qualify Tabor/e500 SPE patches, upstream revisions and vendor samples before reuse.
---
Read docs/task.md, docs/intake.json and docs/feasibility.md. Search the existing Tabor workbench before duplicating source. Identify component, exact revision, patch origin, license, supported CPU/ABI and author modifications independently. Distinguish NXP e500v1/v2 SPE from e500mc and Arm SPE. Record immutable source revisions and per-file SHA256; keep unknown-license or unreleased Hyperion payloads private. A board DTS/audio patch is not a GCC or glibc restoration patch. Update intake evidence with what was actually found and the bounded next experiment; do not claim absence from a filename-only search.
