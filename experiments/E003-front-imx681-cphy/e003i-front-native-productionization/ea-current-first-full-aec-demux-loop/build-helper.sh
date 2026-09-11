#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
DZ=$BASE/dz-current-first-cq-publish-sensor-release
OUT=${1:?output path required}
exec "$DZ/build-helper.sh" "$OUT"
