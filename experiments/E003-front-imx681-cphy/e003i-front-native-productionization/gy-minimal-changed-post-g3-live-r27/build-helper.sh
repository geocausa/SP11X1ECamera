#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/gy-minimal-changed-post-g3-live-r27
ES=$BASE/es-nine-frame-r7-r9-transport
EY=$BASE/ey-eleven-frame-r10-r11-transport
FE=$BASE/fe-twelve-frame-r12-transport
FM=$BASE/fm-fifteen-frame-r15-transport
FT=$BASE/ft-eighteen-frame-r18-transport
GB=$BASE/gb-twentyone-frame-r21-transport
GH=$BASE/gh-twentyfour-frame-r24-transport
GN=$BASE/gn-twentyseven-frame-r27-transport
GR=$BASE/gr-continuous-helper-integration
GQ=$BASE/gq-continuous-control-ring-scheduler
GS=$BASE/gs-continuous-shadow-scheduler-r27
GX=$BASE/gx-minimal-sentinel-helper-integration
GW=$BASE/gw-minimal-changed-post-g3-authority
ENLIVE=$BASE/en-r5-r9-live-producer-integration
GL=$BASE/gl-twentyfour-generation-gain-feed-publisher
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
python3 "$ES/make-nine-frame-helper.py" "$ENLIVE/e003i-en-six-frame-native-aec.c" "$ENLIVE/native-db-schedule.h" "$B/helper-es9.c" "$B/schedule-es9.h" >/tmp/e003i-gy-helper-es9.log
[ "$(sha256sum "$B/helper-es9.c"|awk '{print $1}')" = '6d4268fb5e6c637de78f62079719eaa3c107efcca48578c125a58a17d74c565d' ]
[ "$(sha256sum "$B/schedule-es9.h"|awk '{print $1}')" = '47890d6b37bc6a484310d983a8a303798b56d06eea6f2287dc4df254eaf5eb14' ]
python3 "$EY/make-eleven-frame-helper.py" "$B/helper-es9.c" "$B/schedule-es9.h" "$B/helper-ey11.c" "$B/schedule-ey11.h" >/tmp/e003i-gy-helper-ey11.log
[ "$(sha256sum "$B/helper-ey11.c"|awk '{print $1}')" = 'b5ecb959b95c63eb38c1e7da98e1f37e9c71d9cc4abe4ee6fbc5456e9bd67993' ]
[ "$(sha256sum "$B/schedule-ey11.h"|awk '{print $1}')" = '6d6cfc6833c035d545d5d626a4af479717227732cf94ef301422e6c74f3dd113' ]
python3 "$FE/make-twelve-frame-helper.py" "$B/helper-ey11.c" "$B/schedule-ey11.h" "$B/helper-fe12.c" "$B/schedule-fe12.h" >/tmp/e003i-gy-helper-fe12.log
[ "$(sha256sum "$B/helper-fe12.c"|awk '{print $1}')" = 'e6f2a792dc070c9d6a726817f30d3a8b1da56b554debccbe2832bd0b18ae47de' ]
[ "$(sha256sum "$B/schedule-fe12.h"|awk '{print $1}')" = '1872289bdd280cc067034c4425234b9bfa334e27dce62841ffb540b061f86690' ]
python3 "$FM/make-fifteen-frame-helper.py" "$B/helper-fe12.c" "$B/schedule-fe12.h" "$B/helper-fm15.c" "$B/schedule-fm15.h" >/tmp/e003i-gy-helper-fm15.log
[ "$(sha256sum "$B/helper-fm15.c"|awk '{print $1}')" = 'f68413ae23cdfbfb84ee39129582e40ecee2fd4b3a37ee242a5bceb4997fb4b4' ]
[ "$(sha256sum "$B/schedule-fm15.h"|awk '{print $1}')" = 'b080113d1a07a2600eb8a06b3e5b045422debe0858577d84ab7d61fae03ff54d' ]
python3 "$FT/make-eighteen-frame-helper.py" "$B/helper-fm15.c" "$B/schedule-fm15.h" "$B/helper-ft18.c" "$B/schedule-ft18.h" >/tmp/e003i-gy-helper-ft18.log
[ "$(sha256sum "$B/helper-ft18.c"|awk '{print $1}')" = '24c87150ae6ee447440fe544cb8af1cec27e33d70fc0f70b198b4b7d9f5f23ce' ]
[ "$(sha256sum "$B/schedule-ft18.h"|awk '{print $1}')" = '092c1b1dfaaa09ede3b9b492fc4173915d64f7b6c3d7e7439576314129e3c6cf' ]
python3 "$GB/make-twentyone-frame-helper.py" "$B/helper-ft18.c" "$B/schedule-ft18.h" "$B/helper-gb21.c" "$B/schedule-gb21.h" >/tmp/e003i-gy-helper-gb21.log
[ "$(sha256sum "$B/helper-gb21.c"|awk '{print $1}')" = '8cb43bb96c629ce25c08014192898cc30e21abe226d101d06600f25dba829af5' ]
[ "$(sha256sum "$B/schedule-gb21.h"|awk '{print $1}')" = 'fca5d49b12524a9f24bfca673072cf3bbb85d33645045d3a2cb4b155b58c6aae' ]
python3 "$GH/make-twentyfour-frame-helper.py" "$B/helper-gb21.c" "$B/schedule-gb21.h" "$B/helper-gh24.c" "$B/schedule-gh24.h" >/tmp/e003i-gy-helper-gh24.log
[ "$(sha256sum "$B/helper-gh24.c"|awk '{print $1}')" = 'df20afacd4f839250b0338de22600b8d89a09b6320f4c685fdfcfa76e7fa6b79' ]
[ "$(sha256sum "$B/schedule-gh24.h"|awk '{print $1}')" = '71a88a4ebacb453a84e9eeaebd6f21354b73b3363f18a47d719336a3500c993b' ]
python3 "$GN/make-twentyseven-frame-helper.py" "$B/helper-gh24.c" "$B/schedule-gh24.h" "$B/helper-go27.c" "$B/schedule-go27.h" >/tmp/e003i-gy-helper-gn27.log
[ "$(sha256sum "$B/helper-go27.c"|awk '{print $1}')" = '32ecff0848a3f47fe149ead36ccf63eec26a8c78180075129253a65792dedf1e' ]
[ "$(sha256sum "$B/schedule-go27.h"|awk '{print $1}')" = 'b3db42c9a38da0f428277fccbe79b01cc25a5a42d7f4cf26112d1096e0eedfee' ]
python3 "$GR/make-gr-helper.py" "$B/helper-go27.c" "$B/helper-gr.c" >/tmp/e003i-gy-helper-gr.log
[ "$(sha256sum "$B/helper-gr.c"|awk '{print $1}')" = '7f597f69cb4b5c7230521996db8a5574091c997c76e1b0b322f7dacbd3402e55' ]
python3 "$GS/make-gs-helper.py" "$B/helper-gr.c" "$B/helper-gs.c" >/tmp/e003i-gy-helper-gs.log
[ "$(sha256sum "$B/helper-gs.c"|awk '{print $1}')" = '1dc9d1b2e31ca74c983e6bdf48dc66f3780da1ffbfd369e4c455d88d9266d5b1' ]
python3 "$GX/make-gx-helper.py" "$B/helper-gs.c" "$B/e003i-gy-sentinel-native-aec.c" >/tmp/e003i-gy-helper-gx.log
[ "$(sha256sum "$B/e003i-gy-sentinel-native-aec.c"|awk '{print $1}')" = '8f28624537aa5c81da09b026ab6189f4efa9863f5d4519abe38a10986d01c350' ]
cp "$GQ/continuous-db-schedule.c" "$GQ/continuous-db-schedule.h" "$GW/minimal-dgain-sentinel.c" "$GW/minimal-dgain-sentinel.h" "$GL/gain-feed.c" "$GL/gain-feed.h" "$B/"
[ "$(sha256sum "$B/continuous-db-schedule.c"|awk '{print $1}')" = '8179ef6912a705e7296dd93fc147a6183d9d425b8e2c5052e7424de94cbccea1' ]
[ "$(sha256sum "$B/continuous-db-schedule.h"|awk '{print $1}')" = '001db23f44bf58b2b4ddb0dcfeb9a09d86998bd4d3fea850cdee434c8bb0fd91' ]
[ "$(sha256sum "$B/minimal-dgain-sentinel.c"|awk '{print $1}')" = 'bb2c80f296bc8997f86dd2bac3f2660d507473a9fb3137eb1e14458079c31115' ]
[ "$(sha256sum "$B/gain-feed.c"|awk '{print $1}')" = '2ad568beeeaf0ef9a5229b234ff172e6cbb5f2a3848f063eec103995595031c1' ]
[ "$(sha256sum "$B/gain-feed.h"|awk '{print $1}')" = '60adc6456b9806f50e14c0e3158a74dc49995549af1627e1604ad0496212de79' ]
cc -O2 -std=c11 -Wall -Wextra -Werror -fno-fast-math -ffp-contract=off \
  -I"$B" -I"$ENLIVE" -I"$DT" -I"$DN" -I"$CV" -I"$CU" -I"$CQ" -I"$CR" -I"$CT" -I"$CF" -I"$CE" \
  -I"$CC" -I"$BY" -I"$CG" -I"$CH" -I"$BK" -I"$BJ" \
  "$B/e003i-gy-sentinel-native-aec.c" "$B/gain-feed.c" "$B/continuous-db-schedule.c" "$B/minimal-dgain-sentinel.c" \
  "$CV/native-raw-control-join.c" "$CU/native-raw-aec-loop.c" "$CU/native-stats3a.c" \
  "$CQ/native-imx681-control.c" "$CR/native-effective-analyzers.c" "$CT/native-bhist-bank4.c" \
  "$DN/native-aec-request-loop.c" "$DN/native-internal-cap.c" "$CF/native-final-exposure.c" \
  "$CE/native-final-target.c" "$CC/native-aec-tail.c" "$BY/native-target-aggregate.c" \
  "$CG/native-convergence.c" "$CH/native-t681.c" "$BK/native-aec-state.c" "$BJ/native-log103.c" \
  -pthread -lm -o "$OUT"
echo "GY_HELPER_BUILD=PASS SOURCE_SHA=$(sha256sum "$B/e003i-gy-sentinel-native-aec.c"|awk '{print $1}') SENTINEL_SHA=$(sha256sum "$B/minimal-dgain-sentinel.c"|awk '{print $1}') SCHED_SHA=$(sha256sum "$B/continuous-db-schedule.c"|awk '{print $1}') BINARY_SHA=$(sha256sum "$OUT"|awk '{print $1}')"
