#!/usr/bin/env python3
from pathlib import Path
import json, re, sys

d=Path(__file__).resolve().parent
def fail(msg):
    print("E004aq VERIFY: FAIL - "+msg)
    sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
if r.get("status")!="PASS_WINDOWS_HELLO_SOURCE_CONTROLLER_ENTERS_SECUREISP":
    fail("status")
if r.get("linux_secureisp_runtime_authorized") is not False:
    fail("Linux SecureISP must remain unauthorized")

clean=(d/"evidence/E004AQ-WINDOWS-SUCCESS.txt").read_text(errors="replace")
required_clean=[
    "E004AQ_SET tag=face-enable",
    "requested_flags=0x2 status=Success",
    "E004AQ_SET tag=secure-enable",
    "E004AQ_PARSE tag=secure-after-enable",
    "flags=0x2 capability=0x3",
    "E004AQ_START=Success",
    "E004AQ_ACQUIRED=12",
    "E004AQ_PARSE tag=secure-during-stream",
    "E004AQ_SECURE_DISABLE=Success",
    "E004AQ_FACE_DISABLE=Success",
    "E004AQ_END",
]
for s in required_clean:
    if s not in clean:
        fail("clean-run evidence missing "+s)

summary=(d/"evidence/E004AQ_KERNEL_SUMMARY.txt").read_text(errors="replace")
for s in [
    "QCCamAvs DriverStart=0xfffff80384620000 size=0xad000",
    "CameraSecureISP DriverStart=0xfffff80384810000 size=0x36000",
    "kernel_trace_sha256=5dfac22112c9d0cf2ae9cb1f1ef9cb43a00084aabba6d8e0a8da7c9440086ad3",
    "devicemft_actual_hit_count=0",
    "QCCamAvs_SendPacketInternal=88",
    "SecureISP_ConfigSecureCamera=3",
    "SecureISP_OpDispatcher=48",
    "RERUN CONFIGSECURECAMERA",
]:
    if s not in summary:
        fail("kernel summary missing "+s)

cfg=[ln for ln in summary.splitlines() if ln.startswith("E004AQ_KHIT SecureISP_ConfigSecureCamera")]
if not any("x2=0000000000000001" in ln for ln in cfg):
    fail("no enable-side ConfigSecureCamera hit")
if not any("x2=0000000000000000" in ln for ln in cfg):
    fail("no teardown-side ConfigSecureCamera hit")

dev=(d/"evidence/E004AQ_DEVICEMFT_TRACE.log").read_text(errors="replace")
actual=[ln for ln in dev.splitlines() if ln.startswith("E004AQ_HIT ")]
if actual:
    fail("DeviceMFT unexpectedly has actual target hits")

rerun=(d/"evidence/E004AQ-WINDOWS-KERNEL-TRACED-RERUN.txt").read_text(errors="replace")
for s in [
    "E004AQ_SET tag=face-enable",
    "E004AQ_SET tag=secure-enable",
    "E004AQ_START=Success",
    "E004AQ_ACQUIRED=0",
    "E004AQ_SECURE_DISABLE=Success",
    "E004AQ_FACE_DISABLE=Success",
    "E004AQ_END",
]:
    if s not in rerun:
        fail("instrumented rerun evidence missing "+s)

gold=(d/"POSTRETURN-GOLDEN.txt").read_text(errors="replace")
for s in [
    "7.1.5-sp11-render-parity-v4+",
    "sp11_entry=7.1.5-sp11-fullio-v19c",
    "saved_entry=sp11-audio-fullio-v19c",
    "next_entry=",
    "BootCurrent: 0005",
]:
    if s not in gold:
        fail("Golden return missing "+s)

nodes_section=gold.split("--- nodes ---",1)[1].split("--- camera modules ---",1)[0]
mods_section=gold.split("--- camera modules ---",1)[1] if "--- camera modules ---" in gold else ""
if "/dev/video" in nodes_section or "/dev/media" in nodes_section:
    fail("camera nodes present after return")
if re.search(r"\b(camss|vd55g0|imx681|ov13858)\b",mods_section,re.I):
    fail("camera module present after return")

print("E004aq VERIFY: PASS")
print(" - exact Windows Hello source-controller FaceAuth/SecureMode enable sequence succeeded")
print(" - clean run acquired 12 real IR frames with SecureMode confirmed enabled")
print(" - DeviceMFT trace recorded zero actual target hits")
print(" - kernel trace proves live QCCamAvs -> CameraSecureISP execution")
print(" - ConfigSecureCamera enable and teardown transitions were both observed")
print(" - protected Linux Golden was restored")
print(" - Linux SecureISP remains unauthorized")
