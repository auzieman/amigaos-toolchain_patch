#!/bin/sh
# Ordinary-user software X11 session inside the isolated QEMU guest.
set -eu
export HOME=/home/tabor USER=tabor LOGNAME=tabor
export PATH=/usr/bin:/usr/sbin:/bin:/sbin
export XDG_RUNTIME_DIR=/tmp/tabor-runtime
export XDG_CACHE_HOME=/home/tabor/.cache
export DISPLAY=:0
export ECORE_EVAS_ENGINE=software_x11
export ELM_ENGINE=software_x11
mkdir -p "$XDG_RUNTIME_DIR" "$XDG_CACHE_HOME"
chmod 700 "$XDG_RUNTIME_DIR"
unset DBUS_SESSION_BUS_ADDRESS
Xvfb :0 -screen 0 1280x720x24 -nolisten tcp -ac -noreset -extension MIT-SHM > /tmp/Xvfb.log 2>&1 &
echo "XVFB_PID=$!"
sleep 3
# The guest has NAT only; its RFB port is published solely to host loopback.
x11vnc -display :0 -listen 0.0.0.0 -rfbport 5900 -nopw -forever -shared -noxdamage > /tmp/x11vnc.log 2>&1 &
echo "X11VNC_PID=$!"
echo 'E_SESSION_START: software X11; no GL or physical Radeon acceptance'
exec dbus-run-session -- enlightenment_start -nopause
