# Legacy image review finds Tabor machine mismatch — 2026-11-05

Retained original image: /home/auzieman/Projects/Tabor_debian_8_powerpcspe_5.img.
Read its MBR and transferred only its 40MiB FAT16 boot partition to R730;
no full image extraction, mutation or local compile. Extracted boot files on
R730 with mtools. It has an ext4 second partition, matching the published
Debian USB disk-root recipe at https://wiki.amiga.org/index.php/AmigaOne_Linux.

Original tabor2.dtb identifies the root as varisys,TABOR, as does retained
A-EON 5.4-rc3 tabor3.dts. Vendor tabor_probe matches that same string. Legacy
kernel headers use zero load/entry: uImage.sdk17.2 is Linux-3.12.19-rt30_Daz_Tabor_04
(SHA256 e1623b20443810b3e120392ec2576ebf63a214e3b92be2765d0ab011ca73cb55);
uImage and uImage-3.18.24-JM are identical Linux-3.18.24-Tabor-JM
(SHA256 aa8f3a6094633289b3c697d8a5815db6a0ed5bd28e57265045d15d0c633beede).
These are comparisons, not a known-good fallback for the user's Polaris card.

Concrete local defect: our original machine forward-port patch selects
fsl,tabor, while the actual shipped DTB is varisys,TABOR (hash in receipts).
The exact compiled source under R730 work/tabor-live-002/source confirms this.
Linux 6.12 setup-common.c:614-655 iterates machine descriptions, skips a
nonmatching compatible and loops forever after reporting no suitable machine.
Without early visible output, this can present as the observed post-U-Boot
stall. This establishes a defective input pair; physical root cause acceptance
still requires the corrected binary to boot, and other defects may remain.

Added ordered patch 0002 changing only the machine compatible to the vendor
identity. git apply --check and application passed on an isolated copy of the
exact retained tabor.c. A semantic guard rejects original source/shipped DTB
and accepts the corrected source/same DTB. Packaging now requires exact-build
--machine-source and runs that guard before producing firmware images.
The guard does not prove that an arbitrary supplied source produced an ELF.
Old receipts, original patch, kernels and source trees are preserved.

No corrected kernel has been compiled or written to USB in this review.
Next: rebuild the same physical kernel baseline in a fresh, bounded R730
iteration with both patches, retain exact config/source hashes, run the
machine-match guard, package and replace only after verification. Do not
change root layout, compiler baseline or graphics settings in that experiment.
QEMU's separate generic-board kernel never exercised this board-match path.

Online references revisited: A-EON installation-guide public extract
https://eliyahu.org/tabor/data/Linux_installation_instructions_A1222_Tabor_v0.9.4.pdf
(serial-oriented and DIU/Radeon caveat); kernel U-Boot image format
https://www.kernel.org/doc/html/v5.4/powerpc/bootwrapper.html (uImage adds an image
header, no additional boot code). These do not justify replacing a correct
legacy uImage with a different wrapper without source evidence.
