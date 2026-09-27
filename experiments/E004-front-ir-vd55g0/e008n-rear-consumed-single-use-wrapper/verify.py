#!/usr/bin/env python3
import json
from pathlib import Path

D=Path(__file__).resolve().parent
s=(D/"camss-vfe-e008n-rear-single-use.inc").read_text()
r=json.loads((D/"RESULT.json").read_text())

for x in [
 "atomic_cmpxchg(&e008n_rear_consumed, 0, 1)",
 "e008l_rear_command_alloc",
 "e008k_rear_validate_route",
 "e008k_rear_materialize_all",
 "e008l_rear_command_mark_submitted",
 "e008k_rear_run_unreachable",
 "result->transaction.rtcdm_stopped",
 "result->transaction.owner_released",
 "result->transaction.both_frames_complete",
 "e008l_rear_command_release(vfe, commands, true)",
 "result->reboot_required = true",
 "return -EOPNOTSUPP",
]:
    assert x in s, x

order=[
 "e008l_rear_command_alloc",
 "e008k_rear_validate_route",
 "e008k_rear_materialize_all",
 "e008l_rear_command_mark_submitted",
 "result->reboot_required = true",
 "e008k_rear_run_unreachable",
 "e008l_rear_command_release(vfe, commands, true)",
]
p=[s.index(x) for x in order]
assert p==sorted(p),p
assert "module_param" not in s
assert r["classification"] == "BUILD_ONLY_PASS"
assert r["build"]["module_bytes"] == 14682720
assert r["build"]["module_sha256"] == "1b102acba82ce06acd6cacd347a9c4f36c14cafc3ef1f03ded9da322cc800cd9"
assert r["build"]["w1_warnings_or_errors"] == 0
assert r["consumes_identity_on_first_call"]
assert r["output_dma_reboot_pinned"]
assert r["reboot_required_after_post_preflight_return"]
assert not r["runtime_call_site_present"]
assert not r["runtime_actions_performed"]
print("E008n VERIFY PASS")
