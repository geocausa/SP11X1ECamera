#!/usr/bin/env python3
"""E004hs: offline original SPMI COMMON controller contract and whole-driver callers.

No KD startup, Windows boot, PMIC register action, first 0x93 writer or emitter.
The original qcspmi8380.sys has exactly four direct calls to +0x64d8:
read/standalone, write/direct, masked-read, masked-write.
"""
from pathlib import Path
from hashlib import sha256
import json
import pefile,capstone
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=0x140000000
DRIVER=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qcspmi8380.inf_arm64_9cd00fd0e6e33f85/qcspmi8380.sys")
DIGEST="b6a5868ec2450e713b9a5ada7b4e1a4a77c77427fedf0806fe3eb6541099523c"
CALLS=[0x15b4,0x1870,0x1b38,0x1b70]
CHECKS=[
(0x3e64,"adrp","x8, #0x140001000"),(0x3e68,"add","x10, x8, #0x3a0"),
(0x3e78,"stp","xzr, x10, [sp, #0x130]"),
(0x3e74,"add","x9, x8, #0x660"),(0x3e84,"add","x8, x8, #0x920"),
(0x3e88,"stp","x9, x8, [sp, #0x140]"),
(0x14bc,"cbz","w8, #0x1400014d4"),
(0x14c0,"ubfx","w23, w21, #0x10, #4"),
(0x14c4,"ubfx","w19, w21, #8, #8"),(0x14c8,"and","w20, w21, #0xff"),
(0x14cc,"ubfx","w21, w21, #0x14, #4"),
(0x14d4,"mov","w20, w21"),(0x14d8,"ldp","w23, w19, [x22]"),
(0x14dc,"ldr","w21, [x22, #8]"),
(0x1538,"orr","w4, w20, w19, lsl #8"),
(0x1544,"mov","w6, w25"),(0x154c,"mov","w3, w23"),
(0x1554,"mov","w2, w21"),(0x1558,"mov","w1, w26"),
(0x155c,"mov","w0, #1"),(0x15b4,"bl","#0x1400064d8"),
(0x17f4,"orr","w4, w20, w19, lsl #8"),
(0x17fc,"mov","w6, w25"),(0x1804,"mov","x5, x27"),
(0x180c,"mov","w3, w23"),(0x1810,"mov","w2, w21"),
(0x1814,"mov","w1, w26"),(0x1818,"mov","w0, #0"),
(0x1870,"bl","#0x1400064d8"),
(0x1ad8,"mov","w0, #1"),
(0x1b28,"orr","w19, w19, w21, lsl #8"),
(0x1b2c,"mov","w4, w19"),(0x1b38,"bl","#0x1400064d8"),
(0x1b3c,"cbnz","w0, #0x140001b78"),
(0x1b48,"mov","w6, #1"),(0x1b50,"mov","w4, w19"),
(0x1b54,"bic","w9, w8, w26"),(0x1b58,"and","w8, w27, w26"),
(0x1b5c,"orr","w8, w9, w8"),(0x1b64,"strb","w8, [sp, #0x30]"),
(0x1b68,"mov","w2, w20"),(0x1b6c,"mov","w1, w25"),
(0x1b70,"bl","#0x1400064d8"),
(0x64d8,"pacibsp",""),(0x64dc,"stp","x19, x20, [sp, #-0x50]!"),
(0x6500,"mov","w23, w2"),(0x6508,"mov","w22, w4"),
(0x650c,"mov","x25, x5"),(0x6510,"mov","w26, w6"),
(0x651c,"mov","w27, w0"),(0x6524,"mov","w24, w1")
]
def require(ok,why):
    if not ok:raise AssertionError("E004HS_ORIGINAL_BUS_CONTRACT_FAIL_CLOSED "+why)
def image():
    raw=DRIVER.read_bytes()
    require(sha256(raw).hexdigest()==DIGEST,"original OEM SPMI image bytes changed")
    pe=pefile.PE(data=raw)
    require(pe.FILE_HEADER.Machine==0xaa64 and
            pe.OPTIONAL_HEADER.ImageBase==BASE,"original OEM PE not original ARM64")
    return pe
def ins(pe,rva):
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    a=list(cs.disasm(pe.get_data(rva,4),BASE+rva))
    require(len(a)==1,"missing original OEM instruction "+hex(rva))
    return a[0].mnemonic,a[0].op_str
def direct_calls(pe,target):
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    cs.skipdata=True
    sites=[]
    for sec in pe.sections:
        if not sec.Characteristics&0x20000000:continue
        for a in cs.disasm(sec.get_data(),BASE+sec.VirtualAddress):
            if a.mnemonic=="bl" and a.op_str.startswith("#") and int(a.op_str[1:],16)==BASE+target:
                sites.append(a.address-BASE)
    return sorted(sites)
def timer_write_span(op,address,length):
    """SYNTHETIC 16-bit-address model, not a live Windbg/PMIC result."""
    if not(all(type(x) is int for x in (op,address,length)) and
           0<=address<=0xffff and 0<=length<=0x10000):
        raise AssertionError("invalid synthetic controller arguments")
    # Original controller caller w0=0 denotes write; w4=register
    # start and w6=byte count. 0x1b70 is masked RMW's write stage.
    return op==0 and 1<=length<=256 and address<=0xee41 and address+length>0xee3e
def audit(pe):
    for rva,mn,args in CHECKS:
        require(ins(pe,rva)==(mn,args),"original instruction mismatch "+hex(rva))
    require(direct_calls(pe,0x64d8)==CALLS,
            "whole original executable controller direct caller set drift")
    require(ins(pe,0x3e78)==("stp","xzr, x10, [sp, #0x130]"),
            "read callback offset +0x28 not verified")
    return {
      "original_interface_read_callback_rva":"0x13a0",
      "original_interface_read_callback_offset":"0x28",
      "original_interface_direct_write_callback_rva":"0x1660",
      "original_interface_direct_write_callback_offset":"0x30",
      "original_interface_masked_read_modify_write_callback_rva":"0x1920",
      "original_interface_masked_read_modify_write_offset":"0x38",
      "original_controller_helper_rva":"0x64d8",
      "all_four_original_controller_direct_callsite_rvas":[hex(x) for x in CALLS],
      "standalone_read_callsite_rva":"0x15b4",
      "direct_write_callsite_rva":"0x1870",
      "masked_rmw_read_callsite_rva":"0x1b38",
      "masked_rmw_write_callsite_rva":"0x1b70",
      "all_direct_controller_callers_in_original_executable_checked":True,
      "controller_entry_operation_register":"w0",
      "controller_entry_normalized_bus_register":"w2",
      "controller_entry_normalized_sid_register":"w3",
      "controller_entry_normalized_register_address_register":"w4",
      "controller_entry_data_pointer_register":"x5",
      "controller_entry_byte_count_register":"w6",
      "original_direct_write_op_w0":"0x0",
      "original_read_op_w0":"0x1",
      "original_masked_write_only_after_successful_read":True,
      "conditional_timer_write_selector_bounds_low16":"ee3e..ee41",
      "conditional_timer_write_synthetic_max_bytes":256,
      "out_of_range_or_larger_length_is_proven_impossible_in_actual_original_driver":False,
      "other_drivers_indirect_function_pointers_or_pre_os_firmware_excluded":False,
      "observer_executed_in_new_live_windows_session":False,
      "timer_0x93_first_writer_identified":False,
      "hardware_spmi_completion_or_emitter_fault_off_proven":False
    }
def main():
    previous=ROOT/"experiments/E004-front-ir-vd55g0/e004hr-early-spmi-alternate-masked-timer-kd/evidence/RESULT.json"
    old=json.loads(previous.read_text())
    require(old["status"]=="PASS_FRESH_EARLY_WINDOWS_ALTERNATE_MASKED_SPMI_CALLBACK_BOUNDED_NONHIT_WITH_DIRECT_POSITIVE_GOLDEN_RETURN" and
            old["first_original_idle_timer_byte_0x93_writer_identified"] is False,
            "previous consumed E004hr scope drift")
    result={
      "experiment":"E004hs",
      "status":"PASS_OFFLINE_COMPLETE_ORIGINAL_SPMI_CONTROLLER_CALLER_MAP_LIVE_KD_NOT_EXECUTED",
      "date":"2026-09-20",
      "baseline_commit":"8c040d11a59d0204c560259bccfd4c10d925343b",
      "original_spmi_sha256":DIGEST,
      "prior_e004hr_original_result_sha256":sha256(previous.read_bytes()).hexdigest(),
      "original_complete_controller_calling_convention":audit(image()),
      "synthetic_filter_positive_tests":[
          [0,0xee3e,1],[0,0xee3d,2],[0,0xee3c,6],[0,0xee41,1]],
      "new_windows_boots_consumed":0,
      "remote_debugger_session_executed":False,
      "original_spmi_controller_live_entry_or_real_timer_request_observed":False,
      "new_camera_spmi_pmic_led_emitter_or_login_activity":False,
      "golden_modified":False,
      "native_linux_ir_emitter_authorized":False,
      "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
      "negative_test_sha256":sha256((HERE/"test_contract.py").read_bytes()).hexdigest(),
    }
    for vals in result["synthetic_filter_positive_tests"]:
        require(timer_write_span(*vals),"expected synthetic timer overlap rejected")
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004HS_ORIGINAL_SPMI_READ_DIRECT_WRITE_MASKED_RMW_FOUR_CONTROLLER_CALLS=PASS")
    print("E004HS_SHARED_CONTROLLER_W0_W4_W6_SYNTHETIC_TIMER_FILTER=PASS")
    print("E004HS_LIVE_KD_NOT_EXECUTED_0X93_FIRST_WRITER_UNKNOWN_GOLDEN_UNCHANGED")
if __name__=="__main__":main()
