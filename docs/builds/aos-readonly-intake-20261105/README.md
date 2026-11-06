# Read-only AmigaOS disk/media intake

Real CT240BX500SSD1 /dev/sda: read-only SFTP READ handles,68608 bytes total
for RDB/partition/header identification. No write handle, mount, repair,
partition reread or whole-disk copy. Three checksum-valid RDB partitions
AMDH0/AMDH1/AMDH2 use0x4e474601 (NGF1) and matching boot-header magic.
Kernel has AFFS module but AMIGA_PARTITION is disabled; no sda partition devices.
AFFS is not NGFS. No compatible reader was established; installed OS files were
not accessed or mounted. Filesystem format matches NGFileSystem documentation
inside the user's uploaded A1222 install ISO, including NGF1 identifier.

Existing private uploaded AmigaOneA1222InstallCD-53.37.iso and
EnhancerSoftware2.2 archive inspected with bounded7z listings/text extraction
on edge (not a new laptop extraction or OS boot). No commercial binaries or
full proprietary documentation copied into Git. Media versions do not prove
what is currently installed on the physical disk.

Enhancer2.2 contains RadeonRX.chip and its debug companion; driver README
version2.11 dated2022-01-26 lists Polaris RX cards and A1222 support. It notes
DPM support, embedded compressed microcode, historical PCI revision-ID and
PCIe root/bridge fixes. These are investigation leads, not proof of Linux's
current defect or a license to transplant commercial driver code. Separate
external polaris11_uvd.bin is also present; SMU microcode may be embedded as
README describes, not supplied as a Linux-shaped firmware directory.

Next installed-system comparison should export the active Kicklayout and
RadeonRX driver version/report from AmigaOS using the user's existing FTP.
Do not force-mount NGFS as AFFS or infer installed driver version from media.
