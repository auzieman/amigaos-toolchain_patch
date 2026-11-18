#!/bin/sh
# #35: kmstest3 over formats and modes on HDMI (1 s bars, 120 cube frames each), one line per run.
B=/opt/a1222-gl-spe3/bin; E=/opt/a1222-gl-spe3/exp457; export HOME=/tmp; cd $B
{ for m in 1920x2160@60 1920x1080@60 3840x2160@30 1280x720@60 1920x1080@120; do
  for f in XR24 BX24 AR24 BA24 XB24; do
    out=$(KMS_MODE=$m KMS_FORMAT=$f ./kmstest3 1 120 2>&1); rc=$?
    echo "$m $f rc=$rc | $(echo "$out" | grep -E 'SETUP FAIL|ADDFB|drmModeAddFB2|page flip failed|CUBE' | tr '\n' ' ') | $(echo "$out" | grep 'BO bytes.*RED' | sed 's/.*RED *//')"
  done; done
  echo "taint=$(cat /proc/sys/kernel/tainted)"; dmesg | grep -i -E 'error|fail|warn|bug' | grep -v PWR_TRACE | tail -5; echo DONE; } > $E/kms-matrix.out 2>&1
