#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
B=$R/experiments/E003-front-imx681-cphy/e003h-iq-provider-0072-candidate
D=$R/experiments/E003-front-imx681-cphy/e003h-0075b-atomic-r45-on-0072
V=$(sed -n 's/^VIDEO=//p' "$D/CAPTURE-PREFLIGHT.txt" | tail -1); test -n "$V"; sudo -n test -f "$D/WATCHER.ready"
( set -o noclobber; : > "$D/HELPER-CONSUMED.marker" ) 2>/dev/null || { echo consumed >&2; exit 1; }
printf 'TIME=%s\nVIDEO=%s\n' "$(date -Ins)" "$V" > "$D/HELPER-CONSUMED.marker"
set +e
sudo -n "$B/e003h-v4l2-live-requeue" "$V" "$D/QC10C-0.bin" "$D/QC10C-1.bin" "$D/QC10C-2.bin" "$D/QC10C-3.bin" "$D/QC10C-4.bin" > "$D/RUN.txt" 2>&1
rc=$?; printf 'HELPER_RC=%d\n' "$rc" >> "$D/RUN.txt"; exit "$rc"
