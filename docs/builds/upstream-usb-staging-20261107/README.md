# Inactive live USB staging — 2026-11-07

A1222 SSH healthy, kernel6.12.113-tabor-modular/no modules/taint0. Root device
8:18 is SanDisk sdb2; USB serial03001919041721081205 checked. Mounted FAT sdb1
read-only, hashed existing boot script/kernel/DTB/early firmware, then unmounted.
Hashes before and after inactive staging are identical.

Hardware7.3 bundle uses the clean accepted kernel,42 matching modules installed
with Kbuild modules_install/depmod, unchanged DTB and no firmware replacement.
Legacy U-Boot header/data CRC and gzip payload roundtrip verified; physical
kernel extent0x25164dc stays below the unchanged0x04000000 staging address.
Installed AMDGPU module equals accepted compiled module SHA exactly. Build/source
symlinks omitted from staged module tree; existing module versions not removed.
All Polaris11 firmware names listed by the new module exist in retained source
payload; actual installed firmware must still be checked before activation.

23,480,320-byte update.tar streamed server-to-A1222 through SSH without a local
archive copy. SHA256 ac86b14f4579f56ab8f6c89ec612e19e37126151d79a6996f9e0e1adc582795b
verified at /root/upstream-clean-20261107-001/update.tar. This is inactive staging,
not module installation or a boot-file update. No backup is claimed to exist yet.

Preserve /boot.scr SHAe5905665216e170cb4c6af4954f8ebee35810dc3427606bac9d485703f6d184d
and existing names boot/uImage-modular, boot/tabor.dtb, boot/uRamdisk-fw. Before
activation, retain verified rollback copies, validate target firmware and new
module tree, replace only kernel/DTB paths atomically and recheck script/firmware
hashes. Do not activate until the QEMU secondary-CPU gate is resolved or the
user explicitly chooses a hardware experiment with that limitation. No reboot.
