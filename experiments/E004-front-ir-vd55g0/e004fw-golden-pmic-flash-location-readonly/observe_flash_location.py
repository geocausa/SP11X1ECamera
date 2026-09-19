#!/usr/bin/env python3
"""Observe ONLY live Golden device-tree/sysfs metadata; NO SPMI register I/O."""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json
import subprocess

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TREE = Path("/sys/firmware/devicetree/base")
SPMI = Path("/sys/bus/spmi/devices")
REGMAP = Path("/sys/kernel/debug/regmap")

def need(value: bool, message: str) -> None:
    if not value:
        raise ValueError("E004FW_FAIL_CLOSED " + message)

def dt_text(path: Path) -> list[str]:
    return [part.decode("utf-8") for part in path.read_bytes().split(b"\x00") if part]

def assess(snapshot: dict) -> dict:
    need(snapshot["flash_node_count"] == 1, "flash controller DT node not unique")
    need(snapshot["flash_node"].endswith("/spmi@c42d000/pmic@1/led-controller@ee00"),
         "unexpected board PMIC flash location")
    need(snapshot["flash_compatible"] == ["qcom,pm8550-flash-led", "qcom,spmi-flash-led"],
         "unexpected flash peripheral descriptor")
    need(snapshot["flash_reg"] == 0xee00, "flash peripheral register base mismatch")
    need(snapshot["flash_status"] == "disabled", "flash peripheral enabled on Golden")
    need(snapshot["pmic_compatible"] == ["qcom,pm8550", "qcom,spmi-pmic"],
         "unexpected PMIC type")
    need(snapshot["pmic_reg_sid"] == 1, "unexpected SPMI SID")
    need(snapshot["spmi_of_node_matches"], "Linux bound SPMI PMIC differs from DT node")
    need(snapshot["spmi_driver"] == "pmic-spmi", "unexpected PMIC driver binding")
    need(snapshot["regmap_name"] == "pmic-spmi"
         and snapshot["regmap_range"] == "0-ffff", "unexpected regmap metadata")
    need(snapshot["pcm8380_sids"] == [3,4,5,6], "different PMC8380 PMIC hierarchy")
    need(snapshot["camera_nodes_absent"], "camera active or modified in Golden")
    return {
        "experiment": "E004fw",
        "status": "PASS_READ_ONLY_LIVE_GOLDEN_DT_AND_SPMI_LOCATION",
        "spmi_bus": 0,
        "flash_pmic_sid": 1,
        "flash_pmic_type": "qcom,pm8550",
        "flash_dt_base": "0xee00",
        "flash_dt_status": "disabled",
        "flash_timer_relative_offsets": ["0x3e", "0x3f", "0x40", "0x41"],
        "flash_timer_absolute_addresses_in_candidate": ["0xee3e", "0xee3f", "0xee40", "0xee41"],
        "candidate_regmap_metadata": "0-01 pmic-spmi range 0-ffff",
        "other_pmic_pm8380_sids": [3,4,5,6],
        "register_values_read": False,
        "physical_led_wiring_from_pmic_to_sp11_ir_verified": False,
        "actual_timer_initial_state_verified": False,
        "actual_flash_output_enabled": False,
        "authorization_to_arm_emitter": False,
        "next_gate": "A separately reviewed, narrowly targeted passive register observation of the mapped PMIC at 0-01, then independent electrical/optical cutoff and current authority.",
    }

def snapshot_live() -> dict:
    need(TREE.is_dir() and SPMI.is_dir(),
         "necessary read-only sysfs metadata unavailable")
    debugfs = subprocess.run(["sudo", "-n", "test", "-d", str(REGMAP / "0-01")],
                             capture_output=True, check=False, timeout=8)
    need(debugfs.returncode == 0, "read-only PMIC regmap metadata unavailable")
    flash_nodes = list(TREE.glob("soc@0/arbiter@c400000/spmi@c42d000/pmic@*/led-controller@ee00"))
    need(len(flash_nodes) == 1, "Golden flash nodes changed")
    flash = flash_nodes[0]
    pmic = flash.parent
    sid_bytes = (pmic / "reg").read_bytes()
    flash_reg_bytes = (flash / "reg").read_bytes()
    need(len(sid_bytes) == 8 and len(flash_reg_bytes) == 4,
         "unexpected device-tree address cell widths")
    spmi = SPMI / "0-01"
    need(spmi.is_dir() and (spmi / "of_node").exists()
         and (spmi / "driver").exists(), "SPMI PMIC missing/driver unbound")
    actual_node = (spmi / "of_node").resolve()
    need(actual_node == pmic.resolve(), "SPMI sysfs and live DT do not match")
    regmap_name = subprocess.run(
        ["sudo","-n","cat",str(REGMAP / "0-01/name")],
        check=True, capture_output=True, text=True, timeout=8).stdout.strip()
    regmap_range = subprocess.run(
        ["sudo","-n","cat",str(REGMAP / "0-01/range")],
        check=True, capture_output=True, text=True, timeout=8).stdout.strip()
    pmc = sorted(int(d.name.split("@")[-1],16)
                 for d in pmic.parent.glob("pmic@*")
                 if (d/"compatible").is_file()
                 and "qcom,pmc8380" in dt_text(d/"compatible"))
    return {
        "flash_node_count": len(flash_nodes),
        "flash_node": str(flash),
        "flash_compatible": dt_text(flash / "compatible"),
        "flash_reg": int.from_bytes(flash_reg_bytes,"big"),
        "flash_status": dt_text(flash / "status")[0],
        "pmic_compatible": dt_text(pmic / "compatible"),
        "pmic_reg_sid": int.from_bytes(sid_bytes[:4],"big"),
        "spmi_of_node_matches": actual_node == pmic.resolve(),
        "spmi_driver": (spmi/"driver").resolve().name,
        "regmap_name": regmap_name,
        "regmap_range": regmap_range,
        "pcm8380_sids": pmc,
        "camera_nodes_absent": not any(Path("/dev").glob("media*")),
        "live_dt_sha256": {
            "flash_compatible": sha256((flash/"compatible").read_bytes()).hexdigest(),
            "flash_reg": sha256(flash_reg_bytes).hexdigest(),
            "flash_status": sha256((flash/"status").read_bytes()).hexdigest(),
            "pmic_compatible": sha256((pmic/"compatible").read_bytes()).hexdigest(),
            "pmic_reg": sha256(sid_bytes).hexdigest(),
        },
    }

def main() -> None:
    data = snapshot_live()
    result = assess(data)
    result["live_metadata_sha256"] = data["live_dt_sha256"]
    HERE.joinpath("evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004FW_LIVE_GOLDEN_FLASH_LOCATION=PASS PMIC=0-01 BASE=0xee00")
    print("SPMI_REGISTER_READS=ZERO FLASH_CONTROLLER=DISABLED EMITTER=OFF")

if __name__ == "__main__":
    main()
