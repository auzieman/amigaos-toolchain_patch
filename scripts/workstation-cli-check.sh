#!/bin/sh
# Run inside a booted SPE candidate (QEMU or A1222), never against the host root.
# Read-only checks; installation/configuration belongs to apt/dpkg assembly.
set -u
stage=${1:-base}
case "$stage" in base|libs|apps) ;; *) echo 'usage: workstation-cli-check.sh [base|libs|apps]' >&2; exit 2;; esac
arch=$(dpkg --print-architecture) || exit 1
[ "$arch" = powerpcspe ] || { echo "FAIL: expected powerpcspe root, got $arch" >&2; exit 1; }
failed=0
check() {
 label=$1; shift
 if "$@"; then printf 'PASS: %s\n' "$label"; else printf 'FAIL: %s\n' "$label"; failed=1; fi
}
echo "CLI checkpoint: $stage; target=$arch"
uname -a
check 'package database audit' sh -c 'out=$(dpkg --audit) || exit; [ -z "$out" ] || { printf "%s\n" "$out"; exit 1; }'
check 'installed dependency consistency' apt-get -s --no-download check
check 'bash and arithmetic' bash --noprofile --norc -c 'test "$((17 * 19))" = 323'
check 'coreutils runtime' /usr/bin/env --version
check 'libc loader/runtime' getconf GNU_LIBC_VERSION
check 'writable temporary directory' test -w /tmp
if [ "$stage" != base ]; then
 check 'compression runtime' sh -c 'printf "SPE runtime check\n" | gzip -c | gzip -dc | grep -qx "SPE runtime check"'
 check 'Python shared-library imports' python3 -c 'import ctypes,ssl,zlib,bz2,lzma,sqlite3; print(ssl.OPENSSL_VERSION, sqlite3.sqlite_version)'
fi
if [ "$stage" = apps ]; then
 check 'SSH configuration syntax' /usr/sbin/sshd -t
 check 'D-Bus tool runtime' dbus-daemon --version
 check 'X server runtime' Xorg -version
 check 'terminal runtime' xterm -version
fi
echo "CLI checkpoint complete: failures=$failed"
exit "$failed"
