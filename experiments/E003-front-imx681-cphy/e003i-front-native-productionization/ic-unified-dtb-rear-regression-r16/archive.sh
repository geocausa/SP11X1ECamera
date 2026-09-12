#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ic-unified-dtb-rear-regression-r16
O=$D/runtime-output; ROOT=/home/geoca/Documents/SP11-PROJECT/00-RE-archive/camera-ic
if [ -s "$D/ARCHIVE-PATH.txt" ]; then A=$(cat "$D/ARCHIVE-PATH.txt"); else mkdir -p "$ROOT"; A="$ROOT/attempt1-${1:-unknown}-$(date +%Y%m%dT%H%M%S)"; echo "$A" > "$D/ARCHIVE-PATH.txt"; fi
mkdir -p "$A"; sudo -n cp -a "$O" "$A/runtime-output"; sudo -n chown -R geoca:geoca "$A"
for f in INSTALL.txt ARM.txt ATTEMPT1-CONSUMED.marker ATTEMPT1-PASS.json ATTEMPT1-FAILURE.json DISCOVERY.json LOAD-DMESG.txt DMESG.txt; do [ -f "$D/$f" ] && cp "$D/$f" "$A/$f"; done
printf 'STATUS=%s\nTIME=%s\nHEAD=%s\nBOOT_ID=%s\n' "${1:-unknown}" "$(date -Ins)" "$(git -C "$R" rev-parse HEAD)" "$(cat /proc/sys/kernel/random/boot_id)" > "$A/CANDIDATE-RESULT.txt"
(cd "$A" && find . -type f ! -name MANIFEST.sha256 -print0 | sort -z | xargs -0 sha256sum > MANIFEST.sha256 && sha256sum -c MANIFEST.sha256 >/dev/null)
echo "IC_ARCHIVE=$A"
