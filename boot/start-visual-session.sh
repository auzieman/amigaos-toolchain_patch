#!/bin/sh
# Direct-X diagnostics while E's compositor remains unresolved.
set -eu
export DISPLAY="${DISPLAY:-:1}"
export PATH=/usr/bin:/usr/sbin:/bin:/sbin
existing_x=false
film=false
for arg in "$@"; do
    case "$arg" in
        --existing-x) existing_x=true ;;
        --film) film=true ;;
        *) echo 'Usage: start-visual-session [--existing-x] [--film]' >&2; exit 2 ;;
    esac
done
xvfb_pid=
vnc_pid=
fractal_pid=
gl_pid=
cleanup() {
    trap - EXIT INT TERM HUP
    for pid in "$gl_pid" "$fractal_pid" "$vnc_pid" "$xvfb_pid"; do
        [ -z "$pid" ] || kill "$pid" 2>/dev/null || :
    done
}
trap cleanup EXIT INT TERM HUP
if ! "$existing_x"; then
    Xvfb "$DISPLAY" -screen 0 1024x768x24 -nolisten tcp -ac -noreset >/tmp/Xvfb-visual.log 2>&1 &
    xvfb_pid=$!
    sleep 2
fi
listen=127.0.0.1
if grep -q QEMU /proc/device-tree/model; then listen=0.0.0.0; fi
x11vnc -display "$DISPLAY" -listen "$listen" -rfbport 5900 -nopw -forever -shared -noxdamage -noshm >/tmp/x11vnc-visual.log 2>&1 &
vnc_pid=$!
run-visual-demos fractal &
fractal_pid=$!
# Validate a bounded first GL readback before offering the recording loop.
run-visual-demos gl --frames 120
if "$film"; then
    echo 'FILM_READY: live SPE fractal and Mesa software GL; QEMU timings only'
    while kill -0 "$fractal_pid" 2>/dev/null; do
        run-visual-demos gl --frames 3600 &
        gl_pid=$!
        wait "$gl_pid"
        gl_pid=
    done
else
    wait "$fractal_pid"
fi
