#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(git -C "$ROOT" rev-parse --show-toplevel)"
KERNEL_SOURCE="${KERNEL_SOURCE:?set KERNEL_SOURCE to the accepted SP11 Kbuild source frontend}"
KERNEL_BUILD="${KERNEL_BUILD:?set KERNEL_BUILD to the prepared SP11 kernel output/header tree}"
OUT="${1:-$ROOT/build}"
FRONT="$REPO/src/front-imx681"
IR="$REPO/src/front-ir-vd55g0/sp11-vd55g0-native"
rm -rf "$OUT"; mkdir -p "$OUT/modules" "$OUT/bin" "$OUT/dtb" "$OUT/meta"
python3 "$ROOT/build-unified-dtb.py" \
  --ib "$ROOT/authority/ib-unified-rear-front.dtb" \
  --ir "$ROOT/authority/ir-native-bind.dtb" \
  --hv-builder "$ROOT/fdt_authority.py" \
  --out "$OUT/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" > "$OUT/meta/DTB-BUILD.txt"
FRONT_OUT="$OUT/.front-build"
KERNEL_SOURCE="$KERNEL_SOURCE" KERNEL_BUILD="$KERNEL_BUILD" "$FRONT/build-production.sh" "$FRONT_OUT" > "$OUT/meta/FRONT-BUILD.txt"
install -m 0644 "$FRONT_OUT/qcom-camss.ko" "$OUT/modules/qcom-camss.ko"
install -m 0644 "$FRONT_OUT/imx681.ko" "$OUT/modules/imx681.ko"
install -m 0755 "$FRONT_OUT/front-imx681-capture" "$OUT/bin/front-imx681-capture"
install -m 0755 "$FRONT_OUT/front-imx681-bootstrap-controls" "$OUT/bin/front-imx681-bootstrap-controls"
# Build VD55G0 from a disposable source copy while preserving its canonical debug path.
VDWORK="$OUT/.vd55g0-build"; mkdir -p "$VDWORK"
HEADER="$IR/surface-windows.generated.h"
[ ! -e "$HEADER" ] || { echo "refusing to overwrite existing $HEADER" >&2; exit 1; }
trap 'rm -f "$HEADER"' EXIT
python3 "$IR/generate_windows_header.py" > "$OUT/meta/VD55G0-HEADER.txt"
cp "$IR/sp11-vd55g0.c" "$IR/Makefile" "$HEADER" "$VDWORK/"
rm -f "$HEADER"
MAP="-ffile-prefix-map=$VDWORK=$IR -fdebug-prefix-map=$VDWORK=$IR -fmacro-prefix-map=$VDWORK=$IR"
make -C "$KERNEL_SOURCE" O="$KERNEL_BUILD" M="$VDWORK" clean >/dev/null
make -C "$KERNEL_SOURCE" O="$KERNEL_BUILD" M="$VDWORK" modules KCFLAGS="$MAP" KCPPFLAGS="$MAP" -j4 > "$OUT/meta/VD55G0-BUILD.txt"
install -m 0644 "$VDWORK/sp11-vd55g0.ko" "$OUT/modules/sp11-vd55g0.ko"
install -m 0644 "$ROOT/authority/ov13858-production.ko" "$OUT/modules/ov13858.ko"
rm -rf "$FRONT_OUT" "$VDWORK"; trap - EXIT
sha(){ sha256sum "$1" | awk '{print $1}'; }
[ "$(sha "$OUT/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb")" = 3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb ] || { echo DTB_DRIFT >&2; exit 1; }
[ "$(sha "$OUT/modules/qcom-camss.ko")" = 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ] || { echo CAMSS_DRIFT >&2; exit 1; }
[ "$(sha "$OUT/modules/imx681.ko")" = ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6 ] || { echo IMX681_DRIFT >&2; exit 1; }
[ "$(sha "$OUT/modules/ov13858.ko")" = 13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309 ] || { echo OV13858_DRIFT >&2; exit 1; }
[ "$(sha "$OUT/modules/sp11-vd55g0.ko")" = 4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72 ] || { echo VD55G0_DRIFT >&2; exit 1; }
[ "$(sha "$OUT/bin/front-imx681-capture")" = 70f407f5fd70e6657f9647a33eecde744ac9e1bd19fa9e901a4faf52508e354d ] || { echo FRONT_CAPTURE_DRIFT >&2; exit 1; }
[ "$(sha "$OUT/bin/front-imx681-bootstrap-controls")" = 4721ff6510d806ed63ffcb70d9a88441220047ef734ca760cc40bdc5719cd7ce ] || { echo FRONT_BOOTSTRAP_DRIFT >&2; exit 1; }
(
 cd "$OUT"
 find bin dtb modules -type f -print0 | sort -z | xargs -0 sha256sum > HARDWARE-MANIFEST.sha256
)
printf 'SP11_CAMERA_HARDWARE_AUTHORITY=PASS THREE_SENSORS=YES SECUREISP=NO\n'
cat "$OUT/HARDWARE-MANIFEST.sha256"
