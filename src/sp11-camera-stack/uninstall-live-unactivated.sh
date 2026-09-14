#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
REPO="$(git -C "$ROOT" rev-parse --show-toplevel)"
STATE=/var/lib/sp11-camera-stack
"$REPO/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process >/dev/null
sudo -n test -f "$STATE/installed-camera-stack-manifest.sha256" || { echo managed_state_missing >&2; exit 1; }
sudo -n sh -c 'cd / && sha256sum -c /var/lib/sp11-camera-stack/installed-camera-stack-manifest.sha256 >/dev/null'
while read -r _ path; do [ -n "${path:-}" ] && sudo -n rm -f "/$path"; done < <(sudo -n cat "$STATE/installed-camera-stack-manifest.sha256")
sudo -n rm -f "$STATE/installed-camera-stack-manifest.sha256" "$STATE/installed-front-package-manifest.sha256" "$STATE/INSTALL-STATE.txt"
for root in /usr/lib/sp11-front-imx681 /usr/lib/sp11-camera-stack; do sudo -n test ! -d "$root" || sudo -n find "$root" -depth -type d -empty -delete; done
sudo -n rmdir /var/lib/sp11-camera-stack 2>/dev/null || true
for p in /usr/lib/sp11-front-imx681 /usr/lib/sp11-camera-stack /usr/bin/sp11-front-imx681 /usr/bin/sp11-front-imx681-discover /var/lib/sp11-camera-stack; do sudo -n test ! -e "$p" || { echo "managed path remains: $p" >&2; exit 1; }; done
for m in qcom_camss imx681 ov13858 sp11_vd55g0; do [ ! -d "/sys/module/$m" ] || { echo "camera module active: $m" >&2; exit 1; }; done
echo 'SP11_CAMERA_STACK_LIVE_UNINSTALL=PASS ACTIVATED=NO'
