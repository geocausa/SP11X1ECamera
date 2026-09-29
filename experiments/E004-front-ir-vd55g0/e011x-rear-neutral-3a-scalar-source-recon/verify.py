#!/usr/bin/env python3
import json
from pathlib import Path
D=Path(__file__).resolve().parent
r=json.loads((D/"RESULT.json").read_text())
s=json.loads((D/"LIVE-VALIDATION-SAFE.json").read_text())
assert r["neutral_3a_gate_closed"] is True
assert r["producer_provenance_closed"] is True
assert r["request_phase_binding_closed"] is True
assert r["native_rear_hardware_isp_runtime_authorized"] is False
assert r["lsc_gtm_gate_open"] is True
assert s["request_ids"]=={"first":1,"last":8,"count":8,"sequential":True}
assert s["hit_counts"]=={"trigger":8,"demux":8,"pdpc":8,"wb":8}
assert s["startup_scalar_coverage"]==[8,8,8,2]
assert s["startup_scalar_exact_matches"]==[8,8,8,2]
assert s["startup_scalar_instances_present"]==26
assert s["startup_scalar_instances_exact"]==26
assert s["phase3_scalar_registers"]==["0x3B70","0x3B74"]
assert s["phase3_held_preceding_demux_state_exact"] is True
assert s["holder"]["start_status"]=="Success"
assert s["holder"]["stop_pass"] is True
assert s["holder"]["valid_4k_handles"]==1807
assert not s["raw_register_values_emitted"]
assert not s["raw_packet_bytes_emitted"]
assert not s["raw_process_addresses_emitted"]
print("E011X_LIVE_VALIDATION_SAFE_PASS")
print("startup_scalar_instances=26 exact=26 raw_values_emitted=false")
