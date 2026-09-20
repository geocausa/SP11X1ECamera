#!/usr/bin/env python3
"""E004hx: bounded original UEFI PmicDxe runtime descriptor provenance.

No PMIC, firmware, boot, SPMI, camera or emitter activity. A static image's
zeroed runtime pointers cannot identify their live initialized values.
"""
import importlib.util
import json
import struct
from hashlib import sha256
from pathlib import Path

HERE=Path(__file__).resolve().parent
HW=HERE.parent/"e004hw-uefi-pmic-protocol-owner-static"
S=importlib.util.spec_from_file_location("e004hw_parent",HW/"verify_protocol.py")
assert S and S.loader
hw=importlib.util.module_from_spec(S)
S.loader.exec_module(hw)
HV=hw.hv
INSTRUCTIONS={
  0x12184:("mov","w0, w21"),
  0x12188:("bl","#0x12a98"),
  0x1218c:("mov","x21, x0"),
  0x1221c:("ldp","x11, x8, [x21]"),
  0x12228:("ldrh","w9, [x21, #0x20]"),
  0x1222c:("ldrh","w10, [x8]"),
  0x12230:("ldrh","w8, [x8, #2]"),
  0x12234:("add","w9, w9, w22"),
  0x1223c:("madd","w9, w23, w10, w9"),
  0x12240:("add","w1, w8, w9"),
  0x12244:("bl","#0x8cd0"),
  0x12aa8:("bl","#0x12764"),
  0x12b18:("cmp","w19, #0xd"),
  0x12b20:("adrp","x8, #0x39000"),
  0x12b24:("add","x8, x8, #0xef0"),
  0x12b28:("ldr","x0, [x8, w19, uxtw #3]"),
  0x12790:("ldrb","w8, [x8, #0xee8]"),
  0x12794:("tbnz","w8, #0, #0x12a74"),
  0x12798:("bl","#0x156cc"),
  0x1280c:("bl","#0x131b0"),
  0x12818:("bl","#0x14848"),
  0x12824:("mov","w0, #0x41"),
  0x12828:("bl","#0x13270"),
  0x12830:("mov","w0, #0x42"),
  0x12834:("bl","#0x13270"),
  0x128f4:("mov","w0, #0x3c"),
  0x128fc:("bl","#0x13290"),
  0x12908:("ldrh","w8, [x19, x24, lsl #1]"),
  0x129a4:("ldrh","w8, [x19, x24, lsl #1]"),
  0x129ac:("ldrh","w9, [x28, #0xed8]"),
  0x129b8:("madd","w8, w9, w10, w8"),
  0x129c0:("bl","#0x131e8"),
  0x129c8:("ldrb","w8, [sp, #0x12]"),
  0x129cc:("cmp","w8, #0x2e"),
  0x129dc:("mov","w2, w26"),
  0x129e0:("bl","#0x1236c"),
  0x12390:("mov","w19, w2"),
  0x12410:("add","x23, x23, #0xef0"),
  0x12414:("ldr","x22, [x23, w19, uxtw #3]"),
  0x12424:("ldrh","w9, [x21]"),
  0x12428:("ldrh","w8, [x22, #0x20]"),
  0x1242c:("ldrh","w10, [x10, #0xed8]"),
  0x12430:("sub","w11, w9, w8"),
  0x12438:("sdiv","w19, w11, w10"),
  0x124bc:("mov","w0, #0x3c"),
  0x124c4:("bl","#0x13290"),
  0x12554:("ldrh","w9, [x21]"),
  0x12558:("strh","w9, [x8, #0x20]"),
  0x125f0:("add","x9, x9, #0xed8"),
  0x125fc:("add","x1, x8, #0x18"),
  0x12600:("str","x9, [x8, #8]"),
  0x12628:("ldp","x13, x11, [x22]"),
  0x12630:("ldrh","w12, [x11]"),
  0x12634:("ldrh","w11, [x11, #8]"),
  0x12638:("ldr","w0, [x13]"),
  0x12640:("add","w1, w8, w11"),
  0x12644:("bl","#0x8a80"),
  0x126f4:("ldr","x9, [x8, #0x28]"),
  0x12748:("str","x8, [x23, x19, lsl #3]"),
}
def require(ok,msg):
    if not ok:raise AssertionError("E004HX_FAIL_CLOSED "+msg)
def inspect(pe):
    require(pe.FILE_HEADER.Machine==0xaa64 and pe.OPTIONAL_HEADER.ImageBase==0,
            "not original zero-base ARM64 firmware PE")
    for a,expected in INSTRUCTIONS.items():
        require(HV.instr(pe,a)==expected,"original instruction drift "+hex(a))
    require(struct.unpack("<HH",pe.get_data(0x2fed8,4))==(0x100,0x40),
            "original static fallback descriptor stride/additional offset changed")
    require(pe.get_data(0x39ef0,14*8)==bytes(14*8),
            "original on-disk uninitialized per-device descriptor pointer array changed")
    require(pe.get_data(0x39ee8,1)==b"\0",
            "original on-disk lazy-init flag changed")
    require(HV.direct_bl_sites(pe,0x1236c)==[0x129e0,0x26670],
            "original per-device descriptor initializer call inventory drift")
    require(HV.direct_bl_sites(pe,0x131e8)==[0x129c0,0x26404],
            "original metadata-read helper caller inventory drift")
    periph=0x0e; rel=0x3e; stride=0x100; additional=0x40
    offset=periph*stride+rel+additional
    target=0xee3e
    return {
      "lazy_init_entry_rva":"0x12764",
      "descriptor_getter_rva":"0x12a98",
      "on_disk_uninitialized_descriptor_index0_to13_all_zero":True,
      "on_disk_uninitialized_lazy_flag_zero":True,
      "original_per_device_init_iterates_discovered_tables":True,
      "per_device_init_consumes_runtime_or_firmware_looked_up_records":True,
      "per_device_candidate_init_rva":"0x1236c",
      "per_device_descriptor_store_to_indexed_array_rva":"0x12748",
      "dynamically_sourced_descriptor_base_halfword_stored_at_offset_0x20_rva":"0x12558",
      "on_this_distinct_original_fallback_path_template_rva":"0x2fed8",
      "on_this_distinct_original_fallback_path_stride_hex":hex(stride),
      "on_this_distinct_original_fallback_path_additional_offset_hex":hex(additional),
      "on_this_distinct_original_fallback_path_template_pointer_store_rva":"0x12600",
      "other_existing_descriptor_path_uses_separate_original_metadata_rva":"0x12628",
      "on_template_path_candidate_second_write_address_expression":"discovered_device_base + (0x0e * 0x0100) + 0x3e + 0x40",
      "on_template_path_candidate_second_write_offset_above_discovered_base_hex":hex(offset),
      "on_template_path_required_base_if_second_address_were_0xee3e_hex":hex(target-offset),
      "original_discovered_device_base_value_on_sp11_observed":False,
      "original_descriptor_fallback_path_executed_on_sp11_proven":False,
      "original_candidate_protocol_method_invoked_on_sp11_proven":False,
      "original_candidate_second_write_address_ee3e_proven":False,
      "original_candidate_input_value_0x93_proven":False,
      "physical_emitter_cutoff_proven":False
    }
def main():
    prev=HW/"evidence/RESULT.json"
    prior=json.loads(prev.read_text())
    require(prior["status"]==
      "PASS_ORIGINAL_UEFI_PMIC_PUBLISHED_PROTOCOL_OWNER_AND_RUNTIME_DESCRIPTOR_BOUNDARY_OFFLINE",
      "original prior protocol-owner checkpoint missing")
    pe=HV.original_image()
    out={
     "experiment":"E004hx",
     "status":"PASS_ORIGINAL_UEFI_PMIC_RUNTIME_DESCRIPTOR_LAZY_INIT_AND_FALLBACK_ADDRESS_BOUND_OFFLINE",
     "date":"2026-09-20",
     "baseline_commit":"f5b54ca525e91fe9d9e79f8ec8cec7305a50ea90",
     "original_firmware_pe_sha256":HV.PE_SHA,
     "e004hw_result_sha256":sha256(prev.read_bytes()).hexdigest(),
     "static_runtime_descriptor_provenance":inspect(pe),
     "no_firmware_boot_camera_spmi_pmic_emitter_or_login_activity":True,
     "golden_boot_kernel_login_modified":False,
     "native_ir_emitter_authorized":False,
     "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
     "negative_test_sha256":sha256((HERE/"test_descriptor.py").read_bytes()).hexdigest()
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(out,indent=2)+"\n")
    print("E004HX_ORIGINAL_PMIC_DXE_RUNTIME_DESCRIPTOR_LAZY_INIT_STATIC=PASS")
    print("E004HX_FALLBACK_TEMPLATE_STRIDE_0100_OFFSET_0040_STATIC=PASS")
    print("E004HX_ACTUAL_DEVICE_BASE_CALLER_VALUE_EE3E_TIMER_WRITER_HARDWARE_OFF=UNPROVEN")
if __name__=="__main__":main()
