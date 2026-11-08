# Historical Tabor graphics intake — 2026-11-08

The retained A-EON5.4-rc3 configuration enables DRM_RADEON and explicitly
disables DRM_AMDGPU. The retained tabor_5.4-1.patch modifies platform85xx
Kconfig/Makefile/tabor.c and FSL audio files, not AMDGPU. Inventory records
per-file hashes and full patch path list. This is a source/config finding,
not an exhaustive claim about every historical image.

Primary firsthand controls:
- https://amigax1000.blogspot.com/2016/02/classic-amiga-emulation-on-amigaone.html
  describes working A1222 graphical applications on HD7750 and accelerated
  games after changing to HD5450.
- https://forum.hyperion-entertainment.com/viewtopic.php?t=5125
  May2025: user reports working old SPE Debian/Lubuntu/Void, but no Linux
  after changing to Polaris. Maintainer identifies5.4 as final A1222 kernel.

Archive links are https://www.supertuxkart-amiga.de/amiga/kernel54.html and
https://www.fun-kart-racer.de/2bb57b2bbf87b668a94c/lxtest.html . Web requests
returned502. No recovered .deb, completed binary package comparison or working
Polaris fix is claimed. Keep historical binaries outside the active Trixie root.
Next intake: recover archive index/package manifests and inspect control/scripts,
kernel config, module/firmware lists and corresponding source patches on R730.
The modern physical failure remains DPM_Enable on AMDGPU; historical Mesa/Xorg
packages cannot themselves repair that kernel/PCIe failure.

Archive recovery update: direct HTTP succeeded on R730. Full index and79-link manifest are retained here; server cache is /srv/data1/tabor-build/historical-tabor-20261108. Four Mesa tar bundles selected for resumable acquisition and member/control-file inventory. This supersedes the failed HTTPS-only availability check above. No active system package installs.
