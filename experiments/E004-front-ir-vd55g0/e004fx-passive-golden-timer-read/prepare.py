#!/usr/bin/env python3
"""Metadata-only preflight for ONE bounded, read-only idle PMIC timer snapshot."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OBS = ROOT / "experiments/E004-front-ir-vd55g0/e004fw-golden-pmic-flash-location-readonly/observe_flash_location.py"
REGMAP = Path("/sys/kernel/debug/regmap/0-01")
GOLDEN_BOOT = "c4172e14-03ca-4e99-adbb-ddfb102cbe27"
OBS_SHA = "af9c6dd68a467e45d7fc5fdd724fadecd83e267a2991dcc5d94a761044f06e40"
DEBUGFS_SHA = "6a3aa0eae0efa081b6612a51e2ba462607b41cdd3af92621d68a6541fcffc998"
PMIC_SOURCE_SHA = "cba250364921bfff3e8cfe10372906631cf2cba70365b2d75eabb8822084b9bd"
DEBUGFS_SRC = Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src/drivers/base/regmap/regmap-debugfs.c")
PMIC_SRC = Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src/drivers/mfd/qcom-spmi-pmic.c")
ADDRS = tuple(range(0xee3e, 0xee42))
LINE_BYTES = 9

def need(yes: bool, reason: str) -> None:
    if not yes:
        raise ValueError("E004FX_PASSIVE_PREFLIGHT_FAIL_CLOSED " + reason)

def command(*argv: str, timeout: int = 20) -> str:
    p = subprocess.run(list(argv), capture_output=True, text=True,
                       check=False, timeout=timeout)
    need(p.returncode == 0, "preflight command failed: " + argv[0])
    return p.stdout.strip()

def access_offset(access: str) -> int:
    rows = access.splitlines()
    need(len(rows) == 65536, "SPMI access metadata count differs")
    for address, line in enumerate(rows[:ADDRS[-1]+1]):
        fields = line.split()
        need(len(fields) == 5 and fields[0] == f"{address:04x}:",
             "access metadata sparse, reordered or malformatted")
        need(fields[1] == "y" and fields[4] == "n",
             "register unreadable or precious before target")
    return ADDRS[0] * LINE_BYTES

def validate_kernel_metadata() -> None:
    for path, digest in ((OBS, OBS_SHA), (DEBUGFS_SRC, DEBUGFS_SHA),
                         (PMIC_SRC, PMIC_SOURCE_SHA)):
        need(path.is_file() and sha256(path.read_bytes()).hexdigest() == digest,
             "inspected source/observer hash drift")
    pmic_source = PMIC_SRC.read_text()
    need(".reg_bits\t= 16," in pmic_source and
         ".val_bits\t= 8," in pmic_source and
         ".max_register\t= 0xffff," in pmic_source,
         "SPMI regmap register/address formatting changed")
    debugfs = DEBUGFS_SRC.read_text()
    for marker in ("regmap_calc_tot_len(map, buf, count)",
                   "regmap_debugfs_get_dump_start(map, from, *ppos, &p)",
                   "ret = regmap_read(map, i, &val);",
                   ".llseek = default_llseek",
                   "map->debugfs_reg_len +", "map->debugfs_val_len + 3"):
        need(marker in debugfs, "inspected debugfs read/offset model changed")

def golden_preflight() -> dict:
    need(not (HERE/"evidence/CONSUMED.json").exists(), "one-shot already consumed")
    need(not (HERE/"evidence/RESULT.json").exists(), "snapshot already exists")
    need(command("git", "rev-parse", "HEAD", timeout=8) ==
         command("git", "ls-remote", "origin", "refs/heads/experiment/e004-front-ir-vd55g0",
                 timeout=15).split()[0], "repo and origin differ")
    command("./tools/camera-overlap-guard.sh", "--require-clean-tracked",
            "--require-golden", "--require-no-camera-process", timeout=25)
    boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    need(boot == GOLDEN_BOOT, "SP11 rebooted since E004fw mapping")
    spec = importlib.util.spec_from_file_location("sp11_e004fw_flash_map", OBS)
    need(spec is not None and spec.loader is not None, "cannot load previous mapping observer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    mapping = module.assess(module.snapshot_live())
    need(mapping["flash_pmic_sid"] == 1 and mapping["flash_dt_status"] == "disabled"
         and mapping["register_values_read"] is False, "Golden flash mapping changed")
    validate_kernel_metadata()
    need(command("sudo", "-n", "test", "-r", str(REGMAP/"registers")) == "",
         "registers not read-only-accessible")  # sudo test has no stdout
    access = command("sudo", "-n", "cat", str(REGMAP/"access"), timeout=25)
    offset = access_offset(access)
    need(offset == 548910, "unexpected debugfs byte offset")
    return {
        "experiment": "E004fx",
        "status": "PREPARED_SINGLE_PASSIVE_READ_NOT_CONSUMED",
        "golden_boot": boot,
        "pmic_spmi": "0-01",
        "target_addresses": [f"0x{x:04x}" for x in ADDRS],
        "access_metadata_sha256": sha256((access+"\n").encode()).hexdigest(),
        "target_seek_bytes": offset,
        "target_read_bytes": 4*LINE_BYTES,
        "whole_regmap_read": False,
        "only_four_regmap_values_requested": True,
        "flash_controller_status": "disabled",
        "pmic_registers_read_during_preflight": False,
        "hardware_emitter_enabled": False,
        "physical_timeout_or_ir_eye_safety_verified": False,
    }

def main() -> None:
    result = golden_preflight()
    e = HERE/"evidence"
    e.mkdir(exist_ok=True)
    (e/"PREPARED.json").write_text(json.dumps(result, indent=2)+"\n")
    print("E004FX_PREPARED=PASS GOLDEN=PASS FOUR_TIMER_REGISTERS_ONLY")
    print("TARGET_PMIC=0-01 SNAPSHOT_NOT_YET_CONSUMED REGISTER_IO=NONE")

if __name__ == "__main__":
    main()
