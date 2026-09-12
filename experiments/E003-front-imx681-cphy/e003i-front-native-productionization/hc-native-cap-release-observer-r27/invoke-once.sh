#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/hc-native-cap-release-observer-r27
EX=$BASE/gm-r5-r27-producer-integration
O=$D/runtime-output
V=$(sed -n 's/^VIDEO=//p' "$O/CAPTURE-PREFLIGHT.txt" | tail -1); test -n "$V"
SUBDEV=$(sed -n 's/^SUBDEV=//p' "$O/CAPTURE-PREFLIGHT.txt" | tail -1); test -n "$SUBDEV"
( set -o noclobber; : > "$O/HELPER-CONSUMED.marker" ) 2>/dev/null || { echo consumed >&2; exit 1; }
printf 'TIME=%s\nVIDEO=%s\nSUBDEV=%s\n' "$(date -Ins)" "$V" "$SUBDEV" > "$O/HELPER-CONSUMED.marker"
args=("$V" "$O/R4-bootstrap.bin" "$EX/live-iq-producer.py" "$O/producer" "$O/producer/RESULT.json" "$O/TLBG" "$O/STATS3A")
for i in $(seq 0 26); do args+=("$O/QC10C-$i.bin"); done
set +e
sudo -n env DB_SUBDEV="$SUBDEV" "$O/e003i-hc-caprelease-native-aec" "${args[@]}" > "$O/RUN.txt" 2>&1
rc=$?; printf 'HELPER_RC=%d\n' "$rc" >> "$O/RUN.txt"
set -e
sudo -n v4l2-ctl -d "$SUBDEV" --get-ctrl=vertical_blanking,exposure,analogue_gain,digital_gain > "$O/CONTROLS-POST-AEC.txt" || true
"$D/archive.sh" "helper_rc_$rc"
if [ "$rc" -ne 0 ]; then exit "$rc"; fi
sudo -n env PYTHONDONTWRITEBYTECODE=1 python3 "$D/verify-live.py"
