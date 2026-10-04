#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(name):
    return json.loads((HERE / name).read_text())

def check():
    source = load("SOURCE-SAFE.json")
    result = load("RESULT.json")
    next_source = load("NEXT-SOURCE.json")
    frontier = load("FRONTIER-SAFE.json")

    assert source["experiment"] == "E011EG"
    assert source["status"] == "PASS_SOURCE_QUALIFIED_CRT_STARTUP_ORDER"
    assert result["status"] == source["status"]
    assert result["source_safe_sha256"] == sha(HERE / "SOURCE-SAFE.json")
    assert result["source_script_sha256"] == sha(HERE / "source-private.py")

    assert source["process_attach_source_chain"] == [
        "0xca2d70", "0xca2bc0", "0xca2970", "0xca29d8"
    ]
    assert source["preconstructor_precedes_constructor_iterator"] is True
    assert source["subsystem_table"]["pair_stride_bytes"] == 16
    assert source["subsystem_table"]["pair_count"] == 16
    assert source["subsystem_table"]["lowIO_owner_pair_index"] == 8
    assert source["subsystem_table"]["lowIO_owner_init_RVA"] == "0xcb5dd0"
    assert source["lowIO_startup_owner"]["producer_RVA"] == "0xcc06f0"
    assert source["lowIO_startup_owner"]["producer_success_return_W0"] == 0
    assert source["lowIO_startup_owner"]["producer_required_for_owner_success"] is True
    assert source["constructor_table"]["entries_RVA"] == [
        "0x0", "0xcb3260", "0xcc2580", "0xcfbdb0", "0xcfe2c0"
    ]
    assert source["constructor_table"]["first_nonnull_RVA"] == "0xcb3260"
    assert source["ordering_theorem"]["CC06F0_success_precedes_CB3260"] is True
    assert source["ordering_theorem"]["full_native_CRT_startup_success_qualified"] is False
    assert source["state_handoff"]["startup_CC06F0_to_CB3260_handoff_qualified"] is True
    assert source["state_handoff"]["E011EF_CC08E8_state_joined"] is False
    assert source["state_handoff"]["camera_state_joined"] is False

    cm = ROOT / "experiments/E004-front-ir-vd55g0/e011cm-crt-object-producers"
    assert source["inherited_E011CM"]["result_sha256"] == sha(cm / "RESULT.json")
    assert source["inherited_E011CM"]["bootstrap_sha256"] == sha(cm / "BOOTSTRAP-SAFE.json")
    assert source["inherited_E011CM"]["source_sha256"] == sha(cm / "source-private.py")

    assert result["inherited_E011CM_rerun_exit_code"] == 0
    assert result["inherited_E011CM_rerun_stderr_bytes"] == 0
    assert result["camera_state_joined"] is False
    assert frontier["camera_frontier"]["source_RVA"] == "0xcc6120"
    assert frontier["camera_frontier"]["startup_stream_to_camera_join_qualified"] is False
    assert next_source["experiment"] == "E011EH"
    assert next_source["native_rear_runtime_allowed"] is False
    assert len(source["function_pins"]) == 9
    for pin in source["function_pins"].values():
        assert pin["bytes"] > 0
        assert len(pin["sha256"]) == 64

    return {
        "status": "PASS_E011EG_PORTABLE_REVIEW",
        "function_pins": len(source["function_pins"]),
        "next": "E011EH"
    }

if __name__ == "__main__":
    print(json.dumps(check(), sort_keys=True))
