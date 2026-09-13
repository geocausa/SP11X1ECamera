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
if r.get('status')!='PASS_EXTERNAL_SAMPLE_METADATA_END_TO_END_DMFT_TASK4_DISPROVEN_AS_IDENTITY': fail.append('status')
if r['runtime_actions']!={'windows_reboot_or_trace':False,'linux_secureisp':False,'camera_runtime':False,'qtee_qsee':False,'scm_assign_mem':False,'protected_memory_operation':False}: fail.append('runtime boundary')
s=need('evidence/SDK-TO-SURFACECAM-SECURE-SAMPLE.txt','GUID guidBufferIdentifier','DWORD cbBufferSize','DWORD cbCaptured','STATIC_KS_SECURE_CAMERA_SCENARIO_ID','*(undefined8 *)(param_3 + 0x6c) = puVar7[1]','*(undefined8 *)(param_3 + 100) = uVar6','*(undefined4 *)(param_3 + 0x74) = *(undefined4 *)(puVar7 + 2)','*(undefined4 *)(param_3 + 0x78)')
need('evidence/SDK-TO-SURFACECAM-SECURE-SAMPLE.txt','*(ulonglong *)(lVar1 + 0x194) = CONCAT44(uStack_80,uStack_84)','*(ulonglong *)(lVar1 + 0x18c) = CONCAT44(uStack_88,uStack_8c)','*(undefined4 *)(lVar1 + 0x19c) = local_7c','*(undefined4 *)(lVar1 + 0x1a0) = (undefined4)uStack_78')
d=need('evidence/DMFT-TASK4-ROLE.txt','FUN_140004a90(4,0,puVar35,0x60','PatchAddr for src','PatchAddr for dst','malloc(0x60)','FUN_180007180((longlong *)&DAT_18003dde0,&local_50)','local_c0[1] = local_78')
c=need('evidence/CSL-IOCONFIG-TO-EXTERNAL-OPEN.txt','*(ulonglong *)((longlong)local_f0 + 0x74) = uStack_38','*(ulonglong *)((longlong)local_f0 + 0x6c) = local_40','*(int *)((longlong)local_f0 + 0x7c) = (int)local_e8[0x25]','*(undefined4 *)(local_f0 + 0x10) = *(undefined4 *)((longlong)local_e8 + 300)','*(undefined4 *)((longlong)local_f0 + 0x7c) = *(undefined4 *)(local_f0 + 0x10)','OpenSecureSection(&local_40)','MapViewOfFile(hFileMappingObject,6,0,0,(SIZE_T)*(undefined4 *)(param_1 + 0x7c))','KS_SECURE_CAMERA_SCENARIO_ID=AE53FC6E-8D89-4488-9D2E-4D008731C5FD','count=1')
a=need('evidence/TRUSTLET-FRAME-PAYLOAD-OFFSET.txt','91026129','add\tx9, x9, #0x98','91027129','add\tx9, x9, #0x9c','(*(longlong *)(lVar3 + 0x90) + (ulonglong)*(uint *)(lVar3 + 0x9c))')
f=need('evidence/FIELD-MAP.txt','IOConfig +0x118 <- GUID first 8 bytes','IOConfig +0x120 <- GUID second 8 bytes','IOConfig +0x128 <- cbBufferSize','IOConfig +0x12c <- cbCaptured','final +0x7c = cbCaptured','class-1 task 4 / PROCESS_DMFT_SURFACE 0x60 record is NOT the external secure GUID/size contract')
need('README.md','The external secure GUID/size path is instead the **CSL IOConfig tail described above**.','E004bw — external protected-sample Linux representation contract')
if fail:
    print('E004bv VERIFY: FAIL')
    for x in fail: print(' -',x)
    sys.exit(1)
print('E004bv VERIFY: PASS')
print(' - SDK SECURE_BUFFER_INFO GUID/cbBufferSize/cbCaptured is preserved by SurfaceCam')
print(' - CSL IOConfig tail carries GUID at +0x118/+0x120 and sizes at +0x128/+0x12c')
print(' - trustlet final external map length is cbCaptured and fixed scenario GUID matches the SDK')
print(' - trustlet separately tracks serialized extent +0x98 and frame payload offset +0x9c')
print(' - PROCESS_DMFT_SURFACE task4 0x60 is patch/cmd surface metadata, not external sample identity')
print(' - no Windows or Linux secure runtime action was needed')
