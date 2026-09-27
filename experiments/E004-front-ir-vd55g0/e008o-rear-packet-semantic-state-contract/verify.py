#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
subprocess.run(["python3",str(D/"audit.py")],check=True)
s=(D/"camss-vfe-e008o-rear-semantic-state.inc").read_text()
r=json.loads((D/"RESULT.json").read_text())
a=json.loads((D/"SAFE-AUDIT.json").read_text())
for needle in [
 "struct e008o_rear_packet_semantics",
 "struct e008o_rear_semantic_set",
 "s->regs.scalar.startup_phase != packet",
 "e007v_rear_validate_request(&s->dmi, s->request_id)",
 "e007y_rear_materialize(&s->regs, &s->dmi",
 "commands->hardware_exposed",
 "return -EOPNOTSUPP;"
]:
 assert needle in s, needle
assert r["e008n_shared_register_state_detected"]
assert r["e008n_shared_dmi_state_detected"]
assert r["packet_isolated_register_states"] == 4
assert r["packet_isolated_dmi_states"] == 4
assert not r["native_rear_runtime_authorized"]
assert a["e006z_startup_bank_is_packet_phase_dependent"]
print("E008o VERIFY PASS")
