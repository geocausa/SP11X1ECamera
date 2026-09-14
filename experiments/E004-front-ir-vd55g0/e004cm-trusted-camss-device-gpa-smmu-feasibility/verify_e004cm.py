#!/usr/bin/env python3
from pathlib import Path
import json,sys,re
E=Path(__file__).resolve().parent
fail=[]
def need(rel,*tokens):
 s=(E/rel).read_text(errors='replace')
 for t in tokens:
  if t not in s: fail.append(f'{rel}: missing {t!r}')
 return s
r=json.loads((E/'RESULT.json').read_text())
if r.get('status')!='PASS_GUNYAH_TRUSTED_VM_CANNOT_COOWN_CP_CAMERA_CP_CDSP_RULE_DISCOVERED': fail.append('status')
if any(r['runtime_actions'].values()): fail.append('runtime action occurred')
need('evidence/GUNYAH-RM-IDENTITY.txt','gunyah-resource-manager','src/memparcel/memparcel.c','platform/qcom/src/hyp_assign/hyp_assign.c','vm_device_assignments','533c1d629f498b7185275507c516336ef94ed04fff661fd7e9db63c222c98a6d')
a=need('evidence/GUNYAH-RM-ACL-VALIDATION.txt','memparcel: acl[%d]: invalid vmid or rights','HLOS is not owner','allocated vmid=%d','VM_ALLOCATE')
n=need('evidence/TRUSTED-VM-AC-NORMALIZATION.txt',"trusted_static_vmids_normalized_to_0x3f= ['0x2d', '0x31', '0x32', '0x34', '0x35', '0x36', '0x37', '0x3a']",'cp_camera_0x0d_in_rm_fixed_acl= False')
q=need('evidence/CP-CAMERA-RULE-QUERY.txt','RULES_CONTAINING_BOTH_CP_CAMERA_AND_TRUSTED_CLASS= 0','vmid=0x2a flags=0xff vmid=0xd flags=0xff','vmid=0xd flags=0xff vmid=0x1d flags=0xd0')
need('evidence/QHEE-AC-RULE-TABLE.txt','TOTAL_RULES=116','TARGET_DST=0x8000000000002000','TARGET_FOUND=false')
need('evidence/QHEE-VMID-METADATA.txt','f0_vmid=0x2e','f0_vmid=0x2d','fc_type=0x2','f0_vmid=0xd')
need('evidence/GUNYAH-DEVICE-PASSTHROUGH-POLICY.txt','vm_passthrough_config: Unsupported VMID','0xf6200000000000')
need('README.md','cannot be represented as:','E004cn — CP_CAMERA + CP_CDSP trusted-worker feasibility')
if fail:
 print('E004cm VERIFY: FAIL')
 for x in fail: print(' -',x)
 sys.exit(1)
print('E004cm VERIFY: PASS')
print(' - recovered and reversed the embedded same-machine Gunyah Resource Manager ELF')
print(' - RM memparcel ACL rejects CP_CAMERA as a trusted-guest peer')
print(' - QHEE normalizes static trusted VMs to access-control class 0x3f')
print(' - all 116 QHEE rules contain zero CP_CAMERA + trusted-VM-class combinations')
print(' - direct trusted-VM device passthrough is firmware-policy constrained and not a proven CAMSS binding')
print(' - QHEE explicitly permits CP_CAMERA + CP_CDSP, establishing the next static gate')
print(' - no secure runtime operation was performed')
