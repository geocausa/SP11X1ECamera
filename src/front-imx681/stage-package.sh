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
# The accepted front launcher REQUIRES the exact derived R4 bootstrap.
# Git archive intentionally excludes *.bin, so verify the local source
# independently and add ONLY this 41,088-byte SHA-pinned sidecar. E004ja
# proved that silently omitting it makes the actual front launcher fail.
R4_SRC="$ROOT/userspace/iq/authority/r4-bootstrap.bin"
R4_DEST="$PREFIX/userspace/iq/authority/r4-bootstrap.bin"
R4_SHA=1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa
[ -f "$R4_SRC" ] && [ ! -L "$R4_SRC" ] &&
[ "$(stat -c%s "$R4_SRC")" -eq 41088 ] &&
[ "$(sha256sum "$R4_SRC" | awk '{print $1}')" = "$R4_SHA" ] || {
  echo FRONT_R4_BOOTSTRAP_SOURCE_MISSING_OR_DRIFTED >&2; exit 1;
}
[ ! -e "$R4_DEST" ] || { echo FRONT_R4_UNEXPECTED_IN_GIT_ARCHIVE >&2; exit 1; }
python3 - "$PREFIX/userspace/iq/authority/r4-bootstrap.json" "$R4_SHA" <<'PY'
from pathlib import Path
import json,sys
p=Path(sys.argv[1]); expected=sys.argv[2]; m=json.loads(p.read_text())
assert m['bytes']==41088 and m['sha256']==expected
assert m['derived_normalized_capsule'] is True
assert m['raw_request_slot'] is False
PY
install -m 0600 "$R4_SRC" "$R4_DEST"
[ "$(sha256sum "$R4_DEST" | awk '{print $1}')" = "$R4_SHA" ] ||
  { echo FRONT_R4_STAGED_SHA_DRIFT >&2; exit 1; }
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
