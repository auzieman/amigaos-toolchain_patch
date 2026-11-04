# Next dependency-chain pass — 2026-11-04

Completed rounds013 and016 produced16 inspected source builds /60 debs.
See prior-results.json for exact retained receipt and inspection hashes.
On the same original32-source request set,29 remain deferred; libgcrypt20,
libXt and libVNCServer cleared. The displayed35 includes six additional
Python prerequisites and is not a regression from32 to35 original consumers.

The shared native cache prefill also ran in production: round016's base wave
verified116 newly cached native archives and reused52, with status cached.
No new source/compiler version was selected.

## Reviewed changes for017

* Actual systemd stage1 dose conflict: native libcap2 is
  1:2.75-10+deb13u1+b3, while SPE libcap2 lacks the binary revision.
  Request standard sbuild binNMU3, matching the frozen native package for
  Multi-Arch:same coinstallation. This is not an architecture or source override.
* Actual python3-defaults build called rst2man after nodoc removed its
  python3-docutils build dependency. Remove that optional profile and preserve
  normal Debian helper dependencies rather than adding a consumer workaround.
* Frozen cdebconf explicitly supports pkg.cdebconf.nogtk in both control and
  rules. Select its text/client-library slice for base-passwd; optional GTK
  installer frontend is unselected. Its rules explicitly preserve the identical
  development-header contents under this profile.
* Acquire/register the complete immediate chains: libxmu for Xaw/X11 keyboard
  tools, xft for Tk/BLT/Python, lmdb and libev/libverto for Kerberos/audit/SSH/curl.
  All five source sets match hashes/versions in authenticated frozen metadata.

The first intake request incorrectly named the Xft source libxft; the frozen
metadata guard rejected it before any download/build. Corrected to canonical
Source: xft from the binary index. The intake error now names unknown producers
and directs review to that Source field. Three CLI regression tests passed.

Round017 runs the full selected scope with scoped dose audits, persistent source
and native package caches, ordinary apt/sbuild dependencies and max4 bounded
4-CPU/6GiB workers on R730. Laptop receives only bounded control/evidence work.
Compilation, install-state, GIR/full-glibc and QEMU/physical acceptance remain
separate gates; these configuration changes do not establish a new remaining
count or a ready boot image.
