#!/usr/bin/env bash
set -Eeuo pipefail
D=/var/lib/sp11-camera-e012i
P=/var/lib/sp11-camera-rgb
O=$P/output
TOKEN=sp11_camera_rgb_product=1
ENTRY=sp11_entry=7.1.5-sp11-camera-rgb-product
[[ "$EUID" == 0 ]]
grep -qw "$TOKEN" /proc/cmdline; grep -qw "$ENTRY" /proc/cmdline
[[ "$(uname -r)" == 7.1.5-sp11-render-parity-v4+ ]]
[[ ! -e "$D/ATTEMPT-CONSUMED" ]]
printf 'boot_id=%s\ntime=%s\n' "$(cat /proc/sys/kernel/random/boot_id)" "$(date -Is)" > "$D/ATTEMPT-CONSUMED"
chmod 0600 "$D/ATTEMPT-CONSUMED"
[[ ! -e /dev/video90 && ! -e /dev/video91 && ! -d /sys/module/v4l2loopback ]]
for m in qcom_camss imx681 ov13858 sp11_vd55g0; do [[ ! -d /sys/module/$m ]]; done
mkdir -p "$O"; rm -f "$O/UNIFIED.json" "$O/ACCEPTED-MEDIA-GRAPH.txt" "$O/ACCEPTED-MEDIA-STDERR.txt" "$O/DISCOVERY.json" "$O"/MEDIA-*-LAST-STDOUT.txt "$O"/MEDIA-*-LAST-STDERR.txt
modprobe i2c_qcom_cci
find_compat(){ local addr=$1 compat=$2 p; for p in /sys/bus/i2c/devices/*-"$addr"; do [[ -e "$p" && -r "$p/of_node/compatible" ]] || continue; [[ "$(tr -d '\0' < "$p/of_node/compatible")" == "$compat" ]] && { echo "$p"; return 0; }; done; return 1; }
IR=; REAR=; FRONT=
for _ in $(seq 1 120); do IR=$(find_compat 0060 microsoft,sp11-vd55g0 || :); REAR=$(find_compat 0010 ovti,ov13858 || :); FRONT=$(find_compat 0010 sony,imx681 || :); [[ -n "$IR" && -n "$REAR" && -n "$FRONT" ]] && break; sleep 0.05; done
[[ -n "$IR" && -n "$REAR" && -n "$FRONT" ]]
for mod in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do modprobe "$mod"; done
insmod "$D/modules/qcom-camss.ko" e004j_ir_dphy_windows_parity=1
insmod "$D/modules/ov13858.ko"
insmod "$D/modules/imx681.ko"
insmod "$D/modules/sp11-vd55g0.ko"
for dev in "$IR" "$REAR" "$FRONT"; do for _ in $(seq 1 120); do [[ -L "$dev/driver" ]] && break; sleep 0.05; done; [[ -L "$dev/driver" ]]; done
for dev in "$IR" "$REAR" "$FRONT"; do for _ in $(seq 1 120); do [[ "$(cat "$dev/power/runtime_status" 2>/dev/null || :)" == suspended ]] && break; sleep 0.05; done; [[ "$(cat "$dev/power/runtime_status")" == suspended ]]; done
python3 "$D/helpers/camera-media-graph-diagnostic.py" --live --out-dir "$O" >/dev/null
python3 "$D/helpers/discover-unified.py" --from-file "$O/ACCEPTED-MEDIA-GRAPH.txt" > "$O/UNIFIED.json"
MEDIA=$(python3 -c 'import json;print(json.load(open("/var/lib/sp11-camera-rgb/output/UNIFIED.json"))["media"])')
media-ctl -d "$MEDIA" -p > "$O/E012I-INITIAL-MEDIA.txt"
python3 "$P/route-state.py" "$O/E012I-INITIAL-MEDIA.txt" --expect neutral
insmod "$D/modules/v4l2loopback.ko" devices=2 video_nr=91,90 card_label=SP11-Front-Preview,SP11-Rear-Preview exclusive_caps=0,0 max_buffers=8 max_openers=5
udevadm settle
for v in /dev/video91 /dev/video90; do for _ in $(seq 1 100); do [[ -c "$v" ]] && break; sleep 0.05; done; [[ -c "$v" ]]; done
# Root-sealed product admission contract bound to current installed package/assets/source.
STACK=$(sha256sum /var/lib/sp11-camera-stack/installed-camera-stack-manifest.sha256 | awk '{print $1}')
ASSETS=$(sha256sum "$P/PRODUCT-ASSETS.sha256" | awk '{print $1}')
HEAD=$(cat "$P/SOURCE-HEAD")
cat > "$P/ENABLE.tmp" <<E
schema=sp11-camera-rgb-product-v1
enabled=YES
package_manifest_sha256=$STACK
product_assets_sha256=$ASSETS
source_head=$HEAD
E
chmod 0600 "$P/ENABLE.tmp"; chown root:root "$P/ENABLE.tmp"; mv "$P/ENABLE.tmp" "$P/ENABLE"
systemctl start sp11-camera-rgb.service
for _ in $(seq 1 80); do systemctl is-active --quiet sp11-camera-rgb.service && [[ -S /run/sp11-camera-rgb/control.sock ]] && break; sleep 0.1; done
systemctl is-active --quiet sp11-camera-rgb.service
/usr/local/bin/sp11-rgbctl status | tee "$D/PRODUCT-STATUS-BEFORE-OPTICAL.json"
echo E012I_LIVE_PREP=PASS PRODUCT_DAEMON_ACTIVE=YES CAMERA_SELECTED=OFF
