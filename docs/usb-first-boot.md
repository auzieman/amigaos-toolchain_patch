# First physical USB boot

Target: fresh source-built Linux/SPE shell first. E/GL remain later increments.
The user authorizes preparing the thumbdrive when the build is ready. The
inserted device was a 14.3 GiB SanDisk Cruzer Glide, currently holding an amd64
Debian installer; re-identify it immediately before any write. Device names
such as `/dev/sdb` are observations, not durable write targets.

Use a rear motherboard USB port directly for the first trial, per the user's
hardware recollection. Avoid a hub/front-panel extension initially. The public
Tabor manual documents USB boot but does not establish a rear-only rule; port
mapping still needs verification on this board/firmware revision.

Readiness gates before writing:

- A source-built static shell actually boots and accepts commands in QEMU.
- Board kernel/DTB and firmware-accepted image format/load ranges are verified.
- A local console and USB keyboard are supported, since no serial cable is
  available. Existing config enables FSL DIU/framebuffer console, but the
  initial board patch does not restore DIU board hooks; this is not a verified
  local console. The user uses HDMI, and its controller/card still needs to
  be identified. Radeon DRM is not yet enabled. USB HID is a module, so the
  board payload must include it or rebuild it into the kernel.
- Boot files, checksums and recoverable logs are staged independently of the
  stick. The read-only staging manifest currently says not firmware-boot-ready.
- Confirm the exact removable device and its existing contents before writing;
  preserve internal disks and existing firmware boot defaults.

The legacy A1222 Linux procedure uses FAT-loaded kernel and DTB plus `bootm`.
Its old filenames/load addresses are reference evidence, not automatically a
safe map for our larger modern kernel/initramfs. Do not use the old zero-pad
wrapper as a verified uImage producer, or run `saveenv` during initial trials.
The new QEMU-only ATI driver does not belong on this physical Linux medium.

Sources: [A1222 manufacturer manual](https://intuitionbase.com/sites/default/files/2024-09/trm_tabor_1.0.3.pdf),
[legacy Linux procedure](https://wiki.amiga.org/index.php/AmigaOne_Linux).
