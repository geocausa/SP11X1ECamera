#!/usr/bin/env python3
from pathlib import Path
import json

D = Path(__file__).resolve().parent
src = (D / "camss-e007c-period-cfg.inc").read_text()
contract = json.load(open(
    D.parents[1] /
    "E003-front-imx681-cphy/e003h-windows-parity-transport-static/rtcdm-period-cfg-contract-oracle.json"
))

assert contract["accepted"] is True
c = contract["contract"]
assert c["register"] == "0x8c period_cfg"
assert c["logical_values_per_start"] == 2
assert c["packet_mapping"] == {
    "0": "packet0", "1": "packets123", "2": "packets123", "3": "packets123"
}
assert c["packets_1_2_3_equal_in_every_observed_start"] is True
assert c["qccamisp_0x26838_mutates_period_cfg"] is False
assert contract["linux_consequence"]["captured_windows_period_values_must_not_be_embedded"] is True

for token in (
    "#define E007C_PERIOD_CFG_REG 0x008c",
    "#define E007C_PERIOD_CFG_VALUES 2",
    "#define E007C_STARTUP_PACKETS 4",
    "index = packet ? 1 : 0;",
    "e007c_rear_fill_startup_packet",
    "e006m_rear_fill_startup_scalar",
    "e007c_rear_startup_packet_recipe",
):
    assert token in src

for start in contract["observed_starts"].values():
    for raw in start.values():
        assert raw.lower() not in src.lower()

print("E007C_VERIFY_PASS period_cfg=packet-aware logical_values=2 mapping=0,1,1,1")
print("captured_period_values_embedded=false upstream_derivation=open")
