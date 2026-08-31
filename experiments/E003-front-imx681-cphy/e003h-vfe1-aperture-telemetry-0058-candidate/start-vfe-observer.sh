#!/bin/bash
set -euo pipefail
NEW=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-vfe1-aperture-telemetry-0058-candidate; OUT=$NEW/RUNTIME-VFEAP-0058-APERTURE.json; READY=$NEW/RUNTIME-VFEAP-0058-APERTURE.ready
[ -r /dev/mem ] || { echo 'FAIL: /dev/mem unavailable' >&2; exit 1; }
sudo -n test ! -e "$OUT"; sudo -n test ! -e "$READY"
exec sudo -n python3 "$NEW/watch-vfe1-aperture.py" "$OUT" --ready "$READY" --seconds 4 --interval-ms 1
