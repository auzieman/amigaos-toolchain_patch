# Debian-first powerpcspe build contract

User direction, 2026-11-01: this is a Debian Trixie source rebuild for the
A1222's powerpcspe ABI, founded on our patched compiler, runtime and board
support. Above that foundation, normal Debian packaging and dependency
semantics govern the system. AlpinE/A1222 tools join the same process as packages.

## Authority and ordering

Debian source Build-Depends/Build-Depends-Indep/Build-Conflicts, architecture
restrictions and build profiles define build readiness. Binary Depends and
Pre-Depends define installation ordering. These are different graphs; kernel,
compiler and libc bootstrap stages can also contain genuine cycles.

Use Debian apt/build tooling to resolve dependencies in clean build roots;
use dpkg-checkbuilddeps and normal dpkg-buildpackage/debian/rules to enforce
readiness. The current JSON package list is an intake/recipe allowlist, not a
dependency solver or authoritative build order. Do not build a replacement
resolver from directory contents, smoke results or a manually sorted list.
A file in a sysroot does not satisfy a build dependency's installed-package state.

Native build-host tools, target development packages and the final target root
have separate roles. Resolve architecture/version/profile-qualified dependencies
in the appropriate environment; never satisfy a target library by pointing at
an x86 library or inventing an installed record. Shared-library bootstrap
mappings name actual required packages; they do not prove those packages are
installed in the eventual system.

## Transition from bootstrap to normal package building

1. Pin and validate patched compiler/binutils, Linux headers and bootstrap libc.
   Current compiler is corrected GCC8.5; modern GCC restoration remains separate.
2. Index produced real packages and their sources in a private apt repository
   with architecture/version identities and provenance. Retain bootstrap/full
   distinctions and publish only verified artifacts. Configure repository trust
   deliberately rather than globally disabling apt authentication.
3. Establish clean Debian build roots with the required native and target
   development packages managed normally. Use standard apt/sbuild mechanisms
   for dependency installation and build scheduling, with the patched compiler
   packages selected explicitly. The current isolated runner is bootstrap
   infrastructure, not yet a completed sbuild/apt dependency service.
4. Resolve each source's actual dependency closure. Break necessary bootstrap
   cycles with supported/reviewed profiles, retain the intermediate evidence,
   then rebuild required full-feature packages after the cycle is closed.
   Existing stage2 libc is an intermediate and requires a normal-feature rebuild.
   A nopython build does not provide the omitted Python binding package.
5. Assemble the target through real Debian package installation/configuration:
   maintainer scripts, triggers, Essential assumptions, permissions, accounts,
   init/service state, PAM, D-Bus and package databases survive reboot normally.
   Image size is controlled by package selection, not by bypassing package setup.
6. Package our tooling with normal Build-Depends, Depends, conffiles and service
   definitions, compiled against this same target foundation. Add it after its
   dependencies are available. Hardware acceptance, measured tuning and then
   the AlpinE port remain the agreed sequence; Flatpak is excluded from this target.

## Patch and validation policy

Keep changes at the component where a demonstrated architecture/compiler/ABI,
board or cross-build compatibility failure occurs. Preserve Debian feature and
hardening defaults. Treat current TABOR_SYSROOT/shlibs/transport adjustments as
bootstrap accommodations to retire when normal package-managed build roots
provide that state; do not replicate them indefinitely across the archive.

Compiler/runtime ABI regressions, selected package tests, final boot/session/GL
checks and real hardware tests establish acceptance. Repeating bespoke probes
for every otherwise ordinary source package is not the dependency scheduler.
Retain useful failures and patch provenance without requiring a custom API test
before Debian can compile an unrelated dependency-ready package.

## Current gap and next concrete gate

We have normal .deb artifacts and useful QEMU runtime checks, but no accepted
fully configured Trixie target root and no complete package-managed cross-build
root/repository. Source inspection shows the next dependency closure is wider
than the recent library batch:

- libselinux needs libsepol-dev and libpcre2-dev, plus its selected language/tool
  dependencies. Built libraries alone do not make those dependencies installed.
- audit additionally needs libcap-ng-dev, Kerberos, LDAP (unless the supported
  profile excludes it), libwrap, Linux headers, swig and selected Python tools.
- libcap2 needs PAM development files, patchelf, gperf, indent and debhelper;
  architecture-only builds omit its independent Go build dependencies.

Fresh-source preflight now reports Debian's actual unsatisfied dependencies
without compiling or suppressing checks. Use those results to prepare the
repository/build root and bootstrap closure before scheduling these sources.
Keep fenv rounding (#3), session rendering (#8) and physical board gates visible.

Target architecture scope (user correction, 2026-11-01): source/package builds
are powerpcspe only. Use existing Debian host binaries for scripting and build
orchestration; do not expand target dependency work into rebuilding amd64 libc
or other native counterparts. Keep host compiler tooling outside the target
archive. Cross-compilation has a host and a target, but this is not a multi-target
archive rebuild. Resolve target dependencies in the target environment.
