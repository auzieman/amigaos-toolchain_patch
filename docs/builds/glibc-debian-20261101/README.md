# Debian libc bootstrap packaging — 2026-11-01

Packaged the already compiled and recorded GCC8.5 SPE reference as a real
amd64 native-host package, tabor-spe-toolchain8.5.0+tabor1. Includes compiler
files, relocation links, upstream GPL/LGPL/runtime-exception notices and source
provenance. Native ELF dependencies inspected. Installed it normally into a
pinned libc packaging image with native rdfind/symlinks/Perl. Image digest
is in profiles/images/debian-package-builder.json; package/tool inventories and
source compiler receipt hash retained. No dummy target libc/package records.

Normal Debian libc package preflight originally found native utilities, target
audit headers and compiler/binutils package selection missing. Source patch
selects the actual reference-toolchain package for powerpcspe and keeps generic
architecture compiler dependencies. Standard stage2 omits SELinux integration;
audit development dependency is also excluded there, not in the full build.
Normal-feature rebuild and runtime validation remain mandatory.

- Iteration001: bare installed Multi-Arch:foreign host compiler package does
  not satisfy the chosen :native dependency qualifier in dpkg-checkbuilddeps.
  Verified the unqualified dependency succeeds, then corrected source metadata.
- Iteration002: normal dependency preflight passes and libc compiles with
  e500/SPE/IBM-long-double128 flags. Fails when relocated GCC8 lookup chooses
  native objcopy for a PPC libc object. Retained bounded failure evidence.
- Iteration003: explicit exported cross OBJCOPY in SPE architecture file; fresh
  retry compiling. Version carries ~stage2. This record does not claim resulting
  Debian libc packages, installation, target runtime or full ABI acceptance.

Image/context preparation initially failed because compiler-package work is
root-owned. Corrected by creating a separate owner-owned native image context,
without changing existing build tree ownership. No reference source overwritten.

Additional library intake pins libcap-ng, audit, libcap2, libselinux, libsepol
and pcre2 for the subsequent full-feature dependency closure. Sources cached
on R730 serially; no additional compilation job runs alongside libc. Independent
OpenPGP source-chain verification remains pending, not implied by DSC SHA checks.

One heavy R730 job,4CPU/6GiB, no build network or local compilation, no extra
viewer/services, no target status edits/forced package install, no USB write.
Current package commands and bootstrap limits: ../../debian-package-build.md.

## Latest correction

Iteration003 built seven packages but failed C++ exception unwinding. Reduced
GCC8 protected-PIC return-address probe isolated the active powerpcspe backend.
After a failed inactive-backend candidate, corrected gcc-unwind-003 passes
all18 system-QEMU cases. See 006-compiler-qemu.md and 006-qemu-matrix/receipt.json.
Compiler package8.5.0+tabor2 installed in pinned updated build image; fresh
Debian libc004 compilation running. Original unwind acceptance still pending.
Desktop4 monitors now follow004 and accurately label known open gates; bounded
remote tails avoid streaming huge compiler lines into the laptop UI.

Libc004 subsequently built and passed original/new C++ runtime tests in QEMU;
see007-runtime-result.md. Rounding remains open; no complete ABI/root claim.
