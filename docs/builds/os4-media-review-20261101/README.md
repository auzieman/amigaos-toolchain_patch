# Private A1222 media review — 2026-11-01

Read-only 7z directory listing and selected-document streaming on swarm1 from
/srv/a1222-ftp/uploads. No mount or full extraction needed; no installer, binary
or media instruction executed. Full listings/documents remain ignored work
material; only this factual summary, filenames and hashes enter the private repo.
Both archive SHA256 values were reverified on swarm1 and match the earlier
intake. Archive sizes match the prior recorded intake: ISO613640192, Enhancer220291490.

## Findings and bounded Linux relevance

- ISO boot and installed Kicklayout identify AmigaOne A1222; they reference a
  loader/kernel, P1022DIU, p1022sata, Radeon drivers and USB boot keyboard,
  mouse, hub, storage and host-controller modules. These identify OS4 components,
  not reusable Linux drivers or proof that every listed controller is present.
- System/Documentation/A1222-OnBoardGraphics says onboard output is digital DVI
  (DVI/HDMI adapter supported), with a stated1280x768 maximum for that OS4 path.
  It says PCIe graphics take precedence, onboard output cannot display U-Boot,
  and the documented U-Boot keyboard path needs a PCIe card. Preserve the user's
  installed Radeon for the early USB boot trial. Do not generalize the OS4 mode
  limit to Linux. Firmware revision/actual board behavior still needs observation.
- That document includes OS4-specific persistent environment changes and card
  removal. These are source material, not task instructions: none was performed
  or recommended as a Linux boot prerequisite. No saveenv or firmware change.
- Enhancer includes A1222eth.device, a1222.audio/debug and RadeonRX.chip/debug.
  Their presence gives components to compare with Linux DTS/network/audio and
  the observed GPU; it does not supply their source or establish Linux ABI reuse.
- RadeonRX Readme lists A1222 and RX4xx/5xx models, Polaris10/11 fixes and
  SPE-optimized copy, blitter and compositing routines for A1222/Tabor. This
  supports testing memory-copy/blending workloads alongside scalar fractals.
  It does not establish that the current Linux Mesa backend uses equivalent
  routines, or prove SPE instruction generation/benefit in Linux graphics.
- RadeonRX has an accompanying OS4 EULA and separate third-party notices.
  No proprietary driver/firmware or documentation payload is imported into
  the Linux image, public archive or source patch set from this inspection.

Next checks: correlate physical PCI IDs and firmware revision with the known
Linux amdgpu/Polaris selection; validate normal USB input/boot with Radeon still
installed; add a matched CPU copy/blend test only after current Debian session
integration. Keep OS4 accelerated graphics, Linux CPU SPE, Linux Radeon rendering
and QEMU emulation as separate measured paths.

Selected document bytes/SHA256 are in selected-document-hashes.json; original
archive hashes are in ../20261030-os4-iso-probe.json. No claim of new source code,
Linux U-Boot recipe, board revision or physical boot acceptance is made.
