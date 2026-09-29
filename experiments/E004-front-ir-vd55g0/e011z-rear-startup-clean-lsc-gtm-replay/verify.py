#!/usr/bin/env python3
import json
from pathlib import Path
D=Path(__file__).resolve().parent
r=json.loads((D/"RESULT.json").read_text())
s=json.loads((D/"REPLAY-SAFE.json").read_text())
b=json.loads((D/"BINDING-COMPILE-SAFE.json").read_text())
assert r["lsc"]["clean_startup_lsc_replay_closed"]
assert r["gtm"]["clean_startup_gtm_replay_closed"]
assert r["lsc"]["phase_dmi_presence"] == [True,True,False,False]
assert r["lsc"]["phase_state_schedule"] == [0,1,1,1]
assert r["gtm"]["startup_payload_sha256"] == "b71d4b3eadec95941586227f171e771ae5dc1c70fd48fa5ebf599dcf8fd77d81"
assert s["status"] == "PASS"
assert s["raw_private_inputs_used"] is False
assert s["captured_windows_dmi_used_as_input"] is False
assert r["e008o_binding"]["request_ids_derived_from_packet_phase"] is False
assert r["e008o_binding"]["structural_compile_check_pass"]
assert r["e008o_binding"]["distinct_request_ids_tested"] == [4,5,6,7]
assert b["status"] == "PASS" and b["distinct_materializer_request_ids_tested"] == [4,5,6,7]
assert b["runtime_actions_performed"] is False
assert not r["native_rear_hardware_isp_runtime_authorized"]
print("E011Z_REAR_STARTUP_CLEAN_ADAPTIVE_PASS")
print("LSC=phase0+phase1 exact; GTM=static-seed exact; E008o request IDs caller-owned")
