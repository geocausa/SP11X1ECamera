#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/s-bounded-live-tlbg-runtime
B=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
F=$B/firmware/sp11/e003h
V=$(sed -n 's/^VIDEO=//p' "$D/CAPTURE-PREFLIGHT.txt" | tail -1); test -n "$V"
( set -o noclobber; : > "$D/HELPER-CONSUMED.marker" ) 2>/dev/null || { echo consumed >&2; exit 1; }
printf 'TIME=%s\nVIDEO=%s\n' "$(date -Ins)" "$V" > "$D/HELPER-CONSUMED.marker"
set +e
sudo -n "$D/e003i-s-six-frame-tlbg" "$V" \
  "$F/E003H_PIX_ORACLE_CAPSULE.bin" "$F/E003H_PIX_ORACLE_CAPSULE_R5.bin" "$F/E003H_PIX_ORACLE_CAPSULE_R6.bin" \
  "$D/TLBG" "$D/QC10C-0.bin" "$D/QC10C-1.bin" "$D/QC10C-2.bin" "$D/QC10C-3.bin" "$D/QC10C-4.bin" "$D/QC10C-5.bin" \
  > "$D/RUN.txt" 2>&1
rc=$?
printf 'HELPER_RC=%d\n' "$rc" >> "$D/RUN.txt"
exit "$rc"
