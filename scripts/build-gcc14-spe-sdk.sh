#!/bin/bash
# Portable GCC14 powerpc-linux-gnuspe SDK recipe (e500v2 SPE, double in GPRs, IBM long
# double 128): Debian gcc-14 14.2.0-19 DFSG + the GCC 8.5 powerpcspe imports + the
# patches/gcc/gcc14-spe-candidate series, glibc 2.41 + patches/glibc, Linux UAPI headers.
# Same stages as docs/builds/gcc14-spe-port-20261107 (stage 1),
# gcc14-runtime-20261107 (glibc) and gcc14-sdk-20261108/build.sh (final), with no lab paths.
#
# Run in docker/Dockerfile.gcc14-spe-sdk with this repository at $RECIPE (read-only):
#   WORK=/work/sdk CACHE=/work/cache PREFIX=/opt/tabor-gcc14-spe scripts/build-gcc14-spe-sdk.sh
# Pins and hashes come from the repository: manifest.json (gcc-14),
# profiles/toolchain-bootstrap.json (gcc-8.5.0), profiles/debian-trixie.lock.json (glibc
# and linux). Missing files are fetched into $CACHE and every file is hash-checked.
# Each stage leaves $WORK/<stage>.done; a rerun resumes after the last finished stage.
#
# binutils are Debian's powerpc-linux-gnu-* (SPE instructions via -me500). Every make
# step gets the *_FOR_TARGET tools explicitly (issue #33). The SDK also gets
# PREFIX/powerpc-linux-gnuspe/bin/{ar,as,...} for GCC's own tool search and
# PREFIX/bin/powerpc-linux-gnuspe-{ar,...} for autotools/meson $host-tool lookups.
# Output: $WORK/out$PREFIX (compiler, runtimes, sysroot).
# Package-managed compiler (Debian cross builds against libc6-dev:powerpcspe, as #14 did for
# GCC8): PREFIX=/usr/lib/tabor-spe-toolchain INSTALLED_SYSROOT=/ MULTIARCH=1. The bootstrap
# sysroot then serves only as --with-build-sysroot for the target runtimes.
set -euo pipefail
RECIPE=${RECIPE:-$(cd "$(dirname "$0")/.." && pwd)}
WORK=${WORK:?WORK}; CACHE=${CACHE:?CACHE}; PREFIX=${PREFIX:-/opt/tabor-gcc14-spe}
INSTALLED_SYSROOT=${INSTALLED_SYSROOT:-$PREFIX/sysroot}; MULTIARCH_OPT=${MULTIARCH:+--enable-multiarch}
J=${JOBS:-$(nproc)}; OUT=$WORK/out; SR=$OUT$PREFIX/sysroot; T=powerpc-linux-gnuspe
BIN=/usr/bin/powerpc-linux-gnu-; TOOLS="ar as ld nm ranlib readelf objcopy objdump strip"
mkdir -p "$WORK" "$CACHE"
log() { echo "[$(date +%H:%M:%S)] $*"; }
done_() { [ -f "$WORK/$1.done" ]; }
mark() { touch "$WORK/$1.done"; log "stage $1 done"; }
export MAKEINFO=:
BU="AR_FOR_TARGET=${BIN}ar RANLIB_FOR_TARGET=${BIN}ranlib NM_FOR_TARGET=${BIN}nm"
COMMON="--target=$T --disable-bootstrap --disable-multilib --disable-nls --disable-libsanitizer
  --disable-libquadmath --disable-libgomp --enable-checking=release --with-cpu=8548
  --with-long-double-128 --enable-e500-double --with-as=${BIN}as --with-ld=${BIN}ld"

if ! done_ fetch; then
  python3 - "$RECIPE" "$CACHE" <<'EOF'
import hashlib, json, sys, urllib.request
from pathlib import Path
r, c = Path(sys.argv[1]), Path(sys.argv[2])
want = []
m = json.loads((r/'patches/gcc/gcc14-spe-candidate/manifest.json').read_text())
want += [(f['filename'], f['url'], 'sha256', f['sha256']) for f in m['gcc14_debian_source']['files']]
g = json.loads((r/'profiles/toolchain-bootstrap.json').read_text())['gcc']
want.append((g['filename'], g['url'], 'sha512', g['sha512']))
lock = json.loads((r/'profiles/debian-trixie.lock.json').read_text())['components']
for comp in ('glibc', 'linux'):
    want += [(f['filename'], f['url'], 'sha256', f['sha256']) for f in lock[comp]['files']]
for name, url, algo, digest in want:
    p = c/name
    if not p.exists():
        print('fetch', url, flush=True)
        urllib.request.urlretrieve(url, str(p) + '.part'); Path(str(p) + '.part').rename(p)
    h = hashlib.new(algo); h.update(p.read_bytes())
    if h.hexdigest() != digest:
        sys.exit(f'hash mismatch: {name}')
    print('ok', name, flush=True)
EOF
  mark fetch
fi

if ! done_ sources; then
  rm -rf "$WORK/src"; mkdir -p "$WORK/src"; cd "$WORK/src"
  tar -xf "$CACHE/gcc-8.5.0.tar.xz"
  dpkg-source --no-check -x "$CACHE/gcc-14_14.2.0-19.dsc" gcc14-debian > /dev/null
  mkdir gcc14 && tar -xf "$(ls gcc14-debian/gcc-14.2.0*.tar.* | head -1)" -C gcc14 --strip-components=1
  python3 "$RECIPE/scripts/prepare-gcc14-spe-candidate.py" --gcc8 "$WORK/src/gcc-8.5.0" --gcc14 "$WORK/src/gcc14"
  dpkg-source --no-check -x "$CACHE/$(python3 -c "import json;print(json.load(open('$RECIPE/profiles/debian-trixie.lock.json'))['components']['glibc']['dsc'])")" glibc > /dev/null
  python3 - "$RECIPE" <<'EOF'
import hashlib, json, sys
from pathlib import Path
r = Path(sys.argv[1])
for p in json.loads((r/'patches/glibc/series.json').read_text())['patches']:
    if hashlib.sha256((r/p['path']).read_bytes()).hexdigest() != p['sha256']:
        sys.exit('glibc patch hash: ' + p['path'])
EOF
  for p in $(grep -v '^#' "$RECIPE/patches/glibc/series"); do
    patch -d glibc -p1 --batch --forward --no-backup-if-mismatch -s < "$RECIPE/patches/glibc/$p"
  done
  dpkg-source --no-check -x "$CACHE/$(python3 -c "import json;print(json.load(open('$RECIPE/profiles/debian-trixie.lock.json'))['components']['linux']['dsc'])")" linux > /dev/null
  mark sources
fi

if ! done_ headers; then
  rm -rf "$SR"; mkdir -p "$SR/usr"
  make -C "$WORK/src/linux" ARCH=powerpc INSTALL_HDR_PATH="$SR/usr" headers_install > "$WORK/headers.log" 2>&1
  mark headers
fi

if ! done_ stage1; then
  rm -rf "$WORK/b-stage1"; mkdir -p "$WORK/b-stage1"; cd "$WORK/b-stage1"
  # shellcheck disable=SC2086
  "$WORK/src/gcc14/configure" $COMMON --prefix=/opt/tabor-gcc14-stage1 --enable-languages=c \
    --without-headers --disable-shared --disable-threads --disable-libatomic > "$WORK/stage1-configure.log" 2>&1
  make -j"$J" all-gcc > "$WORK/stage1-gcc.log" 2>&1
  make -j"$J" $BU all-target-libgcc > "$WORK/stage1-libgcc.log" 2>&1
  mark stage1
fi
XGCC="$WORK/b-stage1/gcc/xgcc -B$WORK/b-stage1/gcc/"

if ! done_ glibc; then
  rm -rf "$WORK/b-glibc"; mkdir -p "$WORK/b-glibc"; cd "$WORK/b-glibc"
  env CC="$XGCC --sysroot=$SR" BUILD_CC=gcc CXX=false \
      CFLAGS='-O2 -g0 -mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double -mlong-double-128' \
      AR=${BIN}ar RANLIB=${BIN}ranlib AS=${BIN}as LD=${BIN}ld NM=${BIN}nm OBJDUMP=${BIN}objdump \
      READELF=${BIN}readelf OBJCOPY=${BIN}objcopy STRIP=${BIN}strip \
    sh -c "'$WORK/src/glibc/configure' --build=x86_64-linux-gnu --host=$T --prefix=/usr \
      --with-headers='$SR/usr/include' --disable-werror --disable-nscd --enable-kernel=3.2 \
      > '$WORK/glibc-configure.log' 2>&1 && make -j$J > '$WORK/glibc-build.log' 2>&1 \
      && make -j$J install_root='$SR' install > '$WORK/glibc-install.log' 2>&1"
  mark glibc
fi

if ! done_ final; then
  rm -rf "$WORK/b-final" "$OUT$PREFIX/bin" "$OUT$PREFIX/lib" "$OUT$PREFIX/libexec" "$OUT$PREFIX/$T"
  mkdir -p "$WORK/b-final"; cd "$WORK/b-final"
  # shellcheck disable=SC2086
  "$WORK/src/gcc14/configure" $COMMON $MULTIARCH_OPT --prefix="$PREFIX" --with-sysroot="$INSTALLED_SYSROOT" \
    --with-build-sysroot="$SR" --enable-languages=c,c++ --enable-shared --enable-threads=posix \
    > "$WORK/final-configure.log" 2>&1
  make -j"$J" $BU all-gcc all-target-libgcc all-target-libstdc++-v3 all-target-libatomic > "$WORK/final-build.log" 2>&1
  make -j"$J" $BU DESTDIR="$OUT" install-gcc install-target-libgcc install-target-libstdc++-v3 \
    install-target-libatomic > "$WORK/final-install.log" 2>&1
  mark final
fi

# binutils for GCC's tool search and for $host-prefixed lookups (relative links into /usr/bin).
mkdir -p "$OUT$PREFIX/$T/bin" "$OUT$PREFIX/bin"
for t in $TOOLS; do
  [ -x "${BIN}$t" ] || { echo "missing ${BIN}$t"; exit 1; }
  ln -sfn "${BIN}$t" "$OUT$PREFIX/$T/bin/$t"
  ln -sfn "${BIN}$t" "$OUT$PREFIX/bin/$T-$t"
done

G=$OUT$PREFIX/bin/$T-gcc
printf '#ifndef __SPE__\n#error no SPE\n#endif\ndouble add(double a, double b) { return a + b; }\n' > "$WORK/probe.c"
$G -O2 -S "$WORK/probe.c" -o "$WORK/probe.s" && grep -q efdadd "$WORK/probe.s" && log "emits efdadd"
printf '#include <stdio.h>\nint main(void){printf("hi\\n");return 0;}\n' > "$WORK/hello.c"
$G --sysroot="$SR" -O2 "$WORK/hello.c" -o "$WORK/hello"
"$OUT$PREFIX/bin/$T-ranlib" --version | head -1
log "SDK at $OUT$PREFIX"
