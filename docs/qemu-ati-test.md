# Private AmigaOS ATI experiment

`profiles/qemu/amigaos-ati.json` pins QEMU 11.1.3 and the author's ATI driver 0.1.
The source archive's detached signature was verified against release signer
`CEACC9E15534EBABB82D3FA03353C9CEF108B584`, published on QEMU's download page.
Host build requirements include a C compiler, Python, Meson/Ninja, GLib and
Pixman development files. Build locally without a system installation:

```sh
python3 scripts/build-qemu-ppc.py \
  --archive downloads/qemu-next/qemu-11.1.3.tar.xz \
  --work work/qemu-replay-001
```

The ATI driver is personal/non-commercial and **no redistribution**. Download
from the author into ignored `downloads/`; do not commit it, include it in a
release image, or put it on the physical A1222 stick. It drives QEMU ati-vga,
not a physical Radeon. Upstream QEMU licensing is separate.

For a real accelerated-2D guest test, first prepare a machine-matched AmigaOne
or PegasosII Kickstart directory using the official updates and BBoot recipe.
Our uploaded A1222 kernel is not that prerequisite. The private overlay helper
preserves original files, checks the driver hash, and rejects A1222 Kicklayout:

```sh
python3 scripts/prepare-os4-ati-overlay.py \
  --machine amigaone --kickstart private/amigaone/Kickstart \
  --driver downloads/qemu-next/qemu-ati-vga-driver-0.1.zip \
  --output private/amigaone/ati-test-001
```

With BBoot 0.8 or newer and appropriate matching media, the configuration is:

```sh
qemu-system-ppc -machine amigaone -accel tcg -m 512 \
  -rtc base=localtime -nic none -vga none \
  -device ati-vga,model=rv100,guest_hwcursor=on \
  -kernel private/bboot -initrd private/amigaone/ati-test-001/Kickstart.zip \
  -drive media=cdrom,format=raw,readonly=on,file=private/AmigaOneInstallCD.iso \
  -vnc 127.0.0.1:8
```

This recipe does not create an installed disk. Matching hardware/kernel support
must be established before interpreting a stall as performance. QEMU device
availability, firmware output, successful OS boot, loaded driver and measured
2D behavior are separate results. A successful emulated desktop does not prove
Linux SPE ABI support, physical A1222 boot, or hardware GL acceleration.

Sources: [QEMU releases](https://www.qemu.org/download/),
[BBoot recipe](https://zero.eik.bme.hu/~balaton/qemu/amiga/aos_bboot.html),
[ATI driver](https://zero.eik.bme.hu/~balaton/qemu/amiga/qemu-ati-vga-driver-latest.html).
