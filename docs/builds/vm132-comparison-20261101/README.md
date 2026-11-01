# Live VM132 comparison — 2026-11-01

Read-only QEMU guest-agent inspection of running trixie-smoke-132 on pve1.
Captured actual package versions/states, selected Depends/Recommends, running
services, PAM/Xsession hooks and session state. No reference VM changes.

The reference is a complete Debian session, not merely the same E version.
Our previous six-package state gate was necessary but substantially incomplete.

| Layer | Working VM132 | Current SPE diagnostic image |
| --- | --- | --- |
| Init/device/session | systemd, udev, logind, libpam-systemd | BusyBox PID1/rescue init; manual device/session setup |
| Login | LightDM with Debian PAM stack and common-session | SSH plus direct E launcher; PAM disabled in E build |
| Session environment | Xsession.d establishes/reuses user bus and updates activation environment | Fixed /tmp runtime directory, unset bus address, new dbus-run-session |
| E/EFL features | Packaged engines, loaders, helpers and E modules | Multiple compile-time features explicitly disabled |
| Graphics | Xorg, libinput, GLVND/Mesa EGL/GBM/DRI dependencies | Xvfb/software GL and manual evdev modesetting fallback |
| Desktop services | polkit, UPower, udisks2 running | Missing/disabled services and modules |
| Installation | Individual Debian packages with configured dependency closure | Two custom transport bundles |

The reference X11 engine package depends on EGL/GLES. E and Terminology also
have hard dependencies on Wayland engine libraries even for this X11 session.
Do not discard them merely because the selected desktop session is X11.
Reference session hooks propagate DISPLAY/XAUTHORITY/XDG_CURRENT_DESKTOP to
D-Bus/systemd activation; creating a fresh bus alone does not reproduce this.

profiles/images/vm132-session-baseline.json now defines package seeds and
integration acceptance. Resolve their complete target Depends/Pre-Depends
closure; the seed list is not that closure. Keep the current lean profiles as
diagnostics rather than the desktop baseline. Shell-first boot and one human
user remain compatible with normal Debian service users and login/session setup.
LightDM remains optional for the first console test; its session responsibilities
must still be fulfilled through packaged PAM/login/Xsession.

This comparison does not prove which omission causes black client interiors.
Direct-X tests pass while E-managed clients fail; retain that as a separate
rendering regression until the restored session is tested. No source rebuild,
reference VM mutation or SanDisk write was done in this comparison.

Exclude unrelated VM132 workloads (Samba, CUPS, nginx, modem services) from the
seed list. Preserve relevant package dependencies rather than cloning its full
workstation installation or importing incompatible amd64 binaries.
