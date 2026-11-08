# Derfsss QEMU intake — 2026-11-08

Repository https://github.com/derfsss/qemu . Isolated sparse source checkout:
/srv/data1/tabor-build/source-review/derfsss-qemu-20261108 on R730.
Branches discovered: master6e9a825c1d4e7b62d072e99a89ecd1a74c7f0d55;
g5-amigaone91b22ec4c707bd46c64d3a53fd054dbe00ca898c. Checkout is detached
at the latter. VERSION reports11.0.50 (development version). License/COPYING
notices retained; files remain under their applicable upstream terms.

Latest branch commit changes only hw/ppc/amigaone.c: accepts970 input model,
selects970 interrupt wiring, and changes default7457 to970fx_v3.1. Its own
validation statement is machine creation/reset, not full OS boot or A1222.
This remains the Eyetech/Mai Teron machine; it is not P1022 or SPE hardware.

Source hw/ppc/e500plat.c still describes generic paravirtual e500 and defaults
to e500v2_v30. No dedicated A1222/Tabor machine source appears in hw/ppc.
Our captured control uses Debian QEMU10.0.13 with -M ppce500 -cpu e500v2,
TCG, snapshot disk. Thus the fork's G5 default cannot replace that SPE control.
No emulator, kernel, firmware, boot defaults or target images were changed.

GitHub master...g5-amigaone comparison is diverged (1882ahead/92behind),
not a small vendor-only patchset, and the compare file list is truncated.
Do not attribute all newer upstream changes to this author. Latest G5 patch
reviewed independently. A full upstream-base/delta audit remains open.

Next experiment, if selected: build this pinned source separately on R730 with
normal resource limits, run ppce500/e500v2 against the SAME immutable kernel,
snapshot root and SPE tests, then compare output with the existing10.0.13
control. G5/AmigaOS and minQEMU X5000 are separate experiments. No build or
runtime acceptance is claimed for this checkout; no Polaris hardware model or
DPM fix was identified in this bounded machine-source review.
