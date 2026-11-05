# First physical A1222 Linux SSH acceptance — 2026-11-05

Corrected kernel from commit d8c7f1d boots the actual A1222 from USB ext4.
Key-authenticated tabor login at 192.168.1.249 succeeded; kernel command line,
root PARTUUID and board MAC correlate with this physical trial. Host key was
recorded on first use in the isolated hardware-known-hosts file. No private key
was transferred. Uid is 1000, both CPUs report e500v2, MemTotal 3508464KiB under
intentional mem=3500M. This does not establish full 8GiB usability.

All nine existing ABI CLI checks pass, including fenv, which failed in QEMU.
This is one concrete hardware smoke test, not full library/unwind/ABI coverage.
No GL benchmark, desktop or GPU acceleration acceptance is claimed.

HDMI still shows the firmware's old image. dmesg identifies actual Polaris11
1002:67ff, then reports missing amdgpu/polaris11_sdma.bin (-2), failed SDMA
initialization and fatal GPU init. Ext4 root mount occurs later in the log.
This establishes a concrete graphics firmware/timing problem; review the full
firmware set and early built-in-driver availability before the next correction.
Do not mistake a stale HDMI image for a kernel hang or change the working root.

An initial issue comment incorrectly reported both SSH probes timed out before
the returned results were inspected. It was corrected immediately after the
positive banner and actual login. Retain authenticated evidence as authoritative.
