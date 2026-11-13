# QEMU console and PNY safety recheck

Restarted retained software-e011 QEMU command in isolated
`software-cli-20261111-001`, with kernel/initramfs hashes verified,2CPU/10GiB
host cap and8GiB guest RAM. Kernel reached SHELL_READY/NETWORK_SSH_READY;
tabor SSH login reports ppc. Desktop4 console uses a separate new known_hosts
file populated from ssh-keyscan over the authenticated R730 connection. Older
known_hosts retained. This is the old bootstrap root, not the new Debian root;
no package-managed installation acceptance or graphical test claimed.

PNY serial0700993AAC40D602 is115.4GiB on R730, currently sde, NTFS Backups.
Prior file recovery completed rsync exit0; raw-image backup was incomplete
and previous raw reads reported bad sectors. Mounted part2 read-only at
/mnt/pny-check-ro. Running tabor-pny-backup-verify-20261111 uses rsync -aHAXnc
--delete --itemize-changes: dry-run checksum comparison only, no deletion or
source/destination changes. Log:
/srv/data1/tabor-build/backups/pny-0700993AAC40D602-20261108/verify-20261111.log

No formatting, cleaning, defragmentation or partition changes yet. Wait for
verification and inspect differences/I/O errors before destructive reuse.
Defragmentation is unnecessary for the proposed fresh Linux filesystem.
