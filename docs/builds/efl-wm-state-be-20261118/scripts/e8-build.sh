#!/bin/sh
# #8 reproduction: auzieman's software-session chain, unmodified, with the GCC14 SPE SDK
# (gcc14-pkgsdk-003, tabor3) instead of GCC8: desktop-base (zlib/png/pixman) -> x11-clients ->
# session-deps (incl. Xvfb, x11vnc) -> efl-session (EFL 1.28.1, E 0.27.1, Terminology).
# Each stage's stage/ is the next one's --base-stage. Usage: e8-build.sh [first-step]
# The SDK is mounted at its install path, so its built-in sysroot and binutils resolve (libtool -shared links drop --sysroot).
set -e
W=/srv/data1/tabor-build/work/e8; T=/srv/data1/tabor-build/work/gcc14-pkgsdk-003/out/usr/lib/tabor-spe-toolchain
IMG=$(docker image inspect tabor-local/session --format '{{.Id}}'); mkdir -p $W/runs
# The GCC14 SDK has no built-in sysroot (-print-sysroot is /), and the scripts' libtool shared links
# drop the --sysroot in CFLAGS (GCC8's SDK had it built in). /spetools holds gcc/g++/cpp wrappers
# that add it; every other tool is a symlink to the SDK's.
X=/usr/lib/tabor-spe-toolchain; mkdir -p $W/spetools/bin
for f in $T/bin/*; do n=$(basename $f); case $n in *-gcc|*-g++|*-cpp|*-c++)
  printf '#!/bin/sh
exec %s/bin/%s --sysroot=%s/sysroot "$@"
' $X $n $X > $W/spetools/bin/$n; chmod +x $W/spetools/bin/$n ;;
  *) ln -sf $X/bin/$n $W/spetools/bin/$n ;; esac; done
# OpenSSL's libcrypto needs libatomic (64-bit atomics on PPC32). The SDK's own libatomic goes into
# an extra stage, as auzieman's libatomic001 did for GCC8 (build-session-deps.py --extra-stage).
A=$W/atomic-stage/usr/lib; if [ ! -e $A/libatomic.so.1 ]; then mkdir -p $A
  cp $T/powerpc-linux-gnuspe/lib/libatomic.so.1.2.0 $A/; ln -s libatomic.so.1.2.0 $A/libatomic.so.1; ln -s libatomic.so.1 $A/libatomic.so; fi
run() { n=$1; sc=$2; shift 2; echo "== $n $(date -u +%T)"; docker run --rm -v $W/project:/project:ro -v $W/cache:/cache:ro -v $T:/usr/lib/tabor-spe-toolchain:ro -v $W/runs:/work -v $W/spetools:/spetools:ro -v $W/atomic-stage:/atomic-stage:ro \
  --entrypoint python3 tabor-local/session /project/scripts/$sc --project /project --cache /cache --tools /spetools --sysroot /usr/lib/tabor-spe-toolchain/sysroot --image-id $IMG --jobs 8 "$@" > $W/runs/$n.out 2>&1 || { echo "FAILED $n"; tail -25 $W/runs/$n.out; exit 1; }; tail -2 $W/runs/$n.out; }
S=${1:-base}
case $S in base) run base build-desktop-base.py --work /work/base-001 ;; esac
case $S in base|x11) run x11 build-x11-clients.py --base-stage /work/base-001/stage --work /work/x11-001 ;; esac
case $S in base|x11|deps) run deps build-session-deps.py --base-stage /work/x11-001/stage --extra-stage /atomic-stage --work /work/deps-001 ;; esac
case $S in base|x11|deps|efl) run efl build-efl-session.py --base-stage /work/deps-001/stage --work /work/efl-001 ;; esac
echo "== done $(date -u +%T)"
