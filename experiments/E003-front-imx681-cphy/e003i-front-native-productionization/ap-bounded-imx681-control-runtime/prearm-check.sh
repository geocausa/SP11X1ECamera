#!/bin/bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
BASE=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization
D=$BASE/ap-bounded-imx681-control-runtime
AM=$BASE/am-imx681-exposure-cluster-fix
AO=$BASE/ao-paired-stats-audit-helper
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
fail(){ echo "FAIL: $*" >&2; exit 1; }
"$BASE/ai-deadline-hardened-live-r5-r6-runtime/prearm-check.sh"
T=$(mktemp); trap 'rm -f "$T"' EXIT
make -C "$K" M="$AM" clean >/dev/null
make -C "$K" M="$AM" W=1 -j4 >"$T" 2>&1 || { cat "$T"; fail am_build; }
H=$(sha256sum "$AM/imx681.ko" | awk '{print $1}')
[ "$H" = 'c2b63b747176d3e8a7f8ee658833e0c1806fad9e03185840208ff5e466ce6ba8' ] || fail "am_module_sha_$H"
python3 "$AM/windows-oracle/oracle.py" --self-test >/dev/null
python3 "$AM/prove-am.py" >/dev/null
python3 "$AO/prove-ao.py" >/dev/null
gcc -O2 -std=c11 -Wall -Wextra -Werror -pthread "$AO/e003i-ao-six-frame-live-iq.c" -o /tmp/e003i-ap-helper-prearm
rm -f /tmp/e003i-ap-helper-prearm
python3 "$D/verify.py"
modinfo -F vermagic "$AM/imx681.ko" | grep -Fxq '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64' || fail vermagic
printf 'AP_ROOT_PREARM=PASS AM_MODULE=%s AO_HELPER=b3a8969e...\n' "$H"
