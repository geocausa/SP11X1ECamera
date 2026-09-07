#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ah-bounded-live-r5-r6-runtime
AE=$BASE/ae-bounded-live-trigger-iq-producer
O=$D/runtime-output
V=$(sed -n 's/^VIDEO=//p' "$O/CAPTURE-PREFLIGHT.txt" | tail -1); test -n "$V"
( set -o noclobber; : > "$O/HELPER-CONSUMED.marker" ) 2>/dev/null || { echo consumed >&2; exit 1; }
printf 'TIME=%s\nVIDEO=%s\n' "$(date -Ins)" "$V" > "$O/HELPER-CONSUMED.marker"
set +e
sudo -n "$O/e003i-ah-six-frame-live-iq" "$V" "$O/R4-bootstrap.bin" "$AE/live-iq-producer.py" \
  "$O/producer" "$O/producer/RESULT.json" "$O/TLBG" "$O/STATS3A" \
  "$O/QC10C-0.bin" "$O/QC10C-1.bin" "$O/QC10C-2.bin" "$O/QC10C-3.bin" "$O/QC10C-4.bin" "$O/QC10C-5.bin" \
  > "$O/RUN.txt" 2>&1
rc=$?; printf 'HELPER_RC=%d\n' "$rc" >> "$O/RUN.txt"; exit "$rc"
