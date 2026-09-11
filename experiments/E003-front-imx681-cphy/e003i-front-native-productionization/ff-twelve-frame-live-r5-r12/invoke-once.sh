#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ff-twelve-frame-live-r5-r12
EX=$BASE/fd-r5-r12-producer-integration
O=$D/runtime-output
V=$(sed -n 's/^VIDEO=//p' "$O/CAPTURE-PREFLIGHT.txt" | tail -1); test -n "$V"
SUBDEV=$(sed -n 's/^SUBDEV=//p' "$O/CAPTURE-PREFLIGHT.txt" | tail -1); test -n "$SUBDEV"
( set -o noclobber; : > "$O/HELPER-CONSUMED.marker" ) 2>/dev/null || { echo consumed >&2; exit 1; }
printf 'TIME=%s\nVIDEO=%s\nSUBDEV=%s\n' "$(date -Ins)" "$V" "$SUBDEV" > "$O/HELPER-CONSUMED.marker"
set +e
sudo -n env DB_SUBDEV="$SUBDEV" "$O/e003i-ff-twelve-frame-native-aec" "$V" "$O/R4-bootstrap.bin" "$EX/live-iq-producer.py" \
  "$O/producer" "$O/producer/RESULT.json" "$O/TLBG" "$O/STATS3A" \
  "$O/QC10C-0.bin" "$O/QC10C-1.bin" "$O/QC10C-2.bin" "$O/QC10C-3.bin" "$O/QC10C-4.bin" \
  "$O/QC10C-5.bin" "$O/QC10C-6.bin" "$O/QC10C-7.bin" "$O/QC10C-8.bin" "$O/QC10C-9.bin" "$O/QC10C-10.bin" "$O/QC10C-11.bin" \
  > "$O/RUN.txt" 2>&1
rc=$?; printf 'HELPER_RC=%d\n' "$rc" >> "$O/RUN.txt"
set -e
sudo -n v4l2-ctl -d "$SUBDEV" --get-ctrl=vertical_blanking,exposure,analogue_gain,digital_gain > "$O/CONTROLS-POST-AEC.txt" || true
"$D/archive.sh" "helper_rc_$rc"
if [ "$rc" -ne 0 ]; then exit "$rc"; fi
sudo -n env PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify-live.py"
