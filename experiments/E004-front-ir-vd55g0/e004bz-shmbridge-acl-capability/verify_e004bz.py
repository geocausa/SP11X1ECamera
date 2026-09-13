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
if r.get('status')!='PASS_SHMBRIDGE_ACL_FLEXIBLE_BUT_NOT_MEMORY_OWNERSHIP_PROTECTION': fail.append('status')
if r['runtime_actions']!={'shm_bridge_create':False,'scm_assign_mem':False,'qcomtee_enable_or_load':False,'qtee_qsee_call':False,'camera_runtime':False}: fail.append('runtime boundary')
w=need('evidence/WINDOWS-BRIDGE-REQUEST-MAP.txt','request input length = 0x30','+0x14 u32 -> helper param_5','VMID == 3 (HLOS)','size_and_flags |= (perm << 2) | 2','arg3 = packed_vmids','SMC = 0x02000c1e')
need('evidence/WINDOWS-MEMSHARE-BRIDGE-DECOMP.txt','param_5 - 1 < 4','if (puVar7[-1] == 3)','local_a8 = (ulonglong)param_4 | (ulonglong)param_5 << 9','local_a0 = (ulonglong)puVar7[-1] | local_a0 << 0x10')
h=need('evidence/WINDOWS-HOST-ADDRESSABLE-ALLOCATION.txt','AllocMemFromTreeSMB','*param_4 = lVar13','MmGetPhysicalAddress()','*param_3 = uVar6','FreeMemFromTreeSMB')
l=need('evidence/LINUX-WRAPPER-VS-RAW-BRIDGE.txt','pfn_and_ns_perm = paddr | QCOM_SCM_PERM_RW','ipfn_and_s_perm = paddr | QCOM_SCM_PERM_RW','size_and_flags = size | (1 << QCOM_SHM_BRIDGE_NUM_VM_SHIFT)','QCOM_SCM_VMID_HLOS','qcom_scm_shm_bridge_create')
a=need('evidence/BRIDGE-VS-OWNERSHIP-ASSIGNMENT.txt','QCOM_SCM_MP_SHM_BRIDGE_CREATE','QCOM_SCM_MP_ASSIGN','int qcom_scm_assign_mem','--- no ownership-assignment primitive in MemShare decomp ---')
after=a.split('--- no ownership-assignment primitive in MemShare decomp ---',1)[1].strip()
if after: fail.append('MemShare decomp unexpectedly contains ownership assignment primitive: '+after[:200])
need('README.md','not listed in bridge sharing set != ownership revoked','E004ca — external VTL1 secure-section protection semantics versus Linux primitives')
if fail:
 print('E004bz VERIFY: FAIL')
 for x in fail: print(' -',x)
 sys.exit(1)
print('E004bz VERIFY: PASS')
print(' - raw Windows MemShare bridge request accepts 1..4 explicit VMID/permission pairs')
print(' - VMID 3/HLOS is optional in the bridge sharing list')
print(' - MemShare allocation retains a normal host virtual address and derives its physical address')
print(' - Linux TZMEM wrapper deliberately keeps HLOS RW on bridged memory')
print(' - raw Linux SCM exposes the same lower-level bridge transport')
print(' - SHM bridge and SCM memory ownership assignment are separate operations')
print(' - bridge handle can model backend lifetime but is not the external sample identity by itself')
print(' - no secure runtime operation was performed')
