#!/usr/bin/env python3
"""Pinned Windows flash timer direct-call map. Offline code-only, no camera/PMIC.

Direct BL map does not rule out indirect calls, firmware, earlier state, or
any autonomous timer behavior inside the physical PMIC.
"""
import hashlib
import json
from pathlib import Path
import pefile
import capstone

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ARCH=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
FLASH_HASH="6bc1d698bc3b6da16974cd6f3ea89dc1ba6a8ea102eebe1a5d41129b4eb9ba2b"
BASE=0x140000000
TIMER_HELPER=0x4dd0
EXPECTED_TIMER_CALLS=[0x4938,0x5b2c]
EXPECTED_STROBE_CALLS=[0x4844,0x4918,0x4954,0x5c64,0x5ce4,0x6de8,0x6e60]
EXPECTED_CURRENT_CALLS=[0x492c,0x5b0c,0x5bd4]

def require(ok, msg):
    if not ok:
        raise AssertionError("E004GI_FAIL_CLOSED "+msg)

def disassemble():
    paths=list(ARCH.glob("*/qccamflash8380.sys"))
    require(len(paths)==1,"unique Windows flash binary")
    data=paths[0].read_bytes()
    require(hashlib.sha256(data).hexdigest()==FLASH_HASH,"original PE hash mismatch")
    pe=pefile.PE(data=data)
    require(pe.OPTIONAL_HEADER.ImageBase==BASE,"unexpected preferred image base")
    secs=[s for s in pe.sections if s.Name.startswith(b".text")]
    require(len(secs)==1,"unexpected text layout")
    sec=secs[0]
    md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    md.skipdata=True
    return {i.address-BASE:(i.mnemonic,i.op_str)
            for i in md.disasm(sec.get_data(),BASE+sec.VirtualAddress)}

def direct_bl_callers(instructions,target):
    result=[]
    for addr,(op,args) in instructions.items():
        if op!="bl" or not args.startswith("#"):
            continue
        try: dest=int(args[1:],16)-BASE
        except ValueError: continue
        if dest==target:
            result.append(addr)
    return sorted(result)

def ins_check(code,addr,op,fragment):
    ins=code.get(addr)
    require(ins is not None and ins[0]==op and fragment in ins[1],
            f"unexpected instruction at flash RVA {addr:#x}: {ins}")

def verify(code,archived):
    require(direct_bl_callers(code,TIMER_HELPER)==EXPECTED_TIMER_CALLS,
            "timer direct-call sites changed")
    require(direct_bl_callers(code,0x4d58)==EXPECTED_STROBE_CALLS,
            "flash strobe direct-call sites changed")
    require(direct_bl_callers(code,0x4ce0)==EXPECTED_CURRENT_CALLS,
            "flash current direct-call sites changed")
    # Type 2 enters 0x5af0 and 0x5b28 timer helper. Type 0 branches
    # *past* both: cmp subtype==2; subtype==1; nonzero -> OFF branch;
    # subtype==0 follows 0x5b80..0x5c64 without 0x4dd0.
    ins_check(code,0x5ae8,"cmp","#2")
    ins_check(code,0x5aec,"b.ne","#0x140005b44")
    ins_check(code,0x5b28,"mov","#1")
    ins_check(code,0x5b2c,"bl","#0x140004dd0")
    ins_check(code,0x5b44,"cmp","#1")
    ins_check(code,0x5b48,"b.ne","#0x140005b7c")
    ins_check(code,0x5b7c,"cbnz","#0x140005c88")
    ins_check(code,0x5b84,"bl","#0x1400045d0")
    ins_check(code,0x5c64,"bl","#0x140004d58")
    ins_check(code,0x5ce4,"bl","#0x140004d58")
    # Separate function 0x48c8 follows timer helper only after a
    # current helper and before the strobe request.
    ins_check(code,0x492c,"bl","#0x140004ce0")
    ins_check(code,0x4938,"bl","#0x140004dd0")
    ins_check(code,0x4954,"bl","#0x140004d58")
    # Don't extrapolate the bounded normal helper trace into absence of
    # all other timer callbacks or physical timer-state transitions.
    require(archived["identity_consumed"] is True
            and archived["status"]==
                "PASS_BOUNDED_WINDOWS_PMIC_FLASH_ENABLE_DISABLE_HELPER_OBSERVATION",
            "previous Windows result is not completed")
    require(archived["kd_pre_calls"]==11
            and archived["kd_post_calls"]==11,"bounded prior observation drift")
    require(archived["windows_pmic_module"]=="qcpmic8380.sys",
            "prior PMIC identity drift")

def main():
    code=disassemble()
    path=ROOT/"experiments/E004-front-ir-vd55g0/e004gb-windows-flash-enable-explicit-kd-predicate/evidence/RESULT.json"
    prior=json.loads(path.read_text())
    verify(code,prior)
    out={
        "experiment":"E004gi",
        "verifier_source_sha256":hashlib.sha256((HERE/"verify_callgraph.py").read_bytes()).hexdigest(),
        "negative_test_sha256":hashlib.sha256((HERE/"test_callgraph.py").read_bytes()).hexdigest(),
        "status":"PASS_PINNED_DIRECT_CALL_MAP_TYPE0_HAS_NO_DIRECT_TIMER_CALL",
        "windows_flash_binary_sha256":FLASH_HASH,
        "text_instructions_including_skipdata":len(code),
        "timer_helper_direct_callers":[f"0x{x:x}" for x in EXPECTED_TIMER_CALLS],
        "type2_dispatch_timer_call":"0x5b2c",
        "separate_config_function_timer_call":"0x4938",
        "type0_branch_region":"0x5b7c..0x5c64",
        "type0_region_contains_direct_timer_bl":False,
        "indirect_dispatch_or_other_timer_writer_excluded":False,
        "bounded_live_e004gb_trace_replayed":False,
        "bounded_e004gb_archived_results_rechecked":True,
        "streaming_timer_state_known":False,
        "pmic_electrical_timer_enforcement_measured":False,
        "native_ir_emitter_activation_authorized":False,
        "new_windows_camera_pmic_or_ir_hardware_access":False,
        "previous_emulator_results_reused_not_repeated_windows":True,
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(out,indent=2)+"\n")
    print("E004GI_ORIGINAL_WINDOWS_DIRECT_CALL_MAP=PASS TIMER_HELPER_CALLERS=0x4938,0x5b2c")
    print("E004GI_NORMAL_TYPE0_DISPATCH_DIRECT_TIMER_CALL=NONE TYPE2_CALL=0x5b2c")
    print("OTHER_OR_INDIRECT_CALLERS=UNEXCLUDED PHYSICAL_CUTOFF=UNPROVEN EMITTER=OFF")
if __name__=="__main__":
    main()
