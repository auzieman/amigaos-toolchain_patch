# Producer-chain repair, frozen Trixie SPE

Round012 ended with 32 unique deferred sources (41 phase entries). These are
dependency/foundation gates, not 32 demonstrated compiler failures. Six source
builds produced 22 inspected debs; this does not imply an installed target image.

The earlier intake pattern depended on the first missing relation reported by
dose. That repeatedly exposed another prerequisite only after an incremental
build. Keep dose/apt authoritative for readiness; review complete declared
producer chains before intake instead.

## Reviewed repair

Thirteen additional source sets were acquired with frozen metadata size/SHA256
verification and the explicit exact-file CDN cache transport. Versions, compiler
and baseline lock remain unchanged. Sources accumulate in closure-source-cache-003.

| Chain | Newly registered producers | Selected consumers |
| --- | --- | --- |
| Crypto/device management | libgpg-error, iptables, libmnl, libnfnetlink, libnetfilter-conntrack, libnftnl, kmod | libgcrypt20, systemd/udev, DRM, Xorg, Mesa, PAM/coreutils |
| Authentication | cyrus-sasl2, openldap | Kerberos, audit, SSH, curl, D-Bus |
| Account setup | libdebian-installer | cdebconf, base-passwd |
| Remote graphics | lzo2 | libVNCServer, x11vnc |
| Cross-development metadata | architecture-properties | Genuine cross-exe-wrapper dependency of GLib development tools; no target execution claim |
| Target Python library | python3.13 | python3-defaults/libpython3-dev, ALSA, later introspection |

OpenLDAP's existing pkg.openldap.noslapd profile builds client libraries without
the unselected LDAP server. SASL's declared noldap/nogssapi/nosql profiles break
the client-library cycle; omitted optional authentication plugins remain outside
this slice. Python uses declared cross/nocheck/nodoc semantics and native
generators stay native. Target Python/defaults are now justified by ALSA's
actual Build-Depends; the previous target-language deferral is removed for that
specific prerequisite.

The intake CLI accepts an explicit reviewed source-to-reason manifest, bounded
by the producer allowlist and frozen Sources. This is intake, not a dependency
solver: it neither declares readiness nor invents binary packages or installed
state. It can retain prerequisites hidden behind the solver's first reported
failure, including sources already present in an inventory but not selected
for builds. Candidate-Sources now includes every requested intake component.

## Evidence and limits

cache009 and cache010 receipts/locks record six plus seven verified source sets.
Actual frozen intake completed for all thirteen. Three synthetic CLI regression
checks cover pinned versions, hidden/already-listed sources, rejection of unknown
sources and rejection outside the reviewed scope. Python compilation and diff
checks passed. Synthetic tests are not Debian archive authentication evidence.

Round013 requests the complete selected pipeline, including the producer chains,
using the qualified clean buildd root and up to four ready 4-CPU/6GiB sbuild jobs.
Source caching and submission are not compilation acceptance. Retain actual
build receipts before claiming these consumers unlocked.

Remaining explicit gates include native/target GIR generator handling without
unreviewed target execution, full restored glibc source packaging, actual binary
dependency closure/maintainer scripts, QEMU desktop painting and physical
A1222 CPU/RAM/Radeon validation. No new image is accepted here.

## Qualified audit scheduling repair

Found another repeated cost: every stage and every four-job wave audited the
entire source inventory and all unrelated profile groups. The audit now accepts
an explicit source request list while retaining the entire verified native/SPE
binary dependency pool. Stages request only their pending sources; later waves
omit already-attempted sources, and empty stages skip unnecessary solver work.
Debian dose still supplies installability and sbuild/apt still installs packages.

Five representative sources (ready and blocked, including distinct profiles)
had identical readiness and selected binary installation sets when queried
against the same retained full-audit indexes. A real invocation of the changed
CLI processed exactly its two requested sources/two profile groups. See
source-subset-equivalence.json and scoped-audit-cli-receipt.json. This qualifies
the source-request boundary, not every future package build.

Python's reviewed prerequisite intake also completed: gdbm, libnsl, libtirpc,
blt and tk8.6 are now registered. rpcsvc-proto source was cached for inspection
but is NOT queued as a target rebuild: the native generator remains native.
Thus eighteen additional target producer sources are registered in total;
nineteen source sets were cached. The selected request inventory is now88
sources; that is not the number of unresolved original workstation consumers.

Round013 is running the thirteen-producer repair with four actual sbuild jobs
observed (architecture-properties, cyrus-sasl2, kmod, libdebian-installer).
Round014 is explicitly queued after013, carrying the scoped audit scheduling
and five additional Python prerequisites. It reuses accepted results and does
not overlap package workers. Source compilation and final gap reduction must
be reported from subsequent receipts, not these configuration changes.

## Close the remaining native acquisition gap

Round013's first four real jobs produced three successful source builds:
cyrus-sasl2 eight debs, libdebian-installer three, architecture-properties three.
Their inspected receipt hashes are in round013-first-passes.json.
Kmod stopped before compilation on frozen scdoc_1.11.3-1_amd64.deb, Snapshot503.

Native cache fill now runs before each opted-in build wave for the native
packages in Debian dose's actual installation sets. Exact package/version/arch
tuples are matched against the retained authenticated NativePackages; custom
SDK and SPE binaries do not get replaced by native archives. Verified files
are reused without network. Missing files try exact-file CDN then the same
pinned Snapshot file with bounded attempts and SHA256 verification. The native
cache is persistent; ordinary sbuild/apt still installs packages and manages state.
If network acquisition remains partial, normal apt can still attempt its frozen
source. An integrity/provenance failure stops the batch instead of publishing
bad bytes. This is not a live apt mirror or a version change.

Three additional native-cache regressions passed: verified reuse without any
network call, failed-CDN recovery through the same Snapshot file (discarding
the failed partial), and rejection of wrong-hash bytes. The real failed scdoc
artifact was recovered/verified into the shared pool (native-prefetch-proof.json).
The automatic whole-wave integration is requested in round016, not yet accepted
as a completed batch result.

Round014 was cancelled while waiting, before any package worker started; its
prior receipt is retained. Round015 submission failed safely before starting a
controller (reserved unit and existing immutable snapshot). Also tightened
predecessor matching to the actual --output argument: a waiting controller's
--after-receipt reference must not be mistaken for its own run identity.
Round016 is now queued after013 with native cache prefetch, scoped audits and
the Python prerequisite group. Round013 workers were not stopped.
