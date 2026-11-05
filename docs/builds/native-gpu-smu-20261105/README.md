# Physical Polaris SMU failure — 2026-11-05

Updated rescue boots and root operator-key SSH works. HDMI still shows stale
U-Boot; no DRM framebuffer. Cleanup warnings wrapped original boot log, so a
live /dev/kmsg capture and one controlled bind reprobe retained the first cause.
Driver reaches 4GiB VRAM, 256MiB BAR/GART and UVD/VCE firmware discovery. BAR0
resize reports -22 but initialization continues. Fatal sequence is SMU Firmware
start failed, Failed to load SMU ucode, fw load failed and probe -22.

Exact source polaris10_smumgr.c:239 fails the SMU_PASS check after upload/start.
smu7_smumgr.c:454-464 uploads using native uint32_t reads into register writes
without explicit endian conversion. This is a big-endian AUDIT CANDIDATE, not
a demonstrated fix; establish expected firmware word order and MMIO conversion
before changing code. PCI resource mapping and SMU state also remain candidates.
DPM parameter is read-only live; no speculative change applied.

Similar firsthand report on different hardware (T1040/Polaris12):
https://community.nxp.com/t5/T-Series/AMDGPU-fails-during-Polaris12-SMU-firmware-startup/td-p/2367532
NXP suspects big-endian compatibility and supplies no fix. Corroboration only,
not proof for A1222/Polaris11.

Read-only native inventory collected under /root and retrieved privately via
SFTP, including live DTB, CPU/memory/interrupt maps and PCI resources. Hashes
only are committed; actual device blobs remain in ignored work. No ROM enable,
ROM dump or flash read/write performed. Rescue tar lacks creation support;
SFTP was used rather than rebuilding tools or copying unrelated data.
Next: review SMU upload endian handling and PCI windows; define one qualified
correction or temporary diagnostic boot, preserving the working SSH/root.
