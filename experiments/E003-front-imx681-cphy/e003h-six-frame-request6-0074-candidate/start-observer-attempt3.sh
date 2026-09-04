#!/bin/bash
set -euo pipefail
NEW=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
STAGES=$NEW/RUNTIME-V4L2-0074-A3-RTCDM-STAGES.txt
READY=$NEW/RUNTIME-V4L2-0074-A3-WATCHER.ready
PREF=$NEW/ATTEMPT3-CAPTURE-PREFLIGHT.txt
grep -qx 'STATUS=PASS' "$PREF"
sudo -n rm -f "$STAGES" "$READY"
exec sudo -n python3 "$NEW/watch-rtcdm-stage.py" "$DIAG" "$STAGES" --ready "$READY"
