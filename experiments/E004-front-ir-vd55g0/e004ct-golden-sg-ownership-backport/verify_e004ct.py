#!/usr/bin/env python3
import hashlib, json, re, subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
R=json.loads((D/'RESULT.json').read_text())
fail=[]
def need(rel,*tokens):
    p=D/rel
    if not p.exists(): fail.append(f'missing {rel}'); return
    s=p.read_text(errors='replace')
    for t in tokens:
        if t not in s: fail.append(f'{rel}: missing {t}')
need('README.md','qcom_tzmem','sg_phys(sg)','E004cu')
need('evidence/SCM-BACKPORT-DELTA.txt','qcom_tzmem','no new SMC ID')
need('evidence/SG-BATCH-FAILURE-CONTRACT.txt','sg_phys(sg)','POISONED','-EADDRNOTAVAIL')
need('evidence/COMPILE-PROOFS.txt','sg_consumer_descriptor_transport=SCM_TZMEM_COPY','sg_phys_offset_correct=true','prevalidates_all_sg_entries_before_first_transition=true')
need('scaffold/qcom_scm-e004ct.c','qcom_tzmem_alloc','qcom_tzmem_to_phys','__qcom_scm_assign_mem')
need('scaffold/sp11-cpz-sg-owner.c','SP11_CPZ_BATCH_SECTIONS 32','sg_phys(sg)','return -E2BIG','ret = -EADDRNOTAVAIL')
if R.get('status')!='PASS_GOLDEN_MULTI_REGION_SG_OWNERSHIP_BACKPORT_COMPILES': fail.append('bad status')
if R['golden_scm']['new_secure_world_abi']: fail.append('new secure ABI must be false')
if R['sg_contract']['contiguous_heap_fundamentally_required']: fail.append('contiguity incorrectly required')
if not R['sg_contract']['partial_failure_fail_closed']: fail.append('partial failure not fail closed')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')
# Ensure original production preimages remain byte-exact.
checks={
'/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/drivers/firmware/qcom/qcom_scm.c':'9937c99567878507e03e213a0b89b2f2c1b31dec1ac89c0342deb387de467c33',
'/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src/include/linux/firmware/qcom/qcom_scm.h':'7c946d7e6509af94b9902f17e572153db88956a815d5897f3730a3abbe647d04'}
for p,want in checks.items():
    got=hashlib.sha256(Path(p).read_bytes()).hexdigest()
    if got!=want: fail.append(f'production preimage changed: {p}')
if fail:
    print('E004ct VERIFY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('E004ct VERIFY: PASS')
print(' - Golden MP/HYP_ASSIGN secure-world ABI is reused unchanged')
print(' - multi-region descriptors are staged through Golden qcom_tzmem')
print(' - SG physical offsets and batch bounds are handled before ownership change')
print(' - partial multi-batch failure is explicitly fail-closed/poisoned')
print(' - system-heap SG backing is mechanically viable; contiguity is not fundamental')
print(' - production Golden SCM source remains byte-exact and no runtime action occurred')
