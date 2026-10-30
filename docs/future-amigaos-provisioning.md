# Deferred AmigaOS provisioning environment — 2026-10-30

User suggested Kyvos v2 / QEMU Pegasos 2 as a future SDK/application test
machine, with existing installation ISOs reportedly on the Seagate drive.
Deferred consideration only: no disk search, mounting, media copying, purchase,
download, guest provisioning or boot was performed.

## Verified primary reference

George Sokianos's Kyvos v2 page:
https://ko-fi.com/s/5ce4b719ed

The author describes a QEMU frontend for AmigaOS 4, MorphOS and AROS; a wizard
locates/downloads dependencies including QEMU and 7zip. The displayed 2.2.0
changelog documents kickstart archive creation/editing for AmigaOne XE/Pegasos 2,
optional driver integration and separate Sam460 handling. This supports keeping
Kyvos in the evaluation plan, but does not independently verify the supplied
workshop's exact full-automation/update sequence or comparative performance.

User-supplied workshop references, not independently retrievable this session:
- https://os4coding.net/forum/amiwest-2026-ai-workshop-presentation-and-notes
- https://www.youtube.com/watch?v=p2t6b83ZHOY
- https://www.youtube.com/watch?v=TEayILCZEYE&t=28

Workshop claims to verify when needed: recommended Pegasos 2 target, exact
7-Zip/mkisofs requirements, unattended partition/install workflow and official
update order. Do not present “optimal” performance/stability as measured here.

## Place in the toolchain project

A Pegasos 2 AmigaOS guest can support repeatable SDK installation, application
smoke tests and ordinary AmigaOS runtime checks once the matching media, SDK,
QEMU/Kyvos versions and target contract are identified. It is a different
machine target from the A1222/e500v2 SPE system. Passing tests there does not
validate the SPE ABI, SPE instruction execution, A1222 drivers, board firmware
handoff, Linux glibc or real A1222 graphics performance.

When scheduled: identify the exact platform edition and hashes of the supplied
media, review the selected Kyvos manual/version, prepare a new guest disk and
record QEMU machine/CPU/device arguments plus installation/update checkpoints.
Keep original ISOs unchanged and outside Git/container build contexts; use
snapshots for SDK and regression experiments. Record what automation actually
completed rather than assuming the workshop description is an acceptance test.
