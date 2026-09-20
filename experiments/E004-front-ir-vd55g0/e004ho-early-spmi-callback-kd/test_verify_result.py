#!/usr/bin/env python3
"""E004ho: reject made-up early SPMI hits, timer first writer and safety claims."""
from pathlib import Path
import copy
import importlib.util
import json
import pefile
import zipfile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004ho_verify",HERE/"verify_result.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
result=json.loads((HERE/"evidence/RESULT.json").read_text())
prep=json.loads((HERE/"evidence/PREPARED.json").read_text())
with zipfile.ZipFile(m.ZIP) as archive:
    raw=archive.read("ORIGINAL-SP7-EARLY-SPMI-CALLBACK-KD.log")
pmic=m.original("qcpmic8380")
spmi=m.original("qcspmi8380")
m.check_log(raw)
m.check_result(result,prep)
m.original_code_check(pmic,spmi)

wrong_result=(
    ("one_shot_natural_callback_entry_observed",False),
    ("positive_control_observes_spmi_software_callback_on_non_timer_write_path",False),
    ("first_original_pmic_idle_timer_0x93_writer_identified",True),
    ("first_entry_packed_selector","0x0001ee3e"),
    ("selector_low_16_bit_register","0xee3e"),
    ("first_entry_payload_byte_count",4),
    ("selector_sid_nibble",2),
    ("first_entry_original_pmic_caller_return_rva","0x23f40"),
    ("controller_mmio_command_or_completion_status_observed_at_first_callback",True),
    ("actual_w1_at_spmi_entry_logged",True),
    ("first_entry_x3_payload_buffer_or_value_logged",True),
    ("pmic_silicon_write_or_illumination_physically_measured",True),
    ("independent_physical_emitter_current_irradiance_pulse_or_host_fault_cutoff_proven",True),
    ("golden_return_boot_id","unverified-boot"),
    ("normal_windows_reboot_to_golden",False),
    ("one_shot_software_code_breakpoint_temporarily_installed_and_cleared",False),
    ("all_debugger_breakpoints_cleared_original_sp7_log_closed_and_kd_stopped",False),
    ("native_linux_ir_emitter_or_login_modified",True),
    ("fresh_windows_boots_consumed",0),
    ("previous_kd_session_or_camera_capture_reused",True),
)
for field,value in wrong_result:
    changed=copy.deepcopy(result)
    changed[field]=value
    try:m.check_result(changed,prep)
    except AssertionError:pass
    else:raise AssertionError("E004HO_UNREJECTED_SCOPE_MUTATION "+field)

raw_mutations=(
    raw+b"tampered",
    raw.replace(b"x2=0000000000019246",b"x2=000000000001ee3e"),
    raw.replace(b"E004HO_EARLY_SPMI_CALLBACK_HIT",
                b"E004HO_EARLY_SPMI_CALLBACK_MISSED"),
    raw.replace(b"E004HO_ALL_BPS_CLEARED_AFTER_EARLY_POSITIVE",
                b"E004HO_BREAKPOINTS_LEFT_ARMED"),
)
for modified in raw_mutations:
    try:m.check_log(modified)
    except AssertionError:pass
    else:raise AssertionError("E004HO_ALTERED_ORIGINAL_KD_LOG_ACCEPTED")
pe_mutations=(
    ("pmic",0x23bac),("pmic",0x23bb8),
    ("pmic",0x23bcc),("pmic",0x23bd4),
    ("pmic",0x23be8),("pmic",0x23bec),
    ("spmi",0x1660),("spmi",0x1688),
    ("spmi",0x1690),
)
for name,rva in pe_mutations:
    original=pmic if name=="pmic" else spmi
    altered=bytearray(original.__data__)
    altered[original.get_offset_from_rva(rva)]^=0x40
    wrong=pefile.PE(data=bytes(altered))
    try:
        m.original_code_check(wrong,spmi) if name=="pmic" else m.original_code_check(pmic,wrong)
    except AssertionError:pass
    else:raise AssertionError("E004HO_ALTERED_OEM_INSTRUCTION_ACCEPTED "+name+" "+hex(rva))
assert result["callback_first_positive_selector_intersects_timer_addresses_0xee3e_0xee41"] is False
assert result["first_original_pmic_idle_timer_0x93_writer_identified"] is False
assert result["pmic_silicon_write_or_illumination_physically_measured"] is False
print("E004HO_FALSE_TIMER_AUTH_GOLDEN_OR_DATA_SCOPE_NEGATIVES=PASS COUNT="+str(len(wrong_result)))
print("E004HO_IMMUTABLE_ORIGINAL_SP7_KD_MUTATION_NEGATIVES=PASS COUNT="+str(len(raw_mutations)))
print("E004HO_ORIGINAL_PMIC_SPMI_ARM64_INSTRUCTION_NEGATIVES=PASS COUNT="+str(len(pe_mutations)))
print("E004HO_EARLY_SOFTWARE_POSITIVE_CONTROL_NEVER_PHYSICAL_EMITTER_CUTOFF=PASS")
