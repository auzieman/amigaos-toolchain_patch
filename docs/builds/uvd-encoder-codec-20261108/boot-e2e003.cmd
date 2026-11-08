# Matched A1222 kernel/modules test; saved firmware startup command unchanged.
echo Booting 6.12.113-tabor-e2e-001
if usb reset; then
 if fatload usb 0:1 0x04000000 /boot/e2e-003/uImage; then
  if iminfo 0x04000000; then
   if fatload usb 0:1 0x08000000 /boot/e2e-003/tabor.dtb; then
    setenv bootargs root=PARTUUID=a1221105-02 rootfstype=ext4 rootwait rw init=/init mem=3500M console=ttyS0,115200 console=tty0 loglevel=8 ignore_loglevel panic=-1
    if fatload usb 0:1 0x0a000000 /boot/uRamdisk-fw; then
     if iminfo 0x0a000000; then
      bootm 0x04000000 0x0a000000 0x08000000
     fi
    fi
   fi
  fi
 fi
fi
echo Rescue boot failed or returned; saved firmware settings unchanged.
