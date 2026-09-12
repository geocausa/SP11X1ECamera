#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004c-bounded-linux-idprobe
KO=$D/build/sp11-vd55g0-idprobe.ko
"$D/runtime-preflight.sh"
date -Ins > "$D/ATTEMPT1-CONSUMED.marker"
BEFORE=$(sudo -n dmesg | wc -l)
set +e
sudo -n insmod "$KO"
INS=$?
set -e
sleep 0.5
sudo -n dmesg | tail -n +$((BEFORE+1)) > "$D/ATTEMPT1-DMESG.txt"
sudo -n rmmod sp11_vd55g0_idprobe 2>/dev/null || true
LOG=$D/ATTEMPT1-DMESG.txt
OK=1
for PAT in  'SP11_VD55G0_IDPROBE_BEGIN'  'SP11_VD55G0_IDPROBE_MCLK_Hz=19200000 expected_Hz=19200000'  'SP11_VD55G0_IDPROBE_VDDIO_uV=1800000 expected_uV=1800000'  'SP11_VD55G0_IDPROBE_VCORE_uV=1152000 expected_uV=1152000'  'SP11_VD55G0_IDPROBE_VANA_uV=2800000 expected_uV=2800000'  'SP11_VD55G0_IDPROBE_MODEL '  'be=0x3047 windows_qti_expected_be=0x3047'  'SP11_VD55G0_IDPROBE_REVISION '  'SP11_VD55G0_IDPROBE_READS_COMPLETE sensor_data_writes=0 patch=0 boot=0 configure=0 stream=0 illumination=0'  'SP11_VD55G0_IDPROBE_POWER_OFF reset_asserted=1'  'SP11_VD55G0_IDPROBE_END status=0 powered_off=1'
do
  grep -Fq "$PAT" "$LOG" || OK=0
done
[ ! -d /sys/module/sp11_vd55g0_idprobe ] || OK=0
MODEL=$(grep 'SP11_VD55G0_IDPROBE_MODEL ' "$LOG" | tail -1 || true)
REV=$(grep 'SP11_VD55G0_IDPROBE_REVISION ' "$LOG" | tail -1 || true)
if [ "$INS" -eq 0 ] && [ "$OK" -eq 1 ]; then
python3 - "$MODEL" "$REV" <<'PY'
import json,sys
from pathlib import Path
d=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E004-front-ir-vd55g0/e004c-bounded-linux-idprobe')
o={'schema':'sp11-camera-e004c-attempt1-v1','status':'PASS_IDENTITY_REVISION_ONLY_POWERED_OFF',
'model_log':sys.argv[1],'revision_log':sys.argv[2],
'sensor_data_register_writes':0,'patch_upload':False,'sensor_boot':False,
'sensor_configure':False,'stream':False,'illumination':False,'powered_off':True,
'retry_authorized':False,'next':'reboot to Golden immediately'}
(d/'ATTEMPT1-PASS.json').write_text(json.dumps(o,indent=2)+'\n')
PY
  echo 'E004C_ATTEMPT1=PASS'
  echo "$MODEL"
  echo "$REV"
  echo 'E004C_REBOOT_TO_GOLDEN_REQUIRED=YES'
  exit 0
fi
python3 - "$INS" "$MODEL" "$REV" <<'PY'
import json,sys
from pathlib import Path
d=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E004-front-ir-vd55g0/e004c-bounded-linux-idprobe')
o={'schema':'sp11-camera-e004c-attempt1-v1','status':'FAIL_BOUNDED_NO_RETRY',
'insmod_exit':int(sys.argv[1]),'model_log':sys.argv[2],'revision_log':sys.argv[3],
'retry_authorized':False,'next':'reboot to Golden and analyze offline'}
(d/'ATTEMPT1-FAILURE.json').write_text(json.dumps(o,indent=2)+'\n')
PY
echo "E004C_ATTEMPT1=FAIL NO_RETRY INS=$INS"
exit 1
