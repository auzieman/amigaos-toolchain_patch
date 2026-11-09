# Rescue module tool defaults corrected — 2026-11-08

The new console USB included the old4de0ebee BusyBox module utility whose
CONFIG_DEFAULT_MODULES_DIR and CONFIG_DEFAULT_DEPMOD_FILE were both empty.
First normal modprobe stopped at userspace chdir(""); no GPU initialization
was attempted. -n/-d are not supported by this BusyBox variant, so a launcher
flag workaround was rejected after reading its actual source.

A private copied output/source tree on R730 sets /lib/modules and modules.dep,
then rebuilds with the same accepted GCC8 SPE SDK under2CPUs/2GiB. Binary
SHA256ae2d1ed0f6ecab70a6c26cec5778b9472a03c79aca7fe98d9feb3d360b44a912.
Physical -D dependency-only output resolves all13 installed dependencies with
/proc/modules still empty. The old binary is retained on USB as
/sbin/busybox-modules-before-path-fix; atomic installation is hash checked,
root synced and returned to read-only before a captured single actual bind.
Normal installed modprobe then returns0; no module/kernel source change was
needed for this setup failure. See dry-run.txt/install.txt and the separate
candidate008 hardware receipt.

The live image001 full-media receipt predates this one-file correction.
build-corrected.py creates a fresh image002 with the corrected utility; do not
redistribute image001 as a fixed module-loader image. The running Cruzer already
contains the persistent correction. No physical reflash/reboot was performed.
