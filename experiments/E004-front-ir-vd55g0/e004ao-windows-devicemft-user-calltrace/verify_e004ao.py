#!/usr/bin/env python3
from pathlib import Path
import json, re, sys
d=Path(__file__).resolve().parent
def die(s): print('E004ao VERIFY: FAIL - '+s); sys.exit(1)
r=json.loads((d/'RESULT.json').read_text())
if r.get('status')!='PASS_DYNAMIC_FACEAUTH_DOES_NOT_ENTER_DEVICEMFT_SECURE_BROKER': die('status mismatch')
w=d/'recovered-windows'
mon=(w/'job_iI7vPkpqZRkzawGpBW7spNrg'/'terminal.log').read_text(errors='replace')
face=(w/'job_5x5HkWSlMWMF49hNVAVDbIa2'/'terminal.log').read_text(errors='replace')
kd=(d/'recovered-sp7'/'E004AO_LOADHELD_TRACE.log').read_text(errors='replace')
for s in ('E004AO_UMDBG_ATTACH_PASS pid=14784','E004AO_UMDBG_TARGET_LOAD pid=14784','base=0x7ffd47cb0000','QcDeviceMFT8380.dll','E004AO_UMDBG_TARGET_RELEASE=ARMED','E004AO_UMDBG_DETACHED'):
    if s not in mon: die('load-hold evidence missing '+s)
for s in ('E004AN_FACEAUTH_INIT_PASS','E004AN_FACEAUTH_START=Success','E004AN_FACEAUTH_ACQUIRED=12','E004AN_FACEAUTH_STOP_PASS','status=NotSupported'):
    if s not in face: die('FaceAuth evidence missing '+s)
names=('CreateCameraControls','CaptureProperties_Initialize','RegisterPropertyObservers','SecureMode_PropertyAccessor','CDeviceMFT_KsProperty','CPinConfigurer_KsProperty','CCameraControls_KsProperty','SecureMode_SetProperty','SecureMode_GetProperty','CaptureProperties_OnSetSecureMode','CaptureProperties_OnGetSecureMode','SecureUsecaseBuilder')
for name in names:
    if ('E004AO_LHIT '+name) not in kd: die('breakpoint definition missing '+name)
actual=[ln for ln in kd.splitlines() if ln.startswith('E004AO_LHIT ')]
if actual: die('unexpected actual hit(s): '+repr(actual[:3]))
if '===E004AO_FINAL_ZERO_HITS===' not in kd: die('final zero-hit marker missing')
if '===E004AO_TRACE_CLOSED===' not in kd: die('trace close marker missing')
gold=(d/'POST-RETURN-GOLDEN.txt').read_text()
for s in ('7.1.5-sp11-render-parity-v4+','sp11_entry=7.1.5-sp11-fullio-v19c','saved_entry=sp11-audio-fullio-v19c','next_entry=','BootCurrent: 0005'):
    if s not in gold: die('Golden evidence missing '+s)
if r['interpretation']['securemode_write_runtime_hit_proven']: die('false SecureMode hit claim')
if r['interpretation']['secure_usecase_runtime_hit_proven']: die('false secure usecase hit claim')
if r['interpretation']['linux_secureisp_runtime_authorized']: die('false Linux authorization')
print('E004ao VERIFY: PASS')
print(' - DeviceMFT load held before execution in FrameServer PID 14784')
print(' - live base 0x7ffd47cb0000 traced with 12 process-specific targets')
print(' - FaceAuth initialized, streamed 12 real IR frames, and stopped')
print(' - zero accepted DeviceMFT SecureMode/KS/secure-usecase runtime hits')
print(' - returned to protected Golden')
