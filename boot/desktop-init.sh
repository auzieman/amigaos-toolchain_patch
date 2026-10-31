#!/bin/sh
# New RAM-root only. Keep the existing shell/network init as PID 1.
mkdir -p /var/lib/dbus
/usr/bin/dbus-uuidgen --ensure=/etc/machine-id
ln -s /etc/machine-id /var/lib/dbus/machine-id
exec /init
