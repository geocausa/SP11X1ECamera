#!/bin/bash
set -euo pipefail
D=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0076-longpoll-candidate
V=$(sed -n 's/^VIDEO=//p' "$D/CAPTURE-PREFLIGHT.txt" | tail -1); test -n "$V"; sudo -n test -f "$D/WATCHER.ready"
X=$(cat /sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag); case "$X" in *'seq=0 stage=0 name=idle fifo_seq=0'*'error=0'*'faulted=0'*) ;; *) echo "FAIL RTCDM=$X" >&2; exit 1;; esac
( set -o noclobber; : > "$D/HELPER-CONSUMED.marker" ) 2>/dev/null || { echo consumed >&2; exit 1; }
printf 'TIME=%s\nVIDEO=%s\n' "$(date -Ins)" "$V" > "$D/HELPER-CONSUMED.marker"
set +e
sudo -n "$D/e003h-v4l2-six-frame-longpoll" "$V" "$D/QC10C-0.bin" "$D/QC10C-1.bin" "$D/QC10C-2.bin" "$D/QC10C-3.bin" "$D/QC10C-4.bin" "$D/QC10C-5.bin" > "$D/RUN.txt" 2>&1
rc=$?; printf 'HELPER_RC=%d\n' "$rc" >> "$D/RUN.txt"; exit "$rc"
