#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(n): return json.loads((HERE/n).read_text())
def check():
    s=load("SOURCE-SAFE.json"); w=load("WINDOWS-SAFE.json"); r=load("RESULT.json")
    f=load("FRONTIER-SAFE.json"); n=load("NEXT-SOURCE.json")
    assert s["experiment"]=="E011EJ" and s["case_count"]==4
    assert s["slot3_publication_qualified"] and s["complete_CC6108_return_qualified"]
    assert s["source_runtime_CRT_image_flag"]=="0x80000000"
    assert not s["allocation_failure_path_qualified"] and not s["alternate_runtime_flag_paths_qualified"]
    assert s["exact_key_store_chunks"]==16 and s["rejected_altered_contracts"]==20
    assert w["user_mode"]["native_stream_count"]==512
    assert w["user_mode"]["native_runtime_CRT_image_flag"]=="0x80000001"
    assert w["user_mode"]["prestart_slot3_nonnull"] and w["user_mode"]["existing_slot_path_observed"]
    assert not w["user_mode"]["lazy_slot3_allocation_observed"]
    assert w["user_mode"]["complete_CC6108_return_observed"]
    assert w["user_mode"]["front_StartAsync_success"]
    assert not w["user_mode"]["frame_handle_success_this_run"]
    assert not w["native_rear_runtime_allowed"]
    assert r["source_script_sha256"]==sha(HERE/"source-private.py")
    assert r["source_safe_sha256"]==sha(HERE/"SOURCE-SAFE.json")
    assert r["windows_safe_sha256"]==sha(HERE/"WINDOWS-SAFE.json")
    assert f["camera_frontier"]["source_RVA"]=="0xcc60a0"
    assert n["experiment"]=="E011EK" and not n["native_rear_runtime_allowed"]
    return {"status":"PASS_E011EJ_PORTABLE_REVIEW","source_cases":4,"native_flag":"0x80000001","next":"E011EK"}
if __name__=="__main__": print(json.dumps(check(),sort_keys=True))
