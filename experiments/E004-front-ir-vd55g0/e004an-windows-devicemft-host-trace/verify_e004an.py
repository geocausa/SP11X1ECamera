#!/usr/bin/env python3
from pathlib import Path
import json, sys
d=Path(__file__).resolve().parent
def die(s):
    print('E004an VERIFY: FAIL - '+s); sys.exit(1)
r=json.loads((d/'RESULT.json').read_text())
if r.get('status')!='PASS_DYNAMIC_DEVICEMFT_HOST_FACEAUTH_CORRELATION': die('RESULT status mismatch')
w=d/'recovered-windows'
face1=(w/'job_OeAPSggCK_EMwDhmR4o1-_s3'/'terminal.log').read_text(errors='replace')
watch1=(w/'job_5kzNUtmOGsaOt4ww8aSeFlxM'/'terminal.log').read_text(errors='replace')
face2=(w/'job_krq12Gyc5YoJGn4HQnm1vAXQ'/'terminal.log').read_text(errors='replace')
watch2=(w/'job_tZUTWTBhFy8u7U8VR7Jzg09y'/'terminal.log').read_text(errors='replace')
gate=(w/'job_6bbdDb3UQygEL5qWmovmghZY'/'terminal.log').read_text(errors='replace')
gatejob=(w/'job_JxlRiCKZ1HMza_VE_0NWwEI5'/'terminal.log').read_text(errors='replace')
kd=(d/'recovered-sp7'/'E004AN-KD-TRANSCRIPT.utf8.txt').read_text(errors='replace')
for text,name in ((face1,'face1'),(face2,'face2')):
    for s in ('E004AJ_FACEAUTH_START=Success','E004AJ_FACEAUTH_ACQUIRED=12','E004AJ_FACEAUTH_STOP_PASS'):
        if s not in text: die(name+' missing '+s)
if 'pid=3676 proc=svchost' not in watch1 or 'QcDeviceMFT8380.dll' not in watch1: die('first host observation missing')
for s in ('pid=12512 proc=svchost','svchost.exe -k Camera -s FrameServer','name=FrameServer','display=Windows Camera Frame Server'):
    if s not in watch2: die('host metadata missing '+s)
for s in ('pid=8180 proc=svchost','svchost.exe -k Camera -s FrameServer','name=FrameServer','display=Windows Camera Frame Server'):
    if s not in gate: die('gated host metadata missing '+s)
for s in ('E004AN_FACEAUTH_INIT_PASS','E004AN_FACEAUTH_POSTINIT_GATE'):
    if s not in gatejob: die('gated helper missing '+s)
for s in ('!process 0n8180 1','Cid: 1ff4','Image: svchost.exe'):
    if s not in kd: die('KD evidence missing '+s)
golden=(d/'POST-RETURN-GOLDEN.txt').read_text()
for s in ('7.1.5-sp11-render-parity-v4+','saved_entry=sp11-audio-fullio-v19c','next_entry=','BootCurrent: 0005'):
    if s not in golden: die('Golden evidence missing '+s)
if r['interpretation']['device_mft_ksproperty_runtime_hit_proven']: die('false DeviceMFT runtime claim')
if r['interpretation']['securemode_write_runtime_hit_proven']: die('false SecureMode runtime claim')
if r['interpretation']['linux_secureisp_runtime_authorized']: die('false Linux authorization')
print('E004an VERIFY: PASS')
print(' - QcDeviceMFT8380.dll repeatedly correlates with FaceAuth IR')
print(' - host is Windows Camera Frame Server')
print(' - gated PID 8180 independently confirmed by KD')
print(' - gated stream was interrupted; no false SecureMode claim')
print(' - protected Golden return verified')
