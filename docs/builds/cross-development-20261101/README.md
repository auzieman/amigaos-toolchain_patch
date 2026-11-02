# Debian build-environment increment — 2026-11-01

Real progress: shared target-libc discovery now works with installed Debian cross-development metadata; fresh Debianutils003, Diffutils002 and Mawk002 produce genuine powerpcspe packages without new per-package shlibs patches. The configured target root and desktop are still not accepted.

## Reproducible bootstrap mechanism

Debian documents converting bootstrap libc to cross-development packages in https://wiki.debian.org/ToolChain/Cross and https://manpages.debian.org/trixie/dpkg-cross/dpkg-cross.1.en.html . The converter is deprecated in Trixie, so this is a bounded toolchain-bootstrap bridge, not a proposed replacement for native target apt/sbuild roots or modern general dependency management.

`scripts/build-cross-development-packages.py` checks receipt and input artifact hashes, then runs unmodified Debian dpkg-cross for powerpcspe. Inputs are our real stage2 libc6/libc6-dev packages and powerpcspe-only kernel headers. Converted packages are Architecture: all host cross-development packages, retained outside the target archive. No target installed records are fabricated.

`prepare-cross-development-context.py` verifies those outputs and selects exact converted packages for a Docker context. `Dockerfile.cross-development` checks SHA256SUMS and normally installs the converted runtime libc with dpkg. Its real ownership and generated shlibs metadata now let dpkg-shlibdeps derive libc6:powerpcspe dependencies. `/etc/ld.so.conf.d/tabor-spe-cross.conf` exposes the standard cross-library directory to Debian's search logic; no package-specific search override or fallback shlibs mapping is added.

Only the converted runtime libc is installed in image001. Converted libc6-dev still requires libc-dev-bin-powerpcspe-cross; development-package closure is NOT claimed installed. The compiler still uses the recorded bootstrap sysroot. Full package-aware target build dependencies and a native configured target root remain unfinished. Existing compiler/libc ABI/fenv and hardware gates remain separate.

To reproduce conversion/context creation on the R730, mount the project read-only at /project, source receipts/artifacts read-only at /base and a writable work directory at /work, then run:

```sh
python3 /project/scripts/build-cross-development-packages.py \
 --base /base --manifest /project/profiles/repositories/cross-development-bootstrap.json \
 --output /work/cross-development-NEW --image-id IMAGE_DIGEST
python3 /project/scripts/prepare-cross-development-context.py \
 --receipt /work/cross-development-NEW/receipt.json \
 --dockerfile /project/docker/Dockerfile.cross-development \
 --output /work/cross-development-image-NEW libc6-powerpcspe-cross
```

Build the generated context with `BUILD_INFRA_IMAGE` set to the pinned infrastructure image. Use fresh output paths; do not overwrite prior iterations. All actual image digests and artifact hashes are adjacent.

## Normal package checks and results

- Debianutils003: dpkg-buildpackage completed; Pre-Depends libc6:powerpcspe >=2.41.
- Diffutils002: dpkg-buildpackage completed; Pre-Depends libc6:powerpcspe >=2.41.
- Mawk002: host autoconf-dickey supplied normally; dpkg-buildpackage completed; Depends libc6:powerpcspe >=2.41.
- The three cross builds retain cross,nocheck bootstrap profiles; compilation/packaging does not claim target runtime or full upstream test acceptance.
- Signed target archive006 contains36 real powerpcspe/all packages, including base-files001 and the three new builds. Signature verification passes; selected library simulation passes, but complete Essential/desktop closure remains blocked (apt-check009).
- Pinned and cached base-passwd3.6.7, init-system-helpers1.69~deb13u1 and debconf1.5.91 sources. Payload hashes retained; independent source OpenPGP chain verification is still pending.
- Dpkg001 preflight blocks on pkgconf and target libmd/zlib/bzip2/lzma/zstd/SELinux/ncurses development packages. Base-passwd001 blocks on DocBook tools and target cdebconf/SELinux development packages. No dependency checks suppressed.

## Independent scripting/data package correction

The runner now supports normal `-A` independent builds and asserts every generated binary package has Architecture: all. Its cross compiler and sysroot environment are removed for this mode: otherwise dpkg-architecture infers a cross host from CC and incorrectly requests target Perl/Python for a host scripting build. This is the scripting exception, not an amd64 library/application source rebuild. Compiled target packages retain the exact SPE compiler/flags and powerpcspe architecture gate.

An empty build-profile selection is now supported. DEB_BUILD_OPTIONS only includes nocheck when that profile was explicitly selected, allowing independent packages to run their normal tests. Init-system-helpers003 first identifies missing fakechroot/libtest-deep-perl; image010 installs those real host packages. Iteration004 then exposes the slim base image's missing Perl files despite their recorded installed ownership. Rather than changing or skipping upstream tests, image011 removes the inherited slim path-exclusion config and normally reinstalls host perl-base/perl. That repairs the relevant host package payload; it does not claim all historical slim-image omissions have been restored.

Debconf003 builds all independent packages with no nocheck profile. Init-system-helpers005 completes its normal fakechroot and DPKG_ROOT test runs and builds its real Architecture: all package. No test-specific patch or nocheck profile is used. A pre-existing undefined ${perl:Depends} packaging warning remains visible; no generated package dependency was invented to hide it.

R730 constraints: one package compile at a time,4CPU/6GiB; host image preparation2CPU/2GiB; conversion1CPU/2GiB and archive work1CPU/1GiB. Laptop does orchestration only. Existing recording display1 and USB remain unchanged. Next acceptance is a complete genuine Essential/package-manager closure, normal target package configuration and disk-root boot, followed by the full desktop package selection and its dependencies.

Final retained archive007: 42 real target/data artifacts, signed and verified. Apt-check010 still reports complete Essential/desktop closure blocked. Init-system-helpers005 passes8 upstream test suites with1064 top-level TAP checks and0 failing checks; summary and full-log SHA256 retained. Source-built debconf003/init-system-helpers005 are now included in the archive, with the original target package identities preserved.
