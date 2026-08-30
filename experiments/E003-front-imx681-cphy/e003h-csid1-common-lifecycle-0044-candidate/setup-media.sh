#!/bin/bash
set -euo pipefail
REPO=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
OLD=$REPO/experiments/E003-front-imx681-cphy/e003h-bounded-vfe1-pix-runtime-candidate
[ "$(sha256sum "$OLD/setup-pix-media.sh" | cut -d' ' -f1)" = 666e458daf9a3ed8938d81d10fd3d3a0e4f760252db920e09531bd7aa3ef633f ] || { echo 'FAIL: setup-media oracle drift' >&2; exit 1; }
exec "$OLD/setup-pix-media.sh" "${1:-/dev/media0}"
