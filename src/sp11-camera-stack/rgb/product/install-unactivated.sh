#!/usr/bin/env bash
# Install only camera-free pre-release service assets. Never enable/start/arm.
set -Eeuo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
DEST=/usr/local/libexec/sp11-camera-stack/rgb/product
SERVICE_DEST=/usr/local/libexec/sp11-camera-stack/rgb/service
ROUTING_DEST=/usr/local/libexec/sp11-camera-stack/routing
STATE=/var/lib/sp11-camera-rgb
"$REPO/tools/camera-overlap-guard.sh" --require-clean-tracked --require-golden --require-no-camera-process >/dev/null
[[ ! -e /dev/media0 && ! -d /sys/module/qcom_camss && ! -d /sys/module/imx681 && ! -d /sys/module/ov13858 ]]
python3 -m unittest discover -s "$HERE/../service/tests" -p 'test_*.py' -q
python3 -m unittest discover -s "$HERE/tests" -p 'test_*.py' -q
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
CFLAGS=(-O3 -std=c11 -Wall -Wextra -Werror -pedantic -fno-fast-math -ffp-contract=off -DSP11_CAMERA_ALLOW_CONTINUOUS=1 -DSP11_RGB_NV12_VIDEO_RANGE=1 -DSP11_RGB_NV12_BT601_TAG=1 '-DSP11_CAMERA_BOOT_TOKEN="sp11_camera_rgb_product=1"')
gcc "${CFLAGS[@]}" "$HERE/../front-direct-publisher.c" -o "$TMP/front-direct-publisher"
gcc "${CFLAGS[@]}" "$HERE/../rear-direct-publisher.c" -o "$TMP/rear-direct-publisher"
# Product boot token is absent on Golden, so even copied binaries remain inert.
! grep -qw 'sp11_camera_rgb_product=1' /proc/cmdline
sudo -n install -d -m 0755 "$DEST" "$SERVICE_DEST" "$ROUTING_DEST"
for f in product_owner.py product_daemon.py productctl.py private_optical_preview.py; do sudo -n install -m 0755 "$HERE/$f" "$DEST/$f"; done
sudo -n install -m 0755 "$HERE/recover-golden.sh" "$DEST/recover-golden.sh"
for f in session.py media_backend.py rgb_device_backend.py; do sudo -n install -m 0644 "$HERE/../service/$f" "$SERVICE_DEST/$f"; done
for f in route_policy.py graph_contract.py; do sudo -n install -m 0644 "$REPO/src/sp11-camera-stack/routing/$f" "$ROUTING_DEST/$f"; done
sudo -n install -d -m 0700 "$STATE" "$STATE/bin" "$STATE/output" "$STATE/private-optical"
sudo -n install -m 0700 "$TMP/front-direct-publisher" "$STATE/bin/front-direct-publisher"
sudo -n install -m 0700 "$TMP/rear-direct-publisher" "$STATE/bin/rear-direct-publisher"
sudo -n install -m 0700 "$HERE/start-session.sh" "$STATE/start-session.sh"
sudo -n install -m 0700 "$HERE/record-stop.py" "$STATE/record-stop.py"
# Reuse exact maintained route parser; no physical route operation occurs here.
sudo -n install -m 0600 "$REPO/experiments/E004-front-ir-vd55g0/e004ma-guarded-opt-in-rgb-selector-service-one-shot/route-state.py" "$STATE/route-state.py"
sudo -n install -m 0600 "$REPO/experiments/E004-front-ir-vd55g0/e004ma-guarded-opt-in-rgb-selector-service-one-shot/camera-session-contract.py" "$STATE/camera-session-contract.py"
sudo -n install -m 0644 "$HERE/sp11-camera-rgb.service" /etc/systemd/system/sp11-camera-rgb.service
sudo -n install -m 0644 "$HERE/sp11-camera-rgb-publisher@.service" /etc/systemd/system/sp11-camera-rgb-publisher@.service
sudo -n install -m 0644 "$HERE/sp11-camera-rgb-recover.service" /etc/systemd/system/sp11-camera-rgb-recover.service
sudo -n install -m 0755 "$HERE/productctl.py" /usr/local/bin/sp11-rgbctl
printf '%s\n' "$(git rev-parse HEAD)" | sudo -n tee "$STATE/SOURCE-HEAD" >/dev/null
sudo -n chmod 0600 "$STATE/SOURCE-HEAD"
sudo -n bash -c 'find "$1" "$2" "$3" "$4" -type f ! -name PRODUCT-ASSETS.sha256 -print0 | sort -z | xargs -0 sha256sum > "$4/PRODUCT-ASSETS.sha256"' bash "$DEST" "$SERVICE_DEST" "$ROUTING_DEST" "$STATE"
sudo -n chmod 0600 "$STATE/PRODUCT-ASSETS.sha256"
sudo -n sh -c 'cd / && sha256sum -c /var/lib/sp11-camera-rgb/PRODUCT-ASSETS.sha256 >/dev/null'
sudo -n systemd-analyze verify /etc/systemd/system/sp11-camera-rgb.service /etc/systemd/system/sp11-camera-rgb-publisher@.service /etc/systemd/system/sp11-camera-rgb-recover.service
sudo -n systemctl daemon-reload
sudo -n systemctl disable sp11-camera-rgb.service >/dev/null 2>&1 || :
sudo -n rm -f "$STATE/ENABLE"
! sudo -n systemctl is-active --quiet sp11-camera-rgb.service
! sudo -n systemctl is-enabled --quiet sp11-camera-rgb.service
sudo -n "$HERE/verify-unactivated.py"
echo SP11_RGB_PRODUCT_INSTALL=PASS ACTIVATED=NO BOOT_ENTRY=NONE
