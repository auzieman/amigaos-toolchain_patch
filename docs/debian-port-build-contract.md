# Debian-first powerpcspe build contract

Scope clarification (2026-11-03): profiles/port-build-scope.json bounds active
work to the selected base, X11/E/Mesa and service closure. Broad native build
prerequisite provisioning and source metadata discovery do not authorize an
automatic target web-server/language/compiler port. Build base libraries first
with supported Debian bootstrap profiles as required, then their consumers.
Record omitted outputs and close full-build gates needed by the selected final
binary packages. Keep native tools native and preserve Debian installation.

Current package/desktop entrypoint: [.agents/skills/tabor-debian-port](../.agents/skills/tabor-debian-port/SKILL.md).
The [broad build-server provisioning](builds/port-build-server-20261102/README.md)
retains native tools and downloads on the R730. Each source build starts from
a qualified clean buildd base; sbuild/apt installs its dependencies and honors
Build-Conflicts. Broad provisioning does not mean universally cloning the
installed host-tool superset into disposable roots. Preserve verified source,
apt and target-artifact caches independently of installed package state.
Use authenticated metadata to extend missing producer intake without changing
the frozen baseline. This clarification supersedes the earlier universal
native-template wording; old provisioning receipts remain historical evidence.

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
dependency solver or authoritative build order. Compiled target jobs use
Debian autobuilder-style dpkg-buildpackage -B; separately reviewed independent
scripting/data jobs use -A with native tools. Do not combine optional independent
documentation production into every cross-architecture binary build. Do not build a replacement
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

Build-stage execution clarification (2026-11-02): the x86 build host runs
native compilers, packaging tools and required native code generators. It does
not run the newly compiled powerpcspe binaries as part of cross compilation.
Use Debian's supported cross/nocheck profiles where appropriate and patch
recipes that incorrectly execute target tools. Architecture:all scripting/data
outputs are permitted. Target runtime tests belong to a separately recorded
QEMU or physical A1222 stage; a successful package build does not imply they ran.

The 73-source readiness group is the working scope for the first graphical
candidate, not a numerical acceptance threshold. Acceptance requires the
selected packages' real dependency closure, successful Debian configuration,
then boot, SSH, X11, E and GL checks. Preserve failures and continue independent
dependency-ready sources rather than reducing that closure to meet a count.


Cumulative cross-root update (2026-11-02): opt-in serial queues may install
receipt/hash-pinned Multi-Arch:same SPE libraries into immutable child build
images through ordinary offline apt, with no removals, clean audit and unchanged
native package state. Retry blocked sources after installed dependencies change;
keep compile failures for reviewed fixes and preserve required full bootstrap
rebuilds. Native apt build-dep provides a host-tool superset, never evidence that
a target library is installed. This does not promote outputs to the target
archive or replace the target filesystem's normal package configuration stage.
