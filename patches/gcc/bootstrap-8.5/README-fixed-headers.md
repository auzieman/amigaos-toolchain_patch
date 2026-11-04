# GCC8 generated fixed-header integration

The recorded GCC8.5 SDK runs `fixincludes` against modern glibc headers. Its
machine-name rewriting changed five quoted `__has_include("linux/…")` operands
to `"__linux__/…"`. The generated sys/mount.h and sys/rseq.h then select fallback
declarations even when the corresponding Linux UAPI headers exist.

SDK packaging revision 8.5.0+tabor6 runs
`scripts/repair-spe-fixed-headers.py` while staging the package. It corrects only
the five demonstrated string operands, preserves every other generated fix and
the compiler-owned limits headers, asserts the expected inputs, and records
before/after hashes. No installed SDK or application source is edited in place.
The compiler frontend, ABI defaults, target runtimes and frozen source versions
are unchanged. The base lock records the original SDK baseline; current sbuild
inputs explicitly pin this reviewed packaging correction and core adapter spe5.

`scripts/check-spe-fixed-headers.py` extracts genuine target development/UAPI
packages and uses the read-only native template for syntax-only compilation.
Regression003 enables GNU declarations, reproduces four original
mount/rseq/sched/statx failures and passes all five
corrected header combinations. No target executable runs. Regression001 also
reached an unrelated missing cross-assembler in the diagnostic native root;
the syntax-only header test avoids that dependency and is not a linker test.
Actual package compilation remains a separate acceptance gate.

GCC documents generated fixed headers and their lifecycle:
https://gcc.gnu.org/onlinedocs/gcc/Fixed-Headers.html

A future compiler-source rebuild should address the old machine-name rule
itself and retain these probes. The bounded staging repair is part of the
reproducible SDK recipe, not a claim of a modern GCC backend restoration.
