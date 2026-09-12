#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ic-unified-dtb-rear-regression-r16
[ -s "$D/ARCHIVE-PATH.txt" ] || { echo 'FAIL: no archive path' >&2; exit 1; }
A=$(cat "$D/ARCHIVE-PATH.txt"); [ -d "$A" ] || { echo 'FAIL: archive missing' >&2; exit 1; }
for f in GOLDEN-RETURN.txt RETIRE.txt ATTEMPT1-PASS.json ATTEMPT1-FAILURE.json; do [ -f "$D/$f" ] && cp "$D/$f" "$A/$f"; done
(cd "$A" && find . -type f ! -name MANIFEST.sha256 -print0 | sort -z | xargs -0 sha256sum > MANIFEST.sha256 && sha256sum -c MANIFEST.sha256 >/dev/null)
sha256sum "$A/MANIFEST.sha256"
echo "IC_ARCHIVE_FINAL=PASS PATH=$A"
