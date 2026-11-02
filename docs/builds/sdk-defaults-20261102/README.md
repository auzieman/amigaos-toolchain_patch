# Installed compiler defaults and dependency closure — 2026-11-02

The previous SDK defaulted to /sysroot. Ordinary Debian packaging may replace
DEB_CFLAGS_MAINT_APPEND, so injected sysroot/ABI flags were not a valid shared
architecture foundation. Libsepol501 and PCRE2-501 exposed that defect.

Fresh GCC8.5 source build gcc-system-root-001 passes, with installed sysroot /
and a separate immutable bootstrap build sysroot /sysroot. Its defaults select
big-endian SPE/no-FPR/IBM128 and produce SPE float/double assembly without ABI
flags. The compiler remains a historical bootstrap, not modern GCC restoration.
Native SDK5 is packaged from that exact receipt and installs normally into the
existing configured development root. All nine binutils lookups select cross
tools. Fresh C/C++ sources include installed headers and link using defaults;
ELF32/big-endian/PowerPC and absence of RPATH/RUNPATH are checked statically.
No target executable runs during these checks or package compilation.

The managed package runner now removes injected maintainer ABI/sysroot flags
and validates compiler defaults before touching source. Normal Debian hardening
and package-specific flags remain in control. Existing conditional transport
patches are inactive because TABOR_SYSROOT is absent. Libsepol502 and PCRE2-502
both pass normal Debian packaging. Their receipts show no injected ABI/sysroot
flags and no bootstrap shlibs mapping. This closes the focused issue14 gate;
full runtime acceptance remains separate.

An initial SDK packaging attempt failed before source execution because its
frozen project omitted the packaging helper. Corrected snapshot002 contains
that helper and the pinned bootstrap profile; original compiler output and
all failed attempts remain intact. Package receipt identifies exact inputs.

Native build dependencies are reviewed separately: host documentation tools,
code generators and Architecture:all protocol data use Debian binaries.
Target development libraries must come from actual SPE packages. The queue
uses Debian dependency checks, retains failures, and never treats its allowlist
or package count as complete dependency resolution. Full target package setup,
new graphical image, runtime/ABI and bare-metal validation remain pending.

Native development-root libraries libacl1, libmd0 and libcap-ng0 carry Debian
+b1 binary rebuild revisions, while our first target builds used their source
versions. Co-installation requires exact Multi-Arch:same binary versions.
The runner now supports an explicitly reviewed binary-NMU number through Debian
`dch --bin-nmu`, followed by normal source packaging. It does not edit a .deb or
installed dpkg state. Rebuilds and subsequent installation are still pending.
Reference: https://manpages.debian.org/trixie/devscripts/debchange.1.en.html
