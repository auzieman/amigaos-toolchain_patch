#!/bin/sh
set -eu
cache="$HOME/.cache/tabor-demos"
mkdir -p "$cache"
export DISPLAY="${DISPLAY:-:0}"
mode="${1:-help}"
[ "$#" -eq 0 ] || shift
case "$mode" in
 gl)
    echo 'Software GL diagnostic; renderer identity is printed below.'
    export LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=softpipe
    exec /usr/bin/gl-spe-demo --ppm "$cache/gl-readback.ppm" "$@"
    ;;
 fractal)
    /usr/bin/fractal-test > "$cache/fractal.log"
    grep 'FRACTAL_TIME\|FRACTAL_PASS' "$cache/fractal.log"
    exec /usr/bin/spe-fractal-view "$cache/fractal.log"
    ;;
 smp) exec /usr/bin/spe-smp-check ;;
 *) echo 'Usage: run-visual-demos gl [--frames N] | fractal | smp'; exit 1 ;;
esac
