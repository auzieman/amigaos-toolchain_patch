# Derfsss A1222 firmware source review — 2026-11-08

Pinned repository: https://github.com/derfsss/u-boot_A1222/tree/9bfbc801b8ebec66bb4860fe0e8d15db9d786626
Read six files: board/aeon/tabor/{tabor.c,video.c}, include/configs/tabor.h,
docs/{hardware.md,status.md,booting-amigaos.md}. Full source content and notices
cached in work/derfsss-uboot-review-20261108; hashes in intake.json.
Discord identity remains unverified. This is U-Boot, not received Linux GPU patches.

## Concrete comparisons

1. video.c explicitly reports RX560/Vega64 testing on X5000, not A1222.
   status.md confirms A1222 AmigaOS boot and keyboard, but marks PCIe graphics
   console not independently verified. Do not relabel this as a proven A1222
   Linux/Polaris fix.
2. Firmware POST executes the card's x86 VBIOS, chooses a linear VBE mode and
   translates its PCI bus framebuffer address with pci_bus_to_virt. Geometry,
   pixel format and scanline pitch are validated. A useful basis for a separate
   firmware-framebuffer handoff investigation; no Linux simple-framebuffer node
   or physical Linux fbcon acceptance was established by this review.
3. VGA bridge forwarding explicitly opens legacy VGA/I/O decode during POST
   and restores it afterward. Comments describe X5000 Vega bridge machine checks.
   This solves a firmware POST routing problem; our existing stock firmware
   displays and Linux ring tests pass before DPM_Enable. It is not evidence that
   copying this temporary bridge workaround repairs our later DPM transition.
4. PCIE1 memory bus0xe0000000 maps to CPU physical0xc40000000, size512MiB;
   I/O physical0xfffc20000 maps to bus0. Our off-board boot capture already
   reports exactly these memory and I/O ranges. Historical tabor3.dts agrees.
   The gross outbound-map mismatch hypothesis is weakened; inbound DMA windows,
   coherency and GPU DPM table addresses remain distinct and unverified here.
5. The source describes fixed board clocks, PCIe1-only slot use, and reference
   board differences (no PIXIS/ICS307). Documentation leaves PCIe clock-chip
   contents and several straps unverified. These are comparison inputs, not
   measured corrections to our hardware.

## Next bounded action

Audit the DPM table's actual serialized addresses/values against the owning
SMU7 SRAM/firmware contract and inspect the transition path for platform PCIe
power/link assumptions. Ask contributor for exact Linux patches separately.
Firmware-framebuffer handoff can be pursued for a console independently of
accelerated AMDGPU. Do not flash this firmware or issue another GPU bind merely
because source is available. No hardware mutations performed in this review.
