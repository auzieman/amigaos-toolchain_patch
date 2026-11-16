#!/bin/bash
# Replica-local: install each M-A same powerpcspe .deb given as args next to its amd64 counterpart (dpkg checks shared files).
set -u; dpkg --add-architecture powerpcspe; apt-get update -qq >/dev/null 2>&1
same=(); names=()
for d in "$@"; do [ "$(dpkg-deb -f "$d" Multi-Arch)" = same ] && { same+=("$d"); names+=("$(dpkg-deb -f "$d" Package)"); }; done
amd=(); for n in "${names[@]}"; do apt-cache show "$n:amd64" >/dev/null 2>&1 && amd+=("$n:amd64"); done
apt-get install -y -qq "${amd[@]}" >/tmp/amd.log 2>&1 || { echo "amd64 install failed"; tail -3 /tmp/amd.log; }
dpkg --force-depends -i "${same[@]}" >/tmp/spe.log 2>&1; grep -E "trying to overwrite|different version|error processing" /tmp/spe.log | sort -u | head -20
echo "M-A same powerpcspe: ${#same[@]}, amd64 counterparts: ${#amd[@]}, dpkg problems: $(grep -c 'error processing archive' /tmp/spe.log)"
