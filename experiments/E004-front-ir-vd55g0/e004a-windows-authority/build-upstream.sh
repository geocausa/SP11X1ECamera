#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004a-windows-authority
SRC=$R/src/front-ir-vd55g0/st-vd55g0
K=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826
B=$D/build
rm -rf "$B"
mkdir -p "$B"
cp "$SRC/vd55g0.c" "$SRC/vd55g0_patches.h" "$SRC/Kbuild" "$SRC/Makefile" "$B/"
make -C "$B" KERNEL_SRC="$K" -j2
modinfo "$B/vd55g0.ko"
sha256sum "$B/vd55g0.ko"
