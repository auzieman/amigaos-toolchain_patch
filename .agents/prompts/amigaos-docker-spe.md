# AmigaOS Docker compiler/SPE follow-up

Read AGENTS.md, docs/task.md, docs/amigagccondocker-integration.md and
bench/amigaos/README.md. Use the tabor-spe-forward-port skill. Work on the
AmigaOS experiment branch independently of Linux kernel/glibc work.

Select an exact compiler-image digest, GCC/adtools revision and target runtime.
Preserve the GCC6 image as reference. Reproduce the smallest failure before
selecting a patch. Use the existing container runner with fresh output,
hash-verified source helpers and recorded resource limits. Keep source/image
intake separate from network-disabled compilation. Verify the driver-to-assembler
CPU mapping as well as frontend flag recognition and emitted instructions.

Do not describe the specs overlay as a modern GCC backend restoration or force
Linux libc/long-double flags into the AmigaOS runtime. Preserve integer-only
module boundaries for this demo, SDK licensing and all original source notices.
Never infer native execution from cross-compilation or execute OS4 binaries on
Linux. A physical software-only run and an optional explicitly selected native
SPE comparison need separate logs, image checksums and OS version evidence.
Record context/signal/thread/exception gaps rather than assuming a kernel update
fixes them. Keep wider ABI and modern compiler restoration as explicit next gates.
