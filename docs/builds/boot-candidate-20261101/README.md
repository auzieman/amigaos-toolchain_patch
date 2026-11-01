# SPE-only boot-image prerequisites

The new complete Trixie disk-root image is **not ready**. The previous two lab
bundle packages are not a configured Debian Essential system. Preserve that
baseline while completing the genuine target package closure and normal
maintainer-script configuration. No SanDisk write or new noVNC image is claimed.

Verified this increment:

- Linux `qemu-live-008`, Debian 6.12.113-1, boots the existing diagnostic
  initramfs. `kernel-storage-004.json` and `.log` prove two e500v2 CPUs,
  8 GiB configured / 8240288 kB MemTotal, cgroup v2 (`cpuset cpu memory pids`),
  and virtio/ext4 data surviving unmount/remount on a disposable 64 MiB file.
  The 12 GiB container limit accommodates an 8 GiB guest and emulator/initrd
  overhead; execution stays on R730. This is not a Debian disk-root boot.
- `linux-headers-003.json`: Debian's `binary_libc-dev` rule produced
  `linux-libc-dev` 6.12.113-1+tabor1, Architecture powerpcspe. Export only
  PowerPC UAPI and the powerpc-linux-gnuspe include tuple. The source packaging
  patch changes the all-architecture header package to a target-specific one;
  other architectures are not built. Host tools use ordinary installed packages.
- `debian-gzip-004.json`: genuine Debian gzip 1.13-1+deb13u1+tabor1 package.
  `gzip-spe-compile-command.log` confirms SPE/double-GPR/LD128/sysroot flags
  alongside Debian hardening. Actual .deb payload and guest readback hashes
  match; `gzip-runtime-004/receipt.json` proves compression/decompression
  roundtrip against private libc004 under existing system-QEMU. No package
  setup or installation is implied by that execution test.
- `archive-005.json`: signed, receipt/hash-pinned binary archive, **powerpcspe
  only**, 30 .deb artifacts; excludes the host compiler. `apt-check-006.json`
  authenticates indexes and resolves the selected development-library closure
  with host apt operating on an empty target status database. It neither adds
  a foreign architecture nor simulates coinstallation with amd64 libraries.
  `development-closure-final.log` is a solver simulation, not executed setup.

`essential-gaps-final.log` is the remaining installation seed gap. Most of
Essential still needs genuine target packages: base-files/base-passwd, libgcc,
Bash/coreutils, Debian utilities, text/file tools, tar, Perl, dpkg/debconf,
init-system-helpers and account/PAM packages, plus their dependencies. Runtime
and desktop packages follow dependency closure, not this prose list's order.
Seven additional small Essential source inputs are cached and hash-locked in
`profiles/boot-essential-sources.lock.json`; that is intake, not compilation.
The physical-board `tabor-live-002` kernel rebuild is a separate gate.

Retained failures: header001/002 used unsuitable cross-qualified host-tool
preflights; header003 correctly checks the header-export host tool dependencies
as host dependencies. Kernel test001 lacked host mkfs.ext4; test002 required
an absent diagnostic awk applet; test003 assumed cgroup v2 was mounted already.
Test004 uses shell builtins and explicitly mounts the guest cgroup filesystem.
No kernel failure was hidden by those harness fixes.

Gzip preflight001 lacked host `less`; a normal Debian host-tool install fixed
that. Gzip002 compiled but dpkg-shlibdeps could not locate the SPE libc.
The bounded Essential-bootstrap patch supplies the recorded real sysroot and
shlibs mapping without skipping dependency checks. Retire this accommodation
when package-managed build roots provide library state. Gzip003 packaged but
its rules overwrote caller C flag additions; it was not promoted. Patch0002
changes assignment to append, preserving caller SPE flags and upstream -Wall.
Gzip004 was rebuilt and tested before archive inclusion. Maintainer scripts
are generated normally and must execute normally during real root installation.

## Live recording session

`software-e-011` now boots the verified kernel008 with the existing diagnostic
RAM root005, 8 GiB and two CPUs. The prior validation guest010 was retired after
its private tests were retained. Fresh guest SSH host key was checked through
the authenticated R730 path before trusting the reused local port12238.
The existing loopback noVNC6089 service now forwards to RFB5923 and the existing
Desktop4 browser was refreshed; the guest terminal was replaced individually.
No new local browser/VM or local compilation was started.

`film-runtime-011.log` proves fresh equal-image fractal checks and Mesa25.0.7
softpipe OpenGL3.3 pixel-readback PASS. `film-preview-011.png` shows the actual
fractal pair and rotating cube. The source session script's optional `--film`
mode keeps the cube running in bounded frame batches after its first GL check;
normal diagnostic mode still performs one120-frame GL test. This is a live
software-rendered demonstration, not E compositor or Radeon acceptance. The
root remains the earlier diagnostic root, not the completed Trixie disk image.

Compiler defaults were inspected directly: `compiler-default-abi.json` records
8548, SPE, double GPR and LD128 without added flags. Gzip003 never switched
architectures. Its packaging overwrote additional maintainer C flags; gzip004
preserves those explicit flags and was tested before promotion. The distinction
matters: do not report a target-architecture failure that was not observed.
