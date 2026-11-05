# Compiler generation versus the selected Trixie baseline

The accepted SPE compiler is GCC8.5.0, packaged as8.5.0+tabor6 after SDK
header/layout repairs. The tabor6 suffix does not mean GCC was upgraded.
The immutable baseline lock explicitly retains GCC8.5.0. It pins glibc2.41
and Linux6.12 separately; this is a mixed-generation bootstrap foundation,
not compiler parity with Trixie.

The authenticated frozen NativePackages index selects native gcc-14
14.2.0-19 (gcc-defaults4:14.2.0-1). The same gcc-14 source version is recorded
in profiles/port-dependency-sources.lock.json. Availability of those sources,
and native/ordinary PowerPC GCC14 binaries, is not evidence of a restored
GCC14 SPE backend or ABI-compatible libgcc. No such acceptance is recorded.
GCC8 was the last upstream SPE compiler generation; restoring that support
onto GCC14 is a distinct unfinished foundation task (docs/feasibility.md).
Do not silently advance the frozen build's compiler or substitute ordinary
PowerPC hard-float binaries for SPE.

The user's expectation was compiler/runtime restoration relative to the
chosen Debian release. Earlier progress language blurred modern libc/kernel
work with modern compiler completion; that interpretation was incorrect.
Record this gap explicitly when discussing SDK completeness.

Observed failures must still be attributed by evidence. The 730-artifact
per-job staging loop, invalid Docutils :native qualifier, missed existing
binary rebuild requests and archive filename bugs were process/packaging
problems. BLT's unconditional C23 variadic declaration is a demonstrated
compiler-generation mismatch. Neither category explains all deferred sources.
Target Python, GIR/introspection, normal feature-complete bootstrap rebuilds
and final package-managed desktop configuration remain separate gates.

Maintained Debian ppc64el/ppc64 ports are the template for archive/buildd,
source dependency/profile and package semantics. Their binaries and ABI flags
are not substitutes for32-bit big-endian e500v2/SPE. References:
https://www.debian.org/ports/
https://wiki.debian.org/CrossBuildPackagingGuidelines
https://wiki.debian.org/sbuild

Continue the selected110-source workstation dependency closure through normal
Debian tooling, with failed sources retained and independent ready work
continuing. Expand from genuine workstation package dependency metadata, not
an arbitrary package-count target. Report source builds separately from binary
package counts. Thousands of final binary packages do not imply thousands of
independently selected source packages or simultaneous jobs.
