A1222 historical SPE rescue root on ext4; no E desktop or GCC14 claim.
Use top-right USB port, mouse disconnected if enumeration fails.
Temporary manual launch (USB device 0):
usb reset
fatload usb 0:1 0x09000000 /boot.scr
source 0x09000000
Script support must be checked with help source. No saveenv.
Manual fallback:
fatload usb 0:1 0x04000000 /boot/uImage
iminfo 0x04000000
fatload usb 0:1 0x08000000 /boot/tabor.dtb
setenv bootargs root=PARTUUID=a1221105-02 rootfstype=ext4 rootwait rw init=/init mem=3500M console=ttyS0,115200 console=tty0 loglevel=8 ignore_loglevel panic=-1
bootm 0x04000000 - 0x08000000
Root waits for this image PARTUUID; no internal filesystem is mounted.
SSH tabor/key-only. Root local shell. /tmp/network-boot.log.
Power down cleanly before removal; ext4 retains host keys and logs.
Physical boot and display still unverified.
