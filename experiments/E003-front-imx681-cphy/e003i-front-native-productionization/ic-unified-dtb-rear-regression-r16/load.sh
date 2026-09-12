#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ic-unified-dtb-rear-regression-r16
P=$D/package-root/usr/lib/sp11-front-imx681
"$D/runtime-preflight.sh"
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$P/build/qcom-camss.ko"
sudo -n insmod "$D/build/ov13858-production.ko"
sudo -n insmod "$P/build/imx681.ko" 'dyndbg=+p'
for _ in $(seq 1 50); do if ls /dev/media* >/dev/null 2>&1 && PYTHONDONTWRITEBYTECODE=1 "$D/discover-unified.py" > "$D/DISCOVERY.json.tmp" 2>/dev/null; then mv "$D/DISCOVERY.json.tmp" "$D/DISCOVERY.json"; break; fi; sleep 0.1; done
[ -s "$D/DISCOVERY.json" ]
python3 - <<PY
import json
j=json.load(open('$D/DISCOVERY.json')); assert j['rear_route']==['msm_csiphy1','msm_csid0','msm_vfe0_rdi0','msm_vfe0_video0']; assert j['front_route']==['msm_csiphy2','msm_csid1','msm_vfe1_pix','msm_vfe1_video3']
PY
sudo -n dmesg | tail -n 400 > "$D/LOAD-DMESG.txt"
echo 'IC_LOAD=PASS MODULES=CAMSS+OV13858+IMX681 UNIFIED_DISCOVERY=PASS STREAM_EXECUTED=NO'
