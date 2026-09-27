#!/usr/bin/env python3
import json
from pathlib import Path

D=Path(__file__).resolve().parent
s=(D/"camss-vfe-e008j-rear-prebus.inc").read_text()
r=json.loads((D/"RESULT.json").read_text())

for x in [
    "e008j_rear_alloc_pair_no_mmio",
    "e008j_rear_bind_pair_no_mmio",
    "e008j_rear_prepare_slot0_after_packet0",
    "e008d_rear_dma_alloc",
    "e008d_rear_build_addresses",
    "e008h_rear_validate_pair_disjoint",
    "e007z_rear_bind",
    "e008d_rear_prepare_addresses_disabled",
    "e008h_rear_fault_ledgers",
    "return -EOPNOTSUPP",
]:
    assert x in s, x

alloc=s[s.index("e008j_rear_alloc_pair_no_mmio"):s.index("e008j_rear_bind_pair_no_mmio")]
bind=s[s.index("e008j_rear_bind_pair_no_mmio"):s.index("e008j_rear_prepare_slot0_after_packet0")]
assert "writel" not in alloc and "readl" not in alloc
assert "writel" not in bind and "readl" not in bind
assert "e008d_rear_prepare_addresses_disabled" not in alloc
assert r["packet0_before_bus_config_preserved"]
assert r["two_slot_allocation_before_mmio"]
assert r["two_slot_binding_before_mmio"]
assert r["slot0_disabled_prepare_after_packet0"]
assert not r["runtime_actions_performed"]
assert not r["runtime_call_site_present"]
print("E008j VERIFY PASS")
