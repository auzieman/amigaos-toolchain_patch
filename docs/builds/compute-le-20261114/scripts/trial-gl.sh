#!/bin/sh
# One instrumented radeonsi trial on a FRESH boot (run on the A1222 as root).
# Usage: sh trial-gl.sh <outdir> <modprobe-args...>
# Stops before any shader work unless the parameters read back as requested and
# the packet-only checks pass. Writes everything to <outdir> (tmpfs).
OUT=$1; shift
mkdir -p "$OUT"; exec >"$OUT/trial.log" 2>&1
B=/opt/a1222-gl; export LD_LIBRARY_PATH=$B/lib HOME=/tmp MESA_SHADER_CACHE_DISABLE=true
say() { echo "[$(cut -d' ' -f1 /proc/uptime)] $*"; }
say "kernel $(uname -r) taint $(cat /proc/sys/kernel/tainted)"
lsmod | grep -q '^amdgpu ' && { say "STOP: amdgpu already loaded (not a fresh boot)"; exit 9; }
dmesg | grep -iE 'orphan|EXT4-fs error' | tail -3
say "modprobe amdgpu $*"; modprobe amdgpu "$@"; say "modprobe rc=$?"
P=/sys/module/amdgpu/parameters
for p in polaris11_le_user_ib cg_mask ppfeaturemask; do say "param $p=$(cat $P/$p)"; done
[ "$(cat $P/polaris11_le_user_ib)" = Y ] || { say "STOP: polaris11_le_user_ib is not Y"; exit 9; }
mountpoint -q /sys/kernel/debug || mount -t debugfs none /sys/kernel/debug
D=/sys/kernel/debug/dri/0
fence() { grep -A2 '(gfx)' $D/amdgpu_fence_info | tr -s ' ' | sed -n '2,3p' | tr '\n' ' '; echo; }
reg() { dd if=$D/amdgpu_regs bs=4 skip=$(($1)) count=1 2>/dev/null | od -A n -t x4 | tr -d ' '; }
regs() {
  echo "$(cut -d' ' -f1 /proc/uptime) GRBM_STATUS=$(reg 0x2004) GRBM_STATUS2=$(reg 0x2002) GRBM_SE0=$(reg 0x2005)" \
       "CP_STAT=$(reg 0x21a0) CP_BUSY=$(reg 0x219f) CPF=$(reg 0x2087) ME_HDR=$(reg 0x21a1) PFP_HDR=$(reg 0x21a2)" \
       "RB0_RPTR=$(reg 0x21c0) RB0_WPTR=$(reg 0x3045) IB1_LO=$(reg 0xc0cc) IB1_SZ=$(reg 0xc0ce)" \
       "SRBM=$(reg 0x394) VMC1_FAULT=$(reg 0x537) VMC1_ADDR=$(reg 0x53f) RLC_CGCG=$(reg 0xec49)"
}
say "idle regs:"; regs
say "fence before packet tests: $(fence)"
for v in "le" "le vram" "le uswc"; do
  r=$(timeout 30 $B/bin/gfx-write $v | grep -E '^GFX_NATIVE_WRITE=')
  say "gfx-write $v: $r"
  [ "$r" = GFX_NATIVE_WRITE=PASS ] || { say "STOP: packet test failed"; exit 8; }
done
say "fence before gltest: $(fence)"
( for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14; do regs; sleep 1; done ) > "$OUT/regs-during.txt" &
# Live wave state (PC, instruction, SGPRs) twice during the hang: a moving PC is a loop,
# a fixed PC is a stall on that instruction. Needs /tmp/wavedump (staged per boot).
[ -x /tmp/wavedump ] && ( sleep 3; /tmp/wavedump > "$OUT/waves-1.txt" 2>&1; sleep 2; /tmp/wavedump > "$OUT/waves-2.txt" 2>&1 ) &
say "gltest clear start"
AMD_DEBUG=vs,ps,cs,asm timeout 60 $B/bin/gltest clear > "$OUT/gltest-clear.txt" 2> "$OUT/gltest-clear-shaders.txt"
rc=$?; say "gltest clear rc=$rc"; grep -E 'RENDERER|bad_pixels|RESULT' "$OUT/gltest-clear.txt"
say "fence after gltest clear: $(fence)"
wait
for f in "$OUT"/waves-*.txt; do [ -f "$f" ] && say "$(basename $f): $(tail -1 $f)"; done
say "regs after:"; regs
dmesg | grep -E 'amdgpu.*(timeout|recover|fault|reset)|VM_CONTEXT|gpu_sched' | tail -10
if [ $rc -eq 0 ]; then
  say "gltest draw start"
  timeout 60 $B/bin/gltest draw > "$OUT/gltest-draw.txt" 2>&1
  say "gltest draw rc=$?"; grep -E 'bad_pixels|RESULT' "$OUT/gltest-draw.txt"
  say "fence after gltest draw: $(fence)"
fi
say "taint $(cat /proc/sys/kernel/tainted) done"
