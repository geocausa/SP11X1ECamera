#!/usr/bin/env python3
from pathlib import Path
import json,sys
E=Path(__file__).resolve().parent
fail=[]
def need(rel,*t):
 s=(E/rel).read_text(errors='replace')
 for x in t:
  if x not in s: fail.append(f'{rel}: missing {x!r}')
 return s
r=json.loads((E/'RESULT.json').read_text())
if r.get('status')!='PASS_CAMERA_ASSIGNMENT_IS_SECURE_SECTION_DEVICE_GPA_MAPPING_NOT_PHYSICAL_OWNER_REPLACEMENT': fail.append('status')
if r['runtime_actions']!={'windows_boot':False,'pkvm_boot':False,'ium_call':False,'hyperv_call':False,'iommu_change':False,'scm_assign_mem':False,'qtee_qsee':False,'camera_runtime':False}: fail.append('runtime boundary')
need('evidence/SECUREKERNEL-DEVICE-GPA.txt','=== IumAssignMemoryToSocDomain ===','SkhalValidateProcessIoDomain','SkmmReferenceSecureSection','SkmmProbeSecureSectionPages','ShvlMapSparseDeviceGpaPages','ShvlpInitiateFastHypercall(199')
need('evidence/SECUREKERNEL-IO-DOMAIN.txt','SkhalValidateProcessIoDomain','if (*piVar4 == param_2)','ShvlMapSparseDeviceGpaPages')
need('evidence/SECUREKERNEL-DEVICE-GPA-LIFETIME.txt','CALLER SkhalpDeleteDomainAssignment','ShvlUnmapSparseDeviceGpaPages','ShvlUnmapDeviceGpaPages')
need('evidence/CAMERA-ASSIGNMENT-PARAMETER-MAP.txt','io_domain = 0x0d','protection = 4','protection 4    -> device GPA flags 0x3','SkhalValidateProcessIoDomain(process_policy, io_domain)')
need('evidence/SUPERSEDED-QCSK-OWNERSHIP-MODEL.txt','E004ck\'s direct {CP_CAMERA,HYP} ownership matrix is therefore not the correct model','Secure-Kernel-owned protected pages + Hyper-V device-GPA map to IO domain 0x0d, R/W flags 0x3')
need('README.md','pKVM conceptually','E004cm — trusted CAMSS device-GPA/SMMU mapping feasibility')
if fail:
 print('E004cl VERIFY: FAIL')
 for x in fail: print(' -',x)
 sys.exit(1)
print('E004cl VERIFY: PASS')
print(' - Secure Kernel validates IO domain against secure-process policy')
print(' - camera protection 4 becomes device-GPA R/W flags 0x3')
print(' - secure section stays referenced while Hyper-V maps sparse device GPA pages')
print(' - assignment handle deletion unmaps the device GPA pages')
print(' - frame-target QcSkExt physical-owner interpretation is superseded')
print(' - pKVM is conceptually reopened; trusted DMA/SMMU control is now the blocker')
print(' - no runtime operation was performed')
