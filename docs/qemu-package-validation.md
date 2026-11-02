# QEMU validation after the base load

Keep target execution out of cross-build jobs. Once a genuine package-managed
SPE base is available, validate accepted package batches in a separate disposable
QEMU guest. Reuse the same accepted kernel/rootfs inputs and record their hashes,
QEMU version, CPU/machine settings and package versions with every result.

## Gates

1. Install each batch through apt from the port archive; preserve normal
   maintainer scripts, triggers and dependency resolution. Retain install logs,
   `dpkg --audit`, `apt-get check` and the installed version manifest. A package
   that unpacks but does not configure fails this gate.
2. Run package-provided autopkgtests where available through Debian's
   autopkgtest infrastructure. Use the QEMU backend once the SPE guest boot and
   control transport are supported; do not claim compatibility before proving
   that integration. Preserve test restrictions, dependency requirements and
   individual pass/fail/skip results. Lack of a test is not a runtime pass.
3. For packages without tests, use explicit relevant smoke tests: executable
   startup/basic operations, library ABI/load probes, service start and a real
   connection where applicable. Test libraries through consumers; do not try to
   execute every installed file. Record exactly which behavior was exercised.
4. At the end of the base batch, boot normally and test proc/dev/sys mounts,
   dbus, user session and permissions, networking and SSH login. Then test X11,
   E, a painted Terminology client interior and the GL demo/renderer identity.
   Package installation success alone does not close the black-window issue.

Run serially on the R730, with bounded resources; no laptop emulation and no
competing heavy build. Initially use batch validation at milestones to avoid
rebooting for every small library. A failed package/test stays recorded while
independent tests continue; dependency failures are distinguished from crashes.
No existing visible QEMU session is replaced until the new image is prepared.

## Promotion and evidence

Retain the tested package batch hashes, package states, raw logs, exit statuses,
serial/kernel logs and graphical captures where relevant. A summary must report
built, installed/configured, tested-pass, tested-fail and untested separately.
Keep the last accepted image unchanged and use a new writable image/overlay for
each validation round. Reuse the existing installation-state audit; it is only
a metadata gate and does not itself run maintainer scripts or establish runtime
correctness.

QEMU results establish emulator behavior. Physical A1222 validation separately
checks boot firmware/USB, both CPUs, usable RAM/MMU, SPE behavior and Radeon/GL.
QEMU timings are not physical SPE performance or Radeon acceleration evidence.

Status: accepted validation direction, pending a complete package-managed base.
No new guest test, autopkgtest integration or hardware pass is claimed here.
