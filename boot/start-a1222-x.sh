#!/bin/sh
# Root console starts only the X server. Launch E/demos separately as tabor.
set -eu
/usr/bin/a1222-xorg-config
exec /usr/bin/Xorg :0 -config /tmp/tabor-xorg.conf -nolisten tcp -ac -noreset -logfile /tmp/Xorg-hardware.log
