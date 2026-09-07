#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/al-bounded-imx681-control-runtime
AJ=$BASE/aj-imx681-exposure-controls
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }

# Reuse the entire proven AI Golden/scheduling/producer prearm gate unchanged.
"$BASE/ai-deadline-hardened-live-r5-r6-runtime/prearm-check.sh"
# Rebuild the committed AJ source in a clean external-module invocation.
T=$(mktemp); trap 'rm -f "$T"' EXIT
make -C "$K" M="$AJ" clean >/dev/null
make -C "$K" M="$AJ" W=1 -j4 >"$T" 2>&1 || { cat "$T"; fail aj_build; }
H=$(sha256sum "$AJ/imx681.ko" | awk '{print $1}')
[ "$H" = '15855b65512a15e66a732b1bf023fa8935a86b937426e2f590e161d25944bd54' ] || fail "aj_module_sha_$H"
python3 "$AJ/windows-oracle/oracle.py" --self-test >/dev/null
python3 "$AJ/prove-aj.py" >/dev/null
python3 "$D/verify.py"
modinfo -F vermagic "$AJ/imx681.ko" | grep -Fxq '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' || fail vermagic
printf 'AL_ROOT_PREARM=PASS AJ_MODULE=%s\n' "$H"
