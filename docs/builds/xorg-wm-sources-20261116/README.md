# Source lock for unaccelerated Xorg, twm and xterm on powerpcspe (#42) — 2026-11-16

## What this adds

`profiles/xorg-wm-sources.lock.json` locks 13 Debian trixie sources that no earlier lock has. They are needed to build Xorg (modesetting, AccelMethod none), Mesa's softpipe build, evdev input, twm and xterm for powerpcspe:

| source | version |
|---|---|
| apr-util | 1.6.3-3+deb13u1 |
| libepoxy | 1.5.10-2 |
| libglvnd | 1.7.0-1 |
| libunwind | 1.8.1-0.1 |
| libutempter | 1.2.1-4 |
| libvdpau | 1.5-3 |
| libxres | 2:1.2.1-1 |
| libxv | 2:1.0.11-1.1 |
| lua5.4 | 5.4.7-1 |
| xcb-util-renderutil | 0.3.10-1 |
| xcb-util-wm | 0.4.2-1 |
| twm | 1:1.0.10-1 |
| xterm | 398-1 |

Existing locks are not changed, because build receipts pin their hashes.

## How the versions were chosen

`scripts/lock-snapshot-sources.py` (new) runs in the frozen build root (`20261102T220000Z` snapshot) with that snapshot's `deb-src` lines added. It reads each version, size and SHA256 from apt's signed Sources index, downloads every payload and re-checks its hash. So each locked version is the one whose amd64 binaries the build root installs, which Multi-Arch: same coinstallation needs. The URLs point at the snapshot, so they keep working after trixie point releases.

## How the source list was found

`srcclosure.py` (replica-local helper, kept here as evidence) walks Build-Depends from `mesa xorg-server xinit xserver-xorg-input-evdev xterm twm`:

- Arch qualifiers are evaluated for powerpcspe.
- `<!nocheck>` alternatives are dropped, since the runner builds with `cross,nocheck`.
- `:native`, `Architecture: all` and Multi-Arch foreign/allowed packages are skipped, because they come from the build host.
- Sources already built for GCC14 powerpcspe are left out.

`closure-depth4.txt` is the result four levels deep. It lists 41 sources: these 13 new ones, and 28 that are already locked but not yet built (for example nettle, pixman, libxfont, lm-sensors, wayland, dbus).

Limits:

- The walk follows only Build-Depends. Runtime Depends of the target packages, and binaries a source build disables per architecture, show up only when sbuild runs.
- The first package-level `pkgconf`/`pkg-config` entries are host tools.
- The dbus → apparmor → apache2 → apr-util/lua5.4 chain is real for Debian's dbus. A build profile may cut it, which would make apr-util and lua5.4 unnecessary.
