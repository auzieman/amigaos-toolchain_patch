#!/bin/bash
# Replica-local: assemble the #27 A1222 bundle. Test programs built with the packaged GCC14
# toolchain (tabor2) against the sbuild-built powerpcspe packages, plus those packages'
# libraries, run through the bundled ld.so.1 so nothing is installed on the board.
# Expected outputs come from the same programs built for x86-64 Debian (or fixed references).
set -euo pipefail
B=/srv/data1/tabor-build/linux-live-001/work; Z=/srv/data1/tabor-build/work/zcur
O=${1:?output dir}; rm -rf "$O"; mkdir -p "$O"/{root,bin,expected,data}
JOBS="gcc14-glibc-003 gcc14-runtime-002 sbuild-zlib-gcc14-003 sbuild-libffi-gcc14-002 sbuild-glib2.0-gcc14-001 sbuild-pcre2-gcc14-001
 sbuild-util-linux-gcc14-001 sbuild-libselinux-gcc14-001 sbuild-freetype-gcc14-001 sbuild-fontconfig-gcc14-001 sbuild-libpng1.6-gcc14-001
 sbuild-bzip2-gcc14-001 sbuild-brotli-gcc14-002 sbuild-expat-gcc14-001 sbuild-sqlite3-gcc14-001 sbuild-readline-gcc14-001
 sbuild-ncurses-gcc14-002 sbuild-openssl-gcc14-003 sbuild-libzstd-gcc14-001 sbuild-icu-gcc14-004 sbuild-libjpeg-turbo-gcc14-004"
for j in $JOBS; do for d in "$B/$j"/*_powerpcspe.deb; do
  case "$d" in *dbgsym*|*-dbg_*|*udeb*) continue;; esac
  case "$(basename "$d")" in libc6_*|libc6-dev_*|libc-bin_*|tabor-spe-lib*|zlib1g_*|minizip_*|libminizip1t64_*|lib*[0-9]_*|lib*t64_*|libffi8_*|sqlite3_*|openssl_*|icu-devtools_*|libjpeg-turbo-progs_*|fdisk_*|libglib2.0-0t64_*|libfreetype6_*|libfontconfig1_*|fontconfig-config_*) dpkg-deb -x "$d" "$O/root";; esac
done; done
ln -sfn usr/lib "$O/root/lib" 2>/dev/null || true
docker run --rm -v "$O":/o -v $Z:/z:ro -v /srv/data1/tabor-build/work/dyn-test:/d:ro -v $B:/w:ro --entrypoint bash tabor-local/glibc-full-pkg -c '
set -e; debs=""; for d in $(ls /w/sbuild-{glib2.0-gcc14-001,libffi-gcc14-002,pcre2-gcc14-001,zlib-gcc14-003,util-linux-gcc14-001,libselinux-gcc14-001,libsepol-gcc14-001,elfutils-gcc14-002,bzip2-gcc14-001,xz-utils-gcc14-001,libzstd-gcc14-001,lz4-gcc14-002,xxhash-gcc14-002,freetype-gcc14-001,fontconfig-gcc14-001,libpng1.6-gcc14-001,brotli-gcc14-002,expat-gcc14-001}/*_powerpcspe.deb); do case "$(dpkg-deb -f $d Section)" in libs|libdevel) debs="$debs $d";; esac; done
dpkg --force-depends -i $debs >/dev/null 2>&1 || true; export PKG_CONFIG_LIBDIR=/usr/lib/powerpc-linux-gnuspe/pkgconfig:/usr/share/pkgconfig
CC=powerpc-linux-gnuspe-gcc; $CC --version | head -1 > /o/toolchain.txt
powerpc-linux-gnuspe-g++ -O2 -pthread /d/t.cc -o /o/bin/cxx-dyn -latomic
$CC -O2 /z/ffi.c -o /o/bin/ffi -lffi
$CC -O2 /z/gtest.c -o /o/bin/glib $(pkgconf --cflags --libs gio-2.0 gobject-2.0)
$CC -O2 /z/ft.c -o /o/bin/ft $(pkgconf --cflags --libs freetype2 fontconfig)'
docker run --rm -v "$O/data":/o tabor-local/frozen-root-001 bash -c 'apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq fonts-dejavu-core >/dev/null 2>&1; cp /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf /o/'
printf '<?xml version="1.0"?>\n<fontconfig><dir>DATA</dir><cachedir>/tmp/hw27-fc-cache</cachedir></fontconfig>\n' > "$O/data/fonts.conf.in"
# Expected outputs (x86-64 Debian builds of the same sources, recorded earlier today, or fixed values).
cp $Z/glib-host.out "$O/expected/glib.out"; cp $Z/ft-host.out "$O/expected/ft.out"
printf 'ffi_call 3000000009.7509999 direct 3000000009.7509999 closure 5000000029\n' > "$O/expected/ffi.out"
printf 'caught unwind\nsqrt(2)=1.4142135623730951 n=300000 42\n' > "$O/expected/cxx-dyn.out"
cat > "$O/data/q.sql" <<'SQL'
create table t(x real, s text);
with recursive c(i) as (select 1 union all select i+1 from c where i<20000) insert into t select (i*0.1)/3.0 + 1e-9*i, printf('%08d', i*7919 % 100003) from c;
select printf('%.17g', sum(x)), printf('%.17g', avg(x)), printf('%.17g', min(x*x - 2.5)), count(*) from t;
select printf('%.17g', 1.0/3.0), printf('%.17g', exp(1.0)), printf('%.17g', sqrt(2.0)), printf('%.17g', pow(2.0, 0.5) - sqrt(2.0)), round(2.675, 2), cast('1e308' as real)*10;
select s from t order by s desc limit 1; select group_concat(s, ',') from (select s from t order by x limit 3);
SQL
sqlite3 :memory: < "$O/data/q.sql" > "$O/expected/sqlite.out"
head -c 1000000 /dev/urandom > "$O/data/blob.bin"; openssl dgst -sha256 -r "$O/data/blob.bin" | cut -d' ' -f1 > "$O/expected/sha256.out"
printf 'Grüße, 東京, Ελλάδα, ñandú\n' > "$O/data/utf8.txt"; printf 'Grusse, dong jing, Ellada, nandu\n' > "$O/expected/uconv.out"
cat > "$O/run.sh" <<'RUN'
#!/bin/sh
# #27 hardware check: packaged GCC14 powerpcspe libraries on the A1222. Run from this directory.
# Uses only the bundled loader and libraries; installs nothing; writes only under /tmp.
H=$(cd "$(dirname "$0")" && pwd); R=$H/root; L="$R/usr/lib/powerpc-linux-gnuspe:$R/usr/lib"
X() { ${EMU:-} "$R/usr/lib/ld.so.1" --library-path "$L" "$@"; }  # EMU: optional emulator prefix for a dry run off the board
pass=0; fail=0; chk() { if cmp -s "$2" "$H/expected/$1"; then echo "PASS $1"; pass=$((pass+1)); else echo "FAIL $1"; diff "$H/expected/$1" "$2" | head -5; fail=$((fail+1)); fi; }
uname -m; cat /proc/cpuinfo | grep -m1 -i "^cpu"
X "$H/bin/cxx-dyn" > /tmp/hw27-cxx.out; chk cxx-dyn.out /tmp/hw27-cxx.out
X "$H/bin/ffi" > /tmp/hw27-ffi.out; chk ffi.out /tmp/hw27-ffi.out
X "$H/bin/glib" > /tmp/hw27-glib.out; chk glib.out /tmp/hw27-glib.out
sed "s#DATA#$H/data#" "$H/data/fonts.conf.in" > /tmp/hw27-fonts.conf; FONTCONFIG_FILE=/tmp/hw27-fonts.conf X "$H/bin/ft" "$H/data/DejaVuSans.ttf" > /tmp/hw27-ft.out; chk ft.out /tmp/hw27-ft.out
X "$R/usr/bin/sqlite3" :memory: < "$H/data/q.sql" > /tmp/hw27-sqlite.out; chk sqlite.out /tmp/hw27-sqlite.out
X "$R/usr/bin/openssl" dgst -sha256 -r "$H/data/blob.bin" | cut -d' ' -f1 > /tmp/hw27-sha.out; chk sha256.out /tmp/hw27-sha.out
X "$R/usr/bin/uconv" -x 'Any-Latin; Latin-ASCII' "$H/data/utf8.txt" > /tmp/hw27-uconv.out; chk uconv.out /tmp/hw27-uconv.out
rm -rf /tmp/hw27.zip /tmp/hw27-unz; (cd "$H/data" && X "$R/usr/bin/minizip" -o -9 /tmp/hw27.zip blob.bin >/dev/null) && mkdir -p /tmp/hw27-unz && cd /tmp/hw27-unz && X "$R/usr/bin/miniunzip" -o /tmp/hw27.zip >/dev/null && cmp -s blob.bin "$H/data/blob.bin" && { echo "PASS minizip"; pass=$((pass+1)); } || { echo "FAIL minizip"; fail=$((fail+1)); }
echo "hw27: $pass passed, $fail failed"; [ $fail -eq 0 ]
RUN
chmod +x "$O/run.sh"; (cd "$O" && find bin root -type f | sort | xargs sha256sum > MANIFEST.sha256)
echo "bundle: $(du -sh "$O" | cut -f1), $(ls "$O/bin" | wc -l) programs, $(find "$O/root" -name '*.so*' | wc -l) libraries"
