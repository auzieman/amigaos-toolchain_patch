# GPU and desktop handoff — 2026-11-13

Polaris11 on A1222/PPC32 BE now draws correct clear/RGB triangle probes and a physically visible rotating cube. `AMD_DEBUG=vs,ps`, without `check_vm`, completed **1,199 frames in 19.945616 seconds (60.113460 FPS)**. The user confirmed smoother visible output; no logged GPU fault/reset and SSH remained responsive. A direct HDMI clip separately confirms the cube under the heavier debug configuration.

## What changed

* Paired Mesa/kernel compute IB software-LE publication covers shader-upload auxiliary contexts as well as graphics submissions.
* RG8/RGBA8 colour buffers no longer reverse array-format channels again in hardware; the same clear/readback fixture changes from scrambled colours to pass.
* State-tracker native parameters bypassed the driver's LE32 uploader when `prefer_real_buffer_in_constbuf0` was true. Disable that shortcut on BE so both application uniforms and state constants use the existing conversion. Identical uniform-driven RGB triangle changes from zero pixels to pass; constant-red geometry already passed.
* ACO native constant loads, executable marker tails and descriptor diagnostics have separately documented scope. Do not attribute every improvement to one patch.

The [patch manifest](../patches/mesa/polaris-be-20261113/manifest.json) and [small regression fixtures](gpu-checkpoint-20261113/) retain reviewable changes and acceptance. This checkpoint builds on prior candidate sources; it is not a self-contained upstream patch stack or distribution image.

## Remaining graphics gate

Normal mode still shows grey. Shader-debug flags influence compilation/initialisation; `si_schedule_initial_compile` waits its initial compiler fence in debug mode. That is a source lead, not a proven race or reason to add global waits. Heavy `check_vm` slows the visible demo to roughly11FPS and is unnecessary for the confirmed60FPS run. The HUD experiment went grey; do not report its capture rate as application FPS. Keep the debugging dependency visible in desktop configuration and release notes. No X11, Enlightenment, complex-model or Quake acceptance follows from the cube.

## Desktop build pulse

No build containers were running at inspection. The latest GCC14 boot-media batch ended `infrastructure-failed` after binary-rebuild/base-library stages, with **17 and60 successful build records**, respectively, plus2 recorded source-build failures. These are stage records, not an installed-system package count. The retry stopped at `Prior pipeline needs infrastructure review`.

Retained fallout includes `db5.3` and `systemd` GCC internal compiler errors (`extract_insn`), target Python development closure, GIR tooling, ALSA consumers, and the requirement to keep the accepted patched glibc foundation. Earlier failures may have later compiler fixes; compare input fingerprints before retrying. Do not submit the unchanged broad queue or claim a running build.

Next: reconcile the controller infrastructure failure and patched GCC14/root identities, retry the failed producers through normal sbuild, then assemble and validate shell/dpkg/apt/SSH with maintainer scripts intact. Install software X11/Enlightenment on that base. Package the reviewed graphics candidate as an opt-in diagnostic layer; retain known console/boot rollback. No image or partition was rewritten by this handoff.
