#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, struct, sys, uuid

d = Path(__file__).resolve().parent
pkg = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342")
dll = pkg / "QcDeviceMFT8380.dll"
inf = pkg / "surfacecamavs8380.inf"
evidence = d / "ghidra" / "DEVICEMFT-EXTERNAL-KS-FACE.txt"
result = json.loads((d / "RESULT.json").read_text())

def die(msg):
    print("E004am VERIFY: FAIL - " + msg)
    sys.exit(1)

if not dll.exists() or not inf.exists():
    die("source package missing")
db = dll.read_bytes()
ib = inf.read_bytes()
if len(db) != 23998368:
    die("DLL size mismatch")
if hashlib.sha256(db).hexdigest() != "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35":
    die("DLL SHA-256 mismatch")
if hashlib.sha256(ib).hexdigest() != "4db3acab414e344dc460478b54d964c9c7b5d3d648ee0c19db13523431262fcb":
    die("INF SHA-256 mismatch")

it = ib.decode("utf-16")
for s in (
    r"SOFTWARE\Classes\CLSID\{4C2331F0-66BE-4177-9841-2FCBA8CCF5CA}",
    r"%13%\QcDeviceMFT8380.dll",
    'ThreadingModel,,"Both"',
    'DMFT.CLSID               = "{4C2331F0-66BE-4177-9841-2FCBA8CCF5CA}"',
):
    if s not in it:
        die("INF registration authority missing: " + s)

BASE=0x180000000
def off_for_va(va):
    rva=va-BASE
    if 0x1000 <= rva < 0x1000+0xF7C304:
        return 0x400 + (rva-0x1000)
    if 0xF7E000 <= rva < 0xF7E000+0x68854C:
        return 0xF7C800 + (rva-0xF7E000)
    raise ValueError(hex(va))

def qword(va):
    return struct.unpack_from("<Q", db, off_for_va(va))[0]

raw = db[off_for_va(0x181350D30):off_for_va(0x181350D30)+16]
if str(uuid.UUID(bytes_le=raw)) != "28f54685-06fd-11d2-b27a-00a0c9223196":
    die("DeviceMFT KS GUID mismatch")

vt=0x181330980
expected={
    0x18:0x180018250,
    0x20:0x1800186f0,
    0x28:0x180018a50,
}
for slot,want in expected.items():
    got=qword(vt+slot)
    if got != want:
        die("DeviceMFT KS vtable %s -> %s != %s" % (hex(slot),hex(got),hex(want)))

if not evidence.exists() or evidence.stat().st_size == 0:
    die("Ghidra evidence missing")
t=evidence.read_text(errors="replace")
for s in (
    "CDeviceMFT::QueryInterface",
    "FUN_180010a70",
    "DAT_181350d30",
    "plVar1 = param_1 + 3",
    "CDeviceMFT::KsProperty",
    "FUN_180018250",
    "Forwarding KsProperty to driver",
    "KsProperty handled in DMFT, not forwarding to driver",
    "param_1 + 0xb0",
    "param_1 + 0x98",
):
    if s not in t:
        die("Ghidra authority missing: " + s)

if result.get("status") != "PASS_STATIC_DEVICEMFT_EXTERNAL_KS_FACE":
    die("RESULT status mismatch")
interp=result["interpretation"]
if not interp["devicemft_has_distinct_ks_face"]:
    die("distinct KS face not marked proven")
if interp["trusted_windows_trigger_resolved"]:
    die("RESULT overclaims trusted Windows trigger")
if not interp["bounded_windows_host_trace_justified"]:
    die("next bounded Windows trace not justified")
if interp["linux_secureisp_runtime_authorized"]:
    die("RESULT incorrectly authorizes Linux SecureISP")

print("E004am VERIFY: PASS")
print(" - INF registers QcDeviceMFT8380.dll as the camera DeviceMFT")
print(" - DeviceMFT QueryInterface exposes a distinct KS-control subobject")
print(" - KS vtable maps Property/Method/Event exactly")
print(" - DeviceMFT handles properties internally before driver forwarding")
print(" - trusted Windows trigger remains unresolved; bounded host trace is justified")
