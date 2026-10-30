---
name: tabor-kernel-build
description: Prepare and verify isolated A1222 kernel builds with pinned sources, ordered patches, Docker tooling and board boot evidence.
---
Read docs/task.md and docs/kernel-build.md. Select an unchanged baseline or a forward-port experiment explicitly. Use scripts/kernel-build.py with a reviewed profile; preserve reference sources and refuse reused work directories. Patch conflicts require source-level review, not fuzz or silent hunk dropping. Preserve the vendor baseline separately when reducing non-Tabor board changes. Retain compiler/binutils versions, image identity, patch/config/DTS hashes, final config, logs and artifact hashes. Use constrained lab execution and distinguish preparation, compilation, QEMU and actual A1222 serial boot. Kernel compilation is freestanding; a successful kernel does not prove target glibc or SPE hard-float compatibility. Do not flash media or alter boot defaults unless included in the task.
