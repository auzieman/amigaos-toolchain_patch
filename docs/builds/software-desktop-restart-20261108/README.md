# Use accepted scanout for software X/E before accelerated GL

User clarification after the console/fractal milestone:2D is sufficient to
advance X11 and software-rendered Enlightenment. Accelerated GL is a separate
workstream; the GFX IB timeout does not itself require postponing all X/E work.
Keep the working007 kernel, matched modules and boot rollback.

Measured physical foundation:

* Readable1920x1080/32bpp HDMI console and correct coloured CPU/SPE Mandelbrot.
* Verified native pixel order, stride7680 and complete framebuffer readback.
* VT/fbcon, evdev, USB HID, Unix sockets, SysV IPC, tmpfs, devtmpfs, inotify
  and epoll enabled in the actual007 config.
* Keyboard event0/1/2 nodes exist. No pointing device is present in the current
  input inventory; INPUT_MOUSEDEV is unnecessary for the selected libinput/evdev
  path. Normal udev/session permissions remain necessary in a desktop root.

The current USB is a rescue `/init`/BusyBox environment, not a configured Debian
desktop. Bash is staged in RAM, not installed by dpkg. Do not copy old manual
E/Xvfb overlays onto it and claim correct package state. The old partial E
session had black client interiors and remains negative evidence. The package
inventory review found existing xinit output, while inspected xorg-server/EFL/E
package receipts remain dependency-blocked; no new X/E package build or target
installation is claimed by this checkpoint.

Prepared explicit test profiles:

* `profiles/images/a1222-xorg-fbdev.conf`: fbdev plus shadow framebuffer,
  existing `/dev/fb0`, no forced resolution; depth24 uses32bpp storage.
* `profiles/images/a1222-xorg-modesetting-software.conf`: alternative DRM KMS
  dumb-buffer route with AccelMethod none, shadow pixels, software cursor and
  DRI3 page flipping disabled. It is not an automatic retry after a fault.

Options are checked against Debian Trixie's primary manpages:
[fbdev](https://manpages.debian.org/trixie/xserver-xorg-video-fbdev/fbdev.4.en.html)
and [modesetting](https://manpages.debian.org/trixie/xserver-xorg-core/modesetting.4.en.html).
These are prepared configurations, not executed Xorg acceptance. Do not install
both profiles or change the active display from this review step.

Next assembly uses the frozen source/archive inputs, qualified SPE foundation,
normal apt/dpkg configuration and the package seeds in
`profiles/images/a1222-graphical-shell.json`. It must include actual Xorg, fbdev,
input/libinput, fonts, xinit/xterm, udev, D-Bus/session permissions and E/Terminology
with their dependencies. The canonical Debian port workflow owns dependency
resolution and sbuild; the old name-ordered manual stager is not the default.
No baseline refresh or unqualified GCC14 package-wide rebuild is authorized by
the existence of a framebuffer. Keep compiler/runtime qualification distinct.

Acceptance order: real X terminal and repaint/input on the physical display,
then software-rendered E and overlapping client windows. Check actual E/EFL
engine settings before launch; do not invent environment switches. After that,
Mesa software GL is useful but remains distinct from a repaired hardware GFX
IB test and Radeon OpenGL acceleration. SSH/root protection stays independent.
