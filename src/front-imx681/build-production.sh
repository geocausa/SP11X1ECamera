#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
KERNEL_BUILD="${KERNEL_BUILD:?set KERNEL_BUILD to the SP11 kernel build/header tree}"
OUT="${1:-$ROOT/build}"
mkdir -p "$OUT"
"$ROOT/build-userspace.sh" "$OUT"
WORK="${SP11_FRONT_KBUILD_WORK:-/tmp/sp11-front-imx681-kbuild}"
LOCK="${WORK}.lock"
exec 9>"$LOCK"
flock 9
rm -rf "$WORK"
mkdir -p "$WORK/camss" "$WORK/imx681"
trap 'rm -rf "$WORK"' EXIT
cp -a "$ROOT/kernel/camss"/. "$WORK/camss/"
cp -a "$ROOT/kernel/imx681"/. "$WORK/imx681/"
MAP="-ffile-prefix-map=$WORK=/usr/src/sp11-front-imx681 -fdebug-prefix-map=$WORK=/usr/src/sp11-front-imx681 -fmacro-prefix-map=$WORK=/usr/src/sp11-front-imx681"
make -C "$KERNEL_BUILD" M="$WORK/camss" clean >/dev/null
make -C "$KERNEL_BUILD" M="$WORK/camss" W=1 KCFLAGS="$MAP" KCPPFLAGS="$MAP" -j4 >/dev/null
make -C "$KERNEL_BUILD" M="$WORK/imx681" clean >/dev/null
make -C "$KERNEL_BUILD" M="$WORK/imx681" W=1 KCFLAGS="$MAP" KCPPFLAGS="$MAP" -j4 >/dev/null
cp "$WORK/camss/qcom-camss.ko" "$OUT/qcom-camss.ko"
cp "$WORK/imx681/imx681.ko" "$OUT/imx681.ko"
printf 'FRONT_IMX681_PRODUCTION_BUILD=PASS\n'
sha256sum "$OUT/front-imx681-capture" "$OUT/front-imx681-bootstrap-controls" "$OUT/qcom-camss.ko" "$OUT/imx681.ko"
modinfo -F vermagic "$OUT/qcom-camss.ko"
modinfo -F vermagic "$OUT/imx681.ko"
