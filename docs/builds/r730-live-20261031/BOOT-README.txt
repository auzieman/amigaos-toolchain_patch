A1222 experimental Linux hardware-rescue USB; no E desktop yet.
Manual U-Boot trial only. Use rear/direct USB for the first trial, as recalled
by the operator; no rear-only firmware requirement has been established.
Identify the USB storage device with usb reset / usb storage / fatls first.
Example for USB device0 partition1 (adjust if the device enumeration differs):

usb reset
fatls usb 0:1
fatload usb 0:1 0x04000000 /boot/uImage
iminfo 0x04000000
fatload usb 0:1 0x08000000 /boot/tabor.dtb
fatload usb 0:1 0x0a000000 /boot/uRamdisk
iminfo 0x0a000000
setenv bootargs console=ttyS0,115200 console=tty0 rdinit=/init panic=-1
bootm 0x04000000 0x0a000000 0x08000000

Do not saveenv. These are temporary settings, not an internal-disk install.
Wait for amdgpu initialization and SHELL_READY on HDMI. If no usable output,
retain OBS capture rather than assuming a successful boot. Serial is optional.

At the shell: cat /etc/tabor-rescue.txt
Wired DHCP and SSH start automatically in the background.
Inspect /tmp/network-boot.log. Manual retry: udhcpc -i INTERFACE; /etc/start-ssh
SSH user tabor uses the privately retained operator key. No password/root SSH.
SPE/glibc: spe-abi-check --cli
Fractal: fractal-test > /tmp/fractal.log
Native ABI results, GPU output and board boot remain unverified until observed.
