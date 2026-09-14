#!/usr/bin/env python3
import json
from pathlib import Path
D=Path(__file__).resolve().parent
R=json.loads((D/'RESULT.json').read_text())
fail=[]
def need(path,*tokens):
    p=D/path
    if not p.exists(): fail.append(f'missing {path}'); return
    t=p.read_text(errors='replace')
    for token in tokens:
        if token not in t: fail.append(f'{path}: missing {token}')
need('evidence/QCOM-CAMERA-CP-CDSP-AUTHORITY.txt','VMID_CP_CAMERA','VMID_CP_CDSP','CAM_MEM_FLAG_CDSP_OUTPUT')
need('evidence/SP11-CDSP-SECUREISP-PAYLOAD.txt','only one CPZ PD allowed to run!!','fastrpc_invoke_mmap_get_cpz_phys','secure_process')
need('evidence/FASTRPC-ASSIGNMENT-SEMANTICS.txt','FASTRPC_ATTR_SECUREMAP','QCOM_SCM_VMID_HLOS','qcom_scm_assign_mem')
need('evidence/LIVE-FASTRPC-DT-POLICY.txt','label=cdsp','qcom,non-secure-domain=')
need('evidence/GOLDEN-CDSP-FASTRPC-INVENTORY.txt','/dev/fastrpc-cdsp-secure','state=running','qccdsp8380.mbn')
need('evidence/WINDOWS-BITML-CDSP-CLIENT-DISCOVERY.txt','QcDeviceMFT8380.dll','libbitml_nsp_v2_skel.so')
need('evidence/DEVICE-MFT-BITML-CDSP-SURFACE.txt','libcdsprpc.dll','_dom=cdsp','CamX::BITMLEngineV2')
need('evidence/DEVICEMFT-IFEDSP-HVX-METHODS.txt','libdsp_streamer_skel.so','CamX::IFEDSPInterface::DSPOpen')
need('README.md','CP_CAMERA + CP_CDSP','E004co — CDSP CPZ protected-process authority')
if R.get('status')!='PASS_CP_CAMERA_CP_CDSP_RULE_AND_CPZ_EXIST_NO_AUTHORIZED_WORKER_BINDING': fail.append('bad status')
if R['linux_fastrpc']['parity_ready']: fail.append('backend must not be parity ready')
if R['cdsp_secure_process']['host_creation_protocol_resolved']: fail.append('CPZ host protocol must remain unresolved')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')
if fail:
    print('E004cn VERIFY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('E004cn VERIFY: PASS')
print(' - Qualcomm camera source and QHEE authorize CP_CAMERA + CP_CDSP protected buffers')
print(' - same-machine CDSP firmware contains CPZ/secure-process and CPZ physical-map machinery')
print(' - Golden FastRPC signed-PD device is not itself CP_CDSP memory authority')
print(' - mainline securemap retains HLOS and X1E provides no CP_CDSP qcom,vmids binding')
print(' - Windows BitML/HVX CDSP clients do not replace the proven VTL1 protected-frame worker')
print(' - no secure runtime operation occurred')
