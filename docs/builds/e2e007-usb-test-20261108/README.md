# Complete candidate007 USB trial

The user authorized installation and a physical trial after the connected source
review, then requested updates to both the canonical toolchain and the public
forge. This is a manually authorized, bounded hardware experiment. The aggregate
offline qualification still reports BLOCKED for complete hardware acceptance;
its nineteen passing suites are not a claim that the GPU or console now works.

The R730 installer selected the complete `6.12.113-tabor-e2e-007` kernel,
43 matching modules, DTB and verified existing Polaris11 firmware on the
identified SanDisk. All80 bundle files passed readback. Root and FAT filesystem
checks passed before and after installation; both partitions are unmounted.
See [the installation receipt](install-receipt.json).

The existing rescue `/init`, SSH credentials and firmware initrd were preserved.
The ordinary `/boot.scr` now loads `/boot/e2e-007/` with the same load addresses,
root PARTUUID and boot arguments. Its source `/boot.cmd` now agrees with the
executed script and displays the correct007 banner. No partition or U-Boot
environment change was made. The prior003 kernel/modules remain installed, and
the exact previous script is retained as `/boot-before-e2e007.scr` on FAT.

The source/build receipt remains in
`../console-selected-path-20261108/build-receipt.json`. The intervening source
changes decode the six V1 raw-state clocks, preserve SMU/PSM transition failures,
and propagate DCE11 surface-programming errors. The last physical003 trial
passed decoder and both encoder primary ring tests but subsequently lost SSH
during the SCLK enabled-mask transition. That negative result remains relevant;
it does not constitute007 acceptance.

## Trial and rollback

Move the safely unmounted drive to the A1222 boot-capable USB port and select the
saved Linux entry. It continues to load ordinary `/boot.scr`; no new firmware
command should be needed. Verify release007, the exact installed module hash,
clean boot and unloaded GPU over SSH. Start off-board `/dev/kmsg` capture and
verify root is read-only before one normal installed `modprobe amdgpu` using
`scripts/test-polaris-offboard.py --installed-release 6.12.113-tabor-e2e-007`.
The module hash is in the receipt. Do not retry bind or unload after a fault.

Only after a healthy bind returns, use
`../console-selected-path-20261108/collect-console-state.sh` and confirm the
actual screen. `/proc/fb` registration alone does not establish readable scanout.
The retained rescue userspace provides a bootstrap shell, not a full Debian
getty/session. Desktop, acceleration and unrestricted RAM remain separate gates.

To choose the previous003 payload from the U-Boot prompt, use the existing saved
script load address with `/boot-before-e2e007.scr` instead of `/boot.scr`, then
`source` that address. This does not require saving a new firmware environment.
If restoring the default from another Linux host, copy the rollback script over
`/boot.scr` only after verifying the identified USB and backing up the007 script.

## Physical result

Candidate007 boot and the visible local console **PASS**. The user confirmed
readable terminal/text. Normal installed `modprobe amdgpu` returned0, SSH
survived, and kernel state shows `amdgpudrmfb`,1920x1080,32bpp,stride7680,
HDMI-A-1 connected/enabled and fbcon bound. At uptime244.01seconds the kernel
remained untainted and root remained read-only. The retained logs contain no
machine-check/completion-timeout signature. See [hardware summary](hardware-summary.json),
`console-state.txt` and `hardware-e2e007-002/` for the protected load receipt and
off-board kmsg.

The previously failing SCLK enabled-mask command0x145 now carries0xff and
receives response1. This agrees with the corrected state-clock pipeline, but
multiple changes were tested together, so their individual causality is not
isolated. GFX/SDMA/PowerPlay/DCE/UVD/VCE hw_init returns are0. The asynchronous
GFX indirect-buffer test still fails-110. No acceleration, Xorg/E, game or full
GPU workload acceptance is claimed. Root-port BAR assignment and GPU BAR resize
warnings remain recorded; they did not prevent this visible console.

The first harness invocation stopped at the read-only-remount gate before any
driver load: sshd had an open writable `/tmp/sshd.log` on root. Mounted32MiB
tmpfs on `/run`, preserved the old log, redirected its original pathname to
`/run/sshd.log`, and HUP-reopened the identified listener. After reconnecting,
the second invocation verified rootRO and performed the **only** GPU load of
this boot. The first invocation is retained as `hardware-e2e007-001/`; it was
not a failed GPU trial. One orphaned reader from that task-owned capture was
stopped. No GPU unload, rebind or reboot followed.

The console already has PID1's interactive BusyBox shell on tty1. At the user's
request, the existing Debian-built `bash-static`5.2.37 SPE package was verified
and its binary staged in `/run/bash`, leaving root read-only. The same binary
passes version/array checks under R730 QEMU e500v2 and on the physical A1222 CPU.
See `bash-static-receipt.json`. This is an ephemeral RAM tool, not a normal dpkg
installation or the complete Debian workstation. Launch it from the local
shell using `/run/bash --noprofile --norc -i`.
