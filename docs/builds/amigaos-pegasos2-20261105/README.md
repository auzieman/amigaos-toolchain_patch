# Separate Pegasos II AmigaOS guest

Prepared on R730 at /home/owner/amigaos-pegasos2-20261105-001 after the user
requested a second QEMU machine, accepting another board for AmigaOS testing.
Existing Linux/e500 guests, images and the A1222 entry probe remain unchanged.
This G4 guest is for ordinary AmigaOS application/SDK testing, not SPE ABI,
Linux/glibc, physical A1222, or Radeon acceptance.

Configuration: Pegasos II,7457 CPU,512MiB guest memory, SM501 graphics,
independent8GiB sparse raw disk (initial allocated bytes4096), loopback VNC
port5912 reserved for the real run, guest network disabled. Preparation and
loader probe used1CPU/1GiB R730 user services, not laptop emulation.

Fetched BBoot0.8 from the author's versioned Codeberg release. Archive/binary
hashes are pinned in profiles/qemu/amigaos-pegasos2.json. Source and COPYING
were inspected and retained alongside the binary on R730 (GPLv2 text and
upstream component notices). Hashes were observed from the HTTPS release,
not verified against an independent detached signature. No proprietary OS
payload is committed. Original ISO was not altered or attached as mismatched
media to this guest.

Actual two-second loader probe reached BBoot0.8, enumerated/configured PCI
host, graphics, IDE, USB and audio functions, then reported the intentionally
missing initrd. QEMU was terminated afterward; no VM is left running and no OS
installation occurred. This is a successful VOF/BBoot setup check, not an
AmigaOS or Workbench boot. Receipt includes exact serial and command evidence.

Remaining private inputs: Pegasos II AmigaOS installation ISO and the prepared
Pegasos II Kickstart.zip with matching official kernel update and emulated
SM502 graphics driver. The existing A1222/Enhancer files do not establish these
inputs. Launcher rejects an A1222/Tabor-labelled Kicklayout for this side guest.
It preserves the ISO read-only and only writes to the new guest disk. It records
input hashes/run logs and bounds the run. A real installer run still requires
explicit observation of boot and subsequent installation checkpoints; timeout
or a live QEMU process does not imply success.

Once those files exist on R730, the launch pattern is:

    systemd-run --user --wait --pipe --collect \
      --unit=amigaos-pegasos2-test \
      --property=CPUQuota=100% --property=MemoryMax=1G \
      python3 /home/owner/amigaos-pegasos2-20261105-001/launch.py \
      --guest /home/owner/amigaos-pegasos2-20261105-001 \
      --iso /private/Pegasos2InstallCD.iso \
      --kickstart /private/Kickstart.zip --seconds 600

VNC binds127.0.0.1:5912 only during that run; use the existing SSH/noVNC pattern
when the guest has actual boot media. Do not open additional desktop windows
or a public VNC listener merely for preparation. The lab-specific preparation
script refuses an existing guest directory and never truncates an old disk.
Source preparation and launch scripts are tracked; guest disk/media remain
outside Git. Python bytecode check of the deployed launcher passed.

Primary recipe:
https://zero.eik.bme.hu/~balaton/qemu/amiga/aos_bboot.html
BBoot release:
https://codeberg.org/qmiga/bboot/releases/tag/v0.8
QEMU boards:
https://qemu-project.gitlab.io/qemu/system/ppc/amigang.html

2026-11-05 online media lookup: read-only listings of the uploaded A1222 ISO
and Enhancer archive found no Pegasos/Peg2 alternate kernel or SM502 driver.
Hyperion offers an official Pegasos II Final Edition ISO digital download:
https://www.hyperion-entertainment.com/index.php/where-to-buy/direct-downloads/321-amigaos-41-final-edition-for-pegasos
Their announcement lists digital purchase with a registration serial:
https://www.hyperion-entertainment.com/index.php/news/36-amigaos-4x/322-amigaos-41-final-edition-for-pegasos-2-is-now-available-digitally
Update3 announcement lists updated Pegasos II and other platform kernels and
registered-user downloads:
https://www.hyperion-entertainment.com/index.php/news/36-amigaos-4x/325-update-3-for-amigaos-41-final-edition-available
The BBoot recipe specifically documents the Update2 kernel preparation path;
Update3 suitability is not assumed without inspecting its actual payload.
No account accessed, serial registered, purchase made or commercial ISO
downloaded. Official product page was dispatched to the existing Opera session,
as requested; launcher reported Opening in existing browser session. No Chrome
launch or browser-default change. Existing registration access should be checked
before obtaining another copy; do not infer an entitlement to a different
platform edition merely from A1222 ownership.
