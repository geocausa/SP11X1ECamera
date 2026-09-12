#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hy-production-one-stream-r27
P=$D/package-root/usr/lib/sp11-front-imx681
"$D/runtime-preflight.sh"
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$P/build/qcom-camss.ko"
sudo -n insmod "$P/build/imx681.ko" 'dyndbg=+p'
for _ in $(seq 1 30); do if ls /dev/media* >/dev/null 2>&1; then break; fi; sleep 0.1; done
grep -q '^imx681 ' /proc/modules;grep -q '^qcom_camss ' /proc/modules
sudo -n "$P/bin/front-imx681-discover.py" --json | tee "$D/DISCOVERY.json" >/dev/null
python3 - <<PY
import json
p=json.load(open('$D/DISCOVERY.json'))
assert p['sensor_entity'].startswith('imx681')
assert p['csiphy_entity']=='msm_csiphy2' and p['csid_entity']=='msm_csid1' and p['pix_entity']=='msm_vfe1_pix' and p['video_entity']=='msm_vfe1_video3'
PY
sudo -n dmesg | tail -n 300 > "$D/LOAD-DMESG.txt"
echo 'HY_LOAD=PASS MODULES=CAMSS+IMX681 DISCOVERY=PASS STREAM_EXECUTED=NO'
