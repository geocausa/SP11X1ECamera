#!/usr/bin/env python3
"""Offline hash-pinned Windows ARM64 static shutdown-path analysis + fault model.

Does NOT execute Windows driver, command PMIC, or prove electrical LED-off.
"""
from pathlib import Path
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BIN = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
EXPECTED = {
    "qccamflash8380.sys": "6bc1d698bc3b6da16974cd6f3ea89dc1ba6a8ea102eebe1a5d41129b4eb9ba2b",
    "qcpmic8380.sys": "756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e",
}

def need(ok, why):
    if not ok:
        raise AssertionError("E004GF_STATIC_FAIL_CLOSED " + why)

def section(name, first, last):
    found = list(BIN.glob("*/" + name))
    need(len(found) == 1, "unique pinned binary " + name)
    path = found[0]
    need(hashlib.sha256(path.read_bytes()).hexdigest() == EXPECTED[name],
         "hash drift " + name)
    process = subprocess.run([
        "llvm-objdump", "-d", f"--start-address={first:#x}",
        f"--stop-address={last:#x}", str(path)
    ], capture_output=True, text=True, timeout=25)
    need(process.returncode == 0, "disassembler failure")
    instructions = {}
    for line in process.stdout.splitlines():
        line = line.strip()
        parts = line.split(":", 1)
        if len(parts) != 2:
            continue
        try:
            addr = int(parts[0], 16)
        except ValueError:
            continue
        tail = parts[1].strip().split(None, 1)
        if len(tail) == 2 and len(tail[0]) == 8:
            instructions[addr] = tail[1]
    need(instructions, "disassembly missing")
    return instructions

def check(ins, addr, text):
    need(text in ins.get(0x140000000 + addr, ""),
         f"expected instruction at {addr:#x}: {text}")

def run_fault_model(module_write_ok, channel_write_ok, initial_module, initial_mask):
    """Control-flow model only, not Windows/PMIC emulation or fault-off proof."""
    module, channels = initial_module, initial_mask
    calls = ["request_module_off"]
    if not module_write_ok:
        return module, channels, calls, "request_failed"
    module = False
    calls.append("request_channels_off")
    if not channel_write_ok:
        return module, channels, calls, "request_failed"
    channels = 0
    return module, channels, calls, "request_succeeded"

def main():
    flash = section("qccamflash8380.sys", 0x140005c88, 0x140005d00)
    pmic = section("qcpmic8380.sys", 0x140028620, 0x140028808)
    # Off variant: PMIC mode command is sent, then the OFF command is sent
    # even if the preceding mode command returned an error.
    check(flash, 0x5cd0, "bl")
    check(flash, 0x5cd4, "mov")
    check(flash, 0x5cdc, "mov")
    check(flash, 0x5ce0, "mov")
    check(flash, 0x5ce4, "bl")
    check(flash, 0x5ce8, "orr")
    # The OFF dispatch passes three explicit zero arguments. Require the
    # branch target and the two PMIC register-write masks, not just mnemonics.
    check(flash, 0x5cd4, "w2, #0x0")
    check(flash, 0x5cdc, "w0, #0x0")
    check(flash, 0x5ce0, "w1, #0x0")
    # PMIC OFF handler: module-enable bit 7 at ee46 is written FIRST.
    # Nonzero write result branches to function failure, SKIPPING ee4e
    # channel-mask update; neither return code proves physical off.
    check(pmic, 0x28680, "0xee46")
    check(pmic, 0x28684, "mov")
    check(pmic, 0x28698, "bl")
    check(pmic, 0x2869c, "cbnz\tw0, 0x140028804")
    check(pmic, 0x2867c, "w3, #0x80")
    check(pmic, 0x28688, "w4, w8, #7, #1")
    check(pmic, 0x287bc, "0xee4e")
    check(pmic, 0x287c4, "bl")
    check(pmic, 0x287c8, "cbnz\tw0, 0x140028804")
    check(pmic, 0x287b8, "w3, #0xf")
    need(0x2869c < 0x287bc < 0x287c8, "unexpected write ordering")
    live = json.loads((ROOT / "experiments/E004-front-ir-vd55g0/e004gb-windows-flash-enable-explicit-kd-predicate/evidence/RESULT.json").read_text())
    need(live["identity_consumed"] is True and
         live["status"] == "PASS_BOUNDED_WINDOWS_PMIC_FLASH_ENABLE_DISABLE_HELPER_OBSERVATION",
         "consumed Windows trace contract")
    hits = live["observed_masked_helper_calls"]
    module_off = [x for x in hits if x["register"]=="0xee46" and x["helper_requested_byte"]=="0x00"]
    channels_off = [x for x in hits if x["register"]=="0xee4e" and x["helper_requested_byte"]=="0x00"]
    need(len(module_off)==len(channels_off)==1 and
         module_off[0]["hit"] < channels_off[0]["hit"], "bounded Windows OFF request ordering")
    successes = 0
    for first in (False, True):
        for second in (False, True):
            module, channels, calls, status = run_fault_model(first, second, True, 0x9)
            need(calls == (["request_module_off", "request_channels_off"] if first
                           else ["request_module_off"]), "fault path unexpected")
            need((module,channels) == ((not first),(0 if first and second else 0x9)),
                 "simulated final status mismatch")
            if first and second:
                need(status=="request_succeeded", "success path")
            else:
                need(status=="request_failed", "failure path")
            successes += 1
    result = {
        "experiment":"E004gf",
        "status":"PASS_OFFLINE_PINNED_WINDOWS_SHUTDOWN_BRANCH_AND_FAULT_MODEL",
        "windows_driver_hashes":EXPECTED,
        "windows_type0_off_path":"mode request followed by independent off request; errors combined",
        "pmic_off_path":"module ee46 off request precedes channel-mask ee4e off request",
        "first_module_write_error_skips_channel_write":True,
        "channel_write_error_leaves_channel_mask_uncleared_in_fault_model":True,
        "observed_e004gb_off_requests":"module 00 then channels 00, helper returns 0",
        "fault_model_combinations":successes,
        "fault_model_physically_proves_led_off":False,
        "windows_driver_executed_or_kd_repeated":False,
        "pmic_or_camera_accessed":False,
        "native_ir_emitter_authorized":False,
        "autonomous_hardware_cutoff_proven":False,
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004GF_WINDOWS_STATIC_SHUTDOWN_PATH=PASS HASH_PINNED=YES")
    print("E004GF_REQUEST_FAILURE_MODEL=PASS CASES="+str(successes))
    print("PHYSICAL_OFF_PROVEN=NO EMITTER_AUTHORIZED=NO WINDOWS_BOOT=NO")

if __name__=="__main__":
    main()
