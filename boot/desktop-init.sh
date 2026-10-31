#!/bin/sh
# New RAM-root only. Keep the existing shell/network init as PID 1.
# Mount device nodes before services open /dev/null. The native rescue init
# also requests devtmpfs; its existing mount error is harmless if already mounted.
if [ ! -e /dev/null ]; then
    /bin/mount -t devtmpfs devtmpfs /dev || exit 1
fi
mkdir -p /var/lib/dbus /tmp/.X11-unix
chmod 1777 /tmp/.X11-unix
/usr/bin/dbus-uuidgen --ensure=/etc/machine-id
ln -s /etc/machine-id /var/lib/dbus/machine-id
# System and session buses have distinct sockets and lifetimes.
if [ -x /usr/bin/dbus-daemon ]; then
    /usr/bin/dbus-daemon --system --fork --nopidfile > /tmp/dbus-system.log 2>&1
fi
exec /init
