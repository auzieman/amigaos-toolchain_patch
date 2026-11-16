#!/bin/bash
# Replica-local: assemble the #38 A1222 bundle: run.c at every valid -fzero-call-used-regs mode x
# -O level and fe.c (rounding survives the zeroing), built with tabor2, plus libc6 and the GCC
# runtimes, run through the bundled ld.so.1 so nothing is installed on the board.
set -euo pipefail
B=/srv/data1/tabor-build/linux-live-001/work; Z=/srv/data1/tabor-build/work/zcur
O=${1:?output dir}; rm -rf "$O"; mkdir -p "$O"/{root,bin}
for d in $B/gcc14-glibc-003/libc6_*_powerpcspe.deb $B/gcc14-runtime-002/*.deb; do dpkg-deb -x "$d" "$O/root"; done
ln -sfn usr/lib "$O/root/lib"
docker run --rm -v "$O":/o -v $Z:/z:ro --entrypoint bash tabor-local/glibc-full-pkg -c '
set -e; powerpc-linux-gnuspe-gcc --version | head -1 > /o/toolchain.txt
for m in skip used-gpr used all-gpr all used-gpr-arg used-arg all-arg; do for o in O0 O1 O2 O3 Os; do
  powerpc-linux-gnuspe-gcc -$o -fzero-call-used-regs=$m /z/run.c -o /o/bin/run-$m-$o -lm; done
  powerpc-linux-gnuspe-gcc -O2 -fzero-call-used-regs=$m /z/fe.c -o /o/bin/fe-$m -lm; done'
cat > "$O/run.sh" <<'RUN'
#!/bin/sh
# #38 hardware check: -fzero-call-used-regs code from tabor2 on the A1222. Run from this directory.
H=$(cd "$(dirname "$0")" && pwd); R=$H/root; L="$R/usr/lib/powerpc-linux-gnuspe:$R/usr/lib"
X() { ${EMU:-} "$R/usr/lib/ld.so.1" --library-path "$L" "$@"; }  # EMU: optional emulator prefix for a dry run
REF="121932631128067367 4.25 2080600 3703703670368 3.625"; FE="1 0x1.5555555555556p-2 0x1.5555555555555p-2"
pass=0; fail=0
for b in "$H"/bin/run-*; do o=$(X "$b"); if [ "$o" = "$REF" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL $(basename "$b"): $o"; fi; done
for b in "$H"/bin/fe-*; do o=$(X "$b"); if [ "$o" = "$FE" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL $(basename "$b"): $o"; fi; done
echo "hw38: $pass passed, $fail failed"; [ $fail -eq 0 ]
RUN
chmod +x "$O/run.sh"; (cd "$O" && find bin root -type f | sort | xargs sha256sum > MANIFEST.sha256)
echo "bundle: $(du -sh "$O" | cut -f1), $(ls "$O/bin" | wc -l) programs"
