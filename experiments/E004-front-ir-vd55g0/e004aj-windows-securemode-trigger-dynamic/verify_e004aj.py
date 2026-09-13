#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import re
import sys

d = Path(__file__).resolve().parent
raw = d / "recovered-sp7" / "E004AJ_R2_TRACE.log"
probes = (d / "WINDOWS-PROBES.txt").read_text()
golden = (d / "POST-RETURN-GOLDEN.txt").read_text()
result = json.loads((d / "RESULT.json").read_text())
devicemft = d.parent / "e004ai-secure-mode-owner-static" / "ghidra" / "DEVICEMFT-SECURE-XREFS.txt"

def die(msg):
    print("E004aj VERIFY: FAIL - " + msg)
    sys.exit(1)

b = raw.read_bytes()
if len(b) != 12935:
    die("R2 log size mismatch")
if hashlib.sha256(b).hexdigest() != "f495dae75e017e001146cc2317ef96cf4f4fba0921e60481753bf82d5b96b37f":
    die("R2 log SHA-256 mismatch")

text = b.decode("utf-8", errors="strict")
expected = {
    "E004AJ_R2_SM_GET ": 3,
    "E004AJ_R2_SM_SET_ENTER ": 0,
    "E004AJ_R2_SM_SET_POST ": 0,
    "E004AJ_R2_SECURE_KMDISP ": 0,
    "E004AJ_R2_QCCAM_OP ": 0,
    "E004AJ_R2_QCCAM_TASK ": 0,
    "E004AJ_R2_QCCAM_FNTABLE ": 0,
    "E004AJ_R2_QCCAM_SECURECFG ": 0,
}
for marker, wanted in expected.items():
    got = len(re.findall(r"(?m)^" + re.escape(marker), text))
    if got != wanted:
        die("runtime marker %r: %d != %d" % (marker, got, wanted))

if "===E004AJ_R2_END_SET_REJECTED_BEFORE_KMD===" not in text:
    die("R2 end marker missing")
if "surfacecamavs8380+0x83120" not in text or "qccamsecureisp8380+0x4a90" not in text:
    die("current-image breakpoint authority missing")

for s in (
    "flags=0x1 capability=0x3",
    "SET enable after selecting NV12 644x604",
    "hr=0xc00d36b3",
    "QI(IKsPropertySet): 0x80004002",
    "12 real frames",
    "policy was NOT weakened",
):
    if s not in probes:
        die("probe evidence missing: " + s)

for s in (
    "7.1.5-sp11-render-parity-v4+",
    "saved_entry=sp11-audio-fullio-v19c",
    "next_entry=",
    "BootCurrent: 0005",
):
    if s not in golden:
        die("Golden evidence missing: " + s)

if not devicemft.exists():
    die("DeviceMFT static authority missing")
db = devicemft.read_bytes()
if hashlib.sha256(db).hexdigest() != "fb9336fa5b42d9892fa3dc4dac5a73eb819242e88188191b1eec1d69933fd499":
    die("DeviceMFT static authority SHA mismatch")
dt = db.decode("utf-8", errors="replace")
for s in (
    "CProperty_SecureMode::SetProperty",
    "CaptureProperties::OnSetSecureMode",
    "SecureMode Enabled",
    "MFMediaType_Protected",
    "IFE_LITE_SECURE_MODE",
    "CameraSecureISP",
):
    if s not in dt:
        die("DeviceMFT authority missing: " + s)

if result.get("status") != "PASS_VALID_NEGATIVE_GENERIC_CLIENT_SET_REJECTED_BEFORE_KMD":
    die("RESULT status mismatch")
if result["interpretation"]["securemode_successfully_enabled"]:
    die("RESULT incorrectly claims successful enable")
if result["interpretation"]["linux_secureisp_runtime_authorized"]:
    die("RESULT incorrectly authorizes Linux SecureISP")

print("E004aj VERIFY: PASS")
print(" - exact SecureMode GET is proven: disabled, capability=3")
print(" - generic MF/WinRT SET is rejected before the KMD setter")
print(" - runtime-only KD markers: 3 GET, 0 SET/secure/qccam hits")
print(" - DeviceMFT broker boundary is statically anchored")
print(" - protected Golden FullIO v19c restored")
