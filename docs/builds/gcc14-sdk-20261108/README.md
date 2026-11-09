# Full GCC14 SPE SDK build — 2026-11-08

User requested a fresh GCC14 Debian build set alongside GPU work. Existing
sbuild plans still select GCC8.5+tabor6; submitting them unchanged would not be
a GCC14 rebuild. The prior GCC14 C-only/headerless bootstrap cannot supply the
selected desktop's C++/threaded/shared runtime requirements.

Started `tabor-gcc14-sdk-20261108-001` on R730, four CPUs/6GiB, network disabled,
using the digest-pinned tools image in launch-receipt.json. Baseline SDK/root,
patched GCC source and compiler, glibc source and UAPI are mounted read-only.
The previously successful glibc-gcc14-002 output is copied with reflinks into a
private directory before installing its libc into a new sysroot. Fresh GCC14
configuration enables C/C++, POSIX threads and shared runtimes; requested
outputs include libgcc, libstdc++ and libatomic. Source/component baseline is
profiles/trixie-spe-sdk-candidate.json, not a new upstream release.

`build.sh` records build and staging commands. No target tests run inside that
cross-compilation step. The separate bounded systemd service
`tabor-gcc14-sdk-followup-20261108` waits for completion, then compiles the existing
C/C++ ABI probes against the staged SDK and runs them separately with e500v2
QEMU. It retains compile logs, each exit/output, and qualification.json. Existing
QEMU fenv discrepancies remain explicit; a failed probe is not suppressed.

R730 evidence directory:
`/srv/data1/tabor-build/linux-live-001/work/gcc14-sdk-20261108-001/`

This checkpoint starts a full SDK foundation build, **not yet the Debian
workstation package batch**. Next acceptance is runtime/relocation qualification,
genuine SDK/runtime Debian packaging, and a qualified clean sbuild root selecting
that exact package. Then normal Debian readiness governs the selected desktop
closure. Neither accepted base lock nor active package plans were silently changed.

Long-term delivery remains a pinned container entrypoint invoking Debian's
package builders and apt/dpkg image assembly with persistent verified caches,
resource bounds, pinned source/patch inputs and separate runtime/hardware gates.
The current container is the foundation stage of that pipeline, not a claim of
an end-to-end distribution builder already completed.
