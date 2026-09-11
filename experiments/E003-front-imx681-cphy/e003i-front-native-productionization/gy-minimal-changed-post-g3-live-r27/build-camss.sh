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
SRC=/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src/drivers/media/platform/qcom/camss
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
OUT=${1:?output module required}
B=$D/build/camss
rm -rf "$B"; mkdir -p "$B"; cp -a "$SRC"/. "$B"/
python3 "$ES/make-nine-frame-camss.py" "$SRC/camss.c" "$B/camss-es9.c" >/tmp/e003i-gy-camss-es9.log
[ "$(sha256sum "$B/camss-es9.c"|awk '{print $1}')" = '683255664a320bf63b1c852c56a8c0373014d6723b6d48a69a277bd02d18706f' ]
python3 "$EY/make-eleven-frame-camss.py" "$B/camss-es9.c" "$B/camss-ey11.c" >/tmp/e003i-gy-camss-ey11.log
[ "$(sha256sum "$B/camss-ey11.c"|awk '{print $1}')" = '335e15f48cac9835d9ddfa0f1dc96f559346f167f2e8cce1c384635b872d13aa' ]
python3 "$FE/make-twelve-frame-camss.py" "$B/camss-ey11.c" "$B/camss-fe12.c" >/tmp/e003i-gy-camss-fe12.log
[ "$(sha256sum "$B/camss-fe12.c"|awk '{print $1}')" = 'deee56e61090bba938f602a7baeae054435762e6312e47d2cac9dbf9a210f15d' ]
python3 "$FM/make-fifteen-frame-camss.py" "$B/camss-fe12.c" "$B/camss-fm15.c" >/tmp/e003i-gy-camss-fm15.log
[ "$(sha256sum "$B/camss-fm15.c"|awk '{print $1}')" = '592f31d591ff9542f8f67d8228e5f45808afb63088368107ce56422b4d8e34d6' ]
python3 "$FT/make-eighteen-frame-camss.py" "$B/camss-fm15.c" "$B/camss-ft18.c" >/tmp/e003i-gy-camss-ft18.log
[ "$(sha256sum "$B/camss-ft18.c"|awk '{print $1}')" = 'a096493ae74fc3a22945f71f670f8777f0ea375bd3ad667c7451c96116d2ef6c' ]
python3 "$GB/make-twentyone-frame-camss.py" "$B/camss-ft18.c" "$B/camss-gb21.c" >/tmp/e003i-gy-camss-gb21.log
[ "$(sha256sum "$B/camss-gb21.c"|awk '{print $1}')" = 'd09cd0bf6d91ed7c51c981455d9643d1f486cb0374fec23a375376b83e837fb4' ]
python3 "$GH/make-twentyfour-frame-camss.py" "$B/camss-gb21.c" "$B/camss-gh24.c" >/tmp/e003i-gy-camss-gh24.log
[ "$(sha256sum "$B/camss-gh24.c"|awk '{print $1}')" = 'b47e9ca26d4591b55d5208eaf40edcef1794d4d6d7fb2e3c33e72edf5f527386' ]
python3 "$GN/make-twentyseven-frame-camss.py" "$B/camss-gh24.c" "$B/camss.c" >/tmp/e003i-gy-camss-gn27.log
[ "$(sha256sum "$B/camss.c"|awk '{print $1}')" = '117136b2c624de5ef3f4c081cdcf9c363cda9f6db5c752b7ade5f5e11b1b3e95' ]
make -C "$K" M="$B" clean >/dev/null
make -C "$K" M="$B" W=1 -j4 >/tmp/e003i-gy-camss-build.log 2>&1 || { cat /tmp/e003i-gy-camss-build.log; exit 1; }
[ "$(modinfo -F vermagic "$B/qcom-camss.ko")" = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' ]
mkdir -p "$(dirname "$OUT")"; cp "$B/qcom-camss.ko" "$OUT"
echo "GY_CAMSS_BUILD=PASS SOURCE_SHA=$(sha256sum "$B/camss.c"|awk '{print $1}') MODULE_SHA=$(sha256sum "$OUT"|awk '{print $1}')"
