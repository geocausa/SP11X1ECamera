#!/usr/bin/env python3
"""E004hu: reject fabricated UEFI archive identity, literal and timer ownership."""
from pathlib import Path
import importlib.util
import json

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hu_provenance",HERE/"verify_firmware.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
capsule=v.CAPSULE.read_bytes()
modules=sorted(p for p in v.DUMP.rglob("body.bin")
               if "PE32 image section" in p.parent.name)
assert len(modules)==255
record=v.scan(capsule,modules)
assert record["archived_capsule_bytes_equals_running_firmware_bytes_verified"] is False
assert record["original_first_0x93_timer_writer_identified"] is False
assert record["actual_hw_reset_value_or_independent_led_cutoff_established"] is False
assert record["capsule_undifferentiated_two_byte_ee3e_hits"]==95
assert record["capsule_exact_literal_signature_occurrences"]["first_timer_dword_le"]==0
assert v.prior()
# A timer literal inserted into a modified archived image must invalidate
# capsule identity; no mutated firmware is ever executed or written to ESP.
mutations=(
    ("capsule append",capsule+b"\x3e\xee\x00\x00",modules),
    ("capsule shorten",capsule[:-1],modules),
    ("missing image",capsule,modules[:-1]),
    ("repeated image",capsule,modules[:-1]+modules[-2:-1]),
)
for why,fw,images in mutations:
    try:v.scan(fw,images)
    except AssertionError:pass
    else:raise AssertionError("E004HU_UNREJECTED_ORIGINAL_FIRMWARE_MUTATION "+why)
# Explicit 16-bit address is too common in arbitrary ARM64 code/metadata to
# attribute an original flash-timer operation without a decoded callsite.
for key in ("PmicDxe","SPMI"):
    assert record["original_pmic_spmi_uefi_modules"][key][
        "explicit_first_timer_address_16bit_le_hits"]==0
    assert record["original_pmic_spmi_uefi_modules"][key][
        "explicit_first_timer_address_32bit_le_hits"]==0
result=json.loads((HERE/"evidence/RESULT.json").read_text())
assert result["experiment"]=="E004hu"
assert result["original_uefi_firmware_bounded_audit"]==record
for field in ("new_windows_boot_or_kd_spmi_pmic_camera_led_login_activity",
              "firmware_flashing_or_uefi_mutation",
              "native_ir_emitter_authorized","golden_modified"):
    assert result[field] is False,field
print("E004HU_ORIGINAL_UEFI_IMAGE_AND_INVENTORY_MUTATION_NEGATIVES=PASS COUNT=4")
print("E004HU_ARCHIVED_BIOS_VERSION_MATCH_IS_NOT_PROOF_OF_ACTUAL_TIMER_FIRST_WRITER=PASS")
