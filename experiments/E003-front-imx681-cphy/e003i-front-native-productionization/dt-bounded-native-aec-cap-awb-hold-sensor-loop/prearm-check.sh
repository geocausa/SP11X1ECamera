#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/dt-bounded-native-aec-cap-awb-hold-sensor-loop
DN=$BASE/dn-native-aec-internal-cap
DQ=$BASE/dq-windows-awb-zero-weight-fallback
DR=$BASE/dr-native-awb-zero-weight-hold
DS=$BASE/ds-live-iq-producer-awb-hold
Z=$BASE/z-live-3a-runtime
CW=$BASE/cw-imx681-atomic-dynamic-control-cluster
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }
"$BASE/ai-deadline-hardened-live-r5-r6-runtime/prearm-check.sh"
T=$(mktemp); trap 'rm -f "$T" /tmp/e003i-dt-helper-prearm /tmp/e003i-dt-bootstrap-prearm /tmp/e003i-dr-prearm.json /tmp/e003i-ds-prearm.json' EXIT
make -C "$K" M="$CW" clean >/dev/null
make -C "$K" M="$CW" W=1 -j4 >"$T" 2>&1 || { cat "$T"; fail cw_build; }
H=$(sha256sum "$CW/imx681.ko" | awk '{print $1}')
[ "$H" = '72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1' ] || fail "cw_module_sha_$H"
python3 "$CW/prove-cw.py" >/dev/null
python3 "$DN/verify-dn.py"
python3 "$DQ/verify-dq.py"
sudo -n env PYTHONDONTWRITEBYTECODE=1 python3 "$DR/prove-dr.py" --snapshot-dir "$Z" --manifest /tmp/e003i-dr-prearm.json
sudo -n env PYTHONDONTWRITEBYTECODE=1 python3 "$DS/prove-ds.py" --snapshot-dir "$Z" --iterations 20 --manifest /tmp/e003i-ds-prearm.json
"$D/build-helper.sh" /tmp/e003i-dt-helper-prearm
"$D/build-bootstrap.sh" /tmp/e003i-dt-bootstrap-prearm
python3 "$D/verify.py"
modinfo -F vermagic "$CW/imx681.ko" | grep -Fxq '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' || fail vermagic
printf 'DT_ROOT_PREARM=PASS CW_MODULE=%s\n' "$H"
