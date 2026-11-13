Current requirement: GCC14 throughout target compilation and final artifacts.
Check profiles/compiler-policy.json first. Do not use GCC8 as a fallback or reuse
its packages as compiler-qualified final output. Prioritize the installed Debian
base (console, dpkg/apt, init/devices, network/SSH); software X/E follows.

Use $tabor-debian-port. Continue the frozen Trixie powerpcspe workstation port
on the R730. First reconcile the last completed round, active jobs, accepted
artifacts and grouped blockers with the actual submitted input hashes. If the
last round made no progress, diagnose the shared blocker before resubmission.

Use standard Debian cross-build mechanics and clean disposable buildd roots,
with broad persistent download caches and real target package artifacts.
Provision native tools on the server without forcing the whole installed
superset into every root. Let sbuild/apt honor each source's dependencies and
Build-Conflicts. Qualify environment changes through the real sbuild namespace,
cache and cross-resolver path and representative builds before a broad batch.

Once qualified, build up to four independent ready sources, retain failures
and continue other ready work. Use frozen Debian metadata for missing producer
intake and supported bootstrap profiles. Preserve required full rebuilds,
normal package setup and the powerpcspe ABI. Report new accepted outputs and
shared blockers, then advance apt-installed image and QEMU validation when
its actual closure is ready. Do not treat retries or source counts as success.
