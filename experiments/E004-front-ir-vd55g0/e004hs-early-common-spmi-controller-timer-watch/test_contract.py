#!/usr/bin/env python3
"""E004hs: mutation checks and synthetic timer-span boundaries, no hardware."""
from pathlib import Path
import importlib.util
import pefile,json,copy

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hs",HERE/"verify_contract.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
pe=m.image()
original=m.audit(pe)
assert original["observer_executed_in_new_live_windows_session"] is False
assert original["timer_0x93_first_writer_identified"] is False
assert original["hardware_spmi_completion_or_emitter_fault_off_proven"] is False
assert original["all_direct_controller_callers_in_original_executable_checked"] is True
for addr,count in ((0xee3e,1),(0xee3d,2),(0xee3c,6),
                   (0xee41,1),(0xedff,256),(0xee40,2)):
    assert m.timer_write_span(0,addr,count),(addr,count)
for op,addr,count in (
    (1,0xee3e,1),(0,0xee3d,1),(0,0xee42,1),
    (0,0xee40,0),(0,0xee40,257),(1,0xee3c,4),
    (2,0xee3e,1),(0,0x9246,1),
):
    assert not m.timer_write_span(op,addr,count),(op,addr,count)
invalid=((True,0xee3e,1),(0,True,1),(0,0xee3e,True),
         (0,-1,1),(0,0x10000,1),(0,0xee3e,-1),
         (0,0xee3e,0x10001),(0,"0xee3e",1))
for vals in invalid:
    try:m.timer_write_span(*vals)
    except AssertionError:pass
    else:raise AssertionError("E004HS_INVALID_FILTER_ARGS_ACCEPTED "+str(vals))
checked=0
for rva,_,_ in m.CHECKS:
    altered=bytearray(pe.__data__)
    altered[pe.get_offset_from_rva(rva)]^=0x40
    wrong=pefile.PE(data=bytes(altered))
    try:m.audit(wrong)
    except AssertionError:checked+=1
    else:raise AssertionError("E004HS_ORIGINAL_OPCODE_MUTATION_ACCEPTED "+hex(rva))
assert checked==len(m.CHECKS)
out=json.loads((HERE/"evidence/RESULT.json").read_text())
assert out["status"]=="PASS_OFFLINE_COMPLETE_ORIGINAL_SPMI_CONTROLLER_CALLER_MAP_LIVE_KD_NOT_EXECUTED"
for name in ("remote_debugger_session_executed",
             "original_spmi_controller_live_entry_or_real_timer_request_observed",
             "new_camera_spmi_pmic_led_emitter_or_login_activity",
             "golden_modified","native_linux_ir_emitter_authorized"):
    assert out[name] is False,name
assert out["new_windows_boots_consumed"]==0
print("E004HS_ORIGINAL_SPMI_CORE_ROUTE_OPCODE_MUTATIONS=PASS COUNT="+str(checked))
print("E004HS_SYNTHETIC_WRITE_TIMER_FILTER_POSITIVE_NEGATIVE=PASS COUNT="+str(6+8+len(invalid)))
print("E004HS_NO_LIVE_DEBUGGER_FIRST_TIMER_WRITER_OR_NATIVE_IR_CLAIM=PASS")
