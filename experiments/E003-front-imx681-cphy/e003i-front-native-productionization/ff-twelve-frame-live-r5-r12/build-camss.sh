#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ff-twelve-frame-live-r5-r12
ES=$BASE/es-nine-frame-r7-r9-transport
EY=$BASE/ey-eleven-frame-r10-r11-transport
FE=$BASE/fe-twelve-frame-r12-transport
SRC=/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src/drivers/media/platform/qcom/camss
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
OUT=${1:?output module required}
B=$D/build/camss
rm -rf "$B"; mkdir -p "$B"; cp -a "$SRC"/. "$B"/
python3 "$ES/make-nine-frame-camss.py" "$SRC/camss.c" "$B/camss-es9.c" >/tmp/e003i-ff-camss-es9.log
[ "$(sha256sum "$B/camss-es9.c"|awk '{print $1}')" = '683255664a320bf63b1c852c56a8c0373014d6723b6d48a69a277bd02d18706f' ]
python3 "$EY/make-eleven-frame-camss.py" "$B/camss-es9.c" "$B/camss-ey11.c" >/tmp/e003i-ff-camss-ey11.log
[ "$(sha256sum "$B/camss-ey11.c"|awk '{print $1}')" = '335e15f48cac9835d9ddfa0f1dc96f559346f167f2e8cce1c384635b872d13aa' ]
python3 "$FE/make-twelve-frame-camss.py" "$B/camss-ey11.c" "$B/camss.c" >/tmp/e003i-ff-camss-fe12.log
[ "$(sha256sum "$B/camss.c"|awk '{print $1}')" = 'deee56e61090bba938f602a7baeae054435762e6312e47d2cac9dbf9a210f15d' ]
make -C "$K" M="$B" clean >/dev/null
make -C "$K" M="$B" W=1 -j4 >/tmp/e003i-ff-camss-build.log 2>&1 || { cat /tmp/e003i-ff-camss-build.log; exit 1; }
[ "$(modinfo -F vermagic "$B/qcom-camss.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ]
mkdir -p "$(dirname "$OUT")"; cp "$B/qcom-camss.ko" "$OUT"
echo "FF_CAMSS_BUILD=PASS SOURCE_SHA=$(sha256sum "$B/camss.c"|awk '{print $1}') MODULE_SHA=$(sha256sum "$OUT"|awk '{print $1}')"
