# Diagnostic guest session audit — 2026-11-01

Read-only inspection of software-e011, not a new package-managed Trixie image.

- `/proc`, `/sys`, devtmpfs `/dev` and devpts `/dev/pts` are mounted.
- `/dev/null`, `/dev/zero`, `/dev/random`, `/dev/urandom` and `/dev/ptmx` exist.
- `/dev/shm` and `/run/user` are absent. The isolated E launcher supplies a private runtime directory, but this does not establish normal Debian login/session setup.
- PID1 is `/bin/sh -i`; this diagnostic RAM root does not run Debian's normal service/session initialization.
- System D-Bus daemon exists; this alone does not validate per-user session services or the full installed dependency closure. `dbus-send` was already found missing.
- Latest isolated E log contains animator epoll timing errors and unavailable DPMS; Xvfb log is empty. The terminal X I/O fatal followed deliberate display shutdown and is not evidence of the original paint failure.

These are concrete base/session gaps, not proof of the rendering root cause. Do not infer a QEMU GPU bug from blank client windows or treat Evas primitive success as complete desktop acceptance. Next gate: preserve normal Debian package configuration and init/login/session setup in the genuine target root, then compare E/Terminology with bounded EFL stderr and pixel readback. Keep the working display1 recording untouched.

Expanded Evas probe004 passed rectangle pixel checks with manual rendering, automatic repaint and ARGB alpha, plus nonblack Molten wallpaper readback. These bypass E compositor/Terminology. Source and target binary hashes are retained in evas-direct-004/build-receipt.json; runtime logs and receipt are adjacent. The private display2 probe stopped without changing recording display1.
