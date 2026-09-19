#!/usr/bin/env python3
"""Offline Windows flash auxiliary ON/OFF control flow from original ARM64 PE.

The original flash driver CPU instructions execute, with only OS log/PMIC
transport mocked. NOT a Windows session, physical flash, or fail-safe test.
"""
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import pefile,capstone
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PRIOR=ROOT/"experiments/E004-front-ir-vd55g0/e004gg-windows-arm64-off-emulation/emulate_windows_off.py"
PRIOR_SHA="097b97fdfb197b594410d1dc1d37d96ea7c54e24a87d317040f67610850e84b4"
ON_AUX=0x6db0
OFF_AUX=0x6e28
ON_CALLERS=[0x5900]
OFF_CALLERS=[0x5924,0x5a44]

def need(ok,message):
    if not ok:raise AssertionError("E004GK_FAIL_CLOSED "+message)

def previous():
    need(sha256(PRIOR.read_bytes()).hexdigest()==PRIOR_SHA,"prior emulator source drift")
    spec=importlib.util.spec_from_file_location("e004gg_prior",PRIOR)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def direct_callers(o,target):
    paths=list(o.ARCHIVE.glob("*/qccamflash8380.sys"))
    need(len(paths)==1,"unique original PE")
    binary=paths[0].read_bytes()
    need(sha256(binary).hexdigest()==o.EXPECTED["qccamflash8380.sys"],
         "original Windows binary hash drift")
    pe=pefile.PE(data=binary)
    sections=[x for x in pe.sections if x.Name.startswith(b".text")]
    need(len(sections)==1,"unique PE text section")
    s=sections[0]
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    cs.skipdata=True
    found=[]
    for ins in cs.disasm(s.get_data(),o.BASE+s.VirtualAddress):
        if ins.mnemonic=="bl" and ins.op_str.startswith("#"):
            try:dst=int(ins.op_str[1:],16)-o.BASE
            except ValueError:continue
            if dst==target:found.append(ins.address-o.BASE)
    return sorted(found)

def run_aux(rva,transport_fails=False):
    need(rva in (ON_AUX,OFF_AUX),"only bounded pinned auxiliary callbacks allowed")
    need(type(transport_fails) is bool,"failure parameter must be boolean")
    o=previous()
    vm=o.make_vm("qccamflash8380.sys")
    calls=[]
    def hook(vm,pc,size,user):
        if pc==o.FLASH_LOG:
            o.mock_return(vm,0)
        elif pc==o.FLASH_COMMAND:
            length=vm.reg_read(UC_ARM64_REG_X2)
            need(length==4,"flash payload length changed")
            ptr=vm.reg_read(UC_ARM64_REG_X1)
            calls.append({"command":f"0x{vm.reg_read(UC_ARM64_REG_X0)&0xffffffff:08x}",
                          "payload":list(vm.mem_read(ptr,length))})
            o.mock_return(vm,0xc0000001 if transport_fails else 0)
    vm.hook_add(UC_HOOK_CODE,hook)
    vm.emu_start(o.BASE+rva,o.RETURN,count=800)
    return calls,vm.reg_read(UC_ARM64_REG_X0)&0xffffffff

def check(o):
    need(direct_callers(o,ON_AUX)==ON_CALLERS,"ON auxiliary direct caller map drift")
    need(direct_callers(o,OFF_AUX)==OFF_CALLERS,"OFF auxiliary direct caller map drift")
    on,ok_on=run_aux(ON_AUX)
    off,ok_off=run_aux(OFF_AUX)
    need(on==[{"command":"0x802f0fc8","payload":[1,0,0,1]}] and ok_on==0,
         "auxiliary ON callback did not execute expected original payload")
    need(off==[{"command":"0x802f0fc8","payload":[0,0,0,0]}] and ok_off==0,
         "auxiliary OFF callback did not execute expected original payload")
    onerr,bad_on=run_aux(ON_AUX,True)
    offerr,bad_off=run_aux(OFF_AUX,True)
    need(onerr==on and offerr==off and bad_on==bad_off==1,
         "transport error branch did not set auxiliary failure result")
    return on,off

def main():
    o=previous()
    on,off=check(o)
    prior=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004gb-windows-flash-enable-explicit-kd-predicate/evidence/RESULT.json").read_text())
    need(prior["identity_consumed"] is True,"do not replay Windows one-shot")
    result={
        "experiment":"E004gk",
        "status":"PASS_ORIGINAL_WINDOWS_ARM64_AUXILIARY_ON_OFF_CPU_EMULATION_OFFLINE",
        "prior_emulator_sha256":PRIOR_SHA,
        "source_sha256":sha256((HERE/"emulate_teardown.py").read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_teardown.py").read_bytes()).hexdigest(),
        "original_flash_binary_sha256":o.EXPECTED["qccamflash8380.sys"],
        "original_aux_on_callback_rva":"0x6db0",
        "original_aux_off_callback_rva":"0x6e28",
        "direct_on_aux_callers":[hex(x) for x in ON_CALLERS],
        "direct_off_aux_callers":[hex(x) for x in OFF_CALLERS],
        "on_flash_helper_request":on[0],
        "off_flash_helper_request":off[0],
        "mocked_flash_transport_error_propagates_to_boolean_failure":True,
        "other_untraced_lifecycle_paths_excluded":False,
        "normal_preview_exercised_auxiliary_paths_proven":False,
        "pmic_and_windows_kernel_helpers_mocked":True,
        "original_arm64_cpu_instructions_executed":True,
        "autonomous_hardware_emitter_off_proven":False,
        "new_windows_boot_kd_camera_pmic_or_emitter_action":False,
        "native_linux_emitter_activation_authorized":False,
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004GK_ORIGINAL_WINDOWS_AUX_ON_OFF_ARM64_CPU=PASS")
    print("E004GK_ON_CALLS=0x5900 OFF_CALLS=0x5924,0x5a44")
    print("E004GK_ON_PAYLOAD=1,0,0,1 OFF_PAYLOAD=0,0,0,0 MOCKED_FAILURE_RETURNS=1")
    print("WINDOWS_BOOT=NO PHYSICAL_EMITTER_CUTOFF=NOT_PROVEN NATIVE_IR=OFF")
if __name__=="__main__":main()
