# First GCC14 sbuild consumers: zlib, pkgconf, fuse3, X11 chain (#27) — 2026-11-16

With the GCC14 SDK qualified (`profiles/compiler-policy.json`, 8a18e48), the standard path (`run-sbuild-package.py`: mmdebstrap root, sbuild unshare, apt resolver) now builds powerpcspe packages from the GCC14 foundation only. Nothing from GCC8 was among the inputs.

Host: the Debian 13 WSL2 replica of the build host, laid out as on the R730 (`owner` account with subuid 165536+65536; base `/srv/data1/tabor-build/linux-live-001`; `tabor-{apt-cache,sbuild-repositories,sbuild-tmp}` beside it). `build-frozen-buildd-root.py` ran unmodified. `run-sbuild-package.py` ran unmodified up to libev-001. From libev-002 it has two optional, backward-compatible additions from this work: `binary_nmu_timestamp` and `source_patch.extra_patches`.

## Chain

| step | how | result |
|---|---|---|
| buildd root | `build-frozen-buildd-root.py --lock profiles/trixie-spe-base.lock.json` (snapshot 20261102T220000Z) | `trixie-amd64.tar` sha256 `af29a74a910dae6e...`, native foundation versions as locked |
| UAPI | `run-sbuild-package.py`, spec = `profiles/sbuild/linux-uapi.json` with the local root | `linux-libc-dev_6.12.115-2+spe1_all.deb` |
| cross core | `build-cross-core-metapackage.py` with `packaging/tabor-spe-cross-build-essential` 1.0+spe8 (this commit) | `crossbuild-essential-powerpcspe_1.0+spe8_all.deb` |
| host helper | spec = `profiles/sbuild/dh-golang-host.json` with the local root | `dh-golang_1.63+spe1_all.deb` |
| zlib | spec = `profiles/sbuild/zlib.json`, extra inputs replaced by the GCC14 set below, `binary_nmu: 1` | zlib1g, zlib1g-dev, libminizip1t64, libminizip-dev, minizip `1:1.3.dfsg+really1.3.1-1+b1` powerpcspe (`sbuild-zlib-gcc14-003`) |

zlib's inputs were:
- `tabor-spe-toolchain 14.2.0+tabor1`, through `native_toolchain_inputs`. Its receipt sha256 `c6539872...` equals the policy's `qualified_sdk_receipt_sha256`, so the runner recorded `compiler: {gcc_major: 14, sdk_receipt_sha256: c6539872...}`.
- `libc6` and `libc6-dev` 2.41-12+deb13u4.
- The `tabor-spe-libgcc-s1`, `-libstdc++6` and `-libatomic1` runtimes, 14.2.0+tabor1.
- `linux-libc-dev 6.12.115-2+spe1`, the cross core and dh-golang above.

The final zlib, pkgconf and fuse3 specs set `required_full_rebuild: true`, because they link against the stage2 glibc. They must be rebuilt after the full glibc.

The specs and receipts actually used are in `specs/` and `*.receipt.json`. Their `work/...` receipt paths and hashes refer to this replica, so they are evidence, not R730 profiles.

## Multi-Arch versions

The first zlib build (`sbuild-zlib-gcc14-001`, version `-1`) was not consumable. The frozen root's `zlib1g:amd64` is the binNMU `1:1.3.dfsg+really1.3.1-1+b1`, and dpkg refuses a Multi-Arch `same` pair at different versions: `zlib1g:powerpcspe (…-1) cannot be configured because zlib1g:amd64 is at a different version (…-1+b1)`. Rebuilding with the runner's `binary_nmu: 1` gives `-1+b1`, and `zlib1g:powerpcspe` plus `zlib1g-dev:powerpcspe` then install beside `zlib1g:amd64` in the frozen root. Every Multi-Arch `same` package built here was checked against the root's `installed-versions.json`: libc6, libc6-dev and zlib1g now match, and pkgconf's libpkgconf3 is 1.8.1-4 on both architectures.

## Checks

- sbuild installed `tabor-spe-toolchain (14.2.0+tabor1)` and `crossbuild-essential-powerpcspe (1.0+spe8)`; configure ran `--host=powerpc-linux-gnuspe` with `CC=powerpc-linux-gnuspe-gcc`.
- `libz.so.1`: ELF32 big-endian PowerPC, `Tag_GNU_Power_ABI_FP: hard float`; `zlib1g` `Depends: libc6 (>= 2.41)`.
- Under `qemu-ppc -cpu e500v2` with only the packaged libc6 and zlib (both builds), `minizip -9` compressed 3.5 MB of random data plus text, and `miniunzip` restored it byte for byte. The host's Python `zipfile` also reads and verifies an archive written by the SPE minizip.

## Changes in this commit

- `packaging/tabor-spe-cross-build-essential`, 1.0+spe8: depends on the GCC14 toolchain and runtimes (14.2.0+tabor1). `tabor-spe-libatomic-dev` is gone because the GCC14 toolchain ships `libatomic.so`/`.a` itself.
- `scripts/package-gcc14-spe-target-runtime.py`: the receipt uses the standard `debian-packages-built-not-target-installed` status, which the sbuild runner requires for extra inputs. The rebuilt runtime-002 has the same libraries (sha256) and payload listing as runtime-001.
- `scripts/fetch-locked-component.py` (new): fills an sbuild `source_cache` with one component from a lock, checked against size and sha256.

## Build-host notes

- `prepare-debian-build-host.sh` installed no sbuild tooling. It now also installs `mmdebstrap sbuild uidmap debhelper quilt` and, for Debian kernel control generation (UAPI), `kernel-wedge python3-dacite python3-jinja2 python3-debian`.
- sbuild runs as `owner`, so the runner must be started from a directory `owner` can enter. Starting it inside a private checkout fails with `BUILD_DIR directory ... does not exist`.
- `owner` must be able to write the cross-core output directory, since `dpkg-source` runs as `owner`.

## pkgconf and fuse3

Meson consumers need `pkgconf:powerpcspe`, which is Multi-Arch `same` and provides the triplet `pkg-config`. So `pkgconf 1.8.1-4` was built first, through the same path and the same inputs (`sbuild-pkgconf-gcc14-001`). It then joined fuse3's extra inputs (final: `sbuild-pkgconf-gcc14-002`).

`fuse3 3.17.2-3` was built twice with GCC14:

- **With the pinned #23 series** (`patches/fuse3/series.json`), as `sbuild-fuse3-gcc14-003`: it built fuse3, libfuse3-4, libfuse3-dev and fuse3-dbgsym, and the runner's payload inspection ran. The meson probe printed `Checking if "C++ 64-bit atomic operations" links: NO` and `Library atomic found: YES`, and memfs_ll linked with `-latomic` (`fuse3-atomic-probe.txt`). `libfuse3.so.3.17.2` is ELF32 PowerPC, NEEDED libc.so.6 only. Under qemu e500v2, `fusermount3 -V` prints `3.17.2` and `mount.fuse3` prints its usage.
- **Without the patch** (control), as `sbuild-fuse3-gcc14-unpatched-001`: memfs_ll fails to link with an undefined `std::__atomic_base<unsigned long long>::fetch_add` (`fuse3-unpatched-failure.txt`). That is the same failure #23 recorded under GCC8, so the patch is still needed with GCC14. A 64-bit atomic on 32-bit PowerPC is a libatomic call with either compiler.

## X11 chain

Built in order through the same runner and inputs, each with the previous jobs' powerpcspe packages as pinned inputs. All have `required_full_rebuild`.

| job | version | note |
|---|---|---|
| `sbuild-libxau-gcc14-001` | 1:1.0.11-1 | |
| `sbuild-libmd-gcc14-001` | 1.1.0-2+b1 | `binary_nmu: 1`, matching the snapshot's libmd0:amd64. `patches/libmd` only applies to the old `TABOR_SYSROOT` mode, so it was not used. |
| `sbuild-libbsd-gcc14-001` | 0.12.2-2 | |
| `sbuild-libxdmcp-gcc14-001` | 1:1.1.5-1 | |
| `sbuild-libxcb-gcc14-001` | 1.17.0-2+b1 | `binary_nmu: 1`, matching the snapshot's libxcb1:amd64; all 48 binary packages |
| `sbuild-libx11-gcc14-001` | 2:1.8.12-1 | the reviewed `profiles/x11-configure-cache.json` |

Every Multi-Arch `same` runtime matches the snapshot's amd64 version.

The configure cache value `xorg_cv_malloc0_returns_null=yes` was first measured on the GCC8 stack. It was re-measured here: `bench/x11-alloc-check.c`, built with the packaged GCC14 toolchain and run on glibc-003 under qemu e500v2, printed `malloc_null=0 realloc_null=1 calloc_null=0 xorg_cv_malloc0_returns_null=yes`.

Runtime check: `bench/x11-xvfb-roundtrip.c` (new) was built against the packaged libx11-dev and run under `qemu-ppc -cpu e500v2` against an Xvfb on the build host. It needs only `libX11.so.6` and `libc.so.6`. It printed `vendor=The X.Org Foundation release=12101016 screen=800x600 depth=24 atom=TABOR_SPE_TEST name=spe-gcc14 pixel=ffffff`, then `X11 roundtrip ok`. That exercises the SPE libX11, libxcb, libXau and libXdmcp over the real X protocol.

`specs/mkspec.py` and `specs/runspec.sh` are the replica-local helpers that derived these specs from the zlib one and ran them. They are evidence, not project scripts.

## Full-glibc prerequisites

Debian's full glibc build-depends on `libaudit-dev`, `libcap-dev` and `libselinux1-dev` for the host architecture. Built so far:

| job | version | profiles / note |
|---|---|---|
| `sbuild-pcre2-gcc14-001` | 10.46-1~deb13u3 | Debian's rules already disable JIT on powerpcspe; sljit's PowerPC backend uses FPU instructions e500 lacks |
| `sbuild-libsepol-gcc14-001` | 3.8.1-1 | |
| `sbuild-libselinux-gcc14-001` | 3.8.1-1 | `nopython,noruby` |
| `sbuild-libcap-ng-gcc14-001` | 0.8.5-4+b1 | `nopython`, binNMU 1 |
| `sbuild-libxcrypt-gcc14-002` | 1:4.4.38-1 | |
| `sbuild-flex-gcc14-003` | 2.6.4-8.2+b4 | binNMU 4 (`libfl-dev` must equal `flex`) |
| `sbuild-db5.3-gcc14-003`, `sbuild-db-defaults-gcc14-002` | 5.3.28+dfsg2-9, 5.3.4 | `pkg.db5.3.notcl` |
| `sbuild-pam-gcc14-003` | 1.7.0-5 | `stage1` (no audit/systemd) |
| `sbuild-libcap2-gcc14-001` | 1:2.75-10+deb13u1+b3 | binNMU 3 |

The upstream `patches/{pcre2,libsepol,libcap-ng,libmd}` only change behaviour when `TABOR_SYSROOT` is set, so the standard builds don't use them.

`nodoc` must not be used for Multi-Arch `same` packages. The first libxcrypt was built with `nodoc`, and its man pages came out as `.so` stubs where Debian's amd64 package has full pages. pam's dependency install then failed with `trying to overwrite shared '/usr/share/man/man3/crypt_gensalt_ra.3.gz', which is different from other instances of package libcrypt-dev:powerpcspe` (`pam-nodoc-multiarch-clash.txt`). libxcrypt, flex, db5.3 and db-defaults were rebuilt without `nodoc`.

`specs/coinstall.sh` (replica-local) installs each Multi-Arch `same` powerpcspe package beside its amd64 counterpart from the snapshot, so dpkg checks both the versions and the shared files. Across all 94 such packages built so far, against 91 amd64 counterparts, it found no problems.

Still missing for `libaudit-dev`: audit build-depends on libkrb5-dev, libwrap0-dev and libcap-ng-dev. krb5 needs comerr/ss (e2fsprogs, `+b12`), keyutils, lmdb, openssl and libverto. libverto needs libev and glib2.0, and e2fsprogs needs util-linux's libblkid/uuid. udev, systemd, cron, swig, byacc and docbook-to-man are Multi-Arch `foreign`, so the build can use amd64 for those.

## Terminal and ICU libraries

These are on the way to util-linux (libblkid/uuid for e2fsprogs) and sqlite3:

| job | version | note |
|---|---|---|
| `sbuild-gpm-gcc14-002` | 1.20.7-11+b2 | binNMU 2 |
| `sbuild-ncurses-gcc14-002` | 6.5+20250216-2 | `patches/ncurses/series.json` |
| `sbuild-readline-gcc14-001` | 8.2-6 | |
| `sbuild-tcl8.6-gcc14-001` | 8.6.16+dfsg-1 | |
| `sbuild-icu-gcc14-004` | 76.1-4 | `patches/icu/series.json` (new, below) |

### ICU data broken by cross-endian packaging (fixed)

The first ICU build (`sbuild-icu-gcc14-002`) compiled and packaged normally. But on the target every ICU program failed with `can not initialize ICU. status = U_INVALID_FORMAT_ERROR`. The ICU data header inside libicudata read `27da0090 00000014 00020000 446e6d43`. That is little-endian ICU data (`headerSize 0x0090, magic da27, isBigEndian 0, "CmnD"`) with every 32-bit word byte-swapped. ICU's Makefile converts the data to big-endian correctly (`icupkg -tb`). Two host-order assumptions after that undo it:

- `pkgdata` repackages the items with `writePackageDatFile(..., U_IS_BIG_ENDIAN ? 'b' : 'l')`, which converts them back to the host's order.
- `genccode -a gcc` prints each 32-bit word, read in host order, as `.long`, and the assembler stores it in target order.

`patches/icu/0001-cross-endian-data-library.patch` fixes both. pkgdata takes the type letter from the data package name (`icudt76b`, as `U_ICUDATA_NAME` defines it). genccode swaps the words when the data header's `isBigEndian` differs from the host's. Native builds are unchanged. With it (`sbuild-icu-gcc14-004`) the header reads `0090da27 00140000 01000200 436d6e44` (big-endian, `CmnD`). Under qemu e500v2, `uconv` round-trips UTF-8 → UTF-16BE → UTF-8, its UTF-16BE output matches the host's iconv, and `uconv -x 'Any-Latin; Latin-ASCII'` turns `Grüße, 東京, Ελλάδα, ñandú` into `Grusse, dong jing, Ellada, nandu`.

`scripts/check-icu-data-byte-order.py` (new) checks a libicudata's header against its ELF byte order. It fails on icu-002 and passes on icu-004.

## sqlite3, util-linux, e2fsprogs

| job | version | note |
|---|---|---|
| `sbuild-sqlite3-gcc14-001` | 3.46.1-7+deb13u2 | readline, tcl8.6, icu |
| `sbuild-util-linux-gcc14-001` | 2.41.5-0+deb13u1 | `stage1,pkg.util-linux.noverity`, `patches/util-linux/0001-disable-pam-tools-in-stage1.patch`. Stage1 builds the libraries and fdisk only. |
| `sbuild-e2fsprogs-gcc14-002` | 1.47.2-3+b12 | binNMU 12; fuse2fs against the GCC14 fuse3 |

Runtime checks under qemu e500v2, each compared with the x86-64 Debian tool:
- **sqlite3:** a SQL script with 20,000 REAL rows (sum, avg, min of an expression), exp, sqrt, pow, `round(2.675, 2)`, overflow to Inf, `printf('%.17g')` and text ordering. Its output is byte-identical to x86-64 sqlite3, so SPE double arithmetic and formatting agree.
- **sfdisk:** writing a two-partition GPT with fixed label and partition UUIDs gives an image byte-identical to x86-64 sfdisk, including both CRC32s. That exercises libfdisk, libblkid, libuuid and libsmartcols.
- **e2fsprogs:** the SPE `mke2fs -t ext4` image (metadata_csum, 64bit, orphan_file) passes the host's `e2fsck -fn`. The SPE `e2fsck -fn` passes a host-made ext4 (exit 0).

`coinstall.sh` on these together with their inputs: 47 Multi-Arch `same` packages, 44 amd64 counterparts, no dpkg problems.

## Compression, crypto and GLib

| job | version | note |
|---|---|---|
| `sbuild-keyutils-gcc14-001`, `sbuild-lmdb-gcc14-001`, `sbuild-tcp-wrappers-gcc14-001` | 1.6.3-6, 0.9.31-1+b2, 7.6.q-36 | lmdb binNMU 2 |
| `sbuild-libev-gcc14-002` | 1:4.33-2.1+b1 | binNMU 1 with `binary_nmu_timestamp` (below) |
| `sbuild-xz-utils-gcc14-001`, `sbuild-bzip2-gcc14-001` | 5.8.1-1+deb13u2, 1.0.8-6 | |
| `sbuild-xxhash-gcc14-002`, `sbuild-lz4-gcc14-002`, `sbuild-libzstd-gcc14-001` | 0.8.3-2, 1.10.0-4, 1.5.7+dfsg-1 | xxhash with `patches/xxhash/0001-cross-install.patch` (Debian's install step used plain `cc`) |
| `sbuild-openssl-gcc14-003` | 3.5.7-1~deb13u3 | needed the #38 compiler fix, see `docs/builds/gcc14-spe-zero-call-used-regs-20261116` |
| `sbuild-libtool-gcc14-002`, `sbuild-libffi-gcc14-002` | 2.5.4-4, 3.4.8-2 | the repo's libtool and libffi patches |
| `sbuild-elfutils-gcc14-002` | 0.192-4 | `pkg.elfutils.nodebuginfod`; needs `libc6-dbg:powerpcspe` |
| `sbuild-glib2.0-gcc14-001` | 2.84.4-3~deb13u5 | `noinsttest,nogir` |

From openssl on, consumers use `tabor-spe-toolchain 14.2.0+tabor2` and `crossbuild-essential-powerpcspe 1.0+spe9`. The `specs/zlib-gcc14-binnmu-local.json` template was switched. Its tabor1 form is kept as `specs/template-tabor1.json`.

Runtime checks under qemu e500v2:
- **libffi** (`ffi.c`): an `ffi_call` with nine mixed int/double/long long/float arguments equals the direct call bit for bit, and a closure returns the right value. The SPE ABI holds in libffi.
- **GLib** (`gtest.c`): the output is identical to the same program built against x86-64 GLib 2.84.4 (`glib-roundtrip-spe.out`). It covers:
  - GVariant print and little-endian serialisation hash;
  - a GObject signal with double/int64/string arguments through the libffi generic marshaller;
  - GRegex (PCRE2), GDateTime, `g_ascii_dtostr`/`formatd`/`strtod`;
  - UTF-8 case mapping, GHashTable, GKeyFile, a GMainLoop timeout, GIO file write/read.

### binNMU timestamps and Multi-Arch

sbuild's `--make-binNMU` dates the binNMU changelog entry now, and debhelper takes `SOURCE_DATE_EPOCH` from it. libev's man page records that date, so `libev-dev:powerpcspe` failed to coinstall with amd64: `trying to overwrite shared '/usr/share/man/man3/ev.3.gz'`, with `.TH LIBEV 3 2026-11-16` against Debian's `2024-10-28`. `run-sbuild-package.py` now accepts an optional `binary_nmu_timestamp`, passed to sbuild as `--binNMU-timestamp`. The value is the Debian amd64 binNMU's own trailer date, taken from its `changelog.Debian.amd64.gz` (`Mon, 28 Oct 2024 22:40:46 +0000` for libev). With it, libev coinstalls. No other binNMU built here generates dated shared files: all of them pass `coinstall.sh`.

## krb5 and audit: the full-glibc prerequisites are complete

| job | version | note |
|---|---|---|
| `sbuild-architecture-properties-gcc14-001` | 0.2.6 | `cross-exe-wrapper:powerpcspe`, which girepository-tools (pulled in by libglib2.0-dev) depends on, as auzieman found for GCC8 |
| `sbuild-libverto-gcc14-002` | 0.3.1-1.2+b2 | binNMU 2 with Debian's binNMU timestamp |
| `sbuild-krb5-gcc14-002` | 1.21.3-5+deb13u1 | `stage1` (no LDAP/SASL); `patches/krb5/0001-measured-spe-cross-configure.patch` plus the new `0002-native-myhostname-for-cross-builds.patch` |
| `sbuild-audit-gcc14-002` | 1:4.0.2-2+deb13u1 | `nopython,pkg.audit.noldap`; new `patches/audit/0001-noldap-fixperms-without-audispd-plugins.patch` |

Two Debian packaging bugs were fixed on the way:
- **krb5** build-depends on `libnss-myhostname` so the build can resolve its hostname (#1063648). The NSS module is loaded by the build tools' libc, so a cross build needs the build architecture's copy. Without `:native` it asks for `libnss-myhostname:powerpcspe`, which only systemd provides.
- **audit's own `pkg.audit.noldap` profile** does not build `audispd-plugins`, but `override_dh_fixperms-arch` still chmods `debian/audispd-plugins/etc/audit` and fails. The patch uses `$(wildcard …)` for that path.

`run-sbuild-package.py` gained an optional `source_patch.extra_patches` list. Each entry is pinned by sha256 and applied with `git apply` after the main patch, so krb5 keeps its reviewed 0001 and adds 0002.

So `libaudit-dev`, `libcap-dev` and `libselinux1-dev` now exist for powerpcspe, which a full (non-stage2) glibc needs. `coinstall.sh` over this group (51 Multi-Arch `same` packages) found no problems.

## Image and font libraries

| job | version | note |
|---|---|---|
| `sbuild-libpng1.6-gcc14-001` | 1.6.48-1+deb13u6 | |
| `sbuild-libjpeg-turbo-gcc14-004` | 1:2.1.5-4 | `patches/libjpeg-turbo/series.json` (0001-0003, unchanged; older build records pin its hash) plus the new `0004-qualify-javahelper-native.patch`, all applied as `source_patch` plus `extra_patches` |
| `sbuild-expat-gcc14-001` | 2.9.0-1~deb13u1 | |
| `sbuild-brotli-gcc14-002` | 1.1.0-2+deb13u1 | `nopython` |
| `sbuild-freetype-gcc14-001` | 2.13.3+dfsg-1+deb13u1 | demos built against the SPE libX11 |
| `sbuild-fontconfig-gcc14-001` | 2.15.0-2.3 | |

The runner's `quilt_patch_series` mode cannot carry patches that edit `debian/`. `dpkg-source -b` re-applies them over the already patched `debian/control` and fails, which is what happened with the libjpeg-turbo series and with glibc. Such series are now given as `source_patch` plus `extra_patches` (`git apply`; `specs/series2patch.py`). libjpeg-turbo's existing 0001 qualifies nasm and default-jdk `:native`. The new 0004 does the same for `javahelper`, which is Arch: all without Multi-Arch foreign and so unsatisfiable for the host architecture.

Runtime checks under qemu e500v2, each compared with x86-64 Debian:
- `cjpeg -quality 50/90 -optimize` and `djpeg` give byte-identical output.
- `pngfix --optimize` gives byte-identical output.
- `ft.c` renders 14 code points (Latin, Ä, Ω, Ж) at five pixel sizes with DejaVu Sans, hashes every bitmap and advance, and asks fontconfig for `DejaVu Sans:bold`. The hash, ink total and match are identical: `068a90f517b162b6`, `ink=2069295`, `DejaVu Sans/Bold`.

coinstall over this group: 92 Multi-Arch `same` packages, no problems.

## Hardware bundle (prepared, not yet run)

`hw/make-hw-bundle-27.sh` (replica-local paths) builds a self-contained bundle (`hw-bundle-27.tar.xz`, 43 MB, sha256 `7c24404b90e1c14b…`). It holds four test programs built with tabor2 (`t.cc` C++ threads/atomics/exceptions, `ffi.c`, `gtest.c`, `ft.c`) plus the packaged sqlite3, openssl, uconv and minizip, and the sbuild-built libraries. Each program has an expected output from the x86-64 build or a fixed reference. `run.sh` runs everything through the bundled `ld.so.1 --library-path`, so nothing is installed on the board, and it writes only under `/tmp`.

Dry run under the #3-patched qemu-ppc: 7 of 8 pass. sqlite fails only because qemu-user returns `EINVAL` for `PR_GET_FPEXC`: glibc's e500 `fegetenv` then leaves the saved environment unset, and a later `fesetenv` (from `sqrt`) writes a stale stack word (`0x0fed3bd0`) into SPEFSCR. That is #39, with reproducer `hw/qemu-fpexc-sqrt.c`. The real kernel implements those prctls, so on the A1222 all 8 are expected to pass.

## SDK digest and reproducibility

The policy pins the toolchain receipt `c6539872…`, and the runner checks the `.deb` against that receipt's `package_sha256` (`6d0923e3…`). That `.deb` exists only on this replica. Two things decide whether another build host can produce it:

- **Packaging.** Before this commit, repackaging the same SDK tree gave identical contents but different bytes, because 59 file mtimes differed. `package-gcc14-spe-host-toolchain.py` now clamps every mtime to the GCC release date (`gcc/DATESTAMP`, 20240801) and passes `SOURCE_DATE_EPOCH` to `dpkg-deb`. Two runs on the same tree now give the same `.deb` (`c851c0d3…`). The qualified `6d0923e3…` package predates this and stays as qualified.
- **The SDK compile.** This was not tested. Unstripped target objects carry build paths, so a GCC14 SDK build on the R730 is unlikely to reproduce the digest. Until the binary is shared, or the qualification is re-pinned to an R730 build, the R730 cannot meet the policy.

`profiles/trixie-spe-base.lock.json` still records `gcc: 8.5.0` and `sdk: 8.5.0+tabor5` under `target_foundation`. Changing it alters its hash and invalidates every root receipt, so it is left for the lock owner.

## Remaining (#27)

- The rest of the workstation closure (libX* extensions, Mesa, the session), ideally through `run-port-build.py` once GCC14 defaults exist.
- A full (non-stage2) glibc: all three prerequisites (libaudit-dev, libcap-dev, libselinux1-dev) are built.
- Physical A1222 runs of the dynamically linked packages.
