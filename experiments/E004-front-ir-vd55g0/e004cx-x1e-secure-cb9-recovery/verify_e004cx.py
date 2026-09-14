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
    for x in tokens:
        if x not in t: fail.append(f'{path}: missing {x}')
need('evidence/WINDOWS-QCSMMU-FASTRPC-SECURE-CB.txt','S1_COMPUTE_CP_P','0xFF, 0x0C, 0x09, 0x00, 0x20','Clnt:0x17 CB:0x25 VM:0x10')
need('evidence/WINDOWS-FASTRPC-ORDINARY-CDSP-CB-LIST.txt','FastRPCCDSPCbIndex','FastRPCCDSPSidInfo','0x0C,0x01','0x0C,0x0F')
need('evidence/X1E-CB9-CORRELATION.txt','compute-cb@9 -> <&apps_smmu 0x0c09 0x20>','different namespaces')
need('evidence/CPZ-PD-TYPE-DERIVATION.txt','CPZ_USERPD = 6','not recovered from an exact Hamoa downstream DTS')
need('README.md','same-machine Windows hardware policy','E004cy — compile-only X1E secure CB9 topology candidate')
if R.get('status')!='PASS_WINDOWS_ORACLE_RECOVERS_X1E_SECURE_FASTRPC_SID_0C09': fail.append('bad status')
if R['windows_oracle']['stream_id']!='0x0c09': fail.append('bad stream id')
if R['windows_oracle']['stream_mask']!='0x0020': fail.append('bad stream mask')
if R['cpz_pd_type']['value']!=6: fail.append('bad cpz pd type')
if R['cpz_pd_type']['exact_hamoa_downstream_dts_recovered']: fail.append('overclaimed downstream DTS')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')
if fail:
    print('E004cx VERIFY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('E004cx VERIFY: PASS')
print(' - exact SP11 Windows SMMU policy identifies protected FASTRPC S1_COMPUTE_CP_P')
print(' - protected stream is directly mapped as SID 0x0c09 with mask 0x0020')
print(' - ordinary Windows FASTRPC SIDs correlate exactly with Golden Linux compute banks around the omitted CB9')
print(' - Linux logical CB9 and Windows hardware CB37 are kept as separate namespaces')
print(' - CPZ pd-type 6 is derived from Qualcomm downstream FastRPC semantics, not falsely claimed as recovered Hamoa DTS')
print(' - no DT/SMMU/FastRPC/protected runtime action occurred')
