#!/bin/sh
# #8 test A on the A1222: Xvfb :1 (1280x720x24) in the e8 chroot, then x8-redirect (Composite +
# XGetImage / XShmGetImage readback of a redirected window), then stop Xvfb.
chroot /e8 /bin/sh -c '
Xvfb :1 -screen 0 1280x720x24 -nolisten tcp -fp built-ins > /tmp/xvfb1.log 2>&1 & echo $! > /tmp/xvfb1.pid
for i in 1 2 3 4 5 6 7 8 9 10; do [ -S /tmp/.X11-unix/X1 ] && break; sleep 1; done
DISPLAY=:1 x8-redirect; echo "rc=$?"
kill $(cat /tmp/xvfb1.pid); sleep 1; tail -5 /tmp/xvfb1.log'
