#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
KERNEL_SOURCE="${KERNEL_SOURCE:?set KERNEL_SOURCE to the SP11 Kbuild source frontend used by the accepted modules}"
KERNEL_BUILD="${KERNEL_BUILD:?set KERNEL_BUILD to the prepared SP11 kernel output/header tree}"
OUT="${1:-$ROOT/build}"
CAMSS_SHA=862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7
IMX_SHA=ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6
CAP_SHA=70f407f5fd70e6657f9647a33eecde744ac9e1bd19fa9e901a4faf52508e354d
BOOT_SHA=4721ff6510d806ed63ffcb70d9a88441220047ef734ca760cc40bdc5719cd7ce
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
make -C "$KERNEL_SOURCE" O="$KERNEL_BUILD" M="$WORK/camss" clean >/dev/null
make -C "$KERNEL_SOURCE" O="$KERNEL_BUILD" M="$WORK/camss" W=1 KCFLAGS="$MAP" KCPPFLAGS="$MAP" -j4 >/dev/null
make -C "$KERNEL_SOURCE" O="$KERNEL_BUILD" M="$WORK/imx681" clean >/dev/null
make -C "$KERNEL_SOURCE" O="$KERNEL_BUILD" M="$WORK/imx681" W=1 KCFLAGS="$MAP" KCPPFLAGS="$MAP" -j4 >/dev/null
cp "$WORK/camss/qcom-camss.ko" "$OUT/qcom-camss.ko"
cp "$WORK/imx681/imx681.ko" "$OUT/imx681.ko"
sha(){ sha256sum "$1" | awk '{print $1}'; }
[ "$(sha "$OUT/front-imx681-capture")" = "$CAP_SHA" ] || { echo 'front capture hash drift' >&2; exit 1; }
[ "$(sha "$OUT/front-imx681-bootstrap-controls")" = "$BOOT_SHA" ] || { echo 'front bootstrap hash drift' >&2; exit 1; }
[ "$(sha "$OUT/qcom-camss.ko")" = "$CAMSS_SHA" ] || { echo 'CAMSS hash drift: KERNEL_SOURCE/KERNEL_BUILD do not reproduce accepted E004du authority' >&2; exit 1; }
[ "$(sha "$OUT/imx681.ko")" = "$IMX_SHA" ] || { echo 'IMX681 hash drift: KERNEL_SOURCE/KERNEL_BUILD do not reproduce accepted authority' >&2; exit 1; }
printf 'FRONT_IMX681_PRODUCTION_BUILD=PASS EXACT_ACCEPTED_MODULES=YES\n'
sha256sum "$OUT/front-imx681-capture" "$OUT/front-imx681-bootstrap-controls" "$OUT/qcom-camss.ko" "$OUT/imx681.ko"
modinfo -F vermagic "$OUT/qcom-camss.ko"
modinfo -F vermagic "$OUT/imx681.ko"
