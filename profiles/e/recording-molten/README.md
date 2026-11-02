# Conservative Molten Steel recording profile

Status: **prepared, tested on an isolated display, not promoted**. The E
compositor still produces a black desktop (#8). Keep the proven direct-X
fractal/GL recording session on display1/noVNC6089 until E renders correctly.

`upstream-e.src` is the unchanged standard configuration from Debian e17
0.27.1-1 / Enlightenment0.27.1. `e.src` derives from it under the accompanying
upstream COPYING license. It keeps basic shell, task, pager, clock, file and
configuration modules; disables optional audio/network/power/service modules;
selects the still Molten Steel wallpaper; uses available C locale; and disables
recording-time blanking, DPMS and automatic locking. The existing Liquid Menu
Molten Steel theme is selected through EFL's supported ELM_THEME setting.

Compile the source on the build server, using the retained session-tools image:

    eet -e safe-e.cfg config e.src 1

The executed tooling image is pinned in the evidence receipt. `start-test.sh`
uses a private guest HOME and separate Xvfb display2/VNC5901, software rendering,
no DRI swap buffers and no MIT-SHM. It never changes the normal user's profile
or package installation state. Place generated safe-e.cfg in that private HOME;
the script's startup input is that file. Inspect/stop an existing test before
reusing this display and HOME. It is a diagnostic launcher, not first-boot policy.

The latest test starts E and precaches the selected theme, but stays black.
The theme archive contains desktop groups as well as Elementary groups; this
is not evidence of a fixed rendering pipeline. The temporary display/VNC and
host loopback forward were stopped after capturing evidence. Test results:
`docs/builds/e-molten-safe-20261101/`.
