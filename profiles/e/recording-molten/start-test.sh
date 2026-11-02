#!/bin/sh
set -eu
export HOME=/home/tabor/e-molten-safe USER=tabor LOGNAME=tabor
export PATH=/usr/bin:/usr/sbin:/bin:/sbin DISPLAY=:2
export XDG_RUNTIME_DIR="$HOME/runtime" XDG_CACHE_HOME="$HOME/.cache"
export ELM_THEME=/usr/share/elementary/themes/Molten-Steel-Theme-Liquid-Menu-20261026.edj
export LANG=C LC_ALL=C EVAS_NO_DRI_SWAPBUF=1
export ECORE_EVAS_ENGINE=software_x11 ELM_ENGINE=software_x11 E_COMP_ENGINE=sw
mkdir -p "$HOME/.e/e/config/standard" "$XDG_RUNTIME_DIR" "$XDG_CACHE_HOME"
chmod 700 "$XDG_RUNTIME_DIR"
cp /usr/share/enlightenment/data/config/standard/*.cfg "$HOME/.e/e/config/standard/"
cp "$HOME/safe-e.cfg" "$HOME/.e/e/config/standard/e.cfg"
Xvfb :2 -screen 0 1024x768x24 -nolisten tcp -ac -noreset -extension MIT-SHM >"$HOME/Xvfb.log" 2>&1 &
echo "$!" > "$HOME/Xvfb.pid"
sleep 2
x11vnc -display :2 -listen 0.0.0.0 -rfbport 5901 -nopw -forever -shared -noxdamage -noshm >"$HOME/x11vnc.log" 2>&1 &
echo "$!" > "$HOME/x11vnc.pid"
exec dbus-run-session -- /bin/sh -c '
    printf "%s\n" "$DBUS_SESSION_BUS_ADDRESS" > "$HOME/session-bus"
    exec enlightenment_start -profile standard -nopause
'
