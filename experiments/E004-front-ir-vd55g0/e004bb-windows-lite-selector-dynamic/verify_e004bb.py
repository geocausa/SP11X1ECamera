#!/usr/bin/env python3
from pathlib import Path
import json,sys,re

d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004bb VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_WINDOWS_SURFACE_IR_SETS_CAM_ISP_CAN_USE_LITE_MODE","status")
dc=r["device_config"]
need(dc["observed_hits"]==2,"hit count")
need(dc["payload_sizes"]==["0x900","0x900"],"payload sizes")
need(dc["feature_flag_dword_index"]=="0x23","feature dword")
need(dc["feature_flag_byte_offset"]=="0x8c","feature offset")
need(dc["observed_feature_flags"]==["0x00000002","0x00000002"],"feature flags")
need(dc["bit1_set_both"] is True,"bit1")
need(r["semantic_crosscheck"]["public_macro"]=="CAM_ISP_CAN_USE_LITE_MODE","semantic macro")
need(r["windows_trigger"]["real_frames"]==12,"real frames")
need(r["windows_trigger"]["securemode_during_stream"]==2,"secure mode")
need(r["debugger_mutated_payload"] is False,"read-only debugger")
need(r["linux_secureisp_runtime_executed"] is False,"Linux secure runtime")
need(r["qcomtee_loaded_linux"] is False,"QCOMTEE")
g=r["golden_return"]
need(g["kernel"]=="7.1.5-sp11-render-parity-v4+","Golden kernel")
need(g["next_entry"]=="","one-shot cleared")
need(g["camera_nodes"] is False and g["camera_modules"] is False,"Golden camera state")

kd=(d/"evidence/E004BB-KD-DEVICECONFIG.txt").read_text(errors="replace")
need(kd.count("feature_flag=0x00000002")==2,"two flag=2 observations")
need(kd.count("wrapper_payload_size=0x900")==2,"two 0x900 payloads")
need("raw_sha256=eebe5a17805316bc6f98825368b86bc1a4cf55e3df48eaa504bcf652a7b5a560" in kd,"KD hash")

w=(d/"evidence/E004BB-WINDOWS-RUN-SUMMARY.txt").read_text(errors="replace")
for s in ("real_frames=12","during stream flags=2","SecureMode final flags=1","FaceAuthMode final flags=1"):
    need(s in w,"Windows evidence missing "+s)

post=(d/"POSTRETURN-GOLDEN.txt").read_text(errors="replace")
for s in ("7.1.5-sp11-render-parity-v4+","saved_entry=sp11-audio-fullio-v19c","next_entry=","BootCurrent: 0005"):
    need(s in post,"post-return evidence missing "+s)

print("E004bb VERIFY: PASS")
print(" - two live protected DeviceConfig payloads carried feature_flag 0x2")
print(" - E004ba maps bit 1 to CAM_ISP_CAN_USE_LITE_MODE")
print(" - trusted Windows route acquired 12 real IR frames")
print(" - debugger observation was read-only")
print(" - SP11 returned to protected Golden Linux")
