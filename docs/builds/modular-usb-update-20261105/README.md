# Modular graphics USB update

Linux6.12.113-tabor-modular compiled on R730 with both board patches. Matching
modules installed in a distinct tree, host depmod metadata supplied. Separate
static BusyBox module tools built with the historical SPE SDK and executed on
physical hardware; no compiler upgrade claimed. Native BusyBox does not support
modprobe -S; no alternate-release dry run claimed. Native depmod invocation did
not accept the release argument; retained host-generated dependency metadata is
the installed source, not a successful native depmod result.

Verified all transferred payload hashes before installation. New FAT kernel and
script plus fallback script read back by SFTP. Original kernel/DTB/firmware and
root preserved; default boot.scr selects uImage-modular. FAT synced/unmounted.
Board identity guard passed. No saveenv or internal-disk writes. SSH reboot
command sent; post-reboot kernel/module and graphics acceptance pending.

Fallback from U-Boot: load /boot-known-good.scr at0x09000000 and source it.
The new default uses the same staging addresses, disk-root arguments and small
early firmware archive. Graphics remains unloaded until explicitly requested.

Normal reboot returned without resetting the minimal PID1 setup (uptime remained ~4479s). After sync and FAT unmount, direct BusyBox reboot -f disconnected SSH and the captured video changed from stale handoff output to black. New-kernel boot still awaits verification.

Post-reboot: physical SSH confirms6.12.113-tabor-modular, initial uptime42.62s. All nine SPE ABI checks pass again. No modules loaded initially; /proc/fb empty. First modprobe attempt stopped in userspace because CONFIG_DEFAULT_MODULES_DIR was empty, before GPU access. Separate corrected module-tools build fixes /lib/modules and modules.dep defaults; the staging recipe now records these requirements.

Corrected static loader executed successfully and resolved all AMDGPU module dependencies. Explicit modprobe then returned0 (module inserted), but GPU device probe still returned-22 and no framebuffer registered. Module insertion is not device initialization success. No further rebind attempted; preserve this boot for driver investigation. Full output retained in corrected-module-load.txt; ring wrap means it does not independently locate the first SMU error.
