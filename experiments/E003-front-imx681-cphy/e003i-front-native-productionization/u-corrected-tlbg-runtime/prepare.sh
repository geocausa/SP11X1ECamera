#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/u-corrected-tlbg-runtime
B=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
sudo -n "$B/setup-pix-media.sh" /dev/media0 > "$D/MEDIA.txt"
V=$(sed -n 's/^VIDEO=//p' "$D/MEDIA.txt" | tail -1); test -c "$V"
sudo -n python3 - "$V" <<'PYO'
import os,sys
fd=os.open(sys.argv[1],os.O_RDWR|os.O_CLOEXEC); os.close(fd)
PYO
printf 'STATUS=PASS\nVIDEO=%s\n' "$V" > "$D/CAPTURE-PREFLIGHT.txt"
echo "PASS: E003i-U privileged media/open gate VIDEO=$V"
