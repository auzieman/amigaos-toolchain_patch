# GCC14 SPE foundation as Debian packages (#27) — 2026-11-16

The package loop needs GCC14 SDK, libc and runtime packages; until now only GCC8 ones existed. This records the first complete GCC14 set, built on a local replica of the build host: Debian 13 under WSL2, prepared with `scripts/prepare-debian-build-host.sh` unmodified, Docker 26.1.5. The repository was at `development` 3ef4d70 plus the changes in this commit.

## Packages

| package | sha256 (16) | how |
|---|---|---|
| `tabor-spe-toolchain_14.2.0+tabor1_amd64.deb` (56 MB) | `6d0923e39b2cad74` | `build-gcc14-spe-sdk.sh` with `PREFIX=/usr/lib/tabor-spe-toolchain INSTALLED_SYSROOT=/ MULTIARCH=1`, then `package-gcc14-spe-host-toolchain.py` |
| `linux-libc-dev_6.12.113-1_all.deb` | `d83eb60679e780d9` | `build-spe-linux-headers.py --debian-all-uapi` (unmodified); 53 `powerpc-linux-gnuspe/asm` headers |
| `libc6`, `libc6-dev`, `libc-bin`, `libc-dev-bin`, `libc6-dbg`, `nscd` `_2.41-12+deb13u4_powerpcspe` | `06ecebab0446f9b9` (libc6), `72e0779b5ffa77e0` (libc6-dev) | `build-debian-package.py --package glibc --source-lock profiles/debian-trixie.lock.json --package-managed-root --preserve-debian-version --build-profiles cross,nocheck,stage2,nobiarch --arch-only` in the rebuilt image chain (kernel -> ... -> glibc-package-tools with the GCC14 toolchain .deb); glibc 0001-0007 applied |
| `tabor-spe-libgcc-s1`, `tabor-spe-libstdc++6`, `tabor-spe-libatomic1` `_14.2.0+tabor1_powerpcspe` | `30617ce178196d0d`, `1ce2c56fe392c25a`, `64e94a58ae511c83` | `package-gcc14-spe-target-runtime.py` (debhelper, `dpkg-buildpackage -a powerpcspe -B`) against the installed libc6:powerpcspe |

## Package-managed compiler

Debian cross builds compile against installed `libc6-dev:powerpcspe` multiarch files, as #14 established for GCC8. So the packaged compiler is configured with `--with-sysroot=/ --enable-multiarch`, and the bootstrap sysroot is used only as `--with-build-sysroot`. powerpcspe's `t-linux` gives `MULTIARCH_DIRNAME powerpc-linux-gnuspe` for `--with-cpu=8548`. The packaged compiler reports sysroot `/` and multiarch `powerpc-linux-gnuspe`, and passes `-imultiarch powerpc-linux-gnuspe`. Its library search covers `/usr/lib/powerpc-linux-gnuspe`.

GCC14's `include-fixed` holds only `pthread.h`. The GCC8 `__linux__/` fixed-header rewrite (`repair-spe-fixed-headers.py`) does not occur, so no repair step is applied.

The host executables are stripped: 20 of them, recorded in the receipt. Target objects are left untouched. `Depends` is taken from the actual `NEEDED` libraries of cc1/cc1plus: libc6, libgmp10, libmpfr6, libmpc3 and binutils-powerpc-linux-gnu.

## Changes in this commit

- `scripts/build-gcc14-spe-sdk.sh`: optional `INSTALLED_SYSROOT` and `MULTIARCH` (defaults unchanged).
- `scripts/package-gcc14-spe-host-toolchain.py` (new) and `scripts/package-gcc14-spe-target-runtime.py` (new) with `packaging/gcc14-runtime/debian` (new). The GCC8 packagers are pinned to 8.5.0 and its receipts, so they stay as they are.
- `scripts/build-debian-package.py`, package-managed mode only:
  - glibc no longer sets `LINUX_SOURCE=/usr`, which would select the build host's x86 asm headers. Debian's rules then use `/usr/include/$(DEB_HOST_MULTIARCH)`.
  - glibc may build with no target packages installed yet, since it is the root of the target graph.

## Notes from the runs

- Without `--preserve-debian-version` the libc packages were `2.41-12+deb13u4+tabor1~stage2`. `libc6:amd64` (2.41-12+deb13u4) then `Breaks` them under Multi-Arch, so they cannot coinstall in a build root. The preserved Debian version coinstalls, and the patch identity stays in the receipt (`patch_series_sha256 b8ac02e6...`).
- `libc6` (stage2) has no `Depends`, so it installs before the runtimes. The runtimes got real `dh_shlibdeps` results:
  - `tabor-spe-libgcc-s1` and `tabor-spe-libatomic1`: `libc6 (>= 2.41)`;
  - `tabor-spe-libstdc++6`: `libc6 (>= 2.41), tabor-spe-libgcc-s1 (>= 14.2.0+tabor1)`.

  Each `Provides` its Debian name.
- `libm.so.6` from the package is ELF32 big-endian PowerPC with 13,580 SPE double instructions.

## Validation

In a fresh `glibc-package-tools` container, `apt` installed the toolchain, linux-libc-dev, libc6/libc6-dev/libc-dev-bin and the three runtimes normally. The test program then built and ran:
- `powerpc-linux-gnuspe-g++ -O2 -pthread t.cc -latomic` was used with no `--sysroot`. It exercises a thread, a 64-bit `std::atomic`, a C++ exception, `std::sqrt` and `std::to_string`.
- The result links dynamically against the packaged libraries (`NEEDED` libatomic.so.1, libstdc++.so.6, libm.so.6, libgcc_s.so.1, libc.so.6; interpreter `/lib/ld.so.1`; no RPATH).
- `qemu-ppc -cpu e500v2 -L /` printed `caught unwind`, `sqrt(2)=1.4142135623730951 n=300000 42`, exit 0.

## Remaining (#27)

- A full (non-stage2) glibc rebuild with audit/selinux/cap once those target packages exist.
- `crossbuild-essential-powerpcspe` pinned to these versions.
- A clean frozen buildd root, and representative sbuild consumers.
- Physical A1222 runs of the dynamically linked packages.
