#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-imx681-mode2-parity-0054-candidate
SETUP=$NEW/setup-pix-media.sh
EXP=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["assets"]["setup-pix-media.sh"])' "$NEW/asset-manifest.json")
[ "$(sha256sum "$SETUP" | cut -d' ' -f1)" = "$EXP" ] || { echo 'FAIL: setup-media oracle drift' >&2; exit 1; }
exec "$SETUP" "${1:-/dev/media0}"
