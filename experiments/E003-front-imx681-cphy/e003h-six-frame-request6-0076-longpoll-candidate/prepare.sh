#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
B=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
D=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0076-longpoll-candidate
sudo -n "$B/setup-pix-media.sh" /dev/media0 > "$D/MEDIA.txt"
V=$(sed -n 's/^VIDEO=//p' "$D/MEDIA.txt" | tail -1); test -c "$V"
sudo -n python3 - "$V" <<'PYO'
import os,sys
fd=os.open(sys.argv[1],os.O_RDWR|os.O_CLOEXEC); os.close(fd)
PYO
X=$(cat /sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag)
case "$X" in *'seq=0 stage=0 name=idle fifo_seq=0'*'error=0'*'faulted=0'*) ;; *) echo "FAIL RTCDM=$X" >&2; exit 1;; esac
printf 'STATUS=PASS\nVIDEO=%s\nRTCDM=%s\n' "$V" "$X" > "$D/CAPTURE-PREFLIGHT.txt"
echo "PASS: 0076 privileged media/open gate VIDEO=$V"
