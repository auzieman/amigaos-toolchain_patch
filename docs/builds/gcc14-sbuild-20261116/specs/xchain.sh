#!/bin/bash
# Replica-local: build X extension libraries in order through the sbuild runner.
# Each line: <source> <lock> <representative amd64 binary>; all earlier X jobs are inputs.
S=/srv/data1/tabor-build/specs; W=work; C=bootstrap-source-cache; P=/home/tabor/amigaos-toolchain_patch; B=/srv/data1/tabor-build/linux-live-001
BASE="pkgconf-gcc14-002 libx11-gcc14-001 libxcb-gcc14-001 libxau-gcc14-001 libxdmcp-gcc14-001 libbsd-gcc14-001 libmd-gcc14-001 util-linux-gcc14-001 libselinux-gcc14-001 pcre2-gcc14-001 libsepol-gcc14-001 ${EXTRA_DONE:-}"
done_jobs=""
while read src lock rep; do
  [ -z "$src" ] && continue
  python3 $P/scripts/fetch-locked-component.py --lock $P/profiles/$lock.lock.json --component $src --cache $B/$C >/dev/null || { echo "fetch failed $src"; exit 1; }
  read n ts <<< "$($S/binnmu.sh $rep < /dev/null)"
  D=""; for j in $BASE $done_jobs; do D="$D --dep $W/sbuild-$j"; done
  NM=""; [ "${n:-0}" != 0 ] && [ "$n" != missing ] && NM="--binnmu $n"
  python3 $S/mkspec.py $src --lock profiles/$lock.lock.json --cache $C --profiles cross,nocheck,noudeb $NM $D --out $S/$src-gcc14-local.json >/dev/null
  python3 -c "import json,sys;s=json.load(open(sys.argv[1]));s['configure_cache']=json.load(open(sys.argv[2]))['configure_cache'];json.dump(s,open(sys.argv[1],'w'),indent=2)" $S/$src-gcc14-local.json $P/profiles/sbuild/libx11.json
  if [ -n "$NM" ]; then python3 -c "import json,sys;s=json.load(open('$S/$src-gcc14-local.json'));s['binary_nmu_timestamp']=sys.argv[1];json.dump(s,open('$S/$src-gcc14-local.json','w'),indent=2)" "$ts"; fi
  out=$($S/runspec.sh $src-gcc14 sbuild-$src-gcc14-${RUN:-001} | head -1 | cut -c1-110); echo "$src (binNMU ${n:-0}): $out"
  case "$out" in *debian-packages-built-not-target-installed*) done_jobs="$done_jobs $src-gcc14-${RUN:-001}";; *) grep -m4 -E "unsat-dependency|error:|Error [0-9]" $B/work/sbuild-$src-gcc14-${RUN:-001}/sbuild.log | cut -c1-160; exit 1;; esac
done
