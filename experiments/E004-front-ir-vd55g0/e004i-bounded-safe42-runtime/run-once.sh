#!/usr/bin/env bash
set -euo pipefail
R=/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
D=$R/experiments/E004-front-ir-vd55g0/e004i-bounded-safe42-runtime
KO=$D/build/sp11-vd55g0-config42probe.ko
"$D/runtime-preflight.sh"
date -Ins > "$D/ATTEMPT1-CONSUMED.marker"
BEFORE=$(sudo -n dmesg | wc -l)
set +e
sudo -n insmod "$KO"
INS=$?
set -e
sleep 0.8
sudo -n dmesg | tail -n +$((BEFORE+1)) > "$D/ATTEMPT1-DMESG.txt"
sudo -n rmmod sp11_vd55g0_config42probe 2>/dev/null || true
python3 - "$INS" "$D/ATTEMPT1-DMESG.txt" "$D" <<'PY'
import json,re,sys
from pathlib import Path
ins=int(sys.argv[1]); logp=Path(sys.argv[2]); d=Path(sys.argv[3]); log=logp.read_text()
required=[
 'SP11_VD55G0_CONFIG42_BEGIN addr=0x60 patch_bytes=552 patch_sha256=5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321 safe42_sha256=159647774f45331210044d0680e50bf16e8aaeeb8c3e98449d2cef7adeffacb2 full43_sha256=9664529aab0c65d6f3ae9778c8c31f54fa1675bde748fdaafc8e2d2ab4ea387c safe_config_writes=42 isolated_strobe_reg=0x0468 strobe_write=0 stream=0 illumination=0',
 'SP11_VD55G0_CONFIG42_MCLK_Hz=19200000 expected_Hz=19200000',
 'SP11_VD55G0_CONFIG42_VDDIO_uV=1800000 expected_uV=1800000',
 'SP11_VD55G0_CONFIG42_VCORE_uV=1152000 expected_uV=1152000',
 'SP11_VD55G0_CONFIG42_VANA_uV=2800000 expected_uV=2800000',
 'SP11_VD55G0_CONFIG42_ID model_raw=30,47 model_be=0x3047 revision_raw=11,11 revision=0x1111',
 'SP11_VD55G0_CONFIG42_ID_GATE=PASS model_be=0x3047 revision=0x1111_CUT1 writes=0',
 'SP11_VD55G0_CONFIG42_POLL name=READY_TO_BOOT reg=0x002c expected=0x01 timeout_ms=6',
 'SP11_VD55G0_CONFIG42_PATCH_BEGIN start=0x2000 bytes=552 sha256=5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321',
 'SP11_VD55G0_CONFIG42_PATCH_SETUP writes=553 reg=0x0200 value=0x02',
 'SP11_VD55G0_CONFIG42_POLL name=PATCH_SETUP_COMPLETE reg=0x0200 expected=0x00 timeout_ms=28',
 'SP11_VD55G0_CONFIG42_BOOT writes=554 reg=0x0200 value=0x01',
 'SP11_VD55G0_CONFIG42_POLL name=BOOT_COMPLETE reg=0x0200 expected=0x00 timeout_ms=6',
 'SP11_VD55G0_CONFIG42_POLL name=SW_STBY reg=0x002c expected=0x02 timeout_ms=4',
 'SP11_VD55G0_CONFIG42_READBACK=PASS extclk=19200000 mipi=840000000 line=1200 frame=1955 roi=644x604',
 'SP11_VD55G0_CONFIG42_COMPLETE writes=596 patch_writes=552 setup_writes=1 boot_writes=1 safe_config_writes=42 isolated_strobe_writes=0 final_state=SW_STBY stream=0 illumination=0',
 'SP11_VD55G0_CONFIG42_POWER_OFF reset_asserted=1',
 'SP11_VD55G0_CONFIG42_END status=0 writes=596 powered_off=1 stream=0 illumination=0',
]
missing=[x for x in required if x not in log]
poll_lines=[x for x in log.splitlines() if 'SP11_VD55G0_CONFIG42_POLL ' in x]
poll_ok=len(poll_lines)==4 and all('result=PASS' in x for x in poll_lines)
mb=re.search(r'SP11_VD55G0_CONFIG42_STROBE_ISOLATION_BEFORE reg=0x0468 value=0x([0-9a-fA-F]{2}) write_authorized=0',log)
ma=re.search(r'SP11_VD55G0_CONFIG42_STROBE_ISOLATION_AFTER reg=0x0468 before=0x([0-9a-fA-F]{2}) after=0x([0-9a-fA-F]{2}) unchanged=1 write_authorized=0',log)
strobe_ok=bool(mb and ma and mb.group(1).lower()==ma.group(1).lower()==ma.group(2).lower())
gpio=None
mr=re.search(r'SP11_VD55G0_CONFIG42_READBACK=PASS .* gpio=([0-9a-fA-F]{2}),([0-9a-fA-F]{2}),([0-9a-fA-F]{2}),([0-9a-fA-F]{2})',log)
if mr:
    gpio=[x.lower() for x in mr.groups()]
gpio_ok=bool(gpio and gpio[0]=='01' and gpio[2]=='01' and gpio[3]=='01' and mb and gpio[1]==mb.group(1).lower())
forbidden=any(x in log for x in [
 'isolated_strobe_writes=1','strobe_write=1','writes=597','STREAM_START','ILLUMINATION_ON'
])
ok=ins==0 and not missing and poll_ok and strobe_ok and gpio_ok and not forbidden
out={
 'schema':'sp11-camera-e004i-attempt1-v1',
 'status':'PASS_SAFE42_WINDOWS_CONFIG_STROBE_UNCHANGED_POWERED_OFF' if ok else 'FAIL_BOUNDED_NO_RETRY',
 'insmod_exit':ins,
 'missing_required_markers':missing,
 'poll_lines':poll_lines,
 'sensor_data_writes':596 if ok else None,
 'surface_patch_writes':552 if ok else None,
 'safe_config_writes':42 if ok else None,
 'isolated_strobe_register':'0x0468',
 'isolated_strobe_before':('0x'+mb.group(1).lower()) if mb else None,
 'isolated_strobe_after':('0x'+ma.group(2).lower()) if ma else None,
 'isolated_strobe_unchanged':strobe_ok,
 'isolated_strobe_writes':0,
 'gpio_readback':gpio,
 'windows_config_readback_pass':bool(mr),
 'camss':False,'v4l2':False,'stream':False,'illumination':False,
 'powered_off':ok,'retry_authorized':False,
 'next':'reboot to Golden immediately' if ok else 'reboot to Golden and analyze offline',
}
(d/('ATTEMPT1-PASS.json' if ok else 'ATTEMPT1-FAILURE.json')).write_text(json.dumps(out,indent=2)+'\n')
print('E004I_ATTEMPT1='+('PASS' if ok else 'FAIL NO_RETRY'))
if mb: print('E004I_STROBE_BEFORE=0x'+mb.group(1).lower())
if ma: print('E004I_STROBE_AFTER=0x'+ma.group(2).lower()+' UNCHANGED='+('YES' if strobe_ok else 'NO'))
if gpio: print('E004I_GPIO_READBACK='+','.join(gpio))
for x in poll_lines: print(x)
if missing: print('MISSING='+repr(missing))
sys.exit(0 if ok else 1)
PY
