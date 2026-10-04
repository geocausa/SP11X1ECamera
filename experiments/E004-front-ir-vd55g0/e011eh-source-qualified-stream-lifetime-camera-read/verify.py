#!/usr/bin/env python3
from pathlib import Path
import hashlib, json
HERE=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(n): return json.loads((HERE/n).read_text())
def check():
    s=load("SOURCE-SAFE.json"); r=load("RESULT.json"); f=load("FRONTIER-SAFE.json"); n=load("NEXT-SOURCE.json")
    assert s["experiment"]=="E011EH"
    assert s["status"]=="PASS_SOURCE_QUALIFIED_STREAM_LIFETIME_CAMERA_READ"
    assert r["status"]==s["status"]
    assert r["source_safe_sha256"]==sha(HERE/"SOURCE-SAFE.json")
    assert r["source_script_sha256"]==sha(HERE/"source-private.py")
    assert s["case_count"]==8
    assert sum(x["negative_contract_rejections"] for x in s["cases"])==40
    assert s["startup_stream_state_to_camera_read_join_qualified"] is True
    assert s["camera_stream_pointer_read_qualified"] is True
    ev=s["source_lifetime_evidence"]
    assert ev["constructor_RVA"]=="0xcb3260"
    assert ev["destructor_RVA"]=="0xcb33a0"
    assert ev["camera_read_RVA"]=="0xcc6120"
    assert ev["stream_pointer_writer_sites"]==["0xcb32b0","0xcb32d8","0xcb3400"]
    assert f["camera_frontier"]["source_RVA"]=="0xcc6130"
    assert f["camera_frontier"]["dependency_RVA"]=="0x16a2a50"
    assert f["camera_frontier"]["startup_stream_to_camera_join_qualified"] is True
    assert n["experiment"]=="E011EI"
    assert n["native_rear_runtime_allowed"] is False
    return {"status":"PASS_E011EH_PORTABLE_REVIEW","cases":8,"negative_contract_rejections":40,"next":"E011EI"}
if __name__=="__main__":
    print(json.dumps(check(), sort_keys=True))
