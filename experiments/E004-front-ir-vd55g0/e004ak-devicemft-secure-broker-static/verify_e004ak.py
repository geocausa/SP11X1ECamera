#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import re
import sys

d = Path(__file__).resolve().parent
repo = d.parents[2]
archive = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive")
dll = archive / "sp11-driverdump" / "surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342" / "QcDeviceMFT8380.dll"

files = {
    "focused": d / "ghidra" / "DEVICEMFT-SECURE-BROKER-FOCUSED.txt",
    "broker": d / "ghidra" / "DEVICEMFT-PROPERTY-BROKER.txt",
    "vtable": d / "ghidra" / "DEVICEMFT-SECURE-VTABLE.txt",
    "observer": d / "ghidra" / "DEVICEMFT-PROPERTY-OBSERVER-LOOP.txt",
    "controls": d / "ghidra" / "DEVICEMFT-CCAMERACONTROLS.txt",
    "wiring": d / "ghidra" / "DEVICEMFT-CAMERA-CONTROLS-WIRING.txt",
}
result = json.loads((d / "RESULT.json").read_text())

def die(msg):
    print("E004ak VERIFY: FAIL - " + msg)
    sys.exit(1)

if not dll.exists():
    die("source DLL missing")
b = dll.read_bytes()
if len(b) != 23998368:
    die("source DLL byte size mismatch")
if hashlib.sha256(b).hexdigest() != "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35":
    die("source DLL SHA-256 mismatch")

for name, p in files.items():
    if not p.exists() or p.stat().st_size == 0:
        die(name + " evidence missing")

focused = files["focused"].read_text(errors="replace")
broker = files["broker"].read_text(errors="replace")
vtable = files["vtable"].read_text(errors="replace")
observer = files["observer"].read_text(errors="replace")
controls = files["controls"].read_text(errors="replace")
wiring = files["wiring"].read_text(errors="replace")

for s in (
    "TARGET 1802f7458 FUN_1802f7458@1802f7458",
    "REF 18029324c type=UNCONDITIONAL_CALL caller=FUN_180292f20@180292f20",
    "REF 1802f8fe8 type=PARAM caller=FUN_1802f7458@1802f7458",
    "REF 1802f906c type=PARAM caller=FUN_1802f7458@1802f7458",
    "FUN_180293ad8",
):
    if s not in focused:
        die("focused authority missing: " + s)

for s in (
    "CCameraControls::KsProperty",
    "FUN_18002d0d0",
    "CProperty::RegisterPropertyObserver",
    "FUN_180309760",
    "CCameraControls::NotifyAllObservers",
):
    if s not in broker:
        die("property broker authority missing: " + s)

for s in (
    "CProperty::Handle",
    "(*param_1 + 0xc0)",
    "(*param_1 + 0xb8)",
    "(*param_1 + 0x60)",
    "CProperty::NotifySetObservers",
    "FUN_180047d40(param_1,param_2,1)",
):
    if s not in vtable:
        die("vtable authority missing: " + s)

for s in (
    "CProperty::NotifyGetObservers",
    "FUN_180047d40(param_1,param_2,0)",
    "CProperty::RegisterPropertyObserver",
    "*(undefined4 *)(puVar2 + 4) = param_5",
    "*(undefined4 *)(param_1 + 0x13578) = 1",
    "*(undefined4 *)(param_1 + 0x13578) = 0",
):
    if s not in observer:
        die("observer authority missing: " + s)

for s in (
    "CCameraControls::QueryInterface",
    "FUN_180f5e7c0(param_2,&DAT_181350d10,0x10)",
    "CCameraControls::Initialize",
    "CCameraControls::KsEvent",
):
    if s not in controls:
        die("camera-controls authority missing: " + s)

for s in (
    "CItemFactoryBase::CreateCameraControls",
    "psCInterfaceAccessor::SetCameraControls",
):
    if s not in wiring:
        die("factory wiring evidence missing: " + s)

# DAT_181350d10 is in .rdata at file offset 0x134f510.
iid = b[0x134f510:0x134f520]
if iid.hex() != "0000000000000000c000000000000046":
    die("CCameraControls QueryInterface GUID is not IID_IUnknown")

e004ai = d.parent / "e004ai-secure-mode-owner-static" / "ghidra" / "DEVICEMFT-SECURE-XREFS.txt"
if not e004ai.exists():
    die("E004ai DeviceMFT authority missing")
t = e004ai.read_text(errors="replace")
for s in (
    "if (*(int *)(param_1 + 0x1357c) == 1)",
    "SecureMode Enabled",
    "IFE_LITE_SECURE_MODE",
    "Bypass IPE for SecureBio use case",
):
    if s not in t:
        die("downstream authority missing: " + s)

if result.get("status") != "PASS_STATIC_DEVICEMFT_SECUREMODE_BROKER_CHAIN":
    die("RESULT status mismatch")
if not result["interpretation"]["devicemft_securemode_write_chain_resolved"]:
    die("RESULT does not mark broker chain resolved")
if result["interpretation"]["trusted_external_trigger_resolved"]:
    die("RESULT overclaims external trigger")
if result["interpretation"]["linux_secureisp_runtime_authorized"]:
    die("RESULT incorrectly authorizes Linux SecureISP")

print("E004ak VERIFY: PASS")
print(" - DeviceMFT KS SET -> SecureMode SetProperty -> SET observer chain resolved")
print(" - CaptureProperties OnSetSecureMode state transition resolved")
print(" - secure capture-pipe IFE_LITE_SECURE_MODE consumer resolved")
print(" - CCameraControls is an internal direct-pointer object; QI only exposes IUnknown")
print(" - external trusted trigger remains the next gate; no Windows run required yet")
