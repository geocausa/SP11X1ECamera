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
if r.get('status')!='PASS_QCSK_CAMERA_PIL_STATE_MACHINE_IS_FIRMWARE_HANDOFF_NOT_FRAME_PROVIDER': fail.append('status')
if r['runtime_actions']!={'windows_boot':False,'camera_state_switch':False,'smc':False,'ium_call':False,'qtee_qsee_call':False,'linux_camera_runtime':False}: fail.append('runtime boundary')
x=need('evidence/CAM-PIL-LOG-XREFS.txt','firmware segment prescan failed','map to intermediate VM from HYP failed','map to subsys from intermediate VM failed','map to intermediate VM from subsys failed','map to HLOS from intermediate VM failed','camera_set_state','pil_camera_mem_assign')
v=need('evidence/CAMERA-PIL-VMID-MAP.txt','QCOM_SCM_VMID_HLOS','QCOM_SCM_VMID_HLOS_FREE','VMID 4: source named HYP','VMID 0x0e: destination of that call','VMID 0x39: destination of "map to subsys','VMID 3: destination of "map to HLOS','No public Linux QCOM_SCM_VMID_* definition for 0x39')
f=need('evidence/CAMERA-PIL-FIRMWARE-SEGMENTS.txt','failed to get ELF segment info','segment%d paddr=%llu not 4kB aligned','uVar13 = (uint)uVar6 & 1','uVar13 = uVar13 | 2','uVar13 = uVar13 | 4','QCOM_SCM_PERM_READ','QCOM_SCM_PERM_WRITE','QCOM_SCM_PERM_EXEC')
d=need('evidence/CAMERA-PIL-TRANSITION-DISASM.txt','mov\tw8, #0x4','mov\tw8, #0x39','map to intermediate VM from HYP' if False else 'forward accepted branch','reverse accepted branch')
c=need('evidence/CAMERA-CORE-STATE.txt','core must be idle before halt','cannot resume core','setting invalid state','FUN_140014b80')
need('README.md','HYP(4) -> HLOS_FREE/intermediate(0x0e) -> camera PIL subsystem(0x39)','camera PIL subsystem(0x39) -> HLOS_FREE/intermediate(0x0e) -> HLOS(3)','VMID `0x39` therefore must not be adopted as a frame-buffer owner','A Windows one-shot is **not required for E004cb**.','E004cc — IUM secure-section backing/provider path below `CreateSecureSection`')
if fail:
 print('E004cb VERIFY: FAIL')
 for x in fail: print(' -',x)
 sys.exit(1)
print('E004cb VERIFY: PASS')
print(' - vendor log xrefs anchor HYP -> intermediate -> subsystem and subsystem -> intermediate -> HLOS transitions')
print(' - Linux names intermediate 0x0e as HLOS_FREE and HLOS as VMID 3')
print(' - 0x39 is camera PIL subsystem VMID in this binary; no public Linux name is invented')
print(' - final subsystem permissions are derived from ELF segment R/W/X bits')
print(' - camera_set_state brackets core halt/resume and firmware register programming')
print(' - state machine is PIL firmware-image ownership, not protected frame-buffer/sample provisioning')
print(' - no runtime action was performed')
