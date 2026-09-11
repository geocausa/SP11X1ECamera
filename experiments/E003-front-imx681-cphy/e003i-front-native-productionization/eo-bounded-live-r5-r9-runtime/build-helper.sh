#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
EN=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/en-r5-r9-producer-integration
OUT=${1:?output path required}
exec "$EN/build-helper.sh" "$OUT"
