# Complete AMDGPU requirements and firmware USB audit

Pinned firmware-amd-graphics20250410-2/all package SHA256
22fa89a699044d92e54c9a3b6d737da4f474245fa2001d3cbc039b74d56ac933.
Re-extracted and assembled on R730; no download refresh or laptop extraction.
The exact running kernel is6.12.113-tabor-modular.

Before installation, all42 Polaris10/11 firmware names advertised by the exact
AMDGPU module were already present on physical USB and matched the package.
This includes alternate SMU names. No missing/corrupted Polaris blob was found.
All13 modules resolved by modprobe -D amdgpu also hash-match the accepted modular
kernel build. These checks address files and dependency closure, not working
hardware/firmware compatibility or successful GPU initialization.

Installed the full package firmware payload (892 firmware paths, including
symlink targets) into /lib/firmware with package license/docs. /usr/lib/firmware
now links to that existing firmware directory, without changing loader search
parameters. Every one of892 installed files was hashed on the real A1222 and
matched the pinned package. Retained original subset in
/root/full-amd-firmware-20261105-001/firmware-before; retained the original .deb,
payload archive and manifest/receipt on USB. Root has ample free space.

This minimal rescue does not provide dpkg package management; this is explicit
payload installation, not a claim of a dpkg-configured Debian workstation.
Scripts are exact run snapshots using the recorded R730/work paths, not a
replacement package manager. Boot kernel/DTB/script and installed modules are
unchanged. No GPU reload or reboot performed as part of this audit. The earlier
experimental module remains in memory after its failed probe; default installed
module remains the original. Current SMU failure remains unresolved.
