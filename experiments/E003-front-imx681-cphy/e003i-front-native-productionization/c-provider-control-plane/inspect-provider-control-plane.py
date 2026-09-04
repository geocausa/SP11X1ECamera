#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys
here=Path(__file__).resolve().parent
m=json.loads((here/'BUILD-MANIFEST.json').read_text())
src=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src/drivers/media/platform/qcom/camss/camss.c')
if not src.exists(): raise SystemExit('source workspace missing')
s=src.read_text()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(src)!=m['production_camss_sha256']: raise SystemExit('production CAMSS identity drift')
for bad in ('camss_x1e_pix_runtime_arm','e003h_pix_runtime_arm','e003h_pix_rtcdm_diag','e003h_pix_run_once','request_firmware','CAMSS_X1E_PIX_TRIGGER_FW','camss_x1e_pix_iq_provider_seed_firmware','camss_x1e_pix_gate_once','sp11/e003h'):
    if bad in s: raise SystemExit('forbidden control-plane residue: '+bad)
for required in ('CAMSS_X1E_PIX_IQ_FIRST_STEADY_REQUEST\t4','camss_x1e_pix_iq_provider_next(video, 4,','camss_x1e_pix_iq_provider_next(video, 5,','camss_x1e_pix_iq_provider_next(video, 6,','video->x1e_pix_iq_depth < 3','ret = -EAGAIN;'):
    if required not in s: raise SystemExit('missing provider marker: '+required)
if m.get('runtime_authorized') or m.get('hardware_runtime_executed'): raise SystemExit('runtime gate drift')
print('E003I_PROVIDER_CONTROL_PLANE=PASS')
print('CAMSS_SHA256='+sha(src))
print('RUNTIME_AUTHORIZED=false')
