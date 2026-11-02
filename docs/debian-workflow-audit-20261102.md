# Debian workflow audit — 2026-11-02

The user's concern is supported by the implementation: using normal
`dpkg-buildpackage` and dependency checks did not by itself make our surrounding
build process equivalent to Debian's package builders. Several shared failures
were infrastructure mistakes, rather than unavoidable work for every ported
package. Keep the useful compiler/source fixes and verified binary outputs;
replace custom dependency management with standard Debian mechanisms.

## Documented reference

* [Debian CrossCompiling](https://wiki.debian.org/CrossCompiling): use a package
  build tool for cross builds; a native-build architecture and target/host
  architecture are distinct roles.
* [Trixie sbuild manual](https://manpages.debian.org/trixie/sbuild/sbuild.1.en.html):
  disposable build environments, apt dependency resolution and local dependency
  packages through `--extra-package`; cross builds select the host architecture.
* [Trixie sbuild configuration](https://manpages.debian.org/trixie/sbuild/sbuild.conf.5.en.html):
  documented per-port CROSSBUILD_CORE_DEPENDS for actual compiler/runtime inputs.
* [Trixie mmdebstrap manual](https://manpages.debian.org/trixie/mmdebstrap/mmdebstrap.1.en.html):
  a native buildd root contains Essential packages, apt and build-essential;
  its tarball can be used by sbuild's unshare backend.

## Actual gaps and corrections

| Area | Previous behavior | Correction / gate |
| --- | --- | --- |
| Dependency installation | Check-only preflight in a fixed root, then hand-managed library batches | Let sbuild/apt install actual Build-Depends from repositories/local package inputs |
| Accumulation | Either no feedback or an increasingly populated permanent root | Accumulate verified artifacts in the package pool; recreate each build environment and resolve its requirements |
| Native tools | Hand lists, then a broad native build-dep superset | The broad cache is not target readiness; the per-source resolver owns native/target-qualified requirements |
| Source planning | JSON allowlist / names from diagnostic strings | Intake/provenance only; neither is the authoritative dependency solver or a complete graph |
| Bootstrap cycles | Incremental special roots and omitted-feature builds | Explicit supported profiles, recorded missing outputs and required full rebuilds; review rebootstrap for genuine new-port bootstrap stages |
| Source changes | Git-applied patch series around a direct build | Retain pins, then package reviewed fixes as reproducible Debian source changes for the standard builder |
| Installed state | Some historical payload assembly / bespoke shlibs accommodation | Real packages and normal dependency, configuration, script and trigger behavior; no invented installed records |
| Failures | Readiness blocks and infrastructure skips mixed in aggregate counts | Separate resolver failure, infrastructure failure, source compile failure and runtime acceptance |

The cumulative-root fix was useful diagnostic/bootstrap work, and it did unlock
findutils/sed. It is not the final architecture of the build service. Do not keep
extending it into another Debian dependency resolver. The 92 source candidates
are a discovery estimate including alternatives, not a list of mandatory source
patches or packages already ready to build.

## Next concrete proof

First rebuild Debian's universal UAPI headers with the existing SPE tuple
registration patch and a proper local source revision, 6.12.113-1+spe1.
Architecture:all header export is not another CPU's kernel/userspace build.
Then run unpatched Debian libxdmcp through sbuild with build=amd64 and
host=powerpcspe. Both use a fresh mmdebstrap buildd tarball, not an old custom
compiler/sysroot image. Supply genuine compiler, bootstrap libc/runtime, UAPI,
libcrypt, libbsd and libmd packages through standard extra-package inputs.
Apt owns dependency selection and installation in each disposable root.

The port-specific core configuration names the genuine packaged SDK, native
cross-binutils and real SPE libc development package. It uses sbuild's documented
configuration; it does not invent a crossbuild-essential package or ignore
Build-Depends. Official Debian mirror indexes are restricted to the architectures
they actually publish; locally built SPE packages enter via the separate
sbuild temporary archive/private port archive. Target builds remain SPE-only;
existing native Debian binaries perform the host tools' role.

Acceptance: successful standard dependency-resolution log, actual target
packaging/.buildinfo/.changes, static ELF architecture check and retained input
hashes. A failure stays a failure; do not patch around the resolver to get green.
The baseline libc is still an explicitly recorded stage2 bootstrap input, so
this proof is not normal-feature libc, full target installation or boot/session
acceptance. Continue the 52-source closure after this foundation is established.

Implementation: scripts/run-sbuild-package.py, scripts/submit-sbuild-package.py
and profiles/sbuild/*.json. The clean native root is retained as
work/debian-buildd-root-001. Native controller tools are Debian sbuild,
autopkgtest, mmdebstrap and uidmap. Builds run unprivileged through unshare,
with local logs and resource limits of 4 CPUs/6 GiB.

The Docker backend experiment exposed a Docker-specific compressed-index
setting incompatible with its temporary local file archive. An isolated test
confirmed that cause without disabling apt's sandbox. The ongoing path uses a
clean mmdebstrap root rather than carrying Docker image configuration forward.

Header source preparation also caught two lab mistakes: the local version must
use an UNRELEASED changelog entry, and Debian Linux requires control metadata
regenerated before automated builds. Its normal validation remains enabled.
Run006 then rejected Python bytecode produced during that preparation; run007
sets PYTHONDONTWRITEBYTECODE for the generator rather than adding generated
binary files to the source package. These are preparation failures, not SPE
compiler failures. Run007 subsequently passed normal sbuild packaging and static payload inspection:
linux-libc-dev_6.12.113-1+spe1_all.deb, with .changes/.buildinfo retained.
The clean SPE libxdmcp proof is now run005; its acceptance remains pending.

The earlier research and bootstrap evidence remain valid. The handoff to
Debian's standard builders should have happened earlier in the desktop stage.
Keep the verified patches, artifacts and failure records; replace the custom
dependency-management path. No USB write or new QEMU session is part of this
workflow audit.

## Port scope

Debian's [ports list](https://www.debian.org/ports/) distinguishes the active
POWER/PowerPC ports from the discontinued powerpcspe port. Trixie officially
releases ppc64el; that is not the A1222's 32-bit SPE ABI. This project revives
powerpcspe against newer Debian sources, using Debian's existing porting and
package-building machinery. It does not require inventing a new packaging
system, and an architecture recognition entry alone does not restore the
compiler, libc ABI or package archive.

## Frozen base: no rolling refresh

User correction: choose a base and stop version drift. The selected base is
Linux6.12.115-2, glibc2.41-12+deb13u4 and GCC8.5.0/SPE SDK8.5.0+tabor5.
profiles/trixie-spe-base.lock.json fixes the Debian/debian-security repositories
at 20261102T220000Z. A new mmdebstrap buildd root is being created against that
snapshot and must pass exact native header/libc version checks. Future sbuild
runs require its matching base-lock hash; no live mirror fallback is allowed.
Historical-snapshot expiry is disabled only on those source entries; archive
signature authentication remains enabled.

Libxdmcp005 resolved pkgconf correctly but exposed the existing root's newer
6.12.115-2 headers: asking for6.12.113-1+spe1 would downgrade them. No downgrade
was forced. Source6.12.115-2 is now cached through authenticated Release/Sources
checksums, with original copyright retained (GPL2 base and per-file exceptions).
The UAPI tuple patch must be checked and rebuilt once against that frozen base.
The successful007 header result remains valid evidence for6.12.113; it does not
claim the selected newer header package or kernel has been built yet.

Builds should accumulate accepted package artifacts from this baseline. QEMU
validation is a separate downstream gate; see qemu-package-validation.md.
