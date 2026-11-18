#!/bin/sh
# #8 reproduction on the replica: unpack toolchain_patch (origin/development) as the project and
# fill one source cache from profiles/{x11-sources,session-sources,desktop-seeds}.lock.json with the
# repo's own scripts/fetch-locked-component.py (size and sha256 checked). Files already in the
# replica's linux-live-001 caches are copied in first; the fetcher re-verifies them.
set -e
W=/srv/data1/tabor-build/work/e8; P=$W/project; C=$W/cache
mkdir -p $P $C; [ -f $P/scripts/fetch-locked-component.py ] || tar -xf $W/tcp-dev.tar -C $P
for d in /srv/data1/tabor-build/linux-live-001/*cache*; do cp -n $d/* $C/ 2>/dev/null || true; done
for L in x11-sources session-sources desktop-seeds; do
  for c in $(python3 -c "import json;print(' '.join(json.load(open('$P/profiles/$L.lock.json'))['components']))"); do
    python3 $P/scripts/fetch-locked-component.py --lock $P/profiles/$L.lock.json --component $c --cache $C > /dev/null && echo "ok $L $c" || echo "FAIL $L $c"
  done
done
ls $C | wc -l
