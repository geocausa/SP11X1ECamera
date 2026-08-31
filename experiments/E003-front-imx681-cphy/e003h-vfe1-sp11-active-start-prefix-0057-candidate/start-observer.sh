#!/bin/bash
set -euo pipefail
NEW=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-vfe1-sp11-active-start-prefix-0057-candidate
WATCH=$NEW/watch-rtcdm-stage.py
DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
STAGES=$NEW/RUNTIME-VFEACTIVE-0057-RTCDM-STAGES.txt
READY=$NEW/RUNTIME-VFEACTIVE-0057-WATCHER.ready
[ -r "$DIAG" ] || { echo 'FAIL: diagnostic observer absent' >&2; exit 1; }
sudo -n test ! -e "$STAGES" || { echo 'FAIL: stages file already exists' >&2; exit 1; }
sudo -n test ! -e "$READY" || { echo 'FAIL: ready file already exists' >&2; exit 1; }
exec sudo -n python3 "$WATCH" "$DIAG" "$STAGES" --ready "$READY"
