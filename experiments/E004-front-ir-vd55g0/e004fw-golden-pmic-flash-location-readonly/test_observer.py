#!/usr/bin/env python3
"""Pure fixture-based fail-closed checks; never opens SPMI registers."""
from copy import deepcopy
from observe_flash_location import assess

baseline = {
    "flash_node_count": 1,
    "flash_node": "/sys/firmware/devicetree/base/soc@0/arbiter@c400000/spmi@c42d000/pmic@1/led-controller@ee00",
    "flash_compatible": ["qcom,pm8550-flash-led", "qcom,spmi-flash-led"],
    "flash_reg": 0xee00,
    "flash_status": "disabled",
    "pmic_compatible": ["qcom,pm8550", "qcom,spmi-pmic"],
    "pmic_reg_sid": 1,
    "spmi_of_node_matches": True,
    "spmi_driver": "pmic-spmi",
    "regmap_name": "pmic-spmi",
    "regmap_range": "0-ffff",
    "pcm8380_sids": [3,4,5,6],
    "camera_nodes_absent": True,
}
result = assess(baseline)
assert result["status"] == "PASS_READ_ONLY_LIVE_GOLDEN_DT_AND_SPMI_LOCATION"
assert result["flash_pmic_sid"] == 1 and result["flash_dt_base"] == "0xee00"
assert not result["register_values_read"] and not result["authorization_to_arm_emitter"]
changes = [
    ("flash_node_count", 2, "not unique"),
    ("flash_node", baseline["flash_node"].replace("pmic@1", "pmic@3"), "location"),
    ("flash_compatible", ["qcom,spmi-flash-led"], "descriptor"),
    ("flash_reg", 0xed00, "register base"),
    ("flash_status", "okay", "enabled"),
    ("pmic_compatible", ["qcom,pmc8380", "qcom,spmi-pmic"], "type"),
    ("pmic_reg_sid", 3, "SID"),
    ("spmi_of_node_matches", False, "differs from DT node"),
    ("spmi_driver", "unknown", "binding"),
    ("regmap_name", "unknown", "metadata"),
    ("pcm8380_sids", [1,3,4,5,6], "hierarchy"),
    ("camera_nodes_absent", False, "camera active"),
]
for key, value, expected in changes:
    wrong = deepcopy(baseline)
    wrong[key] = value
    try:
        assess(wrong)
    except ValueError as exc:
        assert expected in str(exc), (key, str(exc))
    else:
        raise AssertionError("unexpected acceptance of " + key)
print(f"E004FW_OFFLINE_NEGATIVE=PASS CASES={len(changes)} NO_PMIC_REGISTER_IO=YES")
