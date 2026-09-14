#!/usr/bin/env bash
set -euo pipefail
DEST=${1:?destination root required}
[ "$DEST" != / ] || { echo 'live root uninstall is intentionally forbidden by this tool' >&2; exit 2; }
STATE="$DEST/var/lib/sp11-camera-stack"
MAN="$STATE/installed-camera-stack-manifest.sha256"
[ -f "$MAN" ] || { echo 'managed install state missing' >&2; exit 1; }
while read -r _ path; do [ -n "${path:-}" ] && rm -f "$DEST/$path"; done < "$MAN"
rm -f "$STATE/installed-camera-stack-manifest.sha256" "$STATE/installed-front-package-manifest.sha256" "$STATE/INSTALL-STATE.txt"
# Remove empty directories only inside package-owned roots; unrelated trees are never traversed.
for root in "$DEST/usr/lib/sp11-front-imx681" "$DEST/usr/lib/sp11-camera-stack"; do
  [ ! -d "$root" ] || find "$root" -depth -type d -empty -delete
done
rmdir "$DEST/usr/bin" 2>/dev/null || true
rmdir "$STATE" 2>/dev/null || true
rmdir "$DEST/var/lib" 2>/dev/null || true
rmdir "$DEST/var" 2>/dev/null || true
rmdir "$DEST/usr/lib" 2>/dev/null || true
rmdir "$DEST/usr" 2>/dev/null || true
echo 'SP11_CAMERA_STACK_ROOT_UNINSTALL=PASS'
