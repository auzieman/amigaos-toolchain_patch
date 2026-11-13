# Incremental QEMU / USB workstation validation

Use the same apt/dpkg-managed powerpcspe root/package manifest for emulator and
USB candidates; retain separate kernel/device-tree/boot envelopes. QEMU does
not validate the physical PCIe GPU. Heavy assembly/emulation runs on R730.
Preserve the known boot script and rollback; never auto-select a block device.

After each accepted package wave, resolve/install genuine packages with apt in
an isolated candidate root, configure packages normally, and retain package
versions and source/artifact hashes. Do not populate a root with loose libraries
or replace its dpkg database. Preserve the previous passing root checkpoint.

Install `scripts/workstation-cli-check.sh` as a diagnostic in the candidate.
Run it inside the booted QEMU guest, recording console, exit status, kernel,
package manifest and image hash. Then run the same stage on the A1222 candidate
when that USB image is explicitly staged. It rejects non-powerpcspe dpkg roots
and performs no package installations or display initialization.

Stages:

* `base`: dpkg audit, apt dependency consistency, bash, coreutils and libc.
* `libs`: base plus compression and Python SSL/compression/SQLite imports.
* `apps`: preceding checks plus SSH config syntax and X/terminal/D-Bus tool
  startup. These are CLI checks, not a graphical session or network acceptance.

Missing tools/configuration fail the selected stage; do not label an earlier
partial package wave as a complete stage pass. Physical login, keyboard,
network/SSH reachability and later software X/E repaint remain explicit checks.
Do not start X or accelerated GL as a side effect of these CLI diagnostics.

2026-11-11: scaffold added and shell syntax checked only. No candidate root
assembled, QEMU boot executed, or thumbdrive modified by this change.
