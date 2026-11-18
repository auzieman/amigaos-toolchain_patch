#!/bin/sh
# #48 on kernel 020: the 301 warning cases launched plainly (no SPEFSCR wrapper).
B=/opt/a1222-gl-spe3; E=$B/exp457; cd $B/deqp/gles3
export HOME=/tmp MESA_SHADER_CACHE_DISABLE=true DEQP_WATCHDOG=disable
{ date; timeout 21600 ./deqp-gles3-0034 --deqp-caselist-file=$E/qw48.txt --deqp-surface-type=pbuffer \
 --deqp-gl-config-name=rgba8888d24s8ms0 --deqp-surface-width=256 --deqp-surface-height=256 --deqp-visibility=hidden \
 --deqp-log-images=disable --deqp-log-filename=$E/qw48-plain.qpa > $E/qw48-plain.log 2>&1
echo "rc=$? $(grep -E 'Passed:|Failed:|Not supported:|Warnings:' $E/qw48-plain.log | tr -s ' \n' ' ') taint=$(cat /proc/sys/kernel/tainted)"
date; echo DONE; } > $E/qw48-plain.out 2>&1
