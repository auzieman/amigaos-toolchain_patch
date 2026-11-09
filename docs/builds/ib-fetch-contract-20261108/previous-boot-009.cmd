# A1222 console live test; GPU load remains manual, no firmware saveenv.
echo Booting Tabor console candidate 009
if usb reset; then
 if fatload usb 0:1 0x04000000 /boot/e2e-009/uImage; then
  if iminfo 0x04000000; then
   if fatload usb 0:1 0x08000000 /boot/e2e-009/tabor.dtb; then
    setenv bootargs root=PARTUUID=a1221108-02 rootfstype=ext4 rootwait rw init=/init mem=3500M console=ttyS0,115200 console=tty0 loglevel=8 ignore_loglevel panic=-1
    if fatload usb 0:1 0x0a000000 /boot/uRamdisk-fw; then
     if iminfo 0x0a000000; then
      bootm 0x04000000 0x0a000000 0x08000000
     fi
    fi
   fi
  fi
 fi
fi
echo Boot returned; saved firmware settings unchanged.
