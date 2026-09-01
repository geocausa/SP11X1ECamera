#!/bin/bash
set -euo pipefail
NEW=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-four-frame-steady-0069-candidate
DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
STAGES=$NEW/RUNTIME-V4L2-0069-RTCDM-STAGES.txt
READY=$NEW/RUNTIME-V4L2-0069-WATCHER.ready
[ -r "$DIAG" ]; sudo -n test ! -e "$STAGES"; sudo -n test ! -e "$READY"
exec sudo -n python3 "$NEW/watch-rtcdm-stage.py" "$DIAG" "$STAGES" --ready "$READY"
