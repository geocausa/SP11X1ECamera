#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# E005b single real FRONT-ONLY production stream; no rear ISP/DMA experiment.
# Never replay after ATTEMPT1-CONSUMED, regardless of outcome.
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D="$R/experiments/E004-front-ir-vd55g0/e005b-production-front-bf-observer-one-shot"
P="$R/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hy-production-one-stream-r27/package-root/usr/lib/sp11-front-imx681"
B=/home/geoca/Documents/SP11-PROJECT/02-kernel/e005b-production-front-bf-observer-build
O=/home/geoca/Documents/SP11-PROJECT/02-kernel/e005b-production-front-bf-private-attempt1
cd "$R"
bash "$D/runtime-preflight.sh"
# A transient eight-minute watchdog returns to persistent Golden even if the
# chat/tool stream disappears. It does not affect later boots or old tasks.
if ! sudo -n systemctl is-active --quiet sp11-e005b-golden-return.timer;then
 sudo -n systemd-run --unit=sp11-e005b-golden-return --on-active=8min \
  /usr/bin/systemctl reboot
fi
sudo -n systemctl is-active --quiet sp11-e005b-golden-return.timer
# The first attempted hardware access consumes this identity permanently.
test ! -e "$O"
mkdir -m 0700 -- "$O"
( set -o noclobber; echo "E005B_CONSUMED_BEFORE_MODULE_LOAD=$(date -Ins)" > "$D/ATTEMPT1-CONSUMED.marker" )
{
 echo 'E005B_ATTEMPT1_CONSUMED_BEFORE_MODULE_LOAD=YES'
 echo "boot_id=$(cat /proc/sys/kernel/random/boot_id)"
 echo "time=$(date -Ins)"
 echo 'front_mode=IMX681_27_QC10C_PRODUCTION_SHADOW'
 echo 'rear_hardware_ISP=DENIED'
 sha256sum "$B/qcom-camss.ko" "$P/build/imx681.ko"
} > "$O/PREFLIGHT.txt"
sync
rc=0
{
 for mod in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci;do
  sudo -n modprobe "$mod"
 done
 # Actual trusted PRODUCTION CAMSS base with isolated E005b status-only edit.
 sudo -n insmod "$B/qcom-camss.ko"
 sudo -n insmod "$P/build/imx681.ko" 'dyndbg=+p'
 for _ in $(seq 1 40);do
  if compgen -G '/dev/media*' >/dev/null && compgen -G '/dev/video*' >/dev/null;then break;fi
  sleep 0.1
 done
 grep -q '^imx681 ' /proc/modules
 grep -q '^qcom_camss ' /proc/modules
 sudo -n "$P/bin/front-imx681-discover.py" --json > "$O/DISCOVERY-PRIVATE.json"
 python3 - "$O/DISCOVERY-PRIVATE.json" <<'PY'
import json,sys
v=json.load(open(sys.argv[1]))
assert v["sensor_entity"].startswith("imx681")
assert (v["csiphy_entity"],v["csid_entity"],v["pix_entity"],v["video_entity"])==(
  "msm_csiphy2","msm_csid1","msm_vfe1_pix","msm_vfe1_video3")
print("E005B_PHYSICAL_FRONT_ROUTE_AND_NODES_VALID")
PY
 echo 'E005B_MODULE_LOAD_AND_FRONT_GRAPH_PASS'
} > "$O/LOAD-PRIVATE.log" 2>&1 || rc=$?
if [ "$rc" -eq 0 ];then
 echo "E005B_ONE_REAL_FRONT_STREAM_BEGIN $(date -Ins)" > "$O/LAUNCH-PRIVATE.log"
 set +e
 timeout -s TERM -k 10s 210s sudo -n env PYTHONDONTWRITEBYTECODE=1 \
  "$P/bin/front-imx681-launcher.py" --execute \
  --post-g3-write-policy shadow --build-dir "$P/build" \
  --output-dir "$O/stream1" >> "$O/LAUNCH-PRIVATE.log" 2>&1
 rc=$?
 set -e
 echo "E005B_LAUNCHER_EXIT=$rc" >> "$O/LAUNCH-PRIVATE.log"
fi
# Preserve private kernel diagnostics and status only on SP11; no image export.
sudo -n journalctl -b -k --no-pager > "$O/KERNEL-PRIVATE.log" || true
chmod 0600 "$O"/*PRIVATE* 2>/dev/null || true
{
 echo "E005B_STATUS=ATTEMPT_CONSUMED"
 echo "E005B_LAUNCH_EXIT=$rc"
 echo "E005B_KERNEL_BOOT_ID=$(cat /proc/sys/kernel/random/boot_id)"
 echo "E005B_SCALAR_LOG_LINES_BEGIN"
 grep -F 'E005B_FRONT_ONLY_BF_STATUS' "$O/KERNEL-PRIVATE.log" | \
   sed -E 's/.*E005B_FRONT_ONLY_BF_STATUS/E005B_FRONT_ONLY_BF_STATUS/' || true
 echo "E005B_SCALAR_LOG_LINES_END"
 echo "E005B_NATIVE_REAR_PROCESSED_ISP_ENABLED=NO"
 echo "E005B_RETRY_AUTHORIZED=NO"
} > "$O/SAFE-SCALAR-ATTEMPT.txt"
cp -- "$O/SAFE-SCALAR-ATTEMPT.txt" "$D/ATTEMPT1-SAFE-SCALARS.txt"
sync
cat "$O/SAFE-SCALAR-ATTEMPT.txt"
# Do NOT unload any hardware module or release any DMA on failure.
# Fabric issues normal reboot to persistent Golden after examining this result.
echo E005B_FRONT_ATTEMPT_CONSUMED_REBOOT_TO_GOLDEN_REQUIRED
exit "$rc"
