# R730 restart and next Debian port batch

The R730 rebooted cleanly and retained source caches, packages and completed
jobs. The native provisioning pass completed for108 selected source groups:
provisioned-root001.json records clean apt/dpkg, frozen foundation checks,
the template hash and1,278 installed native packages. native-installed001.tsv
retains identities. These are native build prerequisites, not rebuilt SPE
packages or a configured target filesystem.

Cross batch005 completed seven sources: libICE, Oniguruma, libunistring,
db-defaults, libidn2, ruby-defaults and slang2. batch005.json retains successes
and two failures. The reviewed metadata inventory includes35 initial producer
candidates plus six further cached producers: db5.3, newt, p11-kit, popt,
ruby3.3 and tcltk-defaults. The frozen compiler/base remains unchanged.

FUSE3 3.17.2-3 compiled its library and examples but memfs_ll lacked libatomic
linkage for64-bit C++ atomics. The version/hash-pinned patches/fuse3 series
performs a compile/link-only probe and links libatomic when required, preserving
the example. Issue23 tracks acceptance; the patch is under rebuild. Java-common
0.76 has no SPE default JRE/JDK selection and produces invalid empty version
substitutions. Native Java tools are provisioned; target Java defaults remain
deferred rather than selecting an unverified new target JVM.

Retry006 hit the6GiB worker limit while unpacking the5.66GiB template into
host /tmp tmpfs, before compilation. Retry007 moved to disk but its temporary
path crossed the private0750 project parent; mapped-user traversal failed.
The final temporary area is /srv/data1/tabor-sbuild-tmp on the data filesystem,
with normal1777 temporary directory permissions. Private project permissions
remain intact. This uses sbuild's documented unshare_tmpdir_template instead
of raising memory limits. Both retries are infrastructure failures. Failed
child-unit journals are now retained with controller logs.

Cross batch008 plus independent batch003 use disk-backed roots. One SPE worker
and three data workers keep the total at four, each4 CPUs/6GiB. Initial jobs:
FUSE, xkeyboard-config, fonts-dejavu and xorgproto. All reached disk extraction;
the FUSE worker used about1.9GiB at that checkpoint. No final result is implied.

Independent jobs use a separate Debian dose audit with native host=amd64,
nocheck and Build-Depends-Indep semantics, followed by sbuild -A. Outputs must
be Architecture:all without ELF payloads. This admits universal scripts/data,
not an amd64 distribution rebuild. The batch also includes xtrans, xcb-proto
and Sphinx; indep-audit001.json retains the audit.

Validation: Python syntax and git diff checks pass; FUSE source preparation
passes normal git/quilt checks on the server. New packaging, normal target
configuration, QEMU painting and physical A1222 gates remain pending.
