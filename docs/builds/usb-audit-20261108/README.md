# R730 USB read-only audit and trace recovery

Identified SanDisk Cruzer Glide serial03001919041721081205 as /dev/sde, root PARTUUIDa1221105-02. Both e2fsck-fn and fsck.fat-n return0. Root inspected with ro,noload to prevent journal replay; FAT mounted read-only. Both partitions unmounted afterward. No boot, filesystem, module or firmware change.

The selected boot script, versioned e2e-003 kernel and installed module match the retained known artifacts. The new0024state-decoding candidate is not installed.

Six existing PPC trace files were recovered from /root to R730 hardware-evidence/recovered-usb-20261108 and verified against source SHA256. Combined matched register events:3665760. Raw traces remain on the server, not copied into Git or loaded on the laptop. Per-file sizes/hashes/register channels are in recovered-traces.json.

Coverage remains filtered: older SMU-index/handshake/upload traces and one graphics-register trace. Large event counts mostly include repeated polling and do not imply complete command/table capture. No raw VBIOS file was found in the inspected root/log/tmp locations. Recovery adds retained evidence, not a complete simulation reference.

Initial identity parsing lacked lsblk --tree; corrected before any mounting. The audit and recovery scripts assert serial, partition identity and unmounted state before access. See receipt.json and filesystem logs. Leave USB unchanged pending broader qualification.
