#!/usr/bin/env python3
from pathlib import Path
import json, sys
d=Path(__file__).resolve().parent
def fail(s):
    print("E004ap VERIFY: FAIL - "+s)
    sys.exit(1)
r=json.loads((d/"RESULT.json").read_text())
if r.get("status")!="PASS_STATIC_WINDOWS_HELLO_OWNS_IR_SOURCE_SECUREMODE_TRIGGER":
    fail("status")
if r["linux_secureisp_runtime_authorized"]:
    fail("Linux SecureISP incorrectly authorized")
if r["extended_camera_control"]["faceauth_property_string"]!="{1CB79112-C0D2-4213-9CA6-CD4FDB927972},35":
    fail("FaceAuth property string")
if r["extended_camera_control"]["securemode_property_string"]!="{1CB79112-C0D2-4213-9CA6-CD4FDB927972},36":
    fail("SecureMode property string")
if r["securemode_behavior"]["enable_flags"]!=2 or r["securemode_behavior"]["disable_flags"]!=1:
    fail("SecureMode flag semantics")
stack=(d/"evidence/WINDOWS-STACK-EVIDENCE.txt").read_text(errors="replace")
for s in (
    "KSCAMERAPROFILE_FaceAuth_Mode,0",
    "644,604;FRT==60,1;SUT==NV12",
    "VirtualSecureMode,0x00010001,0x00000001",
    "FaceRecognitionSensorAdapterVsmSecure.DLL",
    "SecureBioCompanion",
    "QcISPTrustlet8380.dll",
):
    if s not in stack: fail("stack evidence missing "+s)
fp=(d/"ghidra/FACEPROCESSOR-SECURE-CONTROLS.txt").read_text(errors="replace")
for s in (
    "FUN_18004c5b8(uVar12,0x23",
    "FUN_18004c5b8((ulonglong)uVar4,0x24",
    "ToggleFaceMode.GetPropertyBuffer",
    "ToggleFaceMode.SetProperty",
    "ToggleSecureSensor.GetPropertyBuffer",
    "InfraredSourceController->SetPropertyAsync",
    "*(undefined8 *)(param_6 + 0x10) = param_5",
):
    if s not in fp: fail("FaceProcessor decomp evidence missing "+s)
const=(d/"ghidra/FACEPROCESSOR-CONSTANTS.txt").read_text(errors="replace")
if "ADDR 1800e4920" not in const or "UTF16 ,\\0" not in const:
    fail("comma delimiter evidence")
if "1291b71cd2c013429ca6cd4fdb927972" not in const:
    fail("extended-camera GUID bytes")
asm=(d/"evidence/FACEPROCESSOR-SECURE-ASM.txt").read_text(errors="replace")
for s in (
    "1800324e4:",
    "mov\tw1, #0x1",
    "180043f40:",
    "mov\tw1, #0x0",
    "180092578:",
    "uxtb\tw19, w1",
    "180092748:",
    "add\tx21, x19, #0x1",
    "180092768:",
    "bl\t0x18004bd98",
):
    if s not in asm: fail("assembly evidence missing "+repr(s))
print("E004ap VERIFY: PASS")
print(" - Windows Hello FaceProcessor owns FaceAuthMode/SecureMode IR-controller sequence")
print(" - property strings resolve to extended-camera GUID + comma + IDs 35/36")
print(" - SecureMode enable/disable is proven as argument 1/0 -> Flags 2/1")
print(" - Surface AUX FaceAuth profile and SecureBioCompanion package chain are tied")
print(" - Linux SecureISP remains unauthorized")
