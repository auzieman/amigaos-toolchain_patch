#!/bin/sh
# Replica-local: run one spec through the project's sbuild runner. $1 spec name, $2 output job.
B=/srv/data1/tabor-build/linux-live-001; P=/home/tabor/amigaos-toolchain_patch; S=/srv/data1/tabor-build/specs
cd /tmp && python3 $P/scripts/run-sbuild-package.py --project $P --base $B --spec $S/$1-local.json --output $B/work/$2 > /srv/data1/tabor-build/results/$2.log 2>&1
python3 -c "import json;r=json.load(open('$B/work/$2/receipt.json'));print('$2', r['status'], str(r.get('error',''))[:160], sorted(r.get('packages',{})))"
grep -A8 "have unmet dependencies" $B/work/$2/sbuild.log 2>/dev/null | head -9
