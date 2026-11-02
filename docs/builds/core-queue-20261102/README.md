# VM132-directed core queue — 2026-11-02

VM132's broader application/package collection is the functional target. The66-seed session profile is an intermediate acceptance gate, not a permanent minimal scope. The existing reference inventory records2337 installed packages; architecture-specific packages and unavailable components require explicit review rather than copying amd64 payloads or silently discarding applications. Flatpak remains excluded by the user's earlier direction.

This first expanded pass attempts17 pinned core/data sources. Added ACL, tar, bash and coreutils to the reviewed recipe inputs from the existing source locks. Newly cached/hash-pinned adduser, debian-archive-keyring, media-types, tzdata and ca-certificates sources. The normal source intake still records its independent OpenPGP verification limitation. No vendor/Hyperion payload is imported.

## Fail-forward behavior

`scripts/run-core-build-queue.py` runs Debian's architecture/profile-aware dependency preflight, then builds only dependency-ready sources. A blocked preflight, build failure or timeout is recorded and the next source is attempted. The queue is an attempt list, not a new dependency solver: Build-Depends still decides readiness and apt/installed package state remains the target model. No dependency checks, maintainer scripts or package features are disabled to force progress. Scripting/data-only packages use the existing -A mode with normal tests and must produce Architecture: all; compiled packages remain powerpcspe.

Each item has a fresh iteration101, separate preflight/build directories, complete remote logs and receipts. Successful output is not overwritten. Failed items are also collected in deferred.json for a later fresh pass after fixes/dependencies. This pass does not automatically retry failed items, install packages, index artifacts, boot an image or overwrite USB media.

## Durable R730 execution

- systemd unit: tabor-core-queue.service
- frozen scripts/profiles/patches: /srv/data1/tabor-build/linux-live-001/queues/core-20261102-001/project
- queue input: profiles/queues/core-20261102.json in that snapshot
- live summary: /srv/data1/tabor-build/linux-live-001/work/core-queue-20261102-001/receipt.json
- deferred review: the adjacent deferred.json
- per-source output: work/debian-PACKAGE-preflight-101 and work/debian-PACKAGE-101

The snapshot is read-only and its complete file hashes are retained by the queue. Later workspace edits cannot alter this pass. One container at a time,4CPU/6GiB per package,7GiB outer service ceiling, no build network. Two-hour per-item timeout kills that exact task container before falling through. A stop request records interruption and kills only the active queue container. Output conflicts are retained as failures. A file lock prevents a second queue; manual package submission refuses while the queue service is active. No local compilation or extra viewers were started.

Desktop4 monitor state files follow the current preflight/build. QEMU/noVNC remain stopped after the host reboot; monitor text says so. The server archive007 and previous evidence remain intact.

Actual first-item verification: base-passwd preflight blocked, media-types then built its genuine independent package, queue continued to adduser. That exercises real failure continuation and successful builds without a synthetic bypass. Full-pass results are retained in pass001.json and pass002.json. Essential/desktop dependency closure and a normally configured target root remain unfinished.

Pass001 completed all17 attempts:2 source builds succeeded (media-types/adduser),15 were blocked by their actual Debian build dependencies. The queue did not stop on any blocked item. It retained the complete pass/deferred summaries. Three scripting/data sources need host tools only: archive-keyring needs jetring; ca-certificates needs python3-cryptography; tzdata needs python3-debian/natsort/polib. Infrastructure012 installs those normal host packages before retrying those three in a fresh pass. Target-library gaps remain deferred rather than satisfied by host libraries.

Pass002 retried the three host-tool failures against pinned infrastructure012. All three sources built normally with upstream tests enabled. Across both passes:5 successful new source builds,12 sources still dependency-blocked. The latest unresolved list is remaining-deferred.json; raw original failures remain retained. No compiled source was forced past missing target development dependencies. Neither pass leaves an active build after completion. Service execution survives editor closure; a server reboot requires a fresh pass from retained results rather than an implicit resume.

Reviewed successful outputs from both passes were explicitly indexed into signed archive008: 48 binary artifacts (previously42). Signature validation and selected-library APT simulation pass. The minimum Essential/desktop simulations still fail, so no configured root or boot acceptance is claimed.
