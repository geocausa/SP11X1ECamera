#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
NEW=$REPO/experiments/E003-front-imx681-cphy/e003h-csid1-first-irq-geometry-0050-candidate
SETUP=$NEW/setup-pix-media.sh
[ "$(sha256sum "$SETUP" | cut -d' ' -f1)" = 666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f ] || { echo 'FAIL: setup-media oracle drift' >&2; exit 1; }
exec "$SETUP" "${1:-/dev/media0}"
