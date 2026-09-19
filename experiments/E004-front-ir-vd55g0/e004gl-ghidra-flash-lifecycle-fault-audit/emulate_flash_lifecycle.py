#!/usr/bin/env python3
"""Ghidra-guided fault checks on original Windows ARM64 flash lifecycle CPU bytes.

All flash/OS services mocked inside Unicorn VM; not a hardware safety test.
"""
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import UC_ARM64_REG_X0, UC_ARM64_REG_X1

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PRIOR=ROOT/"experiments/E004-front-ir-vd55g0/e004gg-windows-arm64-off-emulation/emulate_windows_off.py"
PRIOR_SHA="097b97fdfb197b594410d1dc1d37d96ea7c54e24a87d317040f67610850e84b4"
ACTIVE_FLAG_RVA=0xe4b5
OTHER_FLAG_RVA=0xe4b4
ERROR=0xc0000001

def require(ok,why):
    if not ok: raise AssertionError("E004GL_CPU_FAIL_CLOSED "+why)

def original():
    require(sha256(PRIOR.read_bytes()).hexdigest()==PRIOR_SHA,
            "prior audited original-PE emulator changed")
    spec=importlib.util.spec_from_file_location("e004gg_lifecycle",PRIOR)
    o=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(o)
    return o

def start(prior_active=False,failure="none"):
    require(type(prior_active) is bool,"prior active flag must be boolean")
    require(failure in ("none","prior_off","current","timer","strobe_on"),
            "unsupported synthetic failure stage")
    require(failure!="prior_off" or prior_active,
            "cannot fail preceding OFF without preceding active flag")
    o=original()
    vm=o.make_vm("qccamflash8380.sys")
    vm.mem_write(o.BASE+ACTIVE_FLAG_RVA,bytes([int(prior_active)]))
    vm.mem_write(o.BASE+OTHER_FLAG_RVA,bytes([0]))
    vm.reg_write(UC_ARM64_REG_X0,4)
    vm.reg_write(UC_ARM64_REG_X1,(700<<32)|700)
    calls=[]
    def intercept(vm,pc,size,userdata):
        if pc==o.BASE+0x4ce0:
            phase="current"
        elif pc==o.BASE+0x4dd0:
            phase="timer"
        elif pc==o.BASE+0x4d58:
            phase="prior_off" if prior_active and not calls else "strobe_on"
        else:
            return
        calls.append(phase)
        o.mock_return(vm,ERROR if phase==failure else 0)
    vm.hook_add(UC_HOOK_CODE,intercept)
    vm.emu_start(o.BASE+0x48c8,o.RETURN,count=500)
    return {"calls":calls,"returned_success":vm.reg_read(UC_ARM64_REG_X0)&0xffffffff==1,
            "software_active_flag":vm.mem_read(o.BASE+ACTIVE_FLAG_RVA,1)[0]}

def stop(fail_off=False):
    require(type(fail_off) is bool,"stop failure parameter must be boolean")
    o=original()
    vm=o.make_vm("qccamflash8380.sys")
    vm.mem_write(o.BASE+ACTIVE_FLAG_RVA,bytes([1]))
    vm.mem_write(o.BASE+OTHER_FLAG_RVA,bytes([0]))
    calls=[]
    def intercept(vm,pc,size,userdata):
        if pc==o.BASE+0x4d58:
            calls.append("strobe_off")
            o.mock_return(vm,ERROR if fail_off else 0)
        elif pc in (o.BASE+0x4bd0,o.BASE+0x3e70,o.BASE+0x40c8):
            calls.append("software_cleanup")
            o.mock_return(vm,0)
    vm.hook_add(UC_HOOK_CODE,intercept)
    vm.emu_start(o.BASE+0x4828,o.RETURN,count=500)
    return {"calls":calls,"returned_success":vm.reg_read(UC_ARM64_REG_X0)&0xffffffff==1,
            "software_active_flag":vm.mem_read(o.BASE+ACTIVE_FLAG_RVA,1)[0]}

def main():
    cases={
        "start_ok":start(),
        "start_current_error":start(False,"current"),
        "start_timer_error":start(False,"timer"),
        "start_strobe_error":start(False,"strobe_on"),
        "start_prior_off_error":start(True,"prior_off"),
        "stop_ok":stop(),
        "stop_bus_error":stop(True),
    }
    expected={
        "start_ok":(["current","timer","strobe_on"],True,1),
        "start_current_error":(["current"],False,0),
        "start_timer_error":(["current","timer"],False,0),
        "start_strobe_error":(["current","timer","strobe_on"],False,0),
        "start_prior_off_error":(["prior_off","current","timer","strobe_on"],True,1),
        "stop_ok":(["strobe_off","software_cleanup"],True,0),
        "stop_bus_error":(["strobe_off"],False,1),
    }
    for key,(calls,success,flag) in expected.items():
        result=cases[key]
        require(result=={"calls":calls,"returned_success":success,"software_active_flag":flag},
                "original ARM64 branch changed for "+key)
    out={
        "experiment":"E004gl",
        "status":"PASS_GHIDRA_DECOMPILED_AND_ORIGINAL_ARM64_LIFECYCLE_FAULT_EMULATION_OFFLINE",
        "prior_emulator_source_sha256":PRIOR_SHA,
        "emulation_script_sha256":sha256((HERE/"emulate_flash_lifecycle.py").read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_flash_lifecycle.py").read_bytes()).hexdigest(),
        "ghidra_script_sha256":sha256((HERE/"VerifyFlashLifecycleGhidra.java").read_bytes()).hexdigest(),
        "ghidra_runner_sha256":sha256((HERE/"verify_ghidra.py").read_bytes()).hexdigest(),
        "original_pe_windows_arm64_instructions_executed":True,
        "windows_os_and_pmic_io_mocked":True,
        "previous_off_request_failure_does_not_prevent_subsequent_rearm_request":True,
        "stop_off_request_failure_returns_failed_and_does_not_clear_software_active_flag":True,
        "new_on_request_error_does_not_trigger_best_effort_off_in_examined_function":True,
        "physical_led_state_after_error_measured":False,
        "real_software_failure_and_hardware_failure_equivalent_proven":False,
        "native_emitter_enable_authorized":False,
        "original_windows_boot_kd_camera_or_pmic_accessed":False,
        "golden_modified":False,
        "vm_cases":cases,
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(out,indent=2)+chr(10))
    print("E004GL_ORIGINAL_ARM64_START_STOP_FAULT_VM=PASS CASES=7")
    print("E004GL_PRIOR_OFF_MOCK_ERROR_STILL_ATTEMPTS_REARM=TRUE")
    print("E004GL_STOP_MOCK_ERROR_LEAVES_ACTIVE_FLAG_SET=TRUE")
    print("E004GL_NO_HARDWARE_LED_OR_TIMER_TEST=YES NATIVE_EMITTER=OFF")

if __name__=="__main__":main()
