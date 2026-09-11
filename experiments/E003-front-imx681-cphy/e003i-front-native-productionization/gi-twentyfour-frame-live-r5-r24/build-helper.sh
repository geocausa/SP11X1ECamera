#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/gi-twentyfour-frame-live-r5-r24
ES=$BASE/es-nine-frame-r7-r9-transport
EY=$BASE/ey-eleven-frame-r10-r11-transport
FE=$BASE/fe-twelve-frame-r12-transport
FM=$BASE/fm-fifteen-frame-r15-transport
FT=$BASE/ft-eighteen-frame-r18-transport
GB=$BASE/gb-twentyone-frame-r21-transport
GH=$BASE/gh-twentyfour-frame-r24-transport
ENLIVE=$BASE/en-r5-r9-live-producer-integration
GF=$BASE/gf-twentyone-generation-gain-feed-publisher
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
python3 "$ES/make-nine-frame-helper.py" "$ENLIVE/e003i-en-six-frame-native-aec.c" "$ENLIVE/native-db-schedule.h" "$B/helper-es9.c" "$B/schedule-es9.h" >/tmp/e003i-gi-helper-es9.log
[ "$(sha256sum "$B/helper-es9.c"|awk '{print $1}')" = '6d4268fb5e6c637de78f62079719eaa3c107efcca48578c125a58a17d74c565d' ]
[ "$(sha256sum "$B/schedule-es9.h"|awk '{print $1}')" = '47890d6b37bc6a484310d983a8a303798b56d06eea6f2287dc4df254eaf5eb14' ]
python3 "$EY/make-eleven-frame-helper.py" "$B/helper-es9.c" "$B/schedule-es9.h" "$B/helper-ey11.c" "$B/schedule-ey11.h" >/tmp/e003i-gi-helper-ey11.log
[ "$(sha256sum "$B/helper-ey11.c"|awk '{print $1}')" = 'b5ecb959b95c63eb38c1e7da98e1f37e9c71d9cc4abe4ee6fbc5456e9bd67993' ]
[ "$(sha256sum "$B/schedule-ey11.h"|awk '{print $1}')" = '6d6cfc6833c035d545d5d626a4af479717227732cf94ef301422e6c74f3dd113' ]
python3 "$FE/make-twelve-frame-helper.py" "$B/helper-ey11.c" "$B/schedule-ey11.h" "$B/helper-fe12.c" "$B/schedule-fe12.h" >/tmp/e003i-gi-helper-fe12.log
[ "$(sha256sum "$B/helper-fe12.c"|awk '{print $1}')" = 'e6f2a792dc070c9d6a726817f30d3a8b1da56b554debccbe2832bd0b18ae47de' ]
[ "$(sha256sum "$B/schedule-fe12.h"|awk '{print $1}')" = '1872289bdd280cc067034c4425234b9bfa334e27dce62841ffb540b061f86690' ]
python3 "$FM/make-fifteen-frame-helper.py" "$B/helper-fe12.c" "$B/schedule-fe12.h" "$B/helper-fm15.c" "$B/schedule-fm15.h" >/tmp/e003i-gi-helper-fm15.log
[ "$(sha256sum "$B/helper-fm15.c"|awk '{print $1}')" = 'f68413ae23cdfbfb84ee39129582e40ecee2fd4b3a37ee242a5bceb4997fb4b4' ]
[ "$(sha256sum "$B/schedule-fm15.h"|awk '{print $1}')" = 'b080113d1a07a2600eb8a06b3e5b045422debe0858577d84ab7d61fae03ff54d' ]
python3 "$FT/make-eighteen-frame-helper.py" "$B/helper-fm15.c" "$B/schedule-fm15.h" "$B/helper-ft18.c" "$B/schedule-ft18.h" >/tmp/e003i-gi-helper-ft18.log
[ "$(sha256sum "$B/helper-ft18.c"|awk '{print $1}')" = '24c87150ae6ee447440fe544cb8af1cec27e33d70fc0f70b198b4b7d9f5f23ce' ]
[ "$(sha256sum "$B/schedule-ft18.h"|awk '{print $1}')" = '092c1b1dfaaa09ede3b9b492fc4173915d64f7b6c3d7e7439576314129e3c6cf' ]
python3 "$GB/make-twentyone-frame-helper.py" "$B/helper-ft18.c" "$B/schedule-ft18.h" "$B/helper-gb21.c" "$B/schedule-gb21.h" >/tmp/e003i-gi-helper-gb21.log
[ "$(sha256sum "$B/helper-gb21.c"|awk '{print $1}')" = '8cb43bb96c629ce25c08014192898cc30e21abe226d101d06600f25dba829af5' ]
[ "$(sha256sum "$B/schedule-gb21.h"|awk '{print $1}')" = 'fca5d49b12524a9f24bfca673072cf3bbb85d33645045d3a2cb4b155b58c6aae' ]
python3 "$GH/make-twentyfour-frame-helper.py" "$B/helper-gb21.c" "$B/schedule-gb21.h" "$B/e003i-gi-twentyfour-frame-native-aec.c" "$B/native-db-schedule.h" >/tmp/e003i-gi-helper-gh24.log
[ "$(sha256sum "$B/e003i-gi-twentyfour-frame-native-aec.c"|awk '{print $1}')" = 'df20afacd4f839250b0338de22600b8d89a09b6320f4c685fdfcfa76e7fa6b79' ]
[ "$(sha256sum "$B/native-db-schedule.h"|awk '{print $1}')" = '71a88a4ebacb453a84e9eeaebd6f21354b73b3363f18a47d719336a3500c993b' ]
cp "$ENLIVE/native-db-schedule.c" "$GF/gain-feed.c" "$GF/gain-feed.h" "$B/"
[ "$(sha256sum "$B/gain-feed.c"|awk '{print $1}')" = '9a4ad8ae24f9672d897d4d6be58394f998df517c9103c8149b59fc0612c57593' ]
[ "$(sha256sum "$B/gain-feed.h"|awk '{print $1}')" = '60adc6456b9806f50e14c0e3158a74dc49995549af1627e1604ad0496212de79' ]
cc -O2 -std=c11 -Wall -Wextra -Werror -fno-fast-math -ffp-contract=off \
  -I"$B" -I"$ENLIVE" -I"$DT" -I"$DN" -I"$CV" -I"$CU" -I"$CQ" -I"$CR" -I"$CT" -I"$CF" -I"$CE" \
  -I"$CC" -I"$BY" -I"$CG" -I"$CH" -I"$BK" -I"$BJ" \
  "$B/e003i-gi-twentyfour-frame-native-aec.c" "$B/gain-feed.c" "$B/native-db-schedule.c" \
  "$CV/native-raw-control-join.c" "$CU/native-raw-aec-loop.c" "$CU/native-stats3a.c" \
  "$CQ/native-imx681-control.c" "$CR/native-effective-analyzers.c" "$CT/native-bhist-bank4.c" \
  "$DN/native-aec-request-loop.c" "$DN/native-internal-cap.c" "$CF/native-final-exposure.c" \
  "$CE/native-final-target.c" "$CC/native-aec-tail.c" "$BY/native-target-aggregate.c" \
  "$CG/native-convergence.c" "$CH/native-t681.c" "$BK/native-aec-state.c" "$BJ/native-log103.c" \
  -pthread -lm -o "$OUT"
echo "GI_HELPER_BUILD=PASS SOURCE_SHA=$(sha256sum "$B/e003i-gi-twentyfour-frame-native-aec.c"|awk '{print $1}') GAIN_FEED_SHA=$(sha256sum "$B/gain-feed.c"|awk '{print $1}') BINARY_SHA=$(sha256sum "$OUT"|awk '{print $1}')"
