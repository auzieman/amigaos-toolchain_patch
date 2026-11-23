#!/bin/sh
# #35: does fbcon get the CRTC back when a KMS client leaves it set? CRTC fb id and mode from
# modetest -p before and after: (1) exit without restoring, (2) SIGKILL while page flipping,
# (3) the same at another mode. The fbcon fb is the one the CRTC shows before any client runs.
B=/opt/a1222-gl-spe3; R="$B/lib/ld.so.1 --library-path $B/lib"; export HOME=/tmp; cd $B/bin
crtc() { $R $B/bin/modetest -M amdgpu -p 2>/dev/null | awk '/^CRTCs:/{c=1;next} c&&/^[0-9]/{print "crtc",$1,"fb",$2,"size",$4; exit}'; }
{ echo "before: $(crtc)"
  KMS_NORESTORE=1 ./kmstest3 1 60 2>&1 | grep -E 'CRTC left|CUBE'; sleep 1; echo "after exit without restore: $(crtc)"
  ./kmstest3 0 100000 > /tmp/k3-kill.log 2>&1 & p=$!; sleep 4; kill -9 $p; wait $p 2>/dev/null; sleep 1
  echo "after SIGKILL while flipping: $(crtc) | $(grep -c . /tmp/k3-kill.log) log lines"
  KMS_MODE=1280x720@60 KMS_NORESTORE=1 ./kmstest3 1 60 2>&1 | grep -E 'CRTC left|CUBE'; sleep 1; echo "after 1280x720 exit without restore: $(crtc)"
  cat /sys/class/graphics/fb0/virtual_size /sys/class/graphics/fb0/modes 2>/dev/null | tr '\n' ' '; echo
  echo "taint=$(cat /proc/sys/kernel/tainted)"; dmesg | grep -v PWR_TRACE | tail -5; echo DONE; } > $B/exp457/kms-handoff.out 2>&1
