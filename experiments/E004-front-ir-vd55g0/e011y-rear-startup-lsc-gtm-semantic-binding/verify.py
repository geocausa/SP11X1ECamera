#!/usr/bin/env python3
import json
from pathlib import Path
D=Path(__file__).resolve().parent
r=json.loads((D/"RESULT.json").read_text())
s=json.loads((D/"LIVE-VALIDATION-SAFE.json").read_text())
assert r["windows_startup_adaptive_schedule_closed"]
assert not r["clean_startup_lsc_replay_closed"]
assert not r["clean_startup_gtm_replay_closed"]
assert not r["native_rear_hardware_isp_runtime_authorized"]
assert r["lsc_startup"]["phase_dmi_presence"] == [True,True,False,False]
assert r["lsc_startup"]["distinct_semantic_states_required"] == 2
assert r["gtm_startup"]["phase_state_schedule"] == [0,1,1,1]
assert len(set(r["gtm_startup"]["phase_payload_sha256"])) == 1
assert s["lsc"]["first_tintless_callback_request"] == 4
assert all(x["pass"] for x in s["live_runs"])
assert not s["raw_private_artifacts_committed"]
print("E011Y_WINDOWS_STARTUP_ADAPTIVE_BINDING_PASS")
print("LSC states=2 phases=[present,present,absent,absent]")
print("GTM states=2 phase schedule=[0,1,1,1] wire_hash_count=1")
