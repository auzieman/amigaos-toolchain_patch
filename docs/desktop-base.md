# Source-built software desktop prerequisites — 2026-10-31

R730 fresh iteration `desktop-base-002` builds zlib, libpng and Pixman against
our isolated GCC8.5 SPE reference compiler and experimental restored glibc2.41
sysroot. The selected software operations execute successfully through ordinary
user SSH in the existing QEMU e500v2 guest. No existing guest image, accepted
sysroot, compiler installation or physical USB was replaced.

Inputs are Debian Trixie source packages, including the current selected
libpng security revision, not generic PowerPC runtime packages:

| Component | Source revision | Selected runtime check |
| --- | --- | --- |
| zlib | 1:1.3.dfsg+really1.3.1-1 | Compression/decompression bytes match |
| libpng1.6 | 1.6.48-1+deb13u6 | 2x2 RGBA encode/decode bytes match |
| Pixman | 0.44.0-3 | ARGB source compositing preserves pixels |

Exact DSC and archive SHA256 values are in
[the source lock](../profiles/desktop-base.lock.json). Debian source extraction
applies each package's supplied changes in a fresh directory. HTTPS DSC plus
payload hashes were verified; independent OpenPGP signature verification is not
claimed. Copyright metadata was inspected and retained; preserve its component
and per-file license notices. These packages do not become project-owned code.

The native build container derives from the retained reference tools image.
Its exact ID is `sha256:eb877fcd41042f17c0a1f67aa6e679c8dc81c10a72bf3ad12287d864e5eacdf0`;
[host package versions](builds/r730-desktop-base-20261031/host-packages.txt)
are retained. The Dockerfile alone does not lock apt resolution for future
image rebuilds. Runtime target flags select e500v2-class SPE hard float and
128-bit long double. Pixman VMX/AltiVec is explicitly disabled because the
A1222 CPU does not provide it. Target pkg-config paths exclude host packages.
Every staged ELF is checked as PPC32 big-endian. This is a software prerequisite
slice; it does not claim the completed X11/EFL dependency closure.

`desktop-base-001` built zlib then failed in libpng header generation because
that preprocessing command did not inherit the include directory from CFLAGS.
The corrected recipe also sets CPPFLAGS, then starts fresh as 002. The failure
receipt remains alongside the successful result. No source patch or compiler
ABI change was needed for this correction.

[Build receipt](builds/r730-desktop-base-20261031/receipt.json),
[recipe hashes](builds/r730-desktop-base-20261031/recipe-hashes.json),
[compiler/libc hashes](builds/r730-desktop-base-20261031/compiler-libc-input-hashes.json)
and [runtime receipt](builds/r730-desktop-base-20261031/runtime-probe/receipt.json)
are retained with [raw guest output](builds/r730-desktop-base-20261031/runtime-probe/guest.log).
Shared libraries and the probe are copied to a unique ordinary-user `/tmp`
directory and selected only through that command's LD_LIBRARY_PATH; they do not
replace the live guest's system libraries. Full source/build trees and logs stay
on R730 under `/srv/data1/tabor-build/linux-live-001/work/desktop-base-002`.

To repeat, use `scripts/fetch-desktop-base.py` with the reviewed lock/cache,
then `scripts/build-desktop-base.py` in the constrained offline container:
project, source cache, compiler tools and base sysroot read-only; fresh work rw.
Use four jobs, four container CPUs and 6GiB memory. The build script requires
all mounts and an exact image ID explicitly. Use `scripts/probe-desktop-base.py`
with an existing loopback guest SSH forward and scoped known_hosts; the private
operator key stays on the workstation. The probe retains failures and hashes.

Next is the source-built X11 protocol/client chain and font dependencies,
followed by native EFL generators and cross EFL/E/Terminology/Xorg. Existing
fenv directed arithmetic still fails in QEMU; these limited integer/pixel tests
do not waive that failure, qualify general rendering correctness or establish
GL/GPU, physical HDMI, U-Boot handoff or a graphical session.

Primary source/version references:
[Debian zlib](https://packages.debian.org/source/trixie/zlib),
[Debian libpng](https://packages.debian.org/source/trixie/libpng1.6),
[Debian Pixman](https://packages.debian.org/source/trixie/pixman).
