#!/bin/bash
set -euo pipefail
NEW=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-vfe1-aperture-telemetry-0058-candidate; WATCH=$NEW/watch-rtcdm-stage.py; DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag; STAGES=$NEW/RUNTIME-VFEAP-0058-RTCDM-STAGES.txt; READY=$NEW/RUNTIME-VFEAP-0058-RTCDM.ready
[ -r "$DIAG" ]; sudo -n test ! -e "$STAGES"; sudo -n test ! -e "$READY"
exec sudo -n python3 "$WATCH" "$DIAG" "$STAGES" --ready "$READY"
