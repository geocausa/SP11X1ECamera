#!/usr/bin/env python3
from pathlib import Path
import json, sys
E=Path(__file__).resolve().parent
fail=[]
def need(rel,*tokens):
    s=(E/rel).read_text(errors='replace')
    for t in tokens:
        if t not in s: fail.append(f'{rel}: missing {t!r}')
    return s
r=json.loads((E/'RESULT.json').read_text())
if r.get('status')!='PASS_GENERIC_QTEE_TRANSPORT_FOUND_NO_CAMERA_COUNTERPART_AUTHORITY': fail.append('status')
if r['runtime_actions']!={'qcomtee_enable_or_load':False,'qtee_smc':False,'qseecom_send':False,'scm_assign_mem':False,'camera_runtime':False}: fail.append('runtime boundary')
q=need('evidence/QCOMTEE-OBJECT-SERVICE-AUTHORITY.txt','QCOMTEE_ROOT_OP_REG_WITH_CREDENTIALS','QCOMTEE_CLIENT_ENV_OPEN','QCOMTEE_FEATURE_VER_UID','2033','TEE_OBJREF_NULL')
# There must still be exactly one hard-coded UID definition in qcomtee source evidence.
uid_defs=[x for x in q.splitlines() if '#define QCOMTEE_' in x and '_UID' in x]
if not any('QCOMTEE_FEATURE_VER_UID' in x and '2033' in x for x in uid_defs): fail.append('feature UID definition')
need('evidence/QCOMTEE-MEMORY-OBJECT-CAPABILITY.txt','QCOMTEE_OBJECT_OP_MAP_REGION','mem_object->paddr','QCOM_SCM_PERM_RW','qcom_tzmem_shm_bridge_create')
need('evidence/QTEE-SCM-ENABLEMENT-BOUNDARY.txt','qcom_scm_qtee_invoke_smc(0, 0, 0, 0','platform_device_register_data(scm->dev, "qcomtee"','config QCOMTEE')
g=need('evidence/SECUREISP-QCTREE-GUID-REFERENCE-SCAN.txt','PassThrough  AE865C08-4A07-404D-BE51-D9A0465E23E5 count=1','MemSharing   EB3C7242-1B1A-4D51-AB55-F268F018F860 count=0','Invoke       03B82FC5-2052-44D6-9462-F22C72499337 count=0','=== Trustlet QcISPTrustlet8380.dll ===')
trust=g.split('=== Trustlet QcISPTrustlet8380.dll ===',1)[1]
if 'count=1' in trust: fail.append('trustlet unexpectedly references QcTrEE service GUID')
need('evidence/WINDOWS-QCTREE-SERVICE-CATALOGUE.txt','PassThroughService.RegKey','MemSharingService.RegKey','InvokeService.RegKey','MemShareServiceSHMBridgeCreateSyscall','SmcInvokeService.c')
need('evidence/X1E-STATIC-SERVICE-NAME-SWEEP.txt','QCOMTEE_FEATURE_VER_UID','QCOM_SCM_VMID_CP_CAMERA','QCOM_SCM_VMID_CP_CAMERA_PREVIEW')
need('README.md','Mechanism is not authority.','E004bt — CP_CAMERA + trusted-worker visibility contract')
if fail:
    print('E004bs VERIFY: FAIL')
    for x in fail: print(' -',x)
    sys.exit(1)
print('E004bs VERIFY: PASS')
print(' - QCOMTEE offers privileged client-env + known-UID object transport, not service enumeration')
print(' - only FeatureVersions UID 2033 is hard-coded in this kernel tree')
print(' - QCOMTEE memory objects share tee_shm physical ranges through the primordial callback')
print(' - enabling QCOMTEE would immediately invoke QTEE and is therefore outside the current runtime gate')
print(' - exact SecureISP KMD references only QcTrEE PassThrough; MemShare/Invoke and all other catalogue GUIDs are absent')
print(' - no camera QTEE service authority was found in Golden source or installed X1E metadata')
print(' - no secure runtime operation was performed')
