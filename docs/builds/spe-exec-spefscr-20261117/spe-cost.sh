#!/bin/sh
# kernel 020 slowdown: the cost of the SPE exception fix-ups. Each dEQP GLES3 group runs twice in
# the same boot: launched plainly (SPEFSCR enables 0x3c, kernel 020's start value) and with
# spe-setfscr.so preloaded and SPE_SETFSCR=0 (enables clear: the hardware saturates instead of
# trapping). spe-execwith cannot do it on 020: patch 0038 sets SPEFSCR at exec. user/sys from time.
B=/opt/a1222-gl-spe3; E=$B/exp457; cd $B/deqp/gles3
export HOME=/tmp MESA_SHADER_CACHE_DISABLE=true DEQP_WATCHDOG=disable
O="--deqp-surface-type=pbuffer --deqp-gl-config-name=rgba8888d24s8ms0 --deqp-surface-width=256 --deqp-surface-height=256 --deqp-visibility=hidden --deqp-log-images=disable"
G="dEQP-GLES3.functional.shaders.matrix.add.* dEQP-GLES3.functional.texture.format.sized.2d.* dEQP-GLES3.functional.texture.format.unsized.* dEQP-GLES3.functional.fbo.blit.conversion.* dEQP-GLES3.functional.rasterization.primitives.* dEQP-GLES3.functional.shaders.builtin_functions.precision.add.highp_vertex.*"
{ for g in $G; do for m in 3c 0; do
    if [ $m = 3c ]; then P=""; else P=/tmp/spe-setfscr.so; fi
    /usr/bin/time -f "%e real %U user %S sys" env LD_PRELOAD=$P SPE_SETFSCR=$m ./deqp-gles3-0035 --deqp-case="$g" $O --deqp-log-filename=$E/cost.qpa > $E/cost.log 2> $E/cost.time
    echo "$g spefscr=$m: $(tail -1 $E/cost.time) | $(grep spe-setfscr $E/cost.time | head -1) | $(grep -E 'Passed:|Warnings:' $E/cost.log | tr -s ' 
' ' ')"
  done; done; echo "taint=$(cat /proc/sys/kernel/tainted)"; date; echo DONE; } > $E/spe-cost.out 2>&1
