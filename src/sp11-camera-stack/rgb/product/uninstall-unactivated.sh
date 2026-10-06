#!/usr/bin/env bash
set -Eeuo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); REPO=$(git -C "$HERE" rev-parse --show-toplevel); STATE=/var/lib/sp11-camera-rgb
"$REPO/tools/camera-overlap-guard.sh" --require-golden --require-no-camera-process >/dev/null
! systemctl is-active --quiet sp11-camera-rgb.service
sudo -n test ! -e "$STATE/ENABLE"
sudo -n systemctl disable sp11-camera-rgb.service >/dev/null 2>&1 || :
for x in sp11-camera-rgb.service sp11-camera-rgb-publisher@.service sp11-camera-rgb-recover.service; do sudo -n rm -f "/etc/systemd/system/$x"; done
sudo -n rm -f /usr/local/bin/sp11-rgbctl
sudo -n rm -rf /usr/local/libexec/sp11-camera-stack/rgb/product /usr/local/libexec/sp11-camera-stack/rgb/service /usr/local/libexec/sp11-camera-stack/routing "$STATE"
sudo -n systemctl daemon-reload
echo SP11_RGB_PRODUCT_UNINSTALL=PASS
