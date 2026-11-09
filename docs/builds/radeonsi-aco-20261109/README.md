# RadeonSI/ACO physical qualification — 2026-11-09

Pinned Mesa25.0.7-2+deb13u1 and kmscube0.0.0~git20210103-1.
Isolated SPE SDK8.5 diagnostic builds on R730, not a GCC14 Debian workstation
build or apt/dpkg-installed image. Kernel remains6.12.113-tabor-e2e-011.

The raw ACO executable upload now serializes instruction dwords after native
symbol relocation. Extracted source fixtures compare x86 and BE PPC across64
cases per architecture, retaining an old-BE negative control. Raw constant-data
bytes remain unchanged; complete shader-constant semantics are not proven.
PM4 remains CPU-native for the kernel legacy user-IB fetch conversion; uniform
and descriptor paths already using Mesa LE helpers must not be double-swapped.

First physical run failed before drawing: GBM mapped default8888 formats using
fixed component ordering while DRI config/image creation used native-endian
aliases. Candidate0002 aligns all eight8888 table entries with native aliases.
Incremental build passed; actual hardware now creates EGL/OpenGL ES2.0 context:
AMD Radeon Graphics (radeonsi, polaris11, ACO, DRM3.61, kernel011).
The test rejects softpipe/llvmpipe. Context creation is not drawing acceptance.

Default and explicitly linear scanout attempts both failed framebuffer
registration with EOPNOTSUPP. No visible accelerated cube is claimed.
Separate render-only execution compiled shaders and performed draw/glFinish/
RGBA readback, with no GL error reported, but every pixel was black: FAIL.
See physical-result.txt and render-only-pixels.json. Offboard kernel capture
retained for every attempt. SSH survived, taint0, VT1 restored, no module reload,
GPU reset, kernel replacement or boot-script modification.

Runtime is isolated at /opt/tabor-radeonsi-20261109. Root was writable only for
copy/update, restored read-only before execution. Initial file hashes verified;
subsequent GBM update hash retained separately. Two revisions of the diagnostic
cube added hardware-only guard and separate render-only readback.

Workstation dependency audit completed using existing verified frozen native
indexes and actual accepted target packages. Seven of16selected sources are
metadata-installable, nine blocked; see workstation-queue-readiness.json.
Metadata readiness is not clean-root coinstallation/build acceptance. Existing
GCC14 qualification still fails two strstream destructor thunks in libstdc++;
no fresh GCC14 workstation compile batch has been started or SDK promoted.

PNY file recovery receipt reports rsync exit0; earlier raw-read bad sectors and
NTFS inconsistency remain material. No wipe/repair/defrag or image deployment
was performed. Verify recovered file completeness and media suitability first.

Next: trace black draw versus readback/format handling and the exact AddFB2
rejection independently; qualify GCC14 C++ runtime and package coinstallation
before widening the standard sbuild workstation batch.
