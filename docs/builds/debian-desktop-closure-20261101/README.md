# Complete desktop installation gate — 2026-11-01

User correction: use the full normal installation closure of the selected desktop applications as the base. This is a Debian-source powerpcspe rebuild; compact selection does not authorize omitting package setup or dependencies.

The VM132 baseline now explicitly requires installation, session, desktop, graphics, desktop services, remote access, package management, graphics tests and browser groups. Added x11vnc, mesa-utils and netsurf-gtk (the previously proposed compact browser, confirmed in Debian Trixie: https://packages.debian.org/trixie/netsurf-gtk). Midori was mentioned as an example; its availability/portability is not established here. LightDM remains optional; normal login/PAM/Xsession is required even for a single human account.

The archive verifier runs a separate complete desktop apt simulation with Recommends enabled. Its final status follows the desktop gate, not the smaller development-library check. Actual archive005 simulation008 authenticates indexes, passes the selected library closure, and correctly reports desktop dependencies BLOCKED. This archive lacks most desktop and Essential packages; it cannot yet produce a complete transitive target installation plan. No substituted amd64 binaries, invented installed records or target installation is claimed.

## Actual build/dependency results

- Build infrastructure006 installs normal host po4a (0.73-2), pinned image sha256:750dd940c9a5660d694c5b103108127aab8749d15ce771313d6c9339764733f9. Host package maintainer scripts/triggers run normally. No native counterpart source rebuild.
- Debianutils002: fresh source and normal dpkg-buildpackage pass compilation; packaging fails because dpkg-shlibdeps cannot locate target libc.so.6 in its package environment. No successful .deb claimed. Retained build.log is a bounded tail; receipt retains source/toolchain/artifact context. Original full log remains on R730.
- Diffutils001: Debian source Build-Depends preflight passes, not compiled.
- Findutils001: blocked by libselinux1-dev.
- Grep001: blocked by libpcre2-dev.
- Sed001: blocked by libselinux-dev and libacl1-dev.
- Mawk001: blocked by native build tool autoconf-dickey.

These are Debian's actual architecture/profile-aware checks, not dependency satisfaction inferred from extracted libraries. Existing libpcre2 and libsepol packages do not establish an installed cross-build environment.

## Next bounded correction

Establish the common package-aware bootstrap/cross-build environment from genuine compiler/libc/development packages, then install each source's actual Build-Depends through Debian tooling. Retain explicit bootstrap/full-build distinctions. Do not replicate per-package shlibs mappings or suppress checks to make this batch pass. Complete the Essential closure and normal target package configuration before disk-root boot, then resolve/install the complete desktop closure and test E/Terminology contents. No RAM-root patch-up counts as this acceptance.

All jobs ran on R730: image preparation limited to2CPU/2GiB, one package job at a time limited to4CPU/6GiB, apt simulation1CPU/1GiB. Working recording display1 and SanDisk remain untouched. QEMU rendering root cause remains unproven; absent shared-memory/runtime/session setup is a concrete diagnostic-root gap, not yet a verified fix.
