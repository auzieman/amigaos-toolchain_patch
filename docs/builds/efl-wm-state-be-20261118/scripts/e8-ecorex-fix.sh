#!/bin/sh
# #8 candidate fix, test build: ecore_x_icccm_state_get reads WM_STATE (format 32, which Xlib returns as
# an array of long) through its first byte; on big-endian that byte of NormalState (1) is 0 =
# WithdrawnState. Patch the efl-001 source tree, rebuild libecore_x incrementally in its own build
# directory (same image, mounts and SDK as e8-build.sh), and copy the library out.
set -e
W=/srv/data1/tabor-build/work/e8; T=/srv/data1/tabor-build/work/gcc14-pkgsdk-003/out/usr/lib/tabor-spe-toolchain
F=$W/runs/efl-001/efl-source/src/lib/ecore_x/ecore_x_icccm.c
grep -q "long state = ((long \*)prop_ret)\[0\]" $F || python3 - $F <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1]); s = p.read_text()
old = """   if ((prop_ret) && (num_ret == 2))
     {
        if (prop_ret[0] == WithdrawnState)
          hint = ECORE_X_WINDOW_STATE_HINT_WITHDRAWN;
        else if (prop_ret[0] == NormalState)
          hint = ECORE_X_WINDOW_STATE_HINT_NORMAL;
        else if (prop_ret[0] == IconicState)
          hint = ECORE_X_WINDOW_STATE_HINT_ICONIC;
     }"""
new = """   if ((prop_ret) && (num_ret == 2) && (format_ret == 32))
     {
        /* Format-32 property data is an array of long (Xlib). Compare the
         * element, not its first byte: on a big-endian host the first byte
         * of NormalState (1) is 0, which reads as WithdrawnState. */
        long state = ((long *)prop_ret)[0];

        if (state == WithdrawnState)
          hint = ECORE_X_WINDOW_STATE_HINT_WITHDRAWN;
        else if (state == NormalState)
          hint = ECORE_X_WINDOW_STATE_HINT_NORMAL;
        else if (state == IconicState)
          hint = ECORE_X_WINDOW_STATE_HINT_ICONIC;
     }"""
assert s.count(old) == 1, "anchor"
p.write_text(s.replace(old, new))
print("patched")
PY
docker run --rm -v $W/project:/project:ro -v $W/cache:/cache:ro -v $T:/usr/lib/tabor-spe-toolchain:ro -v $W/runs:/work -v $W/spetools:/spetools:ro \
  --entrypoint sh tabor-local/session -c 'export PATH=/spetools/bin:$PATH; cd /work/efl-001/efl-build && ninja src/lib/ecore_x/libecore_x.so.1.28.1 > /work/ecorex-fix.log 2>&1; echo "ninja rc=$?"; tail -2 /work/ecorex-fix.log'
L=$W/runs/efl-001/efl-build/src/lib/ecore_x/libecore_x.so.1.28.1; cp $L $W/libecore_x-fix.so; sha256sum $L $W/runs/efl-001/stage/usr/lib/libecore_x.so.1.28.1 | cut -c1-16
