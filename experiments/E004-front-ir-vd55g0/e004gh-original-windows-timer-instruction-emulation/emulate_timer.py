#!/usr/bin/env python3
"""Run hash-pinned original Windows PMIC ARM64 timer callback in an offline CPU VM.

This exercises CPU request encoding / fault exits only. A mocked PMIC write is
NOT timer hardware execution, a physically measured LED-off, or an eye-safety test.
"""
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import struct
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import (
    UC_ARM64_REG_X0, UC_ARM64_REG_X2, UC_ARM64_REG_X3, UC_ARM64_REG_X4,
)

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PREV=ROOT/"experiments/E004-front-ir-vd55g0/e004gg-windows-arm64-off-emulation/emulate_windows_off.py"
PREV_SHA="097b97fdfb197b594410d1dc1d37d96ea7c54e24a87d317040f67610850e84b4"
PMIC_TIMER_START=0x26d50
PMIC_LOG_HELPER=0x20668

def require(ok, why):
    if not ok:
        raise AssertionError("E004GH_TIMER_EMULATION_FAIL_CLOSED "+why)

def imported_vm():
    require(sha256(PREV.read_bytes()).hexdigest()==PREV_SHA, "previous CPU emulator drift")
    spec=importlib.util.spec_from_file_location("e004gg_cpu",PREV)
    prev=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prev)
    return prev

def run_timer(ms, enabled=True, fail_request=0):
    require(type(ms) is int and 0<=ms<=1281, "bounded integer request required")
    require(type(enabled) is bool, "enabled must be bool")
    require(type(fail_request) is int and 0<=fail_request<=5, "invalid fault call")
    prev=imported_vm()
    vm=prev.make_vm("qcpmic8380.sys")
    vm.mem_write(prev.BASE+0x390e0,struct.pack("<Q",prev.BASE+0x390e0))
    # Four synthetic VM-only pairing bytes, pinned by E004fj; no live PMIC.
    vm.mem_write(prev.BASE+0x3b8c8+0x19,bytes((3,2,4,4)))
    payload=struct.pack("<4I",int(enabled),ms,0,0)
    ptr=prev.STACK+0x4000
    vm.mem_write(ptr,payload)
    vm.reg_write(UC_ARM64_REG_X0,ptr)
    writes=[]
    def intercept(vm,pc,size,user_data):
        if pc==prev.PMIC_HELPER:
            idx=len(writes)+1
            writes.append({
                "call":idx,
                "register":f"0x{vm.reg_read(UC_ARM64_REG_X2):04x}",
                "mask":f"0x{vm.reg_read(UC_ARM64_REG_X3):02x}",
                "request":f"0x{vm.reg_read(UC_ARM64_REG_X4):02x}",
            })
            prev.mock_return(vm,0xc0000001 if idx==fail_request else 0)
        elif pc==prev.BASE+PMIC_LOG_HELPER:
            prev.mock_return(vm,0)
    vm.hook_add(UC_HOOK_CODE,intercept)
    vm.emu_start(prev.BASE+PMIC_TIMER_START,prev.RETURN,count=3500)
    return writes,vm.reg_read(UC_ARM64_REG_X0)&0xffffffff

def main():
    cases={}
    expected_addresses=["0xee3e","0xee41","0xee3f","0xee40","0xee40"]
    for ms in (0,10,11,19,20,200,1270,1280,1281):
        writes,status=run_timer(ms,ms!=0)
        if ms==1281:
            require(status!=0 and writes==[], "over-limit must reject with no output request")
            cases[str(ms)]={"rejected":True,"register_requests":[]}
            continue
        require(status==0 and len(writes)==5, f"unexpected timer requests for {ms}")
        require([row["register"] for row in writes]==expected_addresses,
                "original four-channel timer write order drift")
        expected=0 if ms==0 else 0x80+(ms-10)//10
        require([int(row["request"],16) for row in writes]==[expected,expected,0,0,0],
                f"original encoded value mismatch for {ms}")
        require(all(row["mask"]=="0xff" for row in writes), "unexpected timer write masks")
        cases[str(ms)]={"nominal_ms":ms,"encoded_pair_value":f"0x{expected:02x}",
                        "ordered_register_requests":writes}
    injected_failures={}
    # A paired request attempts BOTH channel writes and ORs their errors,
    # then aborts before the NEXT logical LED. The last lone channel stands
    # alone. This is executable original-binary behavior, not a PMIC model.
    for n in range(1,6):
        writes,status=run_timer(200,True,n)
        expected_count=2 if n<=2 else 4 if n<=4 else 5
        require(status!=0 and len(writes)==expected_count,
                f"paired helper-failure behavior mismatch at call {n}")
        injected_failures[str(n)]={"observed_register_requests":len(writes),
                                   "returned_error":True}
    disabled,wstatus=run_timer(200,False)
    require(wstatus==0 and [row["request"] for row in disabled]==["0x00"]*5,
            "disabled timer request unexpectedly kept nonzero time encoding")
    # Existing idle read result is consumed, do not re-read any PMIC hardware.
    idle=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004fx-passive-golden-timer-read/evidence/RESULT.json").read_text())
    require(idle["read_once_identity_consumed"] is True and
            set(idle["idle_timer_register_bytes"].values())=={"93"},
            "archived idle evidence status")
    require(cases["200"]["encoded_pair_value"]=="0x93",
            "Windows software 200ms encoding must agree with archived idle byte, not prove timer activity")
    result={
        "experiment":"E004gh",
        "emulation_source_sha256":sha256((HERE/"emulate_timer.py").read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_timer.py").read_bytes()).hexdigest(),
        "status":"PASS_ORIGINAL_WINDOWS_ARM64_TIMER_HANDLER_CPU_EMULATION_OFFLINE",
        "original_pmic_binary_sha256":prev_sha_pmic(),
        "previous_emulator_source_sha256":PREV_SHA,
        "timer_callback_rva":"0x26d50",
        "tested_nominal_requests_ms":[0,10,11,19,20,200,1270,1280,1281],
        "windows_enabled_nominal_200ms_encoded_byte":"0x93",
        "archived_golden_idle_all_four_timer_bytes":"0x93",
        "archived_idle_byte_proves_timer_enforcement":False,
        "type0_windows_camera_stream_called_timer_handler_proven":False,
        "observed_ordered_timer_requests_200ms":cases["200"]["ordered_register_requests"],
        "five_mock_write_failures_attempt_current_pair_then_stop_next_logical_led":True,
        "injected_failure_results":injected_failures,
        "disabled_request_writes_all_five_zero":True,
        "pmic_write_helper_is_mocked":True,
        "physical_timer_current_irradiance_or_autonomous_fault_off_proven":False,
        "linux_emitter_activation_authorized":False,
        "no_new_windows_kd_camera_pmic_or_emitter_activity":True,
        "case_results":cases,
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004GH_ORIGINAL_WINDOWS_TIMER_CPU=PASS 0_10_200_1280_BOUNDARIES=PASS")
    print("E004GH_TIMER_PAIRWISE_FAILURE_EXIT_FIVE_FAULT_BRANCHES=PASS")
    print("E004GH_IDLE_0x93_RECONCILIATION=SOFTWARE_ENCODING_ONLY")
    print("PHYSICAL_TIMER_CUTOFF=UNPROVEN IR_EMITTER=OFF WINDOWS_BOOT=NO")

def prev_sha_pmic():
    return "756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e"

if __name__=="__main__":
    main()
