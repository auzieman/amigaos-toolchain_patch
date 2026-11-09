#!/bin/sh
DISPLAY=:0 LD_LIBRARY_PATH=/lib /run/busybox-test-tools timeout 180 /run/busybox-test-tools chroot /opt/tabor-gl-20261109 /usr/bin/gl-spe-demo --frames 3600 --ppm /run/gl-cube.ppm > /run/gl-cube.log 2>&1
result=$?
echo "$result" > /run/gl-cube.exit
kill -TERM "$(cat /run/gl-Xorg.pid)"
