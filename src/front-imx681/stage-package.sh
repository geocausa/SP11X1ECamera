#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(git -C "$ROOT" rev-parse --show-toplevel)"
OUT=${1:?staging root required}
BUILD=${BUILD_DIR:-$ROOT/build}
PREFIX="$OUT/usr/lib/sp11-front-imx681"
BINDIR="$OUT/usr/bin"
for f in front-imx681-capture front-imx681-bootstrap-controls qcom-camss.ko imx681.ko; do
  [ -f "$BUILD/$f" ] || { echo "missing build artifact: $BUILD/$f" >&2; exit 1; }
done
rm -rf "$PREFIX"
mkdir -p "$PREFIX" "$BINDIR"
# HEAD archive is deliberate: package only committed runtime assets, never ignored HG caches or build-tree debris.
git -C "$REPO" archive HEAD:src/front-imx681 bin userspace/iq README.md PROVENANCE.json | tar -x -C "$PREFIX"
mkdir -p "$PREFIX/build"
install -m 0755 "$BUILD/front-imx681-capture" "$PREFIX/build/front-imx681-capture"
install -m 0755 "$BUILD/front-imx681-bootstrap-controls" "$PREFIX/build/front-imx681-bootstrap-controls"
install -m 0644 "$BUILD/qcom-camss.ko" "$PREFIX/build/qcom-camss.ko"
install -m 0644 "$BUILD/imx681.ko" "$PREFIX/build/imx681.ko"
cat > "$BINDIR/sp11-front-imx681" <<'WRAP'
#!/usr/bin/env bash
exec /usr/lib/sp11-front-imx681/bin/front-imx681-launcher.py "$@"
WRAP
cat > "$BINDIR/sp11-front-imx681-discover" <<'WRAP'
#!/usr/bin/env bash
exec /usr/lib/sp11-front-imx681/bin/front-imx681-discover.py "$@"
WRAP
chmod 0755 "$BINDIR/sp11-front-imx681" "$BINDIR/sp11-front-imx681-discover"
(
  cd "$OUT"
  find usr -type f -print0 | sort -z | xargs -0 sha256sum > PACKAGE-MANIFEST.sha256
)
printf 'FRONT_IMX681_PACKAGE_STAGE=PASS PREFIX=%s\n' "$PREFIX"
sha256sum "$OUT/PACKAGE-MANIFEST.sha256"
