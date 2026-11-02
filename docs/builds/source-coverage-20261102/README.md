# Failure evaluation and broader source coverage — 2026-11-02

The17-source queue was a selected core/data pass, not our complete source inventory or a VM132-sized target. It should not have been used as a coverage total. The initial full cache audit verified93 distinct Debian sources;19 had some archived build evidence and Linux has a dedicated kernel route. The other73 sources completed a full dependency-readiness pass. Eight missing core dependency sources were then fetched/pinned, bringing input coverage to101; catalog.json retains the original93-source snapshot. Partial/stage2 build receipts do not establish complete source/feature or runtime acceptance. VM132 has2337 installed binary packages; source and binary counts are different, and full VM132 binary-to-source mapping/closure remains unfinished.

## Evaluation of the12 deferred sources

Each of those12 retained failures is at dpkg-checkbuilddeps, before compilation. This pass provides no new SPE compiler failure evidence. Applying more CPU/ABI code patches is not justified by these errors alone.

| Deferred source | Observed blocker and next action |
| --- | --- |
| acl | libattr1-dev already has a real archive artifact; provide genuine installed target development state in the build root. |
| grep | Same environment gap for the already-built libpcre2-dev. |
| libselinux | Already-built libsepol-dev/PCRE2 dev state plus Ruby/Python/SWIG build dependencies; retain normal language bindings instead of silently disabling them. |
| findutils | Needs the resulting SELinux development package. |
| tar | Needs ACL and SELinux development packages. |
| sed | Needs ACL and SELinux development family; resolve Debian aliases through actual package metadata. |
| coreutils | ACL/attr/SELinux plus GMP/OpenSSL/systemd development closure. |
| bash | ncurses development package plus host texi2html/sharutils. |
| base-passwd | cdebconf/SELinux development closure plus host DocBook tools. |
| dpkg | libmd development state plus zlib/bzip2/xz/zstd/SELinux/ncurses development closure; pkgconf architecture/role must also be satisfied by real package metadata. |
| libcap2 | PAM development closure plus host patchelf/indent. |
| audit | libcap-ng development state plus Kerberos/LDAP/tcp-wrappers and Python/SWIG dependencies. |

Several required libraries were compiled and indexed earlier, but their development packages are not installed in the effective package-aware build environment. A library file in the bootstrap sysroot does not satisfy Debian Build-Depends. The installed cross-libc runtime fixed shlibdeps discovery, not the whole development-package closure. Native host tools must not be substituted for target libraries; missing unqualified dependencies can also expose an architecture-role/package-metadata issue rather than an absent executable.

Highest-leverage correction: establish genuine installed target development dependencies for libattr, PCRE2, libsepol, libmd and libcap-ng; then build/configure ACL and SELinux with their normal dependencies. That opens several core sources together. The initial audit identified missing pins for ncurses, bzip2, xz/zstd, GMP, systemd/PAM/cdebconf and portions of Kerberos/LDAP/tcp-wrappers/Python. The first8 dependency sources are now pinned; the latter language/network dependency chains remain to intake. Source intake/build readiness for those must follow actual Debian source metadata; a larger attempt list alone does not install dependencies.

## Broader inventory/readiness workflow

`scripts/catalog-pinned-sources.py` reads all lock formats, finds cached DSCs, verifies sizes and SHA256 of every locked input on the R730, reads canonical Source/Architecture/Binary fields and links existing receipt-pinned archive builds. This found93 sources with no missing/conflicting input entries. Source hashes are verified; this does not add the still-pending independent source OpenPGP chain verification. Normalized pins are retained in profiles/expanded-sources.lock.json and the raw catalog is adjacent.

The existing serial queue now supports an explicit preflight_only mode and reports dependency-ready sources separately from successful builds and deferred failures. The new73-source readiness pass covers X11 libraries/protocols, desktop services, OpenSSL/curl, Mesa/libdrm, EFL/E/Terminology, SSH and core libraries already cached, rather than only the initial17 sources. New sources use full binary dependency checking; sources that are exclusively Architecture: all use the scripting/data -A mode. This evaluation does not claim those packages compile, install, or run yet.

- service: tabor-core-queue.service
- frozen snapshot: queues/coverage-20261102-001/project under the R730 build base
- queue: profiles/queues/coverage-20261102.json
- live receipt: work/coverage-queue-20261102-001/receipt.json
- complete per-source logs/receipts remain on R730; failed attempts continue to the next source
- one4CPU/6GiB container at a time; no local extraction/compilation, no target installation or USB write

The73-source pass completed normally with70 dependency blocks and3 dependency-ready sources; its receipt is retained in readiness.json. The input archive was48 artifacts; only subsequent reviewed successful builds are indexed, never readiness counts.

Full readiness pass completed all73 sources:70 are blocked by actual Debian dependencies;3 pass readiness (libpthread-stubs, libxcvt, zlib). A separate real build pass202 now attempts those three. This separates dependency satisfaction from compilation and package generation. Readiness did not report any source/patch/compiler failure.

The real build pass202 builds libpthread-stubs and libxcvt. Zlib reaches minizip configure and fails because its Debian rules omit --build/--host, causing Autoconf to attempt a target executable on the host. This is an observed cross-build recipe failure, not demonstrated SPE code generation failure. A version/hash-pinned patch preserves minizip and adds existing Debian build/host tuple variables; fresh retry203 checks application/build behavior.

Source intake additionally cached/hash-pinned8 missing Debian dependency sources (bzip2, xz-utils, libzstd, ncurses, gmp, systemd, pam, cdebconf); none overlap the original93. Total pinned cached coverage is now101 sources, still not full VM132 closure. The original93-source catalog remains an honest pre-intake snapshot. The retry queue also attempts the eight new dependency sources, with normal preflight and failure continuation.

Active dependency build pass: service tabor-core-queue.service, frozen queues/dependency-build-20261102-001/project, receipt work/dependency-build-20261102-001/receipt.json. This is a separate9-source build/retry pass (zlib plus8 newly pinned core dependency sources), not a claim that all73 sources built. Final/checkpoint results must state which attempts have completed.

The9-source dependency pass203 completed:7 dependency blocks, zlib link failure and GMP packaging failure. GMP compiled its C/C++ libraries and reaches dh_shlibdeps, which finds /tools/powerpc-linux-gnuspe/lib/libstdc++.so.6 but no owning Debian dependency metadata. This strengthens the foundation gap: real target libgcc/libstdc++ runtime/development packaging is required, not an invented shlibs entry. Existing tests/private runtime files do not provide those packages. This is a packaging failure after compilation, not evidence of a bad SPE instruction.

Zlib203 passes the corrected cross-configure step, then miniunzip lacks a link-time dependency on libz in the uninstalled source tree. The sibling minizip already links -lz; patch0002 gives miniunzip the same explicit dependency without adding RPATH/sysroot/package-database workarounds. Fresh204 retry checks both patches. No native counterpart source build was performed; equal native build/host tuple behavior is inferred from the patch, not separately tested.

Priority is now explicit: finish genuine compiler-runtime packaging (libgcc/libstdc++), install actual already-built target development packages through Debian's package machinery, then close the missing target dependency source chain. The larger source inventory/readiness audit is planning evidence, not a replacement for that work.

Zlib204 compiles/packages with the first two fixes, but its upstream Debian rules unconditionally run target self-tests on x86 and ignore the resulting Exec format errors even with nocheck requested. This is NOT a runtime test pass. Patch0003 makes the recipe honor explicitly requested DEB_BUILD_OPTIONS=nocheck while preserving normal native test behavior. Fresh205 verifies the final patch series; target runtime tests remain pending.

Final zlib205 builds genuine Debian target packages with all3 ordered/hash-checked patches. Its full build log contains no target Exec format error; the requested nocheck option is respected. Source compilation/package generation pass; target runtime tests are explicitly not run. Successful libpthread-stubs202/libxcvt202/zlib205 receipts are retained for explicit archive indexing, while GMP203 remains failed at missing libstdc++ package metadata. All build queues have completed.

Reviewed libpthread-stubs202/libxcvt202/zlib205 output is indexed in signed archive009: 57 artifacts, previously48. Signature and selected-library checks pass. Full minimum Essential/desktop closure still fails, so there is no new configured target root or boot image. All queues in this increment completed.
