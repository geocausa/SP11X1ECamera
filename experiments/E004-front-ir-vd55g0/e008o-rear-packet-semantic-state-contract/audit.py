#!/usr/bin/env python3
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

k=(ROOT/"experiments/E004-front-ir-vd55g0/e008k-rear-complete-unreachable-runner/camss-vfe-e008k-rear-runner.inc").read_text()
n=(ROOT/"experiments/E004-front-ir-vd55g0/e008n-rear-consumed-single-use-wrapper/camss-vfe-e008n-rear-single-use.inc").read_text()
z=(ROOT/"experiments/E004-front-ir-vd55g0/e006z-rear-clean-scalar-bank-providers/camss-e006z-clean-scalar-bank.inc").read_text()
i=(ROOT/"experiments/E004-front-ir-vd55g0/e007i-rear-lsc-dmi-handoff/camss-e007i-rear-lsc-handoff.inc").read_text()
q=(ROOT/"experiments/E004-front-ir-vd55g0/e007q-rear-gtm-clean-handoff/camss-e007q-rear-gtm-handoff.inc").read_text()

assert "e007y_rear_materialize(req->regs, req->dmi_state" in k
assert "dst->regs = src->regs;" in n and "dst->dmi_state = src->dmi_state;" in n
assert "*value = s->startup_phase & 1;" in z
assert "s->lsc.request_id != expected_request_id" in i
assert "s->gtm.request_id != expected_request_id" in q

safe={
 "schema":"E008O-static-audit-v1",
 "e008k_four_packet_loop_uses_one_register_pointer":True,
 "e008k_four_packet_loop_uses_one_dmi_pointer":True,
 "e008n_forwards_shared_register_pointer":True,
 "e008n_forwards_shared_dmi_pointer":True,
 "e006z_startup_bank_is_packet_phase_dependent":True,
 "e007i_lsc_is_request_tagged":True,
 "e007q_gtm_is_request_tagged":True,
 "runtime_actions_performed":False
}
(HERE/"SAFE-AUDIT.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
print("E008O_STATIC_AUDIT_PASS")
