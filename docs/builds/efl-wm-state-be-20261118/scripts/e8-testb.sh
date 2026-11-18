#!/bin/sh
# #8 test B on the A1222, in the e8 chroot on a fresh Xvfb :2 (1280x720x24, MIT-SHM on):
#   1. control: terminology and elementary_test without a window manager or compositor;
#   2. E (standard profile, software_x11, dbus-run-session) as user tabor, then the same clients.
# x8-shot saves the screen and gives each client window's black-pixel share. Output: /e8/tmp/b/*
chroot /e8 /bin/sh -c '
pkill -x Xvfb; sleep 1; rm -f /tmp/.X2-lock /tmp/.X11-unix/X2; mkdir -p /tmp/b; rm -f /tmp/b/*; chmod 1777 /tmp/b; mkdir -p /tmp/tabor-runtime; chown 1000:1000 /tmp/tabor-runtime; chmod 700 /tmp/tabor-runtime
Xvfb :2 -screen 0 1280x720x24 -nolisten tcp -ac -noreset -fp built-ins > /tmp/b/xvfb.log 2>&1 &
for i in 1 2 3 4 5 6 7 8 9 10; do [ -S /tmp/.X11-unix/X2 ] && break; sleep 1; done
U="export HOME=/home/tabor USER=tabor DISPLAY=:2 XDG_RUNTIME_DIR=/tmp/tabor-runtime ECORE_EVAS_ENGINE=software_x11 ELM_ENGINE=software_x11 E_CONF_PROFILE=standard;"
echo "== 1 control: clients without E"
su -s /bin/sh tabor -c "$U terminology > /tmp/b/term1.log 2>&1 & elementary_test > /tmp/b/elmt1.log 2>&1 &"
sleep 25; DISPLAY=:2 x8-shot /tmp/b/shot1-noe.ppm
pkill -x terminology; pkill -x elementary_test; sleep 2
echo "== 2 E session"
su -s /bin/sh tabor -c "$U dbus-run-session -- enlightenment_start -nopause > /tmp/b/e.log 2>&1 &"
sleep 60; DISPLAY=:2 x8-shot /tmp/b/shot2-e.ppm
su -s /bin/sh tabor -c "$U terminology > /tmp/b/term2.log 2>&1 & elementary_test > /tmp/b/elmt2.log 2>&1 &"
sleep 30; DISPLAY=:2 x8-shot /tmp/b/shot3-e-clients.ppm
echo "== E log (selected)"; grep -a -E "ERR|CRI|timeout|async|non-finite|dtoa" /tmp/b/e.log /home/tabor/.e-log.log 2>/dev/null | sort | uniq -c | sort -rn | head -25
echo "== processes"; ps | grep -E "enlightenment|terminology|elementary|Xvfb" | grep -v grep
'
echo "taint=$(cat /proc/sys/kernel/tainted)"
