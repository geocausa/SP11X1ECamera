#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
B=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate
D=$R/experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0076-longpoll-candidate
sudo -n rm -f "$D/RTCDM-STAGES.txt" "$D/WATCHER.ready"
exec sudo -n python3 "$B/watch-rtcdm-stage.py" /sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag "$D/RTCDM-STAGES.txt" --ready "$D/WATCHER.ready"
