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
need('evidence/GOLDEN-HAMOA-FASTRPC-TOPOLOGY.txt','compute-cb@8','compute-cb@9 is secure','compute-cb@10')
need('evidence/LIVE-CPZ-CB9-GAP.txt','live_cdsp_cb9_count=0','live_pd_type_count=0','compute-cb@13')
need('evidence/LIVE-CONTEXT-BANK-INVENTORY.txt','compute-cb@1','compute-cb@13','fastrpc-cdsp-secure')
need('evidence/DOWNSTREAM-PD-TYPE-CONTRACT.txt','pd-type','CPZ_USERPD (6)','pre-typed')
need('README.md','ordinary existing CDSP context banks must not be relabeled','E004cx — X1E downstream secure CB9 recovery')
if R.get('status')!='PASS_CPZ_REQUIRES_OMITTED_SECURE_CB9_EXACT_X1E_DEFINITION_UNRESOLVED': fail.append('bad status')
if R['live_cb9_present']: fail.append('live CB9 unexpectedly present')
if R['live_pd_type_present']: fail.append('live pd-type unexpectedly present')
if R['architecture']['exact_x1e_secure_cb9_iommu_identity_resolved']: fail.append('secure CB9 identity must remain unresolved')
if R['downstream_contract']['arbitrary_ordinary_cb_reuse_authorized']: fail.append('unsafe ordinary CB reuse')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')
if fail:
    print('E004cw VERIFY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('E004cw VERIFY: PASS')
print(' - live SP11 has CDSP FastRPC banks 1-8 and 10-13, but no CB9 or pd-type')
print(' - exact Golden Hamoa/X1E source explicitly identifies compute-cb@9 as secure')
print(' - Qualcomm downstream PD typing requires a preconfigured matching context bank')
print(' - existing ordinary context banks are not accepted as CPZ substitutes')
print(' - exact X1E secure-CB9 IOMMU identity remains the next static authority gate')
print(' - no DT/IOMMU/FastRPC/protected runtime action occurred')
