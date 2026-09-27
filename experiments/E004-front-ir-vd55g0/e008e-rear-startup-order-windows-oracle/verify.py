#!/usr/bin/env python3
import hashlib, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = "5fb0e6a3eda1a05cf0347dcc5820f8f42fed5cca"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

safe = json.loads((HERE/"SAFE-ORDER.json").read_text())
run = json.loads((HERE/"WINDOWS-RUNTIME.json").read_text())
res = json.loads((HERE/"RESULT.json").read_text())

assert sha(HERE/"SAFE-ORDER.json") == "a636c16290f3778a520b5e378b285fdd46b95aeb7e5eecb108979f6d61dfbc3c"
assert sha(HERE/"WINDOWS-RUNTIME.json") == "6dbf79e6e6a47bdc29033fcb993afa97b50f2e69c92984692ec6ce8e6fc89959"
assert sha(HERE/"holder.ps1") == "8d0c1c42c9af8e86408ec44cd00f27a5d0418cedd99bde8566e14ce684344cdc"
assert run["parent_git_revision"] == PARENT
assert run["holder_identity"] == "E008E" and run["holder_consumed"] is True
assert run["media_capture_init_pass"] is True
assert run["record_start_status"] == "Success" and run["record_stop_pass"] is True
assert run["valid_4k_handles"] == 91
assert run["protected_golden_restored"] is True
assert run["linux_native_rear_isp_runtime_performed"] is False
assert not run["pixel_bytes_read"] and not run["pixel_data_exported"] and not run["dma_contents_exported"]
assert safe["event_count"] == len(safe["events"]) == 54
ev = safe["events"]
assert ev[0] == "E008E EV BATCH 0 COUNT=4"
assert ev[1:11] == ["E008E EV BUS_CONFIG"] * 10
assert ev[11:20] == ["E008E EV BUS_SET"] * 9
assert ev[20:30] == [f"E008E EV ADDR {i:x}" for i in range(10)]
assert ev[30:33] == ["E008E EV BATCH 1 COUNT=6", "E008E EV CSID_START_CALL", "E008E EV ISP_START_DONE"]
assert ev[-9:] == ["E008E EV BUS_SET"] * 9
assert safe["contains_pixel_data"] is False and safe["contains_dma_contents"] is False
assert res["status"] == "PASS" and res["protected_golden_restored"] is True
print("E008e VERIFY PASS")
