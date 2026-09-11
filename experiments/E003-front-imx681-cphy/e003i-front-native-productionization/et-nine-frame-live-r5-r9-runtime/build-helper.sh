#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/et-nine-frame-live-r5-r9-runtime
ES=$BASE/es-nine-frame-r7-r9-transport
EN=$BASE/en-r5-r9-live-producer-integration
DT=$BASE/dt-bounded-native-aec-cap-awb-hold-sensor-loop
DN=$BASE/dn-native-aec-internal-cap
CU=$BASE/cu-native-aec-raw-stats-request-loop
CQ=$BASE/cq-aec-output-imx681-control-adapter
CR=$BASE/cr-native-aec-effective-analyzer-producer
CT=$BASE/ct-native-aec-bhist-bank4-replay
CF=$BASE/cf-native-aec-final-exposure-si
CE=$BASE/ce-native-aec-final-target-producer
CC=$BASE/cc-native-aec-adrc-darkboost-tail
BY=$BASE/by-native-aec-method11-point-aggregation
CG=$BASE/cg-native-aec-qword-convergence-input
CH=$BASE/ch-native-aec-t681-preview-arbitration
BK=$BASE/bk-native-aec-history-state
BJ=$BASE/bj-native-aec-log103-coordinate
CV=$BASE/cv-native-aec-offline-sensor-control-join
OUT=${1:?output path required}
B=$D/build/helper
rm -rf "$B"; mkdir -p "$B"
python3 "$ES/make-nine-frame-helper.py" "$EN/e003i-en-six-frame-native-aec.c" "$EN/native-db-schedule.h" "$B/e003i-et-nine-frame-native-aec.c" "$B/native-db-schedule.h" >/tmp/e003i-et-helper-generate.log
[ "$(sha256sum "$B/e003i-et-nine-frame-native-aec.c"|awk '{print $1}')" = '6d4268fb5e6c637de78f62079719eaa3c107efcca48578c125a58a17d74c565d' ]
[ "$(sha256sum "$B/native-db-schedule.h"|awk '{print $1}')" = '47890d6b37bc6a484310d983a8a303798b56d06eea6f2287dc4df254eaf5eb14' ]
cp "$EN/native-db-schedule.c" "$EN/gain-feed.c" "$EN/gain-feed.h" "$B/"
cc -O2 -std=c11 -Wall -Wextra -Werror -fno-fast-math -ffp-contract=off \
  -I"$B" -I"$EN" -I"$DT" -I"$DN" -I"$CV" -I"$CU" -I"$CQ" -I"$CR" -I"$CT" -I"$CF" -I"$CE" \
  -I"$CC" -I"$BY" -I"$CG" -I"$CH" -I"$BK" -I"$BJ" \
  "$B/e003i-et-nine-frame-native-aec.c" "$B/gain-feed.c" "$B/native-db-schedule.c" \
  "$CV/native-raw-control-join.c" "$CU/native-raw-aec-loop.c" "$CU/native-stats3a.c" \
  "$CQ/native-imx681-control.c" "$CR/native-effective-analyzers.c" "$CT/native-bhist-bank4.c" \
  "$DN/native-aec-request-loop.c" "$DN/native-internal-cap.c" "$CF/native-final-exposure.c" \
  "$CE/native-final-target.c" "$CC/native-aec-tail.c" "$BY/native-target-aggregate.c" \
  "$CG/native-convergence.c" "$CH/native-t681.c" "$BK/native-aec-state.c" "$BJ/native-log103.c" \
  -pthread -lm -o "$OUT"
echo "ET_HELPER_BUILD=PASS SOURCE_SHA=$(sha256sum "$B/e003i-et-nine-frame-native-aec.c"|awk '{print $1}') BINARY_SHA=$(sha256sum "$OUT"|awk '{print $1}')"
