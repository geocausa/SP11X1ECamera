#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(git -C "$ROOT" rev-parse --show-toplevel)"
HW=${1:?hardware authority build directory required}
OUT=${2:?staging root required}
[ "$(sha256sum "$HW/HARDWARE-MANIFEST.sha256" | awk '{print $1}')" = ad96f706b5e0c5440707c0b9dc5d40a1376391b792f03d3d20bba5d23244f53c ] || { echo hardware_manifest_drift >&2; exit 1; }
(cd "$HW" && sha256sum -c HARDWARE-MANIFEST.sha256 >/dev/null)
rm -rf "$OUT"; mkdir -p "$OUT"
FB="$OUT/.front-build-input"; mkdir -p "$FB"
install -m 0755 "$HW/bin/front-imx681-capture" "$FB/front-imx681-capture"
install -m 0755 "$HW/bin/front-imx681-bootstrap-controls" "$FB/front-imx681-bootstrap-controls"
install -m 0644 "$HW/modules/qcom-camss.ko" "$FB/qcom-camss.ko"
install -m 0644 "$HW/modules/imx681.ko" "$FB/imx681.ko"
BUILD_DIR="$FB" "$REPO/src/front-imx681/stage-package.sh" "$OUT" > "$OUT/.front-stage.log"
mv "$OUT/PACKAGE-MANIFEST.sha256" "$OUT/FRONT-PACKAGE-MANIFEST.sha256"
rm -rf "$FB"
HP="$OUT/usr/lib/sp11-camera-stack/hardware"; mkdir -p "$HP/modules" "$HP/dtb" "$OUT/usr/lib/sp11-camera-stack/meta"
install -m 0644 "$HW/modules/qcom-camss.ko" "$HP/modules/qcom-camss.ko"
install -m 0644 "$HW/modules/imx681.ko" "$HP/modules/imx681.ko"
install -m 0644 "$HW/modules/ov13858.ko" "$HP/modules/ov13858.ko"
install -m 0644 "$HW/modules/sp11-vd55g0.ko" "$HP/modules/sp11-vd55g0.ko"
install -m 0644 "$HW/dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb" "$HP/dtb/"
install -m 0644 "$HW/HARDWARE-MANIFEST.sha256" "$HP/HARDWARE-MANIFEST.sha256"
# Package only committed stack metadata; no experiment/build debris.
git -C "$REPO" archive HEAD:src/sp11-camera-stack README.md PROVENANCE.json | tar -x -C "$OUT/usr/lib/sp11-camera-stack/meta"
(
 cd "$OUT"
 find usr -type f -print0 | sort -z | xargs -0 sha256sum > CAMERA-STACK-MANIFEST.sha256
)
printf 'SP11_CAMERA_STACK_STAGE=PASS ACTIVATED=NO\n'
# Production front RGB launch requires a separately SHA-verified R4 capsule
# that git archive would otherwise omit. Both manifests must cover it.
python3 "$ROOT/verify-package.py" "$OUT" --require-r4 > "$OUT/.rgb-r4-stage-verification.log"
sha256sum "$OUT/FRONT-PACKAGE-MANIFEST.sha256" "$OUT/CAMERA-STACK-MANIFEST.sha256"
