#!/bin/bash
set -euo pipefail
NEW=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-vfe1-cgc-release-0062-candidate; DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag; STAGES=$NEW/RUNTIME-VFECGC-0062-RTCDM-STAGES.txt; READY=$NEW/RUNTIME-VFECGC-0062-WATCHER.ready
[ -r "$DIAG" ]; sudo -n test ! -e "$STAGES"; sudo -n test ! -e "$READY"; exec sudo -n python3 "$NEW/watch-rtcdm-stage.py" "$DIAG" "$STAGES" --ready "$READY"
