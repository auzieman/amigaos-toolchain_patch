#!/bin/sh
# Run inside an existing X session. Never loads drivers or changes the session.
set -eu
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 NEW-EVIDENCE-DIRECTORY" >&2
    exit 2
fi
: "${DISPLAY:?Run from the X session to be tested}"
for tool in glxinfo glxgears timeout; do
    command -v "$tool" >/dev/null || { echo "Missing package tool: $tool" >&2; exit 2; }
done
umask 077
mkdir "$1"
out=$(cd "$1" && pwd)
uname -a > "$out/kernel.txt"
cat /proc/cmdline > "$out/cmdline.txt"
printf 'DISPLAY=%s\nLIBGL_ALWAYS_SOFTWARE=%s\nGALLIUM_DRIVER=%s\n' \
    "$DISPLAY" "${LIBGL_ALWAYS_SOFTWARE-unset}" "${GALLIUM_DRIVER-unset}" > "$out/environment.txt"
if command -v dpkg-query >/dev/null; then
    dpkg-query -W > "$out/packages.txt"
fi
{
    for dev in /sys/bus/pci/devices/*; do
        [ -r "$dev/class" ] || continue
        case $(cat "$dev/class") in
            0x03*)
                echo "$dev"
                cat "$dev/vendor" "$dev/device"
                readlink "$dev/driver" || true
                ;;
        esac
    done
} > "$out/display-pci.txt"
timeout 30 glxinfo -B > "$out/glxinfo.txt" 2>&1
echo 'Showing gears for 20 seconds. Check motion, colors and window repaint.'
set +e
timeout --signal=TERM --kill-after=5 20 glxgears -info > "$out/gears.txt" 2>&1
code=$?
set -e
printf '%s\n' "$code" > "$out/gears-exit.txt"
case $code in
    124) echo "Visual interval finished. Evidence: $out" ;;
    *) echo "Gears ended unexpectedly ($code). Inspect $out/gears.txt" >&2; exit 1 ;;
esac
echo 'This records a GL session; human visual inspection and renderer identity determine acceptance.'
