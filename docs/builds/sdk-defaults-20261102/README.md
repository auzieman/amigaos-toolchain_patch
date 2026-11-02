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
installed dpkg state. All three +b1 rebuilds and their normal apt/dpkg coinstallation pass with
clean audit (bin-nmu-install.log).
Reference: https://manpages.debian.org/trixie/devscripts/debchange.1.en.html

## First dependency wave and build-mode correction

The frozen20-source wave completes:15 pass, xz fails packaging,4 sources are
blocked by declared dependencies (zstd, ncurses, libjpeg-turbo, libselinux).
Compiler defaults and source patches were unchanged during this wave.
Actual SELinux/PCRE2 prerequisite packages install normally before the queue;
source-built libmd/ACL/libcap-ng development pairs also install normally in a
subsequent development root. The latter is a bounded512MiB, one-core metadata/
package-installation check alongside the single4CPU/6GiB compiler job.

The xz failure is in liblzma-doc, not target compilation: combined -b plus
nocheck skips its independent documentation configuration, then expects API
output. Normal architecture autobuilders use -B. Future compiled-source jobs
now use -B; explicitly reviewed scripting/data jobs remain -A with native tools.
This preserves runtime rules and does not patch away documentation installation.
Issue15 tracks fresh xz retry acceptance, still pending here.
https://www.debian.org/doc/manuals/maint-guide/build.en.html#autobuilder

Reviewed native source/binary metadata also pins normal binary-NMU counters
where source-identical Multi-Arch:same coinstallation needs Debian's +bN version.
The native inventory and source-matched version review are retained. All target
rebuilds still compile source normally; no .deb control/status rewriting occurs.

Libjpeg-turbo's Build-Depends requests target default-jdk/nasm even though they
are native generator executables. A pinned source packaging patch adds :native
qualifiers while preserving architecture restrictions/features. Fresh compile
and packaging remain required; no target JDK is being ported by this change.

## Additional source intake

GPM1.20.7-11 and LZ4 1.10.0-4 are absent from the existing reviewed cache paths.
Normal authenticated apt Release/Sources metadata downloads their exact sources;
archive hashes are pinned in profiles/terminal-compression-sources.lock.json.
Separate DSC-signer verification is not claimed. Copyright notices are retained:
GPM is GPL-2.0+ with GPL-3.0+ script exceptions; LZ4 libraries are BSD-2-clause,
with GPL-2+ tools/packaging and per-file exceptions recorded in its copyright.
These are ordinary Linux dependencies, not NXP samples or AmigaOS runtime code.
No board support is inferred from them. Initial intake001 rejects a conflicting
hard-coded .gpg Signed-By path; intake002 reuses Debian's configured .pgp trust
path rather than overriding source authentication. Fresh outputs retain both
attempts. Next: source compile/package, normal installation, then ncurses/zstd.

## Runtime coinstallation gate (issue17)

The first nine-library development-root installation fails normally at GMP's
C++ dependency: converted cross metadata is not a configured target runtime.
Canonical target GCC8 and native GCC14 runtimes cannot coinstall as different
versions of the same Multi-Arch:same package. No dependency override is used.

The optional runtime assembly mode now builds real tabor-spe-libgcc-s1 and
tabor-spe-libstdc++6 providers for this isolated build root. They contain the
same packaged ELF payload as the canonical GCC8 target packages, keep the real
8.5.0+tabor1 version, own target library paths and their own documentation, and
truthfully Provide the canonical runtime names at that version. Debhelper emits
canonical shlibs dependencies. Native GCC14 remains installed normally. Normal
apt configuration of providers plus GMP and eight other development-library
pairs passes with clean audit. Source/patch/license inputs and payload hashes
remain recorded. Target-archive creation explicitly rejects build_root_only
providers; final-target canonical runtime identities remain unchanged.

Verification compares canonical/provider libraries after normal Debian stripping,
then checks the installed bytes. It also compiles/links C/C++ with defaults and
runs native dpkg-shlibdeps over the target output, proving canonical runtime
Depends from genuine installed owners. No target code executes. An earlier
verification incorrectly compared stripped installed files against raw compiler
files; that check failed and is superseded by the explicit packaged comparison.
Runtime byte identity is not a new runtime or hardware test.
https://www.debian.org/doc/debian-policy/ch-relationships.html#virtual-packages-provides

A failed nested read-only verification mount was followed accidentally by a
queue submission against the previous04aa build root. Its receipts retain that
actual image, with GPM/xxHash/GMP built and four dependencies blocked. Those
results are not claimed as validation of the new root. Subsequent submission
uses the verified image only after checked validation completes; snapshots are
not modified during execution. GPM's known native +b2 counter is selected in its
fresh505 build; the earlier504 was a compile/package check at the source version.

## Remaining dependency wave

Source-pinned xxHash0.8.3-2 is added for LZ4's declared libxxhash-dev dependency.
Normal signed apt source metadata and per-file hashes are retained; library
code is BSD-2-clause with GPL-2+ CLI/packaging and listed exceptions. No upstream
notices are removed. GPM505 and xxHash505 compile/package normally. Installing
those real libraries unlocks the ncurses/LZ4 retries. Libjpeg's second pinned
patch uses the matching existing native Debian tjbench for help2man only when
cross compiling; native builds keep the just-built executable. This preserves
the manual and avoids target execution. Fresh packaging acceptance is pending.

## Binary rebuild changelog correction

GPM505 at +b2 compiles/packages but normal apt rejects its common changelog:
repeating dch --bin-nmu created intermediate +b1/+b2 entries. Debian's normal
shared-file handling removes only the current binary-only entry. No file
conflict, version check or maintainer script is bypassed. The source runner now
uses python-debian's Changelog writer to create one binary-only stanza directly
at the reviewed +bN, appending the original upstream changelog bytes unchanged.
It records the correct cross target in that stanza. Fresh GPM506 packaging
passes; normal coinstallation retry is pending at this note. This same fix
applies to all reviewed +b2/+b3/+b4 builds, rather than patching their outputs.

The launchers now accept --expected-image and reject a mismatching profile
before remote work. The stale-image rejection was checked locally. Submission
still freezes recipes before builds; existing source/output directories are
never overwritten. The closure queue uses a new002 submission because001 had
already been reserved for earlier prerequisite-context metadata.

## Verified follow-up checkpoint

Fresh507 retry finishes all four sources successfully: GPM, libjpeg-turbo,
libpciaccess and libfontenc. The JPEG series now also registers SPE alongside
existing PowerPC32 JNI symbol-availability exceptions. Its existing JAVA_ARCHS
whitelist excludes SPE; strict symbol checking stays enabled and now matches
that feature decision. No broad symbol-check relaxation or target execution
is used. Source GMP506 and PNG506 also pass in the real runtime-managed root.

GPM506 exposed a further source-changelog grammar issue: the newly generated
binary-only block lacked a separator before the preserved upstream header,
so common changelog extraction dropped that header. The writer now guarantees
the separating blank line and parses both versions before building. GPM507
then installs normally beside native +b2 with clean audit, together with actual
xxHash505 development packages. Both failed installation contexts remain on
R730; no force-overwrite or package-data edits were used.

All15 selected latest source outputs pass static package-hash/ELF inspection:
67 package artifacts,69 ELF files, all ELF32/big-endian/PowerPC, no ELF in
independent data packages. This is architecture/payload evidence, not a new
ABI runtime or physical test. Canonical/provider installed runtime bytes and
C++ dependency generation pass separately. JPEG/PNG/PCI/font development
packages also install normally into the next isolated build root.

Next constrained serial queue: LZ4 and ncurses508, with their actual xxHash/GPM
prerequisites installed. Full Essential/desktop closure, normal-feature libc,
new graphical image and A1222 hardware acceptance remain pending. Additional
providers/themes and target runtime tuning are not expanded in this slice.

## GNU/SPE feature-test follow-up (issue18)

LZ4-508 compiles/packages and its runtime/development pair installs normally.
Ncurses508 reaches substantial narrow/static/C++ compilation but wide C fails
with wcwidth undeclared. Its cf_cv_system_name is linux-gnuspe; the GNU/Linux
case lists other GNU ABI variants but omits gnuspe. The generic fallback loses
normal X/Open feature exposure. Pinned ncurses patch adds linux*gnuspe to that
existing case in aclocal.m4 and configure. It does not inject caller flags,
relax diagnostics or disable wide characters. Fresh ncurses509 verification is
running on R730, followed by zstd509 now that its actual LZ4/LZMA/zlib development
dependencies and native package-note tool are installed. Acceptance is pending.
