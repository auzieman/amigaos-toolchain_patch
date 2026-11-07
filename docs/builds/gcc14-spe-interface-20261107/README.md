# GCC14 SPE interface and option audit — 2026-11-07

Pinned baseline remains Debian GCC14.2.0-19 DFSG plus the imported GNU GCC8.5
separate SPE backend, Linux `powerpc-linux-gnuspe`, e500v2/8548, BE32, GPR double,
long double128. Candidate changes do not alter the accepted GCC8 SDK or boot media.

## Verified result

- GCC14.2.0 C-only headerless `all-gcc` bootstrap: pass (stage010 exit 0).
- All 16 serialized patches replayed on the pinned source; final source matches
  the compiled candidate. Formfeed-aware LF serialization fixed a malformed
  diagnostic diff; source formfeeds were retained, not stripped.
- 94 option records preserve names, functional properties and help. The SPE
  CALL_REALLY_USED register initializer is byte-identical.
- 20 compiler checks pass: BE PPC32 ELF, ordinary-C SPE single/double instructions,
  target macros/options, invalid option rejection, tuning default 16 versus an
  explicit override 31, and optimized loop compilation/assembly including the
  original alias-loop crash reproducer.
- The optimized float loop uses8-byte vectors and emits `evfsadd`.
- Final freestanding binary passes in QEMU user-mode/e500v2 and on the actual
  A1222 (exit 0, kernel 6.12.113-tabor-modular, taint 0 before/after). It checks
  selected single/double arithmetic, double varargs, a value across a clobbering
  call and the separately compiled optimized array loop.

Receipts: [hardware](hardware-probe.json),
[QEMU](qualification-004/qemu-result.json),
[automated compiler checks](qualification-004/probe/result.json),
[compiler hashes](compiler-artifacts.json),
[option preservation](option-preservation-check.json), and
[final source replay](reconstruction-final.log).

This is a working **C bootstrap candidate**, not an accepted replacement SDK.
No libgcc/libc was linked into the probe. Full glibc/fenv/signal/TLS/atomics,
long-double operations, C++ unwinding, cross-version ABI interoperability and
generic PowerPC regressions remain mandatory. The accepted SDK/base lock and
active USB kernel are unchanged. No GPU initialization claim follows from this.

## Obsolete option properties are audited, not option deletions

GCC8 `gcc/doc/options.texi:419` defines `Report` as selection of option state for
`-fverbose-asm`. Its `toplev.c` reads `cl_report` to print that state. GCC14's
`opt-functions.awk:182` rejects this removed property and `toplev.cc:741` prints
the decoded command line through `gen_command_line_string` instead.

There are 94 option records with the legacy metadata, although pass005 printed90
errors. The complete audit includes SPE, GPR floating-point selection, endianness,
ABI, register/PIC and scheduling options. Removing an option's parser record,
Mask/InverseMask, Var, Save, Init, RejectNegative or handler is not justified by
this reporting change. The candidate drops only reporting metadata; emitted
assembly and `-Q --help=target` still need a working compiler for acceptance.

`option-semantics-audit.json` records individual option names and properties.
A separate preservation check compares record names, properties and help against
the pre-batch candidate; it also checks the SPE call-clobber register table.

## Substantive migrations

- Preserve `max-grow-copy-bb-insns=16` using GCC14's target optimization table,
  rather than removing the legacy default-parameter hook and its behavior.
- Preserve seven other cache/prefetch/peeling/scheduling defaults using
  `SET_OPTION_IF_UNSET`, matching current rs6000 and respecting explicit user
  overrides. See `parameter-migration-audit.json`.
- Use per-function semantic-interposition policy in `decl_replaceable_p`, the
  ABI pointer contract of `choose_hard_reg_mode`, and libcpp's `cpp_macro_p`.
- Resolve the old dual CALL_USED/CALL_REALLY_USED initialization using the
  modern register framework; preserve the SPE table and reserved-register rules.
- Follow current rs6000's non-failing vcond/vcondu expander contract. Existing
  vector feature conditions remain; this does not enable AltiVec/VSX on e500v2.
  Non-SPE generic-vector coverage remains a separate regression requirement.

## Coupled interfaces and regressions addressed

Pass006 collected the old backend's modern API failures. The subsequent object
checks adapted GIMPLE include ordering, target/optimization option state,
argument records, attribute namespaces, comparisons, alignment records, asm and
ABI hooks together, retaining the SPE algorithms behind explicit adapters.
Stage008 compiled the backend but the object-check make request still used the
obsolete unsplit `insn-emit.o` name; stage009 used GCC14's split object targets
and completed the full compiler bootstrap.

Retired vector-cost hook definitions were replaced with a real
`TARGET_VECTORIZE_CREATE_COSTS` adapter, retaining density/copy penalties and
inner-loop weighting, using the explicit SLP vector type, and keeping state per
analysis. The first `-O3` loop test exposed a stale loop auxiliary pointer and
scalar/vector costing-context mix-up. Patch0016 binds the current `vec_info`
and excludes vector-only penalties during scalar costing. The original failing
loop now compiles, and the separately compiled loop both vectorizes and runs.
Vectorization was not disabled to obtain a pass.

The first hardware probe printed PASS but returned inconsistent exit status.
That was a defect in our freestanding test's inline `sc` constraints: it left
status live in a syscall-clobbered volatile register. The corrected fixture
matches [glibc2.41's PowerPC SC contract](https://github.com/bminor/glibc/blob/glibc-2.41/sysdeps/unix/sysv/linux/powerpc/sysdep.h).
The initial failed receipt is retained in `hardware-probe-initial.json`; the
corrected binary passes in both QEMU and hardware with exit 0. This is a useful
example of why emulation and physical validation remain separate gates.

## Repeat and continue

`patches/gcc/gcc14-spe-candidate/manifest.json` hashes the ordered candidate series
and pins its source profile. `scripts/prepare-gcc14-spe-candidate.py` reconstructs
fresh source from cached inputs, verifying the ordered patch/input hashes and
GCC14.2.0 baseline before writing. Earlier batch manifests describe intermediate
diagnostic bytes; the candidate manifest is authoritative for the final series. `scripts/check-gcc14-spe-candidate.py` performs
the selected compile/option/code-generation checks in a new output directory;
use `--qemu` when the worker environment supplies QEMU. The pinned tools image
and launch/configuration commands are retained in the build receipts.

All heavy work stayed on R730 with 4 CPUs/6GiB for compilation; qualification
used 1 CPU/1GiB and source replay 1 CPU/2GiB. No SDK installation or consumer
package rebuild was started. Next: qualify bootstrap libgcc with this compiler,
then the patched glibc2.41/C++ runtime and the full ABI suite before publishing
an SDK or restarting normal Debian workstation package builds.
