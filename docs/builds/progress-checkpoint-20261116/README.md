# Debian SPE progress checkpoint — 2026-11-16

This is a development evidence checkpoint, not a release or a complete source
export of the current working tree. Tabor Linux remains Debian Trixie on
powerpcspe with GCC14. Preserve normal Debian dependencies, Recommends,
features, maintainer scripts and permissions. VM132 is the reference system.

## Build waves

The accompanying [wave inventory](waves.json) records source-level results,
observation time and SHA256 of the retained build receipts. Counts are source
builds, not installed binaries. The live queue can advance after this snapshot.

Broad desktop run: **82 successful source builds**, **14 failures**, **0 running**, **0 queued** at observation. Controller receipt status: `running`.

The emulator-wrapper prerequisite completed. The full EFL dependency lane
stopped before GLib compilation on `Native cache integrity/provenance check
failed`. It is not currently compiling EFL. Restoring Debian's full EFL feature
set remains pending; no rendering fix is claimed from dependency work alone.

Grouped remaining blockers include compiler-package coinstallation for Avahi
and libnvme; target Python configuration during Heimdal/libwebm dependency
installation; cross configure execution for APR and X libraries; Java architecture
mapping; and FFTW/Fortran/MPI prerequisites for ALSA utilities. Other source-build
failures remain listed in the inventory. Retry after a relevant input correction,
not merely with a new run name.

## Target and focused qualification

The retained session evidence records an A1222 boot with all 8GiB, working Xorg,
xterm and responsive Enlightenment menus/desktop switching. Native EFL client
interiors remain empty or incorrectly painted. The same class of symptom was
seen in the earlier GCC8 QEMU setup; that was not a GCC8 physical-board result.
No confirmed cause has been established. This checkpoint does not rerun those
hardware tests or claim that package completeness proves rendering correctness.

Runtime wave002 installed 36 previously missing reference packages through APT;
`dpkg --audit` and APT dependency checks passed, and the X/E test session restarted.
`man-db` remained blocked. Source build totals must not be read as target installs.
The onboard audio driver registers `sndsoctabor`; audible playback remains
unvalidated and ALSA command-line utilities remain missing.

Rust 1.85.1 SPE standard-library qualification passed on physical hardware for
float/double, C libm ABI, formatting, allocation, threads, atomics and unwinding.
Probe SHA256: `0c7543c8b62e37155281852a47669b0ed2bed58b9b65280be4e787caa218427f`.
This is cross-tool support for GStreamer's target helper, not a completed native
Rust compiler port. The private static SPE QEMU also passed that probe.

## Next gates

1. Correct the native-cache failure and requalify the GLib/GIR build path.
2. Complete normal GStreamer and EFL builds without dropping Debian features.
3. Install accepted runtime waves through APT and repeat actual client rendering
   validation; preserve diagnostic failures and avoid asserting a speculative cause.
4. Finish audio tools and test playback separately from desktop rendering.

Tags identify this recorded state only. Uncommitted recipes, SDKs, binary packages,
images and machine-local settings are not included in this documentation export.
