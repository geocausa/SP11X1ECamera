#!/usr/bin/env bash
set -euo pipefail

KERNEL_SRC=${KERNEL_SRC:-/home/geoca/Documents/SP11-PROJECT/02-kernel/linux-7.1.5}
KERNEL_BUILD=${KERNEL_BUILD:-/lib/modules/$(uname -r)/build}
OUT=${OUT:-/tmp/e004ar-qcomtee-build}

rm -rf "$OUT"
mkdir -p "$OUT"
cp "$KERNEL_SRC"/drivers/tee/qcomtee/*.[ch] "$KERNEL_SRC"/drivers/tee/qcomtee/Makefile "$OUT"/

echo "This is build-only. The script does not install or load qcomtee."
make -C "$KERNEL_BUILD" M="$OUT" CONFIG_QCOMTEE=m modules
modinfo "$OUT/qcomtee.ko"
sha256sum "$OUT/qcomtee.ko"
