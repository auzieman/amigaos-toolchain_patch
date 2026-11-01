# Debian dependency readiness — 2026-11-01

Read the [Debian-first contract](../../debian-port-build-contract.md).
Four fresh hash-locked source preflights ran on R730 using the same pinned
native image, corrected compiler and architecture/profile inputs as normal
builds. Each invokes dpkg-checkbuilddeps directly; no compilation or dependency
installation is performed. The ready/blocked classification is Debian's result,
not a custom graph solver or assertion based on sysroot files.

- libselinux: blocked on target sepol/PCRE development packages and selected
  Python/Ruby/native tool dependencies.
- audit: blocked on cap-ng, Kerberos, LDAP, libwrap development packages and
  selected language/native tools.
- libcap2: blocked on PAM development files, patchelf and indent.
- libcap-ng with supported nopython profile: dependency-ready, not rebuilt.

Exact unmet expressions and profiles are in summary.json and per-source raw
logs/receipts. Blocked containers exit nonzero and retain blocked status; the
known-ready control exits0 with build-dependencies-satisfied-not-built. Neither
status claims package installation, compilation, runtime or root acceptance.

Next: establish real repository/build-root dependency state using normal Debian
apt/sbuild mechanisms, including correct host/target roles and required bootstrap
profiles/cycle closure. Built .deb files alone are not installed Build-Depends.
This report captures full selected cross,nocheck source requirements (arch-only);
standard nopython/noruby/etc profiles can be used deliberately where appropriate,
with omitted outputs/features and required follow-up builds recorded.
