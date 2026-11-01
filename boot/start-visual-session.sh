#!/bin/sh
# A direct-X diagnostic, deliberately separate from E's unresolved compositor.
set -eu
export DISPLAY="${DISPLAY:-:1}"
export PATH=/usr/bin:/usr/sbin:/bin:/sbin
if [ "${1:-}" != --existing-x ]; then
    Xvfb "$DISPLAY" -screen 0 1024x768x24 -nolisten tcp -ac -noreset >/tmp/Xvfb-visual.log 2>&1 &
    xvfb_pid=$!
    sleep 2
fi
listen=127.0.0.1
if grep -q QEMU /proc/device-tree/model; then listen=0.0.0.0; fi
x11vnc -display "$DISPLAY" -listen "$listen" -rfbport 5900 -nopw -forever -shared -noxdamage -noshm >/tmp/x11vnc-visual.log 2>&1 &
vnc_pid=$!
cleanup() { kill "$vnc_pid" 2>/dev/null || :; if [ -n "${xvfb_pid:-}" ]; then kill "$xvfb_pid" 2>/dev/null || :; fi; }
trap cleanup EXIT INT TERM
run-visual-demos fractal &
fractal_pid=$!
run-visual-demos gl --frames 120
wait "$fractal_pid"
