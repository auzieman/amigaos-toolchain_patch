# Display/admin USB update — 2026-11-05

Exact SanDisk serial 03001919041721081205 reidentified. Root initially inspected
read-only/noload; saved network log confirms hardware SSH boot, and no GPU
re-probe log was present. No diagnosis of the user's later lockup is inferred.

Applied the 1.49MiB early Polaris firmware archive and temporary boot script;
kernel and DTB hashes unchanged, ext4 root and mem=3500M retained. Added direct
operator-key root SSH, password login remains disabled. No su/sudo binary or
known root password was added. Existing discarded-random-password hash permits
key login without account-lock rejection. Existing private host keys retained;
no client private key copied. Removed unsupported UsePAM from PAM-free sshd.
Private original shadow/config backups remain in ignored root-only work storage.

A separate R730 disk snapshot with early firmware booted in QEMU. Actual root
key login returned uid0; sshd -T confirms password auth disabled and publickey
required. Ordinary tabor key login, PTY and matched fractal also passed; known
QEMU fenv failure persists. Native hardware previously passed the ABI smoke.
No physical graphics success is claimed yet.

Installed /usr/sbin/a1222-qemu-inventory, exercised in QEMU. Root can run it
with a new private output directory. It captures live DTB, CPU/memory/resources,
PCI IDs/resources, interrupts and dmesg. It does not enable/read ROM, read raw
flash, collect credentials or alter PCI/driver settings. ROM acquisition is a
separate qualified step; dumps alone cannot implement absent QEMU peripherals.

Repeatable helpers: configure-rescue-admin.py, update-rescue-display-admin.py;
new root builds opt in via build-layered-rescue-usb.py --operator-root-ssh.
Both updated USB partitions remounted read-only and independently checked:
firmware/script hashes, unchanged kernel/DTB, root public-key ownership/mode,
and inventory bytes. Unmounted and powered off. Physical retry pending.

Temporary boot sequence is unchanged:

    usb reset
    fatload usb 0:1 0x09000000 /boot.scr
    source 0x09000000

No saveenv or firmware flashing. Next boot supports key-only root administration
for proper shutdown, GPU logs and private hardware inventory.
