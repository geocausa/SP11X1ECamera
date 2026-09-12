#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004f-bounded-prefix-runtime
KO=$D/build/sp11-vd55g0-prefixprobe.ko
"$D/runtime-preflight.sh"
date -Ins > "$D/ATTEMPT1-CONSUMED.marker"
BEFORE=$(sudo -n dmesg | wc -l)
set +e
sudo -n insmod "$KO"
INS=$?
set -e
sleep 0.7
sudo -n dmesg | tail -n +$((BEFORE+1)) > "$D/ATTEMPT1-DMESG.txt"
sudo -n rmmod sp11_vd55g0_prefixprobe 2>/dev/null || true
python3 - "$INS" "$D/ATTEMPT1-DMESG.txt" "$D" <<'PY'
import json,re,sys
from pathlib import Path
ins=int(sys.argv[1]); logp=Path(sys.argv[2]); d=Path(sys.argv[3]); log=logp.read_text()
required=[
 'SP11_VD55G0_PREFIX_BEGIN addr=0x60 patch_bytes=552 patch_sha256=5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321 final_config_writes=0 stream=0 illumination=0',
 'SP11_VD55G0_PREFIX_MCLK_Hz=19200000 expected_Hz=19200000',
 'SP11_VD55G0_PREFIX_VDDIO_uV=1800000 expected_uV=1800000',
 'SP11_VD55G0_PREFIX_VCORE_uV=1152000 expected_uV=1152000',
 'SP11_VD55G0_PREFIX_VANA_uV=2800000 expected_uV=2800000',
 'SP11_VD55G0_PREFIX_ID model_raw=30,47 model_be=0x3047 revision_raw=11,11 revision=0x1111',
 'SP11_VD55G0_PREFIX_ID_GATE=PASS model_be=0x3047 revision=0x1111_CUT1 writes=0',
 'SP11_VD55G0_PREFIX_POLL name=READY_TO_BOOT reg=0x002c expected=0x01 timeout_ms=6',
 'SP11_VD55G0_PREFIX_PATCH_BEGIN start=0x2000 bytes=552 sha256=5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321',
 'SP11_VD55G0_PREFIX_PATCH_SETUP writes=553 reg=0x0200 value=0x02',
 'SP11_VD55G0_PREFIX_POLL name=PATCH_SETUP_COMPLETE reg=0x0200 expected=0x00 timeout_ms=28',
 'SP11_VD55G0_PREFIX_BOOT writes=554 reg=0x0200 value=0x01',
 'SP11_VD55G0_PREFIX_POLL name=BOOT_COMPLETE reg=0x0200 expected=0x00 timeout_ms=6',
 'SP11_VD55G0_PREFIX_POLL name=SW_STBY reg=0x002c expected=0x02 timeout_ms=4',
 'SP11_VD55G0_PREFIX_COMPLETE writes=554 patch_writes=552 setup_writes=1 boot_writes=1 final_config_writes=0 final_state=SW_STBY stream=0 illumination=0',
 'SP11_VD55G0_PREFIX_POWER_OFF reset_asserted=1',
 'SP11_VD55G0_PREFIX_END status=0 writes=554 powered_off=1 stream=0 illumination=0',
]
missing=[x for x in required if x not in log]
poll_lines=[x for x in log.splitlines() if 'SP11_VD55G0_PREFIX_POLL ' in x]
poll_ok=len(poll_lines)==4 and all('result=PASS' in x for x in poll_lines)
forbidden=any(x in log for x in ['final_config_writes=1','writes=555','STREAM_START','ILLUMINATION_ON'])
ok=ins==0 and not missing and poll_ok and not forbidden
out={
 'schema':'sp11-camera-e004f-attempt1-v1',
 'status':'PASS_WINDOWS_PREFIX_TO_SW_STBY_POWERED_OFF' if ok else 'FAIL_BOUNDED_NO_RETRY',
 'insmod_exit':ins,
 'missing_required_markers':missing,
 'poll_lines':poll_lines,
 'sensor_data_writes':554 if ok else None,
 'surface_patch_writes':552 if ok else None,
 'final_43_windows_config_writes':False,
 'sensor_gpio1_strobe_configured':False,
 'camss':False,'v4l2':False,'stream':False,'illumination':False,
 'powered_off':ok,'retry_authorized':False,
 'next':'reboot to Golden immediately' if ok else 'reboot to Golden and analyze offline',
}
(d/('ATTEMPT1-PASS.json' if ok else 'ATTEMPT1-FAILURE.json')).write_text(json.dumps(out,indent=2)+'\n')
print('E004F_ATTEMPT1='+('PASS' if ok else 'FAIL NO_RETRY'))
for x in poll_lines: print(x)
if missing: print('MISSING='+repr(missing))
sys.exit(0 if ok else 1)
PY
