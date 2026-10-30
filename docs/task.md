# Active task — private Tabor SPE toolchain intake

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
