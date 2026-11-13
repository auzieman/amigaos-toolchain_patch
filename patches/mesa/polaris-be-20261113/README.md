# Polaris big-endian incremental checkpoint

Reviewed development changes from the 2026-11-13 side investigation. Source notices and upstream component licenses remain applicable (Mesa MIT; Linux GPL-2.0); this bundle does not relicense components.

These are incremental patches, not a complete pristine-upstream build recipe. Preserve earlier RadeonSI/ACO executable serialization, GBM/KMS format fixes, native vertex handling and kernel VM/ring work. The paired compute-IB patch requires both Mesa software-LE publication and kernel swap0 selection with `polaris11_le_user_ib=1`; using only one changes the fetch contract incorrectly.

The final two changes fix RG8/RGBA8 colour-buffer hardware swapping and route native BE constant-buffer parameters through RadeonSI's existing LE32 uploader. Do not globally swap byte arrays or already serialized buffers. The descriptor-report patch only corrects diagnostics. The ACO marker-tail patch is not independently established as a timeout cause; the constant-load pass has dedicated 32-bit-array compilation evidence, not dedicated physical16/64-bit acceptance.

Kernel base includes Richard Gibbs' VCE fix at the manifest's contributor commit. Its attribution remains in the repository history. The files here preserve existing source context; no proprietary SDK or firmware binaries are included.

Physical results and integration limits: [desktop handoff](../../../docs/gpu-desktop-handoff-20261113.md). The manifest pins patch bytes and qualified artifact identities without including binaries or lab authentication. Preserve patch order and source context; this is not a release claim.
