#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004dk-rgb-alternating-soak
P=$D/package-root/usr/lib/sp11-front-imx681
"$D/runtime-preflight.sh"
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$P/build/qcom-camss.ko"
sudo -n insmod "$D/build/ov13858-production.ko"
sudo -n insmod "$P/build/imx681.ko" 'dyndbg=+p'
for _ in $(seq 1 50); do if ls /dev/media* >/dev/null 2>&1 && PYTHONDONTWRITEBYTECODE=1 "$D/discover-unified.py" > "$D/UNIFIED-DISCOVERY.json.tmp" 2>/dev/null; then mv "$D/UNIFIED-DISCOVERY.json.tmp" "$D/UNIFIED-DISCOVERY.json"; break; fi; sleep 0.1; done
[ -s "$D/UNIFIED-DISCOVERY.json" ]
MEDIA=$(python3 -c "import json;print(json.load(open('$D/UNIFIED-DISCOVERY.json'))['media'])")
media-ctl -d "$MEDIA" -p > "$D/ROUTE-LOAD.txt"
PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" "$D/ROUTE-LOAD.txt" --expect neutral
sudo -n "$P/bin/front-imx681-discover.py" --json >/tmp/e004dk-front-discovery.json
python3 - <<PY
import json
u=json.load(open('$D/UNIFIED-DISCOVERY.json'));p=json.load(open('/tmp/e004dk-front-discovery.json'))
assert u['rear_sensor_entity'].startswith('ov13858 ') and u['front_sensor_entity'].startswith('imx681 ')
assert p['media']==u['media'] and p['csiphy_entity']=='msm_csiphy2' and p['csid_entity']=='msm_csid1' and p['pix_entity']=='msm_vfe1_pix'
PY
sudo -n dmesg -T | cat > "$D/LOAD-DMESG.txt"
echo 'E004DK_LOAD=PASS ROUTE=NEUTRAL MODULES=PINNED_RGB'
