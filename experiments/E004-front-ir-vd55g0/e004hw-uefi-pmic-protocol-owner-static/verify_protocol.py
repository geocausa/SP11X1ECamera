#!/usr/bin/env python3
"""E004hw: original UEFI PMIC protocol owner and runtime-descriptor boundary.
Offline SHA-pinned read of an existing OEM firmware archive. No device writes.
"""
import importlib.util
import json
import struct
from hashlib import sha256
from pathlib import Path

import capstone
import pefile

HERE = Path(__file__).resolve().parent
HV = HERE.parent / "e004hv-firmware-indirect-computed-peripheral-write"
MODULE = importlib.util.spec_from_file_location("original_hv", HV / "verify_indirect.py")
assert MODULE and MODULE.loader
hv = importlib.util.module_from_spec(MODULE)
MODULE.loader.exec_module(hv)
GUID_INTERFACE_RVA = 0x2f190
GUID_OTHER_RVA = 0x2f2b0
GUID_INTERFACE = bytes.fromhex("6ee96aae3f48ae429cc19fac1b584728")
GUID_OTHER = bytes.fromhex("584b0497a4fed04a9d0be417d60f11a1")
EXPECTED_IMAGE_COUNT = 255
EXPECTED_PROTOCOL_GUID_IMAGES = 13
# Pinned original instruction identities, with no assumption that execution occurred.
INSTRUCTIONS = {
    0x19ec: ("mov", "x1, x19"),
    0x19f0: ("bl", "#0x15394"),
    0x1a54: ("mov", "x1, x19"),
    0x1a58: ("bl", "#0x15394"),
    0x153a0: ("adrp", "x8, #0x39000"),
    0x153a4: ("adrp", "x1, #0x2f000"),
    0x153a8: ("adrp", "x2, #0x2f000"),
    0x153ac: ("adrp", "x3, #0x2f000"),
    0x153b0: ("adrp", "x4, #0x38000"),
    0x153b8: ("ldr", "x8, [x8, #0x108]"),
    0x153bc: ("add", "x1, x1, #0x2b0"),
    0x153c0: ("add", "x2, x2, #0x4d0"),
    0x153c4: ("add", "x3, x3, #0x190"),
    0x153c8: ("add", "x4, x4, #0xb58"),
    0x153cc: ("add", "x0, sp, #8"),
    0x153d0: ("mov", "x5, xzr"),
    0x153d4: ("ldr", "x8, [x8, #0x148]"),
    0x153d8: ("blr", "x8"),
    0x2003c: ("adrp", "x9, #0x3a000"),
    0x20048: ("adrp", "x9, #0x38000"),
    0x20050: ("ldr", "x11, [x9, #0xb50]"),
    0x2005c: ("ldr", "x9, [x9, #0xb50]"),
    0x20064: ("str", "x9, [x8]"),
    0x12b18: ("cmp", "w19, #0xd"),
    0x12b20: ("adrp", "x8, #0x39000"),
    0x12b24: ("add", "x8, x8, #0xef0"),
    0x12b28: ("ldr", "x0, [x8, w19, uxtw #3]"),
    0x12188: ("bl", "#0x12a98"),
    0x12228: ("ldrh", "w9, [x21, #0x20]"),
    0x1222c: ("ldrh", "w10, [x8]"),
    0x12230: ("ldrh", "w8, [x8, #2]"),
    0x1223c: ("madd", "w9, w23, w10, w9"),
    0x12240: ("add", "w1, w8, w9"),
    0x12244: ("bl", "#0x8cd0"),
}
def require(ok, message):
    if not ok:
        raise AssertionError("E004HW_FAIL_CLOSED " + message)

def check_original(pe):
    require(pe.FILE_HEADER.Machine == 0xaa64 and pe.OPTIONAL_HEADER.ImageBase == 0,
            "not original zero-based ARM64 UEFI image")
    for address, expected in INSTRUCTIONS.items():
        require(hv.instr(pe, address) == expected,
                "original firmware instruction changed at " + hex(address))
    require(pe.get_data(GUID_INTERFACE_RVA, 16) == GUID_INTERFACE,
            "published original interface GUID changed")
    require(pe.get_data(GUID_OTHER_RVA, 16) == GUID_OTHER,
            "neighbor original interface GUID changed")
    require(GUID_INTERFACE != GUID_OTHER, "two published original GUIDs conflated")
    require(struct.unpack("<Q", pe.get_data(0x38d98, 8))[0] == 0x222f8,
            "original candidate method pointer changed")
    require(0x38d98 - 0x38b58 == 0x240, "original method slot not at published interface offset")
    require(struct.unpack("<Q", pe.get_data(0x38b50, 8))[0] == 0x38b18,
            "original PMIC alternate descriptor pointer changed")
    require(pe.get_data(0x39ef0, 14 * 8) == bytes(14 * 8),
            "archived uninitialized per-device descriptor pointer array changed")
    require(hv.direct_bl_sites(pe, 0x15394) == [0x19f0, 0x1a58],
            "original initializer direct-call inventory changed")
    require(hv.direct_bl_sites(pe, 0x2003c) == [0x1f3a8],
            "original descriptor getter direct-call inventory changed")
    require(not hv.direct_bl_sites(pe, 0x222f8),
            "original indirect computed-address method acquired direct call")
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_BASERELOC"]])
    reloc = [(entry.rva, entry.type) for block in pe.DIRECTORY_ENTRY_BASERELOC
             for entry in block.entries if entry.rva == 0x38d98]
    require(reloc == [(0x38d98, 10)], "original function-table pointer relocation changed")
    return {
        "uefi_pmic_entry_initialization_install_wrapper_call_sites": ["0x19f0", "0x1a58"],
        "original_install_wrapper_rva": "0x15394",
        "boot_services_indirect_method_table_offset": "0x148",
        "boot_services_uefi_abi_candidate": "InstallMultipleProtocolInterfaces",
        "published_interface_guid": "ae6ae96e-483f-42ae-9cc1-9fac1b584728",
        "published_interface_table_rva": "0x38b58",
        "published_interface_candidate_method_slot": "0x240",
        "candidate_method_pointer_rva": "0x38d98",
        "candidate_method_target_rva": "0x222f8",
        "candidate_method_pointer_relocation_type": 10,
        "other_published_protocol_guid": "97044b58-fea4-4ad0-9d0b-e417d60f11a1",
        "other_published_protocol_interface_rva": "0x2f4d0",
        "separate_descriptor_getter_rva": "0x2003c",
        "separate_descriptor_getter_initialization_caller_rva": "0x1f3a8",
        "original_14_device_descriptor_slots_at_0x39ef0_in_archived_pe_all_zero": True,
        "runtime_descriptor_lookup_rvas": ["0x12b20", "0x12b24", "0x12b28"],
        "computed_writer_uses_runtime_descriptor_from_index_zero": True,
        "original_published_interface_method_invoked_on_this_sp11_boot_proven": False,
        "original_runtime_descriptor_bytes_observed": False,
        "original_timer_0xee3e_write_or_0x93_writer_identified": False,
        "independent_emitter_hardware_fault_cutoff_proven": False
    }

def scan_consumer_images():
    paths = sorted(p for p in hv.previous.DUMP.rglob("body.bin")
                   if "PE32 image section" in p.parent.name)
    require(len(paths) == EXPECTED_IMAGE_COUNT, "original firmware executable inventory changed")
    matches, other_matches = [], []
    for path in paths:
        data = path.read_bytes()
        if GUID_INTERFACE in data:
            require(data.count(GUID_INTERFACE) == 1, "ambiguous repeated interface GUID in image")
            matches.append(path.parent.parent.name)
        if GUID_OTHER in data:
            other_matches.append(path.parent.parent.name)
    require(len(matches) == EXPECTED_PROTOCOL_GUID_IMAGES,
            "original protocol GUID consumer image count drift")
    require(other_matches == ["41 PmicDxe"],
            "original neighboring interface GUID unexpectedly published elsewhere")
    require("41 PmicDxe" in matches and "78 QcomChargerDxeWp" in matches and
            "97 DisplayDxe" in matches and "88 BdsDxe" in matches,
            "expected original firmware consumers missing")
    return {
        "original_pe_images_scanned": len(paths),
        "interface_guid_present_in_image_count_including_provider": len(matches),
        "interface_guid_present_in_image_names": sorted(matches),
        "other_interface_guid_present_only_in_provider": True,
        "presence_of_guid_is_not_proof_of_method_offset_0x240_invocation": True
    }

def main():
    result_file = HV / "evidence/RESULT.json"
    old = json.loads(result_file.read_text())
    require(old["status"] ==
            "PASS_ORIGINAL_CURRENT_VERSION_UEFI_PMIC_INDIRECT_COMPUTED_PERIPHERAL_WRITE_2BYTE_OFFSET_3E_OFFLINE",
            "missing prior pinned firmware experiment")
    pe = hv.original_image()  # previous stage independently SHA-pins PmicDxe
    result = {
        "experiment": "E004hw",
        "status": "PASS_ORIGINAL_UEFI_PMIC_PUBLISHED_PROTOCOL_OWNER_AND_RUNTIME_DESCRIPTOR_BOUNDARY_OFFLINE",
        "date": "2026-09-20",
        "baseline_commit": "6bfcd355daee97145aa7a87504f6adb689da3071",
        "original_pmic_sha256": hv.PE_SHA,
        "prior_e004hv_result_sha256": sha256(result_file.read_bytes()).hexdigest(),
        "protocol_owner": check_original(pe),
        "archived_original_uefi_guid_inventory": scan_consumer_images(),
        "no_sp11_reboot_camera_pmic_spmi_uefi_kd_or_emitter_activity": True,
        "golden_kernel_boot_login_state_modified": False,
        "native_ir_emitter_authorized": False,
        "verifier_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256": sha256((HERE/"test_protocol.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print("E004HW_ORIGINAL_UEFI_PMIC_DXE_PUBLISHES_INDIRECT_METHOD_SLOT_0x240=PASS")
    print("E004HW_ORIGINAL_PROVIDER_AND_12_OTHER_GUID_CONTAINING_IMAGES=PASS")
    print("E004HW_RUNTIME_DEVICE_DESCRIPTORS_AND_FIRST_TIMER_93_WRITER_STILL_UNKNOWN")
if __name__ == "__main__":
    main()
