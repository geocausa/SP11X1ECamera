#!/usr/bin/env python3
import json
from pathlib import Path

D=Path(__file__).resolve().parent
runner=(D/"camss-vfe-e008k-rear-runner.inc").read_text()
rt=(D/"camss-e008k-rear-rtcdm-bridge.inc").read_text()
cs=(D/"camss-csid-e008k-rear-bridge.inc").read_text()
res=json.loads((D/"RESULT.json").read_text())

for x in [
 "e008k_rear_run_unreachable",
 "e008j_rear_alloc_pair_no_mmio",
 "e008j_rear_bind_pair_no_mmio",
 "e008k_rear_submit_packet(camss, &req->packet[0])",
 "e008j_rear_prepare_slot0_after_packet0",
 "e008h_rear_enable_slot0",
 "e008k_rear_submit_packet(camss, &req->packet[1])",
 "csid680_e008k_rear_enable",
 "e008k_rear_subdev_stream(&csiphy->subdev, true)",
 "e008k_rear_subdev_stream(req->sensor, true)",
 "e008h_rear_epoch0_retarget_slot1",
 "e008k_rear_submit_packet(camss, &req->packet[2])",
 "e008k_rear_submit_packet(camss, &req->packet[3])",
 "e008k_rear_collect_done",
 "csid680_e008a_rear_quiesce",
 "vfe680_e008a_rear_bus_stop",
 "e007z_rear_release_ledger",
 "E005Y_VFE1_OWNER_REAR",
 "return -EOPNOTSUPP",
]:
    assert x in runner, x

order=[
 "e008k_rear_submit_packet(camss, &req->packet[0])",
 "e008j_rear_prepare_slot0_after_packet0",
 "e008h_rear_enable_slot0",
 "e008k_rear_submit_packet(camss, &req->packet[1])",
 "csid680_e008k_rear_enable",
 "e008k_rear_subdev_stream(&csiphy->subdev, true)",
 "e008k_rear_subdev_stream(req->sensor, true)",
 "e008h_rear_epoch0_retarget_slot1",
 "e008k_rear_submit_packet(camss, &req->packet[2])",
 "e008k_rear_submit_packet(camss, &req->packet[3])",
]
pos=[runner.index(x) for x in order]
assert pos == sorted(pos), pos
assert "camss_rtcdm1_windows_fifo0_commit" in rt
assert "csid_e004ns_rear_ipp_enable" in cs
assert "csid_e004ns_rear_ipp_prepare" not in cs
assert res["complete_unreachable_runner"]
assert not res["runtime_call_site_present"]
assert not res["runtime_actions_performed"]
assert not res["dma_free_after_hardware_exposure"]
print("E008k VERIFY PASS")
