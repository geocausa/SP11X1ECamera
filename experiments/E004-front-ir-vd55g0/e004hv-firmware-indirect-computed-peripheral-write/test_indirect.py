#!/usr/bin/env python3
"""E004hv: fail-closed original firmware computed-writer source mutation tests."""
from pathlib import Path
import importlib.util
import pefile
import json

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hv_original_fw",HERE/"verify_indirect.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
original=m.original_image()
proof=m.analyze(original)
assert m.prior()
assert proof["original_direct_bl_to_indirect_function_count"]==0
assert proof["second_register_relative_offset"]=="0x3e"
for key in ("second_write_register_address_equals_ee3e_proven",
            "original_function_called_on_this_sp11_pre_os_boot_proven",
            "original_caller_supplied_two_bytes_equal_0x93_or_0x9393_proven",
            "silicon_completion_or_physical_emitter_cutoff_proven",
            "original_timer_idle_byte_0x93_first_writer_identified"):
    assert proof[key] is False,key
cases=[
    0x38d98,0x22304,0x22308,0x2230c,0x22318,0x22320,
    0x22328,0x22330,0x22334,0x22338,0x2233c,
    0x12168,0x1216c,0x12170,0x12174,0x12178,
    0x121e4,0x121ec,0x121f0,0x12214,0x12220,
    0x12224,0x12228,0x1222c,0x12230,0x12234,
    0x1223c,0x12240,0x12244,0x8cd0,0x8ce0,
    0x8ce8,0x8d34,
]
for rva in cases:
    raw=bytearray(original.__data__)
    raw[original.get_offset_from_rva(rva)]^=0x40
    altered=pefile.PE(data=bytes(raw))
    try:m.analyze(altered)
    except AssertionError:pass
    else:raise AssertionError("E004HV_ORIGINAL_IMAGE_MUTATION_NOT_REJECTED "+hex(rva))
result=json.loads((HERE/"evidence/RESULT.json").read_text())
assert result["original_uefi_pmic_indirect_computed_writer"]==proof
assert result["native_ir_emitter_authorized"] is False
assert result["golden_modified"] is False
assert result["no_windows_kd_camera_pmic_spmi_led_firmware_or_login_activity"] is True
print("E004HV_FIRMWARE_COMPUTED_REGISTER_WRITER_NEGATIVE_MUTATIONS=PASS COUNT="+str(len(cases)))
print("E004HV_REGISTER_LOW_OFFSET_3E_NEVER_PROMOTED_TO_ACTUAL_EE3E_OR_93=PASS")
