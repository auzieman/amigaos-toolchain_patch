# Remaining workstation closure

Round008 ended with dependency/foundation fallout and no new compiler failures.
Round007's five accepted normal-profile sources remain accepted. The35-source
count includes consumers and required full bootstrap rebuilds, not35 separate
patch requests. All work retains the20261102 frozen baseline and SPE ABI.

| Chain | Producer work | Consumers unlocked / limits |
| --- | --- | --- |
| ELF and GLib | Existing elfutils `pkg.elfutils.nodebuginfod` profile supplies selected libelf/libdw without unselected debug HTTP service dependencies. | GLib with nocheck+noinsttest, then libXt/Xaw/X11 tools; full debuginfod is a follow-up. |
| AppArmor library | Add explicit stage1 C-library bootstrap to Debian control/rules; normal package set unchanged. | Required libapparmor for D-Bus/systemd; full AppArmor remains required separately. |
| System libraries | Frozen libgcrypt20/libgpg-error producer intake; inspect next required kmod relation. Existing systemd stage1 excludes optional full-build dependency chains. | libudev/libsystemd, then libdrm/Xorg/Mesa and full PAM/Avahi/coreutils. Do not equate stage1 with full systemd. |
| Authentication | keyutils -> Kerberos -> audit; e2fsprogs/comerr already built. | OpenSSH, full util-linux and D-Bus prerequisites. |
| TLS/network | libevent -> Unbound library -> GnuTLS -> curl/libVNC. | EFL and its selected desktop consumers. |
| Base account setup | libtextwrap -> cdebconf. | base-passwd; preserve normal maintainer scripts. |
| Audio/introspection | Review real target Python and GIR library/generator requirements in frozen control/rules. ALSA has an explicit target libpython dependency. | ALSA/libsndfile/Harfbuzz; do not fabricate native providers or assume a nonexistent nogir/nopython profile. |
| Foundation/runtime | Register the complete reviewed restored glibc source recipe; retain accepted patched foundation meanwhile. | Full source packaging and fenv/runtime gates remain open. No vanilla glibc substitution. |

Archive acquisition is a separate shared blocker: closure-cache005 failed to
complete json-c/keyutils/libevent/libtextwrap because Snapshot returned errors.
Do not treat this as a package compiler defect, switch to newer sources, or
register incomplete archives. Verified cached files remain retained for reuse.

Execution: round009 recorded the first AppArmor draft source-preparation failure.
After correcting the diff and native package-selection/dry-run checks, round010
is queued after009 with AppArmor stage1 and the existing elfutils profile.
The standard full-scope pipeline schedules all dependency-ready jobs, max4;
no known-blocked consumer is submitted just to fill a worker slot. Crypto intake006
is a separately bounded metadata/archive job. Each actual result, not this plan,
advances acceptance. No new image/QEMU claim is made.

Round010 update: elfutils completed11 inspected debs. GLib can now reach its
GIR wrapper gate; its existing nogir profile is selected in011 for C-library
builds without target execution, leaving typelib/full introspection acceptance
explicit. AppArmor stopped before compilation on native autoconf-archive504.
The retry classifier now preserves acquisition errors outside long summary
tails and rechecks historical install-failure logs rather than freezing a
network outage as an unchanged source defect. Round011 consumes these changes.
