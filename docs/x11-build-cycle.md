# Active source-built X11 client cycle — 2026-10-31

R730 now runs a separate detached Docker job for the ordered X11 client chain,
using the tested software prerequisites as read-only inputs. The existing
interactive QEMU guest and desktop 4 noVNC stay running. This cycle builds
libraries and headers; it does not yet launch Xorg or E.

`profiles/x11-sources.lock.json` pins 22 Debian Trixie source packages in build
order: protocol/transport headers, pthread metadata, Xau/Xdmcp authentication,
XCB protocol generator and libraries, Xlib, extensions and selected XCB utils.
Only sources are fetched; all target ELF output is compiled with the isolated
GCC8.5 SPE reference tools and experimental restored glibc sysroot. Native
Python runs the architecture-independent XCB generator, distinct from PPC
runtime libraries. Archives and DSCs are hash checked; independent OpenPGP
signature verification is not claimed. Source license notices are preserved.

`build-x11-clients.py` refuses a reused work directory, extracts Debian source
and applies its package changes freshly. Target pkg-config searches only the
new stage. Explicit e500v2/SPE/long-double flags, compiler/recipe hashes,
per-component state, command logs and final PPC32 big-endian ELF hashes are
recorded. The tested base stage, tools and sysroot are read-only; only the new
work stage is writable. The container runs offline, four CPUs / four make jobs,
6GiB memory; native tooling image is pinned to
`sha256:eb877fcd41042f17c0a1f67aa6e679c8dc81c10a72bf3ad12287d864e5eacdf0`.

Iteration001 built xorgproto and xtrans but stopped on a packaging assumption:
libpthread-stubs ships `debian/copyright.debian`, not `debian/copyright`.
Iteration002 collects those notices plus upstream COPYING/COPYRIGHT and starts
from fresh source. The failed receipt is retained. Launch snapshots are
historical; inspect current receipt/container state for completion.

R730 paths: `/srv/data1/tabor-build/linux-live-001/work/x11-clients-002`,
container `tabor-x11-002`. `receipt.json` is atomically updated with active
component/status. Docker logs have BUILD_START/BUILD_PASS checkpoints; build.log
has actual configure/compiler output. The desktop 4 log viewer follows only
the newest iteration and displays its receipt status, rather than showing old
fatal errors without their iteration context. It continues watching after a
build ends; that alone does not mean compilation is active.

Still required: X11 runtime/link checks, font dependencies, native EFL generators,
EFL/E/Terminology and Xorg server plus display/input drivers. Keep the floating
rounding failure, full ABI gate and physical U-Boot/HDMI validation explicit.
