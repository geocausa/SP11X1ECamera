#!/usr/bin/env bash
set -Eeuo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004ec-side-light-post-g3-shadow-observation
O=$D/runtime-output
HW=/usr/lib/sp11-camera-stack/hardware
P=/usr/lib/sp11-front-imx681
CAMSS=$HW/modules/qcom-camss.ko; IRMOD=$HW/modules/sp11-vd55g0.ko; FRONTMOD=$HW/modules/imx681.ko; REARMOD=$HW/modules/ov13858.ko
"$D/runtime-preflight.sh"
IR=$(sed -n 's/^ir_client_path=//p' "$D/RUNTIME-PREFLIGHT.txt"); REAR=$(sed -n 's/^rear_client_path=//p' "$D/RUNTIME-PREFLIGHT.txt"); FRONT=$(sed -n 's/^front_client_path=//p' "$D/RUNTIME-PREFLIGHT.txt")
[ "$(sha256sum "$CAMSS"|awk '{print $1}')" = 862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7 ]
[ "$(sha256sum "$IRMOD"|awk '{print $1}')" = 4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72 ]
[ "$(sha256sum "$FRONTMOD"|awk '{print $1}')" = ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6 ]
[ "$(sha256sum "$REARMOD"|awk '{print $1}')" = 13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309 ]
[ ! -e "$O" ] && [ ! -e "$D/ATTEMPT1-CONSUMED.marker" ]
( set -o noclobber; : > "$D/ATTEMPT1-CONSUMED.marker" ) 2>/dev/null || exit 1
printf 'schema=sp11-camera-e004ec-attempt1-consumed-v1\nstatus=CONSUMED_BEFORE_CAMERA_MODULE_LOAD\ntime=%s\nboot_id=%s\nhead=%s\nretry=NO\nnative_write_authorized=NO\nlighting=side_lights_on_main_off\n' "$(date -Ins)" "$(cat /proc/sys/kernel/random/boot_id)" "$(git -C "$R" rev-parse HEAD)" > "$D/ATTEMPT1-CONSUMED.marker"
sync; mkdir -p "$O"; BEFORE=$(sudo -n dmesg | wc -l)
on_fail(){ rc=$?; trap - ERR; sudo -n dmesg | tail -n +$((BEFORE+1)) > "$D/DMESG.txt" || true; sudo -n chown -R geoca:geoca "$O" 2>/dev/null||true; python3 - "$rc" "$D" <<'PY' || true
import json,sys
from pathlib import Path
rc=int(sys.argv[1]);d=Path(sys.argv[2]);(d/'ATTEMPT1-FAILURE.json').write_text(json.dumps({'schema':'sp11-camera-e004ec-attempt1-failure-v1','status':'FAIL_BOUNDED_NO_RETRY','exit_code':rc,'candidate_consumed':True,'native_write_authorized':False,'same_boot_retry_performed':False,'golden_return_required':True,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()},indent=2,sort_keys=True)+'\n')
PY
exit "$rc"; }
trap on_fail ERR
for m in mc videodev v4l2_async v4l2_fwnode videobuf2_common videobuf2_memops videobuf2_v4l2 videobuf2_dma_sg v4l2_cci; do sudo -n modprobe "$m"; done
sudo -n insmod "$CAMSS" e004j_ir_dphy_windows_parity=1
sudo -n insmod "$REARMOD"; sudo -n insmod "$FRONTMOD" 'dyndbg=+p'; sudo -n insmod "$IRMOD"
for p in "$IR" "$REAR" "$FRONT"; do for _ in $(seq 1 120); do [ -L "$p/driver" ] && break; sleep 0.05; done; [ -L "$p/driver" ]; done
wait_suspend(){ local p; for p in "$IR" "$REAR" "$FRONT"; do for _ in $(seq 1 120); do [ "$(cat "$p/power/runtime_status" 2>/dev/null||true)" = suspended ] && break; sleep 0.05; done; [ "$(cat "$p/power/runtime_status")" = suspended ]; done; }
wait_suspend
for _ in $(seq 1 100); do if ls /dev/media* >/dev/null 2>&1 && PYTHONDONTWRITEBYTECODE=1 "$D/discover-unified.py" > "$D/UNIFIED-DISCOVERY.json.tmp" 2>/dev/null; then mv "$D/UNIFIED-DISCOVERY.json.tmp" "$D/UNIFIED-DISCOVERY.json"; break; fi; sleep 0.1; done
[ -s "$D/UNIFIED-DISCOVERY.json" ]
MEDIA=$(python3 -c "import json;print(json.load(open('$D/UNIFIED-DISCOVERY.json'))['media'])")
media-ctl -d "$MEDIA" -p > "$D/LOAD-MEDIA.txt"
PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" "$D/LOAD-MEDIA.txt" --expect neutral
sudo -n "$P/bin/front-imx681-discover.py" --json > "$O/FRONT-DISCOVERY.json"
python3 - <<PY
import json
u=json.load(open('$D/UNIFIED-DISCOVERY.json'));p=json.load(open('$O/FRONT-DISCOVERY.json'))
assert p['media']==u['media'] and p['csiphy_entity']=='msm_csiphy2' and p['csid_entity']=='msm_csid1' and p['pix_entity']=='msm_vfe1_pix'
PY
python3 - "$IR" "$REAR" "$FRONT" > "$O/PRE-STREAM-SUSPEND.txt" <<'PY'
from pathlib import Path
import sys
for label,p in zip(('IR','REAR','FRONT'),map(Path,sys.argv[1:])):
 st=(p/'power/runtime_status').read_text().strip();assert st=='suspended',(label,st);print(label+'_PRE_STREAM_SUSPEND=PASS')
PY
sudo -n env PYTHONDONTWRITEBYTECODE=1 "$P/bin/front-imx681-launcher.py" --execute --post-g3-write-policy shadow --build-dir "$P/build" --output-dir "$O/front1" > "$O/FRONT-SHADOW.txt" 2>&1
echo FRONT_LAUNCHER_RC=0 >> "$O/FRONT-SHADOW.txt"
media-ctl -d "$MEDIA" -p > "$O/ROUTE-FRONT-ON.txt"; PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" "$O/ROUTE-FRONT-ON.txt" --expect front-only
sleep 0.5; wait_suspend
python3 - "$IR" "$REAR" "$FRONT" > "$O/POST-STREAM-SUSPEND.txt" <<'PY'
from pathlib import Path
import sys
for label,p in zip(('IR','REAR','FRONT'),map(Path,sys.argv[1:])):
 st=(p/'power/runtime_status').read_text().strip();assert st=='suspended',(label,st);print(label+'_POST_STREAM_SUSPEND=PASS')
PY
media-ctl -d "$MEDIA" -l '"msm_csiphy2":1 -> "msm_csid1":0 [0]'
media-ctl -d "$MEDIA" -l '"msm_csid1":4 -> "msm_vfe1_pix":0 [0]'
media-ctl -d "$MEDIA" -p > "$O/FINAL-NEUTRAL.txt"; PYTHONDONTWRITEBYTECODE=1 "$D/route-state.py" "$O/FINAL-NEUTRAL.txt" --expect neutral
sudo -n dmesg | tail -n +$((BEFORE+1)) > "$D/DMESG.txt"; sudo -n chown -R geoca:geoca "$O" || true
PYTHONDONTWRITEBYTECODE=1 "$D/verify-observation.py"
trap - ERR
echo E004EC_RUN=PASS SHADOW_ONLY=YES NATIVE_WRITE=NO
