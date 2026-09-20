#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PKG=${1:?staged package root required}
DEST=${2:?destination root required}
[ "$DEST" != / ] || { echo 'live root install is intentionally forbidden by this tool' >&2; exit 2; }
[ -d "$PKG/usr" ] || { echo 'package usr tree missing' >&2; exit 1; }
PYTHONDONTWRITEBYTECODE=1 python3 "$ROOT/verify-package.py" "$PKG" >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$ROOT/offline-root-guard.py" install "$PKG" "$DEST" >/dev/null
mkdir -p "$DEST"
STATE="$DEST/var/lib/sp11-camera-stack"
# If a previous managed install exists, remove only its previously listed files first.
if [ -f "$STATE/installed-camera-stack-manifest.sha256" ]; then
  while read -r _ path; do [ -n "${path:-}" ] && rm -f "$DEST/$path"; done < "$STATE/installed-camera-stack-manifest.sha256"
fi
mkdir -p "$STATE"
( cd "$PKG" && tar -cf - usr ) | ( cd "$DEST" && tar -xf - )
install -m 0644 "$PKG/CAMERA-STACK-MANIFEST.sha256" "$STATE/installed-camera-stack-manifest.sha256"
install -m 0644 "$PKG/FRONT-PACKAGE-MANIFEST.sha256" "$STATE/installed-front-package-manifest.sha256"
printf 'schema=sp11-camera-stack-root-install-v1\nactivated=NO\npackage_manifest_sha256=%s\nfront_manifest_sha256=%s\n' \
  "$(sha256sum "$PKG/CAMERA-STACK-MANIFEST.sha256"|awk '{print $1}')" \
  "$(sha256sum "$PKG/FRONT-PACKAGE-MANIFEST.sha256"|awk '{print $1}')" > "$STATE/INSTALL-STATE.txt"
echo 'SP11_CAMERA_STACK_ROOT_INSTALL=PASS ACTIVATED=NO'
