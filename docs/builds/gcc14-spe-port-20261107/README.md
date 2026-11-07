# GCC14 SPE source restoration checkpoint — 2026-11-07

This is experimental compiler bootstrap work, not a qualified SDK or a new
boot image. The accepted GCC8 SDK and active A1222 USB boot files remain unchanged.

The candidate imports the separate GNU GCC8.5 `powerpcspe` backend into the pinned
Debian GCC14.2.0-19 DFSG source. It targets Linux `powerpc-linux-gnuspe`, big endian,
e500v2/8548, SPE double in GPRs, long double128. AmigaOS runtime compatibility is
outside this Linux compiler qualification.

## Reproducible source preparation

Use `scripts/prepare-gcc14-spe-candidate.py --gcc8 EXTRACTED_GCC8 --gcc14 FRESH_GCC14`
on the build server. Inputs are the pinned cached archives from the foundation
qualification. The importer checks all147 reference file hashes before writes,
renames C++ implementation suffixes and references to `.cc`, preserves modes,
applies the ordered candidate patches and regenerates the CPU option table with
the imported upstream generator. It never installs the candidate compiler.

Candidate patches and import receipt are under `patches/gcc/gcc14-spe-candidate`.
The top-level accepted GCC patch series is deliberately unchanged.

Debian's `gcc-gfdl-build.diff` is retained verbatim from GCC14.2.0-19 packaging,
applied at `-p2`: the DFSG archive replaces `tm.texi.in` with a one-line notice.
The resulting genhooks documentation failure is packaging setup, not a missing
SPE hook. It must not be worked around by inventing hook documentation.

Fresh-source reconstruction002 passed (container exit0): imported backend files,
regenerated CPU option table, target configuration and Debian-patched Makefile
match the diagnostic source tree byte for byte. See `reconstruction-002.log`.
Pass005 completed with exit2; the retained log is its final result.

## Diagnostic progression

- Configure selects restored Linux SPE target. First build stops at missing
  GCC14 `.opt.urls` metadata.
- Shared documented options receive companion metadata; no invented URLs for
  removed SPE options. Keep-going pass exposes removed `dbxelf.h` and the DFSG
  manual-generation rule.
- Remove obsolete STABS header and rename the debugger macro to `DEBUGGER_REGNO`;
  preserve the legacy SPE high-register/DWARF mapping function. Use Debian's
  existing manual-generation patch.
- Remove obsolete `NO_IMPLICIT_EXTERN_C`, following modern PowerPC headers.
- GCC14 machine-description generators reject ambiguous iterator references.
  Qualify SFDF and IBM128 mode references using modern rs6000 as the reference.
- Pass005 reaches actual compiler C++ translation units. Current observed
  blockers: `decl_replaceable_p` now requires semantic-interposition policy;
  `choose_hard_reg_mode` now takes an ABI pointer instead of a boolean. The completed keep-going pass also exposes obsolete option `Report` properties
  and additional backend interfaces; this is not a successful compiler.

The diagnostic launch scripts are historical receipts with R730-specific paths,
not the portable build interface. Runs use the pinned native Trixie tools image,
4CPUs/6GiB, network disabled. `all-gcc` is headerless C-only bootstrap; final
C/C++/libgcc/glibc and the full ABI suite remain mandatory before SDK acceptance.

Next: finish the broad diagnostics, adapt backend interfaces with upstream
PowerPC semantics, then validate emitted SPE code and full runtime behavior.
No package queue or hardware-kernel activation depends on this unqualified build.
