#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-csid1-ipp-start-parity-candidate
OLD=$REPO/experiments/E003-front-imx681-cphy/e003h-bounded-vfe1-pix-runtime-candidate
WATCH=$OLD/watch-rtcdm-stage.py
DIAG=/sys/bus/platform/devices/acb7000.isp/e003h_pix_rtcdm_diag
STAGES=$NEW/RUNTIME-CSID1-0042-RTCDM-STAGES.txt
READY=$NEW/RUNTIME-CSID1-0042-WATCHER.ready
[ "$(sha256sum "$WATCH" | cut -d' ' -f1)" = 8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84 ] || { echo 'FAIL: watcher hash drift' >&2; exit 1; }
[ -r "$DIAG" ] || { echo 'FAIL: diagnostic observer absent' >&2; exit 1; }
sudo -n test ! -e "$STAGES" || { echo 'FAIL: stages file already exists' >&2; exit 1; }
sudo -n test ! -e "$READY" || { echo 'FAIL: ready file already exists' >&2; exit 1; }
exec sudo -n python3 "$WATCH" "$DIAG" "$STAGES" --ready "$READY"
