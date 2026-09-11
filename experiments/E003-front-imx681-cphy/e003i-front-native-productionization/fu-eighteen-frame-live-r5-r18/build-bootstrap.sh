#!/bin/bash
set -euo pipefail
D=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/fu-eighteen-frame-live-r5-r18
OUT=${1:?output path required}
cc -O2 -std=c11 -Wall -Wextra -Werror "$D/bootstrap-controls.c" -o "$OUT"
