#!/bin/sh
# #8 sweep, test build: ecore_x_dnd_version_get reads the format-32 XdndAware version through its first
# byte ((int)*prop_data); ecore_x_window_prop_property_get returns format-32 items as unsigned int, so
# on big-endian version 5 reads as 0. Patch the efl-002 tree (0001 already applied), rebuild
# libecore_x incrementally, copy it out; build the x8-dnd probe against the efl-002 stage.
set -e
W=/srv/data1/tabor-build/work/e8; T=/srv/data1/tabor-build/work/gcc14-pkgsdk-003/out/usr/lib/tabor-spe-toolchain
F=$W/runs/efl-002/efl-source/src/lib/ecore_x/ecore_x_dnd.c
grep -q "((unsigned int \*)prop_data)\[0\]" $F || python3 - $F <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1]); s = p.read_text()
old = "        int version = (int)*prop_data;\n"
new = ("        /* Format-32 items come back as unsigned int (ecore_x_window_prop_property_get).\n"
       "         * Read the element, not its first byte: on a big-endian host the first byte of\n"
       "         * version 5 is 0, and every XDND-aware window would look unaware. */\n"
       "        int version = (int)((unsigned int *)prop_data)[0];\n")
assert s.count(old) == 1, "anchor"
p.write_text(s.replace(old, new)); print("patched")
PY
docker run --rm -v $W/project:/project:ro -v $T:/usr/lib/tabor-spe-toolchain:ro -v $W/runs:/work -v $W/spetools:/spetools:ro -v $W:/w \
  --entrypoint sh tabor-local/session -c 'export PATH=/spetools/bin:$PATH; cd /work/efl-002/efl-build && ninja src/lib/ecore_x/libecore_x.so.1.28.1 > /work/dnd-fix.log 2>&1; echo "ninja rc=$?"; tail -1 /work/dnd-fix.log
S=/work/efl-002/stage; export PKG_CONFIG_SYSROOT_DIR=$S PKG_CONFIG_LIBDIR=$S/usr/lib/pkgconfig:$S/usr/share/pkgconfig
/spetools/bin/powerpc-linux-gnuspe-gcc -O2 -Wall -o /w/x8-dnd /w/x8-dnd.c $(pkgconf --cflags --libs ecore-x x11) -Wl,-rpath-link,$S/usr/lib && echo probe built'
cp $W/runs/efl-002/efl-build/src/lib/ecore_x/libecore_x.so.1.28.1 $W/libecore_x-dnd.so; sha256sum $W/libecore_x-dnd.so | cut -c1-16
