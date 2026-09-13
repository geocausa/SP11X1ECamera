#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, struct, sys, uuid

d = Path(__file__).resolve().parent
dll = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll")
result = json.loads((d / "RESULT.json").read_text())

def die(msg):
    print("E004al VERIFY: FAIL - " + msg)
    sys.exit(1)

if not dll.exists():
    die("source DLL missing")
b = dll.read_bytes()
if len(b) != 23998368:
    die("source DLL size mismatch")
if hashlib.sha256(b).hexdigest() != "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35":
    die("source DLL SHA-256 mismatch")

BASE = 0x180000000
def off_for_va(va):
    rva = va - BASE
    if 0x1000 <= rva < 0x1000 + 0xF7C304:
        return 0x400 + (rva - 0x1000)
    if 0xF7E000 <= rva < 0xF7E000 + 0x68854C:
        return 0xF7C800 + (rva - 0xF7E000)
    raise ValueError(hex(va))

def qword(va):
    o = off_for_va(va)
    return struct.unpack_from("<Q", b, o)[0]

# CInterfaceAccessor vtable direct authority.
accessor_vt = 0x1813345A8
if qword(accessor_vt + 0x50) != 0x180050D40:
    die("accessor +0x50 is not SetCameraControls")
if qword(accessor_vt + 0xB8) != 0x180051830:
    die("accessor +0xb8 is not CameraControls getter")

# Getter is exactly: ldr x0,[x0,#0x70]; ret
getter = b[off_for_va(0x180051830):off_for_va(0x180051830)+8]
if getter.hex() != "003840f9c0035fd6":
    die("CameraControls getter instruction bytes changed")

# CCameraControls primary vtable +0x20 -> KsProperty.
camera_vt = 0x1813311B8
if qword(camera_vt + 0x20) != 0x18002D0D0:
    die("CCameraControls +0x20 is not KsProperty")

# Decode the GUID constants used by InitializeTransform.
expected_guids = {
    0x181014BB0: "6a2c4fa6-d179-41cd-9523-822371ea40e5",
    0x181350D10: "00000000-0000-0000-c000-000000000046",
    0x181350D20: "bf94c121-5b05-4e6f-8000-ba598961414d",
    0x181350D30: "28f54685-06fd-11d2-b27a-00a0c9223196",
}
for va, want in expected_guids.items():
    raw = b[off_for_va(va):off_for_va(va)+16]
    got = str(uuid.UUID(bytes_le=raw))
    if got != want:
        die("GUID mismatch at %s: %s" % (hex(va), got))

files = {
    "accessor": d / "ghidra" / "DEVICEMFT-CAMERA-CONTROLS-ACCESSOR.txt",
    "pin": d / "ghidra" / "DEVICEMFT-PINCONFIGURER-KS-BRIDGE.txt",
    "outer": d / "ghidra" / "DEVICEMFT-KSPROPERTY-OWNER.txt",
    "construct": d / "ghidra" / "DEVICEMFT-CONSTRUCTION.txt",
}
for name,p in files.items():
    if not p.exists() or not p.stat().st_size:
        die(name + " evidence missing")

accessor = files["accessor"].read_text(errors="replace")
for s in (
    'CInterfaceAccessor::SetCameraControls',
    '*(longlong **)(param_1 + 0x70) = param_2',
    'FUN_1800517f0',
):
    if s not in accessor:
        die("accessor evidence missing: " + s)

pin = files["pin"].read_text(errors="replace")
for s in (
    "CPinConfigurer::KsProperty",
    "FUN_18004d540",
    "(*(undefined8 *)(*plVar3 + 0xb8))",
    "(*(undefined8 *)(*plVar3 + 0x20)",
):
    if s not in pin:
        die("pin-configurer evidence missing: " + s)

outer = files["outer"].read_text(errors="replace")
for s in (
    "CDeviceMFT::KsProperty",
    "Forwarding KsProperty to driver",
    "KsProperty handled in DMFT, not forwarding to driver",
    "param_1 + 0xb0",
    "param_1 + 0x98",
):
    if s not in outer:
        die("outer route evidence missing: " + s)

construct = files["construct"].read_text(errors="replace")
for s in (
    "&DAT_181014bb0,&DAT_181350d10",
    "&DAT_181350d20",
    "&DAT_181350d30",
    "local_608 + 0xb0",
):
    if s not in construct:
        die("construction evidence missing: " + s)

e004ak = d.parent / "e004ak-devicemft-secure-broker-static" / "verify_e004ak.py"
if not e004ak.exists():
    die("E004ak verifier missing")

if result.get("status") != "PASS_STATIC_DEVICEMFT_INTERNAL_KS_OWNER_CHAIN":
    die("RESULT status mismatch")
interp = result["interpretation"]
if not interp["pinconfigurer_to_camera_controls_chain_resolved"]:
    die("camera-controls chain not marked resolved")
if not interp["camera_controls_to_securemode_chain_resolved_by_e004ak"]:
    die("E004ak continuation not marked resolved")
if interp["trusted_external_trigger_resolved"]:
    die("RESULT overclaims trusted external trigger")
if interp["linux_secureisp_runtime_authorized"]:
    die("RESULT incorrectly authorizes Linux SecureISP")

print("E004al VERIFY: PASS")
print(" - SetCameraControls stores accessor +0x70; vtable +0xb8 returns exactly +0x70")
print(" - CPinConfigurer::KsProperty calls that getter then CCameraControls vtable +0x20")
print(" - CCameraControls vtable +0x20 is CCameraControls::KsProperty")
print(" - outer CDeviceMFT handled-vs-driver-forwarding route is kept separate")
print(" - no Windows runtime needed yet; Linux SecureISP remains unauthorized")
