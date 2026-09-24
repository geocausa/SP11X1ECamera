#!/usr/bin/env python3
"""E004of: source-check actual ISP per-core interface-record creation and use.

Original private same-SP11 OEM binary read only; evidence exported is SAFE
driver-relative RVAs and booleans, not code bytes, pixels, buffers or secrets.
"""
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000

# Two allocation helpers, physical-context enumeration, per-core records,
# callback-table import, and original manager consumption by bounded index.
ANCHORS={
 0x69480:("mov","x0, x21"),
 0x69484:("bl","0x140003918 <.text+0x2918>"),
 0x3944:("lsl","w1, w19, #3"),
 0x3950:("str","x0, [x20, #0x20]"),
 0x3960:("str","x0, [x20, #0x28]"),
 0x3970:("str","x0, [x20, #0x30]"),
 0x3980:("str","x0, [x20, #0x38]"),
 0x3990:("str","x0, [x20]"),
 0x39a0:("str","x0, [x20, #0x8]"),
 0x69578:("adrp","x8, 0x14003f000"),
 0x696d8:("bl","0x1400153c0 <.text+0x143c0>"),
 0x69708:("bl","0x1400153e8 <.text+0x143e8>"),
 0x697cc:("bl","0x140015628 <.text+0x14628>"),
 0x697d0:("mov","x8, #0x30"),
 0x697d4:("smaddl","x19, w20, w8, x26"),
 0x697e4:("str","x8, [x19, #0x10]"),
 0x697f8:("add","x0, x19, #0x8"),
 0x69818:("bl","0x140015698 <.text+0x14698>"),
 0x69820:("bl","0x1400156e8 <.text+0x146e8>"),
 0x6982c:("cbz","x27, 0x1400699ec <PAGE+0x9ec>"),
 0x69854:("str","xzr, [x19, #0x18]"),
 0x69870:("stp","w8, wzr, [x19, #0x20]"),
 0x69874:("ldr","w8, [x27, #0x4]"),
 0x69878:("str","w8, [x19, #0x28]"),
 0x6987c:("add","x8, x24, w21, sxtw #4"),
 0x69880:("str","x8, [x19, #0x30]"),
 0x6989c:("ldr","x9, [x27, #0x10]"),
 0x698a0:("ldr","x9, [x9, w8, sxtw #3]"),
 0x698a8:("stp","x9, xzr, [x6]"),
 0x698b4:("b.lt","0x140069894 <PAGE+0x894>"),
 0x69bfc:("bl","0x140015768 <.text+0x14768>"),
 0x15794:("adrp","x24, 0x14004a000"),
 0x15798:("str","x20, [x24, #0xe88]"),
 0x1586c:("str","x0, [x8, #0x30]"),
 0x15888:("str","x0, [x8, #0x40]"),
 0x158a8:("str","x0, [x20, x21]"),
 0x15f08:("ldr","x8, [x27]"),
 0x15f14:("ldr","x8, [x8, x9]"),
 0x15f1c:("ldr","x0, [x10, x8]"),
 0x15fac:("mov","x8, #0x30"),
 0x15fb0:("umaddl","x9, w19, w8, x9"),
 0x15fbc:("ldr","x0, [x9, #0x8]"),
 0x15fec:("blr","x15"),
 0x16380:("ldr","x8, [x10, #0x30]"),
 0x16384:("umaddl","x8, w21, w9, x8"),
 0x16388:("ldrb","w8, [x8, #0x20]"),
 0x163a4:("umaddl","x8, w21, w9, x8"),
 0x163b0:("ldr","x0, [x8, #0x8]"),
 0x163c8:("blr","x15"),
 0x16408:("ldr","x8, [x8, #0x30]"),
 0x16418:("umaddl","x8, w21, w9, x8"),
 0x1641c:("ldr","x0, [x8, #0x8]"),
 0x16434:("blr","x15"),
 0x1647c:("ldr","x8, [x8, x9]"),
 0x16480:("ldr","x0, [x10, x8]"),
 0x164b4:("blr","x15"),
}

def ensure(ok,reason):
    if not ok:raise AssertionError("E004OF_FAIL_CLOSED "+reason)

def get_asm():
    output=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    return {int(m.group(1),16)-BASE:(m.group(2),m.group(3).split("//",1)[0].strip())
            for m in rx.finditer(output)}

def result():
    return {
      "schema":"sp11-e004of-isp-per-core-interface-creation-consumption-static-v1",
      "parent_git_revision":"334bb32f87612a1f483caa6374016598de86ee29",
      "original_same_SP11_OEM_ISP_sha256":SHA,
      "source_locked_original_ARM64_instruction_anchors":len(ANCHORS),
      "manager_array_allocation_caller_RVA":"0x69484",
      "manager_array_allocation_helper_RVA":"0x3918",
      "manager_global_core_array_initializer_caller_RVA":"0x69bfc",
      "manager_global_core_array_initializer_RVA":"0x15768",
      "dynamic_core_interface_description_lookup_RVA":"0x69820",
      "per_core_record_stride_bytes":0x30,
      "per_core_record_instance_pointer_field_offset_bytes":0x8,
      "per_core_record_callback_vector_field_offset_bytes":0x30,
      "per_core_callback_table_copy_RVA":"0x698a8",
      "core_stage_manager_original_ISP_callback_RVA":"0x15d70",
      "per_core_consumer_0x804_IFE_RVA":"0x15fec",
      "per_core_consumer_0x805_CSID_RVA":"0x163c8",
      "per_core_consumer_0x805_IFE_RVA":"0x16434",
      "per_core_consumer_0x805_CDM_RVA":"0x164b4",
      "core_interface_arrays_allocated_with_source_checked_bounds":True,
      "per_core_producer_imports_descriptors_and_stores_individual_callable_pointers":True,
      "per_core_manager_indexes_and_null_checks_before_indirect_dispatch":True,
      "exact_specific_IFE_CSID_CDM_first_callback_bodies_identified":False,
      "returned_0x804_0x805_per_core_parameter_ABI_and_HW_effects_fully_decoded":False,
      "active_windows_rear_4k_backend_and_actual_ISP_stage_set_observed":False,
      "selector_0x809_real_receiving_core_and_semantics_proven":False,
      "WM16_BF_live_completion_or_verified_stop_DMA_drain_observed":False,
      "Linux_native_rear_4k_processed_ISP_optical_frame_proven":False,
      "Golden_or_camera_device_modified":False,
      "private_original_OEM_binary_code_or_optical_data_exported":False,
    }

def assert_conservative(j):
    ensure(j==result(),"saved scalar schema/source or unverified claim changed")
    for x in ("exact_specific_IFE_CSID_CDM_first_callback_bodies_identified",
              "returned_0x804_0x805_per_core_parameter_ABI_and_HW_effects_fully_decoded",
              "active_windows_rear_4k_backend_and_actual_ISP_stage_set_observed",
              "selector_0x809_real_receiving_core_and_semantics_proven",
              "WM16_BF_live_completion_or_verified_stop_DMA_drain_observed",
              "Linux_native_rear_4k_processed_ISP_optical_frame_proven"):
        ensure(j[x] is False,x)
    return True

if __name__=="__main__":
    ensure(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"exact original ISP SHA")
    a=get_asm()
    for offset,instruction in ANCHORS.items():
        ensure(a.get(offset)==instruction,
               f"original ISA instruction {offset:#x}: {a.get(offset)} vs {instruction}")
    j=result()
    saved=HERE/"RESULT.json"
    if not saved.exists():
        saved.write_text(json.dumps(j,sort_keys=True,indent=2)+"\n")
        print("E004OF_SAFE_SCALAR_RESULT_CREATED")
    else:
        ensure(json.loads(saved.read_text())==j,"persisted original source scalar mismatch")
    tests=(
      ("fake_sha",lambda k:k.__setitem__("original_same_SP11_OEM_ISP_sha256","0"*64)),
      ("fake_pointers",lambda k:k.__setitem__("per_core_record_callback_vector_field_offset_bytes",0x40)),
      ("fake_stride",lambda k:k.__setitem__("per_core_record_stride_bytes",0x28)),
      ("fake_no_producer",lambda k:k.__setitem__("per_core_producer_imports_descriptors_and_stores_individual_callable_pointers",False)),
      ("fake_no_bounds",lambda k:k.__setitem__("core_interface_arrays_allocated_with_source_checked_bounds",False)),
      ("fake_no_null_check",lambda k:k.__setitem__("per_core_manager_indexes_and_null_checks_before_indirect_dispatch",False)),
      ("fake_callback",lambda k:k.__setitem__("per_core_consumer_0x805_CSID_RVA","0x163c4")),
      ("fake_IFE_implementation",lambda k:k.__setitem__("exact_specific_IFE_CSID_CDM_first_callback_bodies_identified",True)),
      ("fake_full_ABI",lambda k:k.__setitem__("returned_0x804_0x805_per_core_parameter_ABI_and_HW_effects_fully_decoded",True)),
      ("fake_selected_profile",lambda k:k.__setitem__("active_windows_rear_4k_backend_and_actual_ISP_stage_set_observed",True)),
      ("fake_809",lambda k:k.__setitem__("selector_0x809_real_receiving_core_and_semantics_proven",True)),
      ("fake_WM16",lambda k:k.__setitem__("WM16_BF_live_completion_or_verified_stop_DMA_drain_observed",True)),
      ("fake_native_4k",lambda k:k.__setitem__("Linux_native_rear_4k_processed_ISP_optical_frame_proven",True)),
      ("fake_golden_edit",lambda k:k.__setitem__("Golden_or_camera_device_modified",True)),
      ("fake_private_export",lambda k:k.__setitem__("private_original_OEM_binary_code_or_optical_data_exported",True)),
    )
    for name,mutate in tests:
        mutant=copy.deepcopy(j)
        mutate(mutant)
        try:assert_conservative(mutant)
        except (AssertionError,KeyError,TypeError):
            continue
        raise AssertionError("E004OF_FAIL_OPEN_NEGATIVE "+name)
    print(f"PASS_E004OF_SAME_SP11_SOURCE_{len(ANCHORS)}_ORIGINAL_ARM64_ANCHORS_"
          f"{len(tests)}_FAIL_CLOSED_NEGATIVES_"
          "CORE_INTERFACE_PRODUCER_RECORD_COPY_AND_MANAGER_CONSUMPTION_"
          "RECEIVING_CORE_IMPLEMENTATIONS_REMAIN_UNPROVEN_GOLDEN_SAFE")
