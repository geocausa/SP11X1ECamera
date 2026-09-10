#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/dy-bounded-full-aec-demux-loop
DN=$BASE/dn-native-aec-internal-cap
DQ=$BASE/dq-windows-awb-zero-weight-fallback
DR=$BASE/dr-native-awb-zero-weight-hold
DS=$BASE/ds-live-iq-producer-awb-hold
DV=$BASE/dv-live-residual-isp-demux
DW=$BASE/dw-iq-producer-live-cq-demux
DX=$BASE/dx-parent-cq-gain-feed
Z=$BASE/z-live-3a-runtime
CW=$BASE/cw-imx681-atomic-dynamic-control-cluster
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }

"$BASE/ai-deadline-hardened-live-r5-r6-runtime/prearm-check.sh"
T=$(mktemp)
trap 'rm -f "$T" /tmp/e003i-dy-helper-prearm /tmp/e003i-dy-bootstrap-prearm; sudo -n rm -f /tmp/e003i-dr-dy.json /tmp/e003i-ds-dy.json /tmp/e003i-dw-dy.json /tmp/e003i-dx-dy.json' EXIT

make -C "$K" M="$CW" clean >/dev/null
make -C "$K" M="$CW" W=1 -j4 >"$T" 2>&1 || { cat "$T"; fail cw_build; }
H=$(sha256sum "$CW/imx681.ko" | awk '{print $1}')
[ "$H" = '72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1' ] || fail "cw_module_sha_$H"
python3 "$CW/prove-cw.py" >/dev/null
python3 "$DN/verify-dn.py"
python3 "$DQ/verify-dq.py"
sudo -n env PYTHONDONTWRITEBYTECODE=1 python3 "$DR/prove-dr.py" --snapshot-dir "$Z" --manifest /tmp/e003i-dr-dy.json
sudo -n env PYTHONDONTWRITEBYTECODE=1 python3 "$DS/prove-ds.py" --snapshot-dir "$Z" --iterations 20 --manifest /tmp/e003i-ds-dy.json
python3 "$DV/verify-dv.py"
sudo -n env PYTHONDONTWRITEBYTECODE=1 python3 "$DW/prove-dw.py" --manifest /tmp/e003i-dw-dy.json
sudo -n env PYTHONDONTWRITEBYTECODE=1 python3 "$DX/verify-dx.py" --manifest /tmp/e003i-dx-dy.json
"$D/build-helper.sh" /tmp/e003i-dy-helper-prearm
"$D/build-bootstrap.sh" /tmp/e003i-dy-bootstrap-prearm
python3 "$D/verify.py"
modinfo -F vermagic "$CW/imx681.ko" | grep -Fxq '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' || fail vermagic
printf 'DY_ROOT_PREARM=PASS CW_MODULE=%s DX_GAIN_FEED=PASS DV_DEMUX=PASS\n' "$H"
