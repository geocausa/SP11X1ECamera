#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(git -C "$ROOT" rev-parse --show-toplevel)"
PKG=${1:?staged package root required}
STACK_SHA=d1d0eb4c504378643630f6975a08d9c15d2b8ac0bedca2f1205bbfb51f885373
STATE=/var/lib/sp11-camera-stack
"$REPO/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process >/dev/null
PYTHONDONTWRITEBYTECODE=1 python3 "$ROOT/verify-package.py" "$PKG" >/dev/null
[ "$(sha256sum "$PKG/CAMERA-STACK-MANIFEST.sha256"|awk '{print $1}')" = "$STACK_SHA" ] || { echo unaccepted_stack_manifest >&2; exit 1; }
for m in qcom_camss imx681 ov13858 sp11_vd55g0; do [ ! -d "/sys/module/$m" ] || { echo "camera module active: $m" >&2; exit 1; }; done
! ls /dev/media* >/dev/null 2>&1 || { echo 'media node active' >&2; exit 1; }
if sudo -n test -f "$STATE/installed-camera-stack-manifest.sha256"; then
  sudo -n sh -c 'cd / && sha256sum -c /var/lib/sp11-camera-stack/installed-camera-stack-manifest.sha256 >/dev/null'
  while read -r _ path; do [ -n "${path:-}" ] && sudo -n rm -f "/$path"; done < <(sudo -n cat "$STATE/installed-camera-stack-manifest.sha256")
else
  for p in /usr/lib/sp11-front-imx681 /usr/lib/sp11-camera-stack /usr/bin/sp11-front-imx681 /usr/bin/sp11-front-imx681-discover; do sudo -n test ! -e "$p" || { echo "unmanaged pre-existing path: $p" >&2; exit 1; }; done
fi
( cd "$PKG" && tar -cf - usr ) | sudo -n tar -xf - -C /
sudo -n mkdir -p "$STATE"
sudo -n install -m 0644 "$PKG/CAMERA-STACK-MANIFEST.sha256" "$STATE/installed-camera-stack-manifest.sha256"
sudo -n install -m 0644 "$PKG/FRONT-PACKAGE-MANIFEST.sha256" "$STATE/installed-front-package-manifest.sha256"
printf 'schema=sp11-camera-stack-live-unactivated-v1\nactivated=NO\npackage_manifest_sha256=%s\nfront_manifest_sha256=%s\n' \
  "$STACK_SHA" "$(sha256sum "$PKG/FRONT-PACKAGE-MANIFEST.sha256"|awk '{print $1}')" | sudo -n tee "$STATE/INSTALL-STATE.txt" >/dev/null
sudo -n chmod 0644 "$STATE/INSTALL-STATE.txt"
echo 'SP11_CAMERA_STACK_LIVE_INSTALL=PASS ACTIVATED=NO'
