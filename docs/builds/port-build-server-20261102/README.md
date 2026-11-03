# Debian port build-server provisioning

User direction: use the R730's available storage for broad Debian dependency
provisioning and source caching, then run the existing Debian cross-build
recipes. Default skill: [tabor-debian-port](../../../.agents/skills/tabor-debian-port/SKILL.md).

`scripts/prepare-port-build-server.py` clones the hash-verified frozen native
buildd root and uses apt build-dep on each original pinned DSC across the108
source inventory. Independent build dependencies are included in this tools
superset. Native Debian binaries are installed, not rebuilt. Package downloads
are retained. Real apt conflicts remain failures; incompatible sets need
separate templates. Only a complete, audited template receives the normal
build-root acceptance receipt and tarball. Future sbuild jobs still resolve
and install each source's actual SPE development requirements themselves.

R730 service `tabor-port-build-server`, work/port-build-server-001, is bounded
to2 CPUs/4GiB. native-provision001-checkpoint.json is a running checkpoint,
not completion evidence. An initial nspawn /etc/localtime bind prevented
tzdata's normal rename; --timezone=off and dpkg --configure -a restored normal
configuration. Resume preserves prior attempts and retries failures.

`scripts/plan-port-dependency-intake.py` expands source discovery from Debian
dose's missing target relations, including virtual providers, using the
authenticated frozen indexes. producer-intake001.json and producer-plan001.json
record35 candidate producers outside the old list. This is discovery, not a
replacement resolver or build-readiness proof: a solver failure may expose
only one missing relation, so re-evaluation follows accepted package outputs.
Native-helper qualification, bootstrap cycles and compiler-related candidates
still require review. Cached GCC14/defaults source is not a compiler upgrade.

`scripts/cache-port-dependency-sources.py` retains candidate source archives
with frozen Sources checksums in port-dependency-source-cache-001. The cache
service uses1 CPU/3GiB; this is source intake, not target execution or builds.
Original source notices remain in archives; inspect debian/copyright before
modifying/reusing source. The frozen compiler/kernel/libc pins do not change.

Validation: both project skills pass the skill-creator validator on the R730;
new Python scripts compile; real server provisioning has installed dependency
sets for19 source groups at this checkpoint and source caching has begun.
The first planner submission had a CLI hyphen/underscore mismatch, corrected
before successful discovery. No new target image, QEMU desktop acceptance or
USB write is claimed here.
