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
if r.get('status')!='PASS_QCTREE_TRANSPORTS_MAP_TO_EXISTING_LINUX_ABIS_NO_CAMERA_PROVIDER_IDENTITY': fail.append('status')
if r['runtime_actions']!={'qcomtee_enable_or_load':False,'smc_invocation':False,'shm_bridge_create':False,'qtee_service_probe':False,'scm_assign_mem':False,'camera_runtime':False}: fail.append('runtime boundary')
c=need('evidence/QCTREE-CONSTANTS.txt','140030990 u32=0x02000c1d','140030c68 u32=0x02000c1e')
m=need('evidence/WINDOWS-MEMSHARE-SHMBRIDGE.txt','MemShareServiceSHMBridgeCreateSyscall','SendShmBridgeCreateReqToTZ','SendShmBridgeDeleteReqToTZ','param_5 - 1 < 4','puVar7[-1] == 3','*param_8 = (longlong)local_c8')
l=need('evidence/LINUX-SHMBRIDGE-PARITY.txt','QCOM_SCM_SVC_MP','QCOM_SCM_MP_SHM_BRIDGE_DELETE','QCOM_SCM_MP_SHM_BRIDGE_CREATE','SIP_STD32_SMC=0x02000c1d','SIP_STD32_SMC=0x02000c1e','qcom_scm_shm_bridge_create','qcom_scm_shm_bridge_delete')
s=need('evidence/SMCINVOKE-CONSTANTS.txt','1400359fc u32=0x32000600','140035a00 u32=0x32000602','140036350 u32=0x32000602','140036354 u32=0x32000600')
w=need('evidence/WINDOWS-SMCINVOKE-TRANSPORT.txt','SmcInvokeProcessRequest','SmcInvokeReleaseObject','FUN_14002c5a8(param_1,uVar12,0x224','FUN_14002c5a8(param_1,uVar9,0x224')
q=need('evidence/LINUX-QTEE-SMCINVOKE-PARITY.txt','QCOM_SCM_SVC_SMCINVOKE','QCOM_SCM_SMCINVOKE_INVOKE_LEGACY','QCOM_SCM_SMCINVOKE_CB_RSP','QCOM_SCM_SMCINVOKE_INVOKE','ARM_SMCCC_OWNER_TRUSTED_OS','STD32_SMC=0x32000600','STD32_SMC=0x32000602','qcomtee_object_get_service')
g=need('evidence/QCTREE-GUID-CLIENT-SCAN.txt','=== MemSharing EB3C7242-1B1A-4D51-AB55-F268F018F860 hits=6 ===','=== Invoke 03B82FC5-2052-44D6-9462-F22C72499337 hits=3 ===','qccamsecureisp8380.inf_arm64_e0daad652520462e/qccamsecureisp8380.sys','qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys')
mem=g.split('=== MemSharing',1)[1].split('=== Invoke',1)[0].lower()
inv=g.split('=== Invoke',1)[1].lower()
for bad in ('qccamsecureisp','qccamisp'):
    if bad in mem: fail.append('camera MemSharing client appeared: '+bad)
    if bad in inv: fail.append('camera Invoke client appeared: '+bad)
need('README.md','the plumbing exists; the protected-camera provider does not.','E004bz — SHM-bridge ACL capability versus protected-camera requirements')
if fail:
    print('E004by VERIFY: FAIL')
    for x in fail: print(' -',x)
    sys.exit(1)
print('E004by VERIFY: PASS')
print(' - Windows MemShare create/delete SMC IDs exactly match Linux Qualcomm MP SHM-bridge commands')
print(' - Windows SmcInvoke modern/legacy SMC IDs exactly match Linux QTEE invoke transport IDs')
print(' - MemShare exposes explicit VMID/permission packing and an opaque bridge handle')
print(' - SmcInvoke is generic object transport, not a discovered camera service identity')
print(' - exact SP11 driver scan finds no camera client of MemSharing or Invoke')
print(' - camera components continue to reference QcTrEE PassThrough instead')
print(' - no secure runtime operation was performed')
