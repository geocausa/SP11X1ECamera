#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re
here=Path(__file__).resolve().parent
m=json.loads((here/'BUILD-MANIFEST.json').read_text())
root=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for rel,want in m['source_sha256'].items():
    p=root/rel
    if not p.exists() or sha(p)!=want: raise SystemExit('source identity drift: '+rel)
c=(root/'drivers/media/platform/qcom/camss/camss.c').read_text()
v=(root/'drivers/media/platform/qcom/camss/camss-video.c').read_text()
h=(root/'drivers/media/platform/qcom/camss/camss.h').read_text()
for x in ['camss_x1e_pix_iq_session_open','camss_x1e_pix_iq_session_close','camss_x1e_pix_iq_submit','x1e_pix_iq_depth != 3','x1e_pix_iq_last_enqueued != 6']:
    if x not in c: raise SystemExit('missing CAMSS ingress marker: '+x)
for x in ['V4L2_CID_USER_BASE + 0x1240','V4L2_CTRL_TYPE_U8','V4L2_CTRL_FLAG_WRITE_ONLY','V4L2_CTRL_FLAG_EXECUTE_ON_WRITE','v4l2_fh_is_singular_file','X1E Front IQ Capsule']:
    if x not in v: raise SystemExit('missing V4L2 ingress marker: '+x)
if 'CAMSS_X1E_PIX_CAPSULE_BYTES 41088' not in h: raise SystemExit('capsule ABI size drift')
for bad in ['request_firmware','e003h_pix_runtime_arm','e003h_pix_run_once','e003h_pix_rtcdm_diag','sp11/e003h']:
    if bad in c or bad in v: raise SystemExit('forbidden legacy control plane: '+bad)
helper=(here/'feed-x1e-iq.c').read_text()
if 'VIDIOC_STREAMON' in helper: raise SystemExit('helper must not execute STREAMON')
if m.get('runtime_authorized') or m.get('hardware_runtime_executed'): raise SystemExit('runtime gate drift')
print('E003I_V4L2_IQ_INGRESS=PASS')
print('CONTROL_ID='+m['control_id_hex'])
print('CAPSULE_BYTES=41088')
print('RUNTIME_AUTHORIZED=false')
