#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
DX=$BASE/dx-parent-cq-gain-feed
OUT=${1:?output path required}
exec "$DX/build-helper.sh" "$OUT"
