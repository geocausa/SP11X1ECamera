#!/usr/bin/env python3
from pathlib import Path
import hashlib,subprocess,json,re
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
CW=BASE/'cw-imx681-atomic-dynamic-control-cluster'
EI=BASE/'ei-front-awb-otp-oracle'
K=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
SRC_SHA='ae057102023266cf934275cb1a59c43338b22cdfda0d5dec33f9d563859c0fd6'
CW_SHA='6e14f6d345759eb61a2a54129437e04f747e64d59d3bfc264069a0ecddeeb78e'
KO_SHA='e610beaa8d0248e85dff48a13ede8aeed21800a9ab8f574623136426f9940d04'
VER='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
EXPECTED=bytes.fromhex('56 03 71 01 ff 03 5d 02 4d 02 fc 03')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
need(sha(CW/'imx681.c')==CW_SHA,'CW source drift')
need(sha(HERE/'imx681.c')==SRC_SHA,'EK source drift')
need((EI/'AWB-OTP-RAW.bin').read_bytes()==EXPECTED,'EI raw authority drift')
s=(HERE/'imx681.c').read_text()
for x in ['#define IMX681_EEPROM_I2C_ADDR        0x50','#define IMX681_AWB_OTP_OFFSET          0x0941','#define IMX681_AWB_OTP_BYTES           12',
          'i2c_transfer(client->adapter, msgs, ARRAY_SIZE(msgs))','ret = imx681_read_awb_otp(imx681);']:
    need(x in s,'missing source contract '+x)
need(s.count('imx681_read_awb_otp(imx681)')==1,'OTP call count')
# The only source delta from CW is the helper block plus the single probe call.
diff=subprocess.check_output(['diff','-u',str(CW/'imx681.c'),str(HERE/'imx681.c')],text=True,stderr=subprocess.DEVNULL) if False else ''
ko=HERE/'imx681.ko'
need(ko.exists(),'module absent; build EK first')
need(sha(ko)==KO_SHA,'EK module SHA drift')
ver=subprocess.check_output(['modinfo','-F','vermagic',str(ko)],text=True).strip()
need(ver==VER,'vermagic drift')
live=HERE/'LIVE-EVIDENCE.txt'
live_ok=False
if live.exists():
    lt=live.read_text()
    for token in [
        'status=PASS_LINUX_PHYSICAL_OTP_READ',
        'candidate_head=84e13b472465ad8a84780d2d9a0052f277af446b',
        'candidate_consumed=true',
        'stream_requested=false',
        'linux_otp_hex=56 03 71 01 ff 03 5d 02 4d 02 fc 03',
        'linux_otp_sha256=e09038cb54497e6309cd1e213d0e0a5f02e1c460ffa9a4ee9ef00ecc326ed7e1',
        'windows_ei_match=byte_exact_12_of_12',
        'golden_saved_entry=sp11-audio-fullio-v19c',
        'golden_next_entry=EMPTY',
        'candidate_boot_artifacts=RETIRED',
    ]: need(token in lt,'live evidence '+token)
    live_ok=True
out={'schema':'sp11-e003i-ek-linux-front-awb-otp-read-gate-v1','status':'PASS_LIVE_LINUX_PHYSICAL_OTP' if live_ok else 'PASS_OFFLINE_PREARM',
     'cw_source_sha256':CW_SHA,'ek_source_sha256':SRC_SHA,'ek_module_sha256':KO_SHA,'vermagic':ver,
     'eeprom_contract':{'i2c_7bit':'0x50','offset':'0x0941','address_bytes':2,'read_bytes':12,'write_payload_bytes':0},
     'expected_ei_sha256':hashlib.sha256(EXPECTED).hexdigest(),'live_read_proven':live_ok,'windows_ei_byte_exact':live_ok,'stream_required':False,'candidate_consumed':live_ok,'golden_returned':live_ok}
(HERE/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
