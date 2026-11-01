# Actual Trixie bootstrap increment — 2026-11-01

The goal is a normal configured Debian-source SPE root, not expansion of the
BusyBox diagnostic transport bundles. This is a custom rebuild, not an official
Debian architecture release. QEMU and physical A1222 share the same target ABI.

Completed:

- Captured Essential/required package and source identities from working VM132.
- Serial server-side intake pins attr, acl, tar, bash, dash, coreutils and gzip
  Trixie sources with DSC/payload SHA256. Independent OpenPGP chain verification
  is still not implemented; HTTPS/hash verification is not described as that.
- Normal Debian attr/libattr1/dev/debug/udeb packages build using the same SPE
  compiler and restored glibc sysroot. Package checks remain enabled.
- Dash first fails because native generators inherit target --sysroot through
  LDFLAGS. Local configure.ac/Makefile.am patch separates LDFLAGS_FOR_BUILD,
  retaining native non-cross behavior. Fresh retry builds Debian dash with its
  actual preinst/postinst/prerm/postrm/templates. Its exact built binary passes
  arithmetic, quoting, function, substitution and exit-status smoke in guest010.
  This is runtime only, not an installation or maintainer-script execution pass.
- Glibc restoration patches and new powerpcspe Debian architecture patch apply
  to fresh2.41-12+deb13u4. Actual debian/control generation succeeds with the new
  architecture and explicit unversioned reference SPE compiler name. No GCC14
  version spoofing or target package dependency bypass. Full libc package build
  needs compiler/build-dependency bootstrap and remains pending.

Kernel/root corrections:

Read effective configs, not just seeds: accepted QEMU007 lacks cgroups and
filesystem ACLs, and virtio block is absent because its BLK_DEV menu was not
selected. Added normal-init/session prerequisites to QEMU seed and physical
fragment and assertions after olddefconfig. Started a single4CPU/6GiB fresh
QEMU008 kernel job. Effective post-olddefconfig cgroups/ACL/virtio-block checks now pass. The initial
container inherited the native image sh entrypoint and failed before starting;
replacement explicitly selects python3 and is compiling. Added a reusable R730
kernel submission command with explicit entrypoint and common job exclusion.
Kernel receipt separately determines its final outcome; do not
call a source config request a successful effective configuration or boot.
Physical kernel fragment updated but not rebuilt/tested in this increment.

Normal root storage is a persistent ext4 disk filesystem. QEMU uses virtio
block; A1222 uses USB storage with separate U-Boot FAT files. Current kernel
and RAM-root diagnostics stay available. Debian initramfs tools may legitimately
use BusyBox for early boot; the installed root's Essential tools and package
state cannot be replaced by unsupported applets. No Sandisk or internal disk
was written and no new QEMU guest was launched here.

Remaining: real libc/libc-bin/libgcc binary packaging and target build-dependency
bootstrap; full GNU Essential/apt closure; maintainer scripts configured inside
a target root; disk-root boot/persistence; then VM132 session/E and Radeon gates.
Existing directed-rounding/fenv failure is still open. An actual Trixie root is
NOT yet built or accepted. Source updates/patches are committed for replay,
not applied ad hoc to an accepted root.
