#!/usr/bin/env python3
"""Execute *exact hash-pinned Windows ARM64 instructions* in an offline Unicorn VM.

Mock imported Windows messaging and PMIC register-access helper functions.
This is CPU control-flow evidence, NOT a Windows boot, physical PMIC behavior,
real bus fault injection, autonomous shutdown, or emitter safety evidence.
"""
from hashlib import sha256
from pathlib import Path
import json
import struct
import pefile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm64_const import (
    UC_ARM64_REG_PC, UC_ARM64_REG_SP, UC_ARM64_REG_X30,
    UC_ARM64_REG_X0, UC_ARM64_REG_X1, UC_ARM64_REG_X2,
    UC_ARM64_REG_X3, UC_ARM64_REG_X4,
)

HERE = Path(__file__).resolve().parent
ARCHIVE = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
BASE = 0x140000000
STACK = 0x70000000
RETURN = STACK + 0xf000
PMIC_HELPER = BASE + 0x23968
FLASH_COMMAND = BASE + 0x4ac0
FLASH_LOG = BASE + 0x3990
EXPECTED = {
    "qccamflash8380.sys": "6bc1d698bc3b6da16974cd6f3ea89dc1ba6a8ea102eebe1a5d41129b4eb9ba2b",
    "qcpmic8380.sys": "756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e",
}

def require(condition, message):
    if not condition:
        raise AssertionError("E004GG_EMULATOR_FAIL_CLOSED " + message)

def make_vm(name):
    sources = list(ARCHIVE.glob("*/" + name))
    require(len(sources) == 1, "unique original " + name)
    data = sources[0].read_bytes()
    require(sha256(data).hexdigest() == EXPECTED[name], "original binary hash drift " + name)
    pe = pefile.PE(data=data)
    require(pe.OPTIONAL_HEADER.ImageBase == BASE, "unexpected Windows PE preferred base")
    mapped = pe.get_memory_mapped_image()
    vm = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    vm.mem_map(BASE, ((len(mapped) + 0xfff) // 0x1000) * 0x1000)
    vm.mem_write(BASE, mapped)
    vm.mem_map(STACK, 0x10000)
    vm.reg_write(UC_ARM64_REG_SP, STACK + 0x8000)
    vm.reg_write(UC_ARM64_REG_X30, RETURN)
    return vm

def mock_return(vm, status):
    vm.reg_write(UC_ARM64_REG_X0, status & 0xffffffffffffffff)
    vm.reg_write(UC_ARM64_REG_PC, vm.reg_read(UC_ARM64_REG_X30))

def run_pmic(enable_payload, fail_stage=0):
    require(enable_payload in ((0,0,0,0),(1,0,0,1)), "unsupported synthetic 4-byte fixture")
    require(fail_stage in (0,1,2), "bad failure stage")
    vm = make_vm("qcpmic8380.sys")
    # Prevent optional tracing imports: set the *emulated* trace-list head to
    # point at itself, without modifying the on-disk image or executable code.
    vm.mem_write(BASE + 0x390e0, struct.pack("<Q", BASE + 0x390e0))
    # Confirmed paired LED1 channels 0 and 3 from active-table evidence.
    # Configure *VM-only* global pairing, not a live kernel/PMIC.
    vm.mem_write(BASE + 0x3b8c8 + 0x19, bytes((3,2,4,4)))
    data_ptr = STACK + 0x4000
    vm.mem_write(data_ptr, bytes(enable_payload))
    vm.reg_write(UC_ARM64_REG_X0, data_ptr)
    observed = []
    def intercept(vm, pc, size, user_data):
        if pc == PMIC_HELPER:
            i = len(observed) + 1
            observed.append({
                "call": i,
                "register": f"0x{vm.reg_read(UC_ARM64_REG_X2):04x}",
                "mask": f"0x{vm.reg_read(UC_ARM64_REG_X3):x}",
                "requested": f"0x{vm.reg_read(UC_ARM64_REG_X4):x}",
            })
            # Simulate a failed hardware-access *request*; nothing here
            # simulates or measures any real hardware register state.
            mock_return(vm, 0xc0000001 if fail_stage == i else 0)
    vm.hook_add(UC_HOOK_CODE, intercept)
    vm.emu_start(BASE + 0x285c0, RETURN, count=1500)
    status = vm.reg_read(UC_ARM64_REG_X0) & 0xffffffff
    return observed, status

def run_flash_off_wrapper(arg0, arg1, arg2, mocked_status):
    require(all(type(x) is int and x in (0,1) for x in (arg0,arg1,arg2)),
            "bad wrapper arguments")
    vm = make_vm("qccamflash8380.sys")
    for reg, val in ((UC_ARM64_REG_X0,arg0),(UC_ARM64_REG_X1,arg1),
                     (UC_ARM64_REG_X2,arg2)):
        vm.reg_write(reg,val)
    calls = []
    def intercept(vm,pc,size,user_data):
        if pc == FLASH_LOG:
            mock_return(vm,0)
        elif pc == FLASH_COMMAND:
            ptr = vm.reg_read(UC_ARM64_REG_X1)
            length = vm.reg_read(UC_ARM64_REG_X2)
            require(length == 4, "Windows flash wrapper payload length")
            cmd = vm.reg_read(UC_ARM64_REG_X0) & 0xffffffff
            calls.append({"command":f"0x{cmd:08x}",
                          "payload":list(vm.mem_read(ptr, length))})
            mock_return(vm,mocked_status)
    vm.hook_add(UC_HOOK_CODE, intercept)
    vm.emu_start(BASE + 0x4d58,RETURN,count=200)
    return calls, vm.reg_read(UC_ARM64_REG_X0) & 0xffffffff

def main():
    calls, success = run_flash_off_wrapper(0,0,0,0)
    require(calls==[{"command":"0x802f0fc8","payload":[0,0,0,0]}]
            and success==0, "actual Windows flash OFF wrapper payload")
    calls, failure = run_flash_off_wrapper(0,0,0,0xc0000001)
    require(calls[0]["payload"]==[0,0,0,0] and
            failure==0xc0000001, "actual Windows wrapper failure propagation")
    disabled, ok = run_pmic((0,0,0,0))
    require(disabled == [
        {"call":1,"register":"0xee46","mask":"0x80","requested":"0x0"},
        {"call":2,"register":"0xee4e","mask":"0xf","requested":"0x0"},
    ] and ok==0, "actual Windows PMIC OFF order/fields")
    armed, arm_status = run_pmic((1,0,0,1))
    require(armed == [
        {"call":1,"register":"0xee46","mask":"0x80","requested":"0x80"},
        {"call":2,"register":"0xee4e","mask":"0xf","requested":"0x9"},
    ] and arm_status==0, "actual Windows PMIC ON request pairing")
    first_failed, first_status = run_pmic((0,0,0,0),1)
    require(first_failed == disabled[:1] and first_status!=0,
            "first register helper error must skip channel request")
    second_failed, second_status = run_pmic((0,0,0,0),2)
    require(second_failed == disabled and second_status!=0,
            "second helper error must propagate after both requests")
    output = {
        "experiment":"E004gg",
        "emulate_source_sha256":sha256((HERE/"emulate_windows_off.py").read_bytes()).hexdigest(),
        "test_source_sha256":sha256((HERE/"test_emulation.py").read_bytes()).hexdigest(),
        "flash_wrapper_nonzero_arguments_confirmed":"(1,0,1) yields [0,1,0,1]",
        "original_windows_driver_bytes_published":False,
        "status":"PASS_OFFLINE_ORIGINAL_ARM64_INSTRUCTION_EMULATION",
        "original_windows_pe_sha256":EXPECTED,
        "arm64_binary_instructions_executed":True,
        "emulator":"Unicorn AArch64 CPU, deterministic temporary in-memory PE mapping",
        "pmic_software_access_stubbed":True,
        "original_flash_off_wrapper":calls[0],
        "windows_off_register_requests":disabled,
        "windows_enable_register_requests":armed,
        "module_write_failed_skips_channel_request":True,
        "channel_write_failed_propagates_status":True,
        "failure_scenarios_emulated":2,
        "physical_regmap_or_bus_accessed":False,
        "driver_loaded_or_executed_on_windows":False,
        "windows_boot_kd_camera_emitter_repeated":False,
        "physical_led_off_or_timer_irradiance_proven":False,
        "native_linux_emitter_enable_authorized":False,
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(output,indent=2)+"\n")
    print("E004GG_REAL_ARM64_OFF_WRAPPER=PASS OFF_PAYLOAD=00000000")
    print("E004GG_REAL_ARM64_PMIC_CALLBACK=PASS EE46_THEN_EE4E")
    print("E004GG_REAL_ARM64_EMULATED_FAILURES=PASS FIRST_SKIPS_SECOND_SECOND_PROPAGATES")
    print("WINDOWS_BOOT=NO HARDWARE_EMITTER=OFF PHYSICAL_CUTOFF_PROVEN=NO")
if __name__=="__main__":
    main()
