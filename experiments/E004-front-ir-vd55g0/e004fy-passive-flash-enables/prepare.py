#!/usr/bin/env python3
"""E004fy single-use passive flash module/channel/trigger snapshot preflight."""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E = HERE / "evidence"
MAPPING = ROOT / "experiments/E004-front-ir-vd55g0/e004fw-golden-pmic-flash-location-readonly/observe_flash_location.py"
DRIVER = ROOT / "experiments/E004-front-ir-vd55g0/e004fk-native-flash-disable-ordering/build/source/leds-qcom-flash.c"
MAP_SHA = "af9c6dd68a467e45d7fc5fdd724fadecd83e267a2991dcc5d94a761044f06e40"
DRIVER_SHA = "cd1f98411545cdb4b679bb21c4c29076a88866517488d5b618c31485caa04727"
PREVIOUS_BOOT = "c4172e14-03ca-4e99-adbb-ddfb102cbe27"
ADDRS = (0xee46,0xee4a,0xee4b,0xee4c,0xee4d,0xee4e)
REGMAP = "/sys/kernel/debug/regmap/0-01/"
OFFSETS = tuple(a*9 for a in ADDRS)

def require(ok, msg):
    if not ok:
        raise ValueError("E004FY_FAIL_CLOSED " + msg)

def run(*args, timeout=28):
    r = subprocess.run(args, text=True, capture_output=True, check=False, timeout=timeout)
    require(r.returncode == 0, "command error: "+str(args[0]))
    return r.stdout.strip()

def inspect_access(content):
    lines = content.splitlines()
    require(len(lines)==65536, "regmap access length drift")
    for a in range(ADDRS[-1]+1):
        tokens = lines[a].split()
        require(len(tokens)==5 and tokens[0]==f"{a:04x}:",
                "sparse or reordered regmap access")
        require(tokens[1]=="y" and tokens[4]=="n",
                "pretarget or target unreadable/precious")
    return True

def check():
    require(not (E/"CONSUMED.json").exists() and not (E/"RESULT.json").exists(),
            "this experimental identity was consumed")
    for p, sha in ((MAPPING, MAP_SHA),(DRIVER,DRIVER_SHA)):
        require(p.is_file() and sha256(p.read_bytes()).hexdigest()==sha,
                "mapping or driver source drift")
    driver = DRIVER.read_text()
    expected = (
        "[REG_MODULE_EN]\t\t= REG_FIELD(0x46, 7, 7)",
        "[REG_CHAN_STROBE]\t= REG_FIELD_ID(0x4a, 0, 6, 4, 1)",
        "[REG_CHAN_EN]\t\t= REG_FIELD(0x4e, 0, 3)",
    )
    require(all(anchor in driver for anchor in expected),
            "flash enable/trigger register mapping drift")
    require(run("git","rev-parse","HEAD",timeout=8) ==
            run("git","ls-remote","origin","refs/heads/experiment/e004-front-ir-vd55g0",
                timeout=15).split()[0], "local HEAD and remote branch differ")
    run("./tools/camera-overlap-guard.sh","--require-clean-tracked",
        "--require-golden","--require-no-camera-process",timeout=30)
    boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    require(boot == PREVIOUS_BOOT, "Golden boot changed since E004fx mapping")
    spec = importlib.util.spec_from_file_location("e004fw_map", MAPPING)
    require(spec and spec.loader, "no mapping helper")
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    mapping = helper.assess(helper.snapshot_live())
    require(mapping["flash_pmic_sid"]==1 and
            mapping["flash_dt_status"]=="disabled" and
            mapping["register_values_read"] is False,
            "PMIC location/disabled status changed")
    access = run("sudo","-n","cat",REGMAP+"access",timeout=25)
    inspect_access(access)
    mode = run("sudo","-n","stat","-c","%a",REGMAP+"registers",timeout=8)
    require(mode=="400","registers view is not read-only")
    return {
        "experiment":"E004fy",
        "status":"PREPARED_UNCONSUMED",
        "boot":boot,
        "spmi":"0-01",
        "flash_dt_status":"disabled",
        "addresses":[f"0x{a:04x}" for a in ADDRS],
        "offsets":list(OFFSETS),
        "total_max_register_bytes":len(ADDRS)*9,
        "access_metadata_sha256":sha256((access+"\n").encode()).hexdigest(),
        "no_register_values_read_in_preflight":True,
        "no_emitter_or_camera_activation":True,
    }

if __name__ == "__main__":
    E.mkdir(exist_ok=True)
    prepared=check()
    (E/"PREPARED.json").write_text(json.dumps(prepared,indent=2)+"\n")
    print("E004FY_PREPARED=PASS TARGET_SPMI=0-01 SIX_READONLY_BYTES")
    print("EMITTER=OFF HARDWARE_REGISTER_READS=ZERO")
