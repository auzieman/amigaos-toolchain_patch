# Standard Piglit GLES2 comparison — 2026-11-09

Purpose: independently test the active stack before further driver changes.
Frozen Trixie metadata selects Piglit0.0~git20250409.af62c0dea-2 andWaffle1.8.1-1.
Sources cached by exact SHA256, checked against the previously authenticated
frozen source indexes. Upstream shader tests, shader runner, core GL utility
and FBO framework byte-match the verified original archive. No local edits to
test source or expected pixels; normal Debian patches retained.

Built GLES2 standard targets shader_runner_gles2, minmax_gles2 and
 glsl-fs-pointcoord_gles2 using upstream CMake, with Waffle surfacelessEGL/GBM
built by upstream Meson. GLX/desktopGL/Vulkan/OpenCL tests not selected for this
GLES2-only diagnostic. R730 Docker bounded2CPUs/4GiB, SDK/sysrootRO, networkoff.
Native PythonNumpy build dependency installed from cached normalamd64 packages,
including its native BLAS/LAPACK runtime dependencies; no targetFortran build.
First apt local-file installation hit percent-encoded cachefilename handling;
normal dpkg installation of the same complete cached package set succeeded.
Missing transitive link dependencies were completed from the SHA-verified
existing runtime closure; no forced links or test-source changes. Build exit0.

Private /opt/tabor-piglit-20261109 contains verified unmodified test binaries,
standard Waffle wflinfo, test files and matching current Mesa/runtime closure.
Root filesystem returnedRO. No kernel/driver reload or source change this pass.
Current013 diagnostic flagY and paired Mesa explicitLE IB/fence/mode corrections
are retained. This does not test unpatched upstreamMesa or package installation.

## Physical comparison

Standard platform: PIGLIT_PLATFORM=surfaceless_egl, EGL_PLATFORM=surfaceless,
-auto -fbo. No VT switch, display modeset or custom readback routine.
Same test binaries/data used for both backends; wflinfo verifies actual renderer.

| Test | softpipe | RadeonSI/Polaris11/ACO |
|---|---|---|
| Waffle GLES2 renderer query | exit0, softpipe | exit0, expected hardware renderer |
| Piglit minmax_gles2 | PASS | PASS |
| Upstream glsl-no-vertex-attribs | PASS | controller timeout40s; GFX watchdog reset |
| Upstream sanity.shader_test RGB draw/probe | PASS | not run after timeout |

The 1x1 point test has constant vertex position/pointsize and constant green
fragment output, no vertex attributes or uniforms. It excludes custom kmscube,
window/scanout and uploaded vertex attributes from this reproduction, but does
not isolate shader generation versus kernel execution/image/fence handling.
Softpipe passing the same test is the standard positive control; no inference
that hardware rendering works follows from capability checks.

Offboard kernel log contains whole boot history. After the standard test begin
marker, the new fault is `ring gfx timeout, signaled seq=17, emitted seq=18`,
followed by kernel-initiated GPU reset, KIQ timeout/KCQ disable failure, BACO
reset and `VRAM is lost due to GPU reset`. Earlier log errors before the marker
are historical and must not be attributed to this test. Local process timeout
cannot guarantee interruption of a kernel/GPU stall. Controller stopped; no
remaining hardware test or manual GPU recovery attempt followed.

Post-recovery SSH responds, taint0, rootext4RO, activeVT1. One shader_runner
zombie remains, not an active rendering process. A clean GPU state/display is
NOT accepted after automatic reset/VRAM loss. There is no evidence here of USB
image corruption; filesystem stayedRO during tests. A fresh boot is required
before any next materially different physical GPU trial. No fresh reboot sent.

## Next gate

Use these standard tests as the regression baseline. Preserve this negative
result and compare complete shader/config plus GPU execution/write/read paths
offline. Avoid further patches justified solely by the custom black-frame test.
Do not run the remaining hardware test or repeat this failed draw on the current
post-reset GPU state. The run wrapper now records controller timeout explicitly;
that logging-only correction has not been rerun against hardware.
