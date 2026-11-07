# Historical Polaris big-endian Linux reference

Primary developer report: Marcus Comstedt,2018-06-12,
https://lists.freedesktop.org/archives/amd-gfx/2018-June/023019.html
Author patch: https://mc.pp.se/amd_powerplay_be.patch
Retrieved SHA256283feb087ae1f32c16726045dd689b2258abdbee50c89b7fa8d8ca514d210b2c,
31641bytes; retained in ignored work/polaris-history-20261105, not default series.

Author reports RX550/Polaris12 on POWER9 working in LE; his BE patch gets SMU
and firmware loading working. Graphics command-ring byte order remains an
unresolved step in that report. This is useful prior startup work, not proof
of a fully working older BE distro or our Polaris11/PPC32 board.

Patch covers firmware-upload decoding, firmware transfer-table fields/layout,
power-table parsing, AtomBIOS bitfield conversions and AVFS constants.
Initial6.12.113 source comparison: several power-table LE conversions already
exist; the old BE-specific SMU_Entry layout remains, native-word firmware
upload remains in baseline, and VRConfig still uses a literal swapped constant.
Review each remaining difference against current structures/callers before
porting. Transfer-table and AVFS changes occur after our current protected-SMU
startup failure; do not present them alone as a fix for the earlier handshake.
Our earlier upload candidate matches the historical patch's LE decode intent
but failed in a warm-state trial. Complete historical patch has not been
ported or hardware tested here.

Reply from AMD/Mesa developer Michel Dänzer:
https://lists.freedesktop.org/archives/amd-gfx/2018-June/023022.html
Explains missing automatic GPU byte swapping and additional Mesa implications.
Author follow-up023026.html still seeks framebuffer success first. Preserve
the distinction between GPU capability, Linux driver implementation and full3D.

Bounded next action: map the author patch against our locked source, retain
already-upstream changes, separate startup fixes from post-start transfer/AVFS
and command-ring work. No firmware flashing, ABI change or base-version drift.

## 2026-11-06 comparison checkpoint

Whole-hunk comparison against locked 6.12.113: 38 historical hunks,
13 old contexts still matching, 7 new contexts already matching, 18 evolved.
These counts are review aids, not a patch-application or semantic acceptance test.
Machine-readable audit retained in ignored work/polaris-history-20261105/hunk-audit.json.

Current atom.c parameter interpreter reads get_unaligned_le32 and writes
cpu_to_le32 (lines 228 and 509 in this baseline). The public execution wrapper
passes the parameter buffer through. Consequently, historical packed-word
swapping cannot simply be copied without checking current union byte-field
layout and interpreter semantics; doing so risks an extra conversion.

Combined upload decoding plus logging was physically tested on November 6:
firmware lookup succeeds but protected SMU startup still fails, no framebuffer.
See builds/smu-diag-le-20261106. No complete historical patch is accepted yet.
Next isolate any remaining pre-start format mismatch, with a byte-level test
of the current parameter structures before another driver build.

## Explicit older-driver comparison — 2026-11-06

Linux6.12 Radeon evergreen.c still implements hardware BUF_SWAP_32BIT for BE
command rings. Primary source: https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/radeon/evergreen.c
That is the older hardware implementation to compare, not a universal software
adapter that transparently covers new ASICs.

Re-read023022 primary archive through urllib after web403. The quoted original
2018 Comstedt report explicitly says software LE ring writes make the ring test
pass, while trying hardware swap values0..3 has no effect. Thus the report already
contains a passing software-encoded command-ring test; earlier wording about
unfinished gfx must not obscure that. It does not establish full framebuffer/3D.
Dänzer's reply attributes missing hardware swapping to newer AMDGPU GPUs and
warns of Mesa shader implications. This closely matches our actual ring evidence.
Use it as a central driver-boundary reference, while keeping A1222/PPC32 acceptance
separate from that POWER9/RX550 report.
