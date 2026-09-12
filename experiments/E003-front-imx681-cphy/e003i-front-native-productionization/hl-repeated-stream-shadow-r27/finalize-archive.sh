#!/usr/bin/env bash
set -euo pipefail
D=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hl-repeated-stream-shadow-r27
A=$(cat "$D/ARCHIVE-PATH.txt"); [ -d "$A" ]
for f in GOLDEN-RETURN.txt RETIRE.txt ATTEMPT1-PASS.json; do [ -f "$D/$f" ] && cp "$D/$f" "$A/$f"; done
(cd "$A" && find . -type f ! -name MANIFEST.sha256 -print0 | sort -z | xargs -0 sha256sum > MANIFEST.sha256 && sha256sum -c MANIFEST.sha256 >/dev/null)
echo "HL_ARCHIVE_FINALIZED=$A MANIFEST_SHA=$(sha256sum "$A/MANIFEST.sha256"|awk '{print $1}')"
