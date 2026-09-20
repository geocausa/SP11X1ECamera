#!/usr/bin/env python3
"""E004hu: read-only original installed-version UEFI PMIC/SPMI code provenance.

The ORIGINAL archive's package version matches the BIOS VERSION OBSERVED on
2026-09-20. A DMI version match does not establish byte parity with the
actually running flash firmware or execution of a firmware function.

Checks exact original UEFI capsule, original extracted two ARM64 PE images and
all extracted UEFI PE payloads for EXPLICIT literal timer address sequences.
An absent 32-bit literal/table NEVER proves no firmware timer initialization:
computed addresses, other boot stages, compressed data, external PMC/PBS
firmware, other engines or silicon reset default remain possible.
No firmware flashing/UEFI-variable writes, PMIC read/writes or LED activation.
"""
from pathlib import Path
from hashlib import sha256
import json
import pefile
import struct

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/recovered-adata/ubi/Documents/SP11/uefi_firmware_peek/surface-uefi-175.222.235-from-windows")
CAPSULE=SOURCE/"Surface_UEFI_175.222.235.bin"
REPORT=SOURCE/"7z-extract/18438CF9.report.txt"
DUMP=SOURCE/"7z-extract/18438CF9.dump"
VERSION="175.222.235"
CAPSULE_SHA="2908e3152b5d3c6141c34114bfee39a15f5e94f20acfe1c49be6a5084ec8cb47"
EXTRACT_SHA={
    "PmicDxe":"402315711a6761441234eac8c0cd3c0ad23cb4fdb7d0a9de3dd94c3ffac38dff",
    "SPMI":"62b53f5daaf46e016962895ff19f26b7449b4566c9859ad3140e2748f87f3ef0",
}
FFS_GUIDS={
    "PmicDxe":"C44697D5-B4AA-4030-9749-29860844183D",
    "SPMI":"2A7B4BEF-80CD-49E1-B473-374BA4D673FC",
}
EXPECTED_PE_COUNT=255
EXPECTED_CAPSULE_SIZE=13608082
TIMER_ADDRESSES=tuple(range(0xee3e,0xee42))
PATTERNS={
    "four_channel_dword_le":b"".join(struct.pack("<I",n) for n in TIMER_ADDRESSES),
    "four_channel_word_le":b"".join(struct.pack("<H",n) for n in TIMER_ADDRESSES),
    "four_channel_byte_low_only":bytes((0x3e,0x3f,0x40,0x41)),
    "first_timer_dword_le":struct.pack("<I",TIMER_ADDRESSES[0]),
    "four_adjacent_0x93_bytes":bytes((0x93,))*4,
}
def require(ok,why):
    if not ok:raise AssertionError("E004HU_FAIL_CLOSED "+why)

def exact_pe(path,expected_sha):
    raw=path.read_bytes()
    require(sha256(raw).hexdigest()==expected_sha,
            "original archived ARM64 PE SHA changed "+path.parent.parent.name)
    pe=pefile.PE(data=raw,fast_load=True)
    require(pe.FILE_HEADER.Machine==0xaa64 and
            pe.OPTIONAL_HEADER.AddressOfEntryPoint==0x1000 and
            pe.OPTIONAL_HEADER.ImageBase==0,
            "not original expected UEFI ARM64 PE "+path.parent.parent.name)
    return raw

def module_path(files,name):
    matches=[p for p in files if p.parent.parent.name.endswith(" "+name)]
    require(len(matches)==1,"original UEFI "+name+" PE is missing/ambiguous")
    return matches[0]

def scan(fw,modules):
    require(len(fw)==EXPECTED_CAPSULE_SIZE and
            sha256(fw).hexdigest()==CAPSULE_SHA,
            "original 175.222.235 UEFI capsule identity changed")
    require(len(modules)==EXPECTED_PE_COUNT,
            "original extracted UEFI PE inventory incomplete/changed")
    require(len({p.resolve() for p in modules})==EXPECTED_PE_COUNT,
            "original extracted UEFI PE paths duplicated")
    report=REPORT.read_text(errors="replace")
    for name,guid in FFS_GUIDS.items():
        lines=[s for s in report.splitlines() if
               guid in s and s.rstrip().endswith("| "+name)]
        require(len(lines)==1 and "DXE driver" in lines[0],
                "original firmware FFS provenance not pinned "+name)
    image_result={}
    for name in ("PmicDxe","SPMI"):
        path=module_path(modules,name)
        raw=exact_pe(path,EXTRACT_SHA[name])
        image_result[name]={
            "raw_sha256":sha256(raw).hexdigest(),
            "image_bytes":len(raw),
            "original_ffs_guid":FFS_GUIDS[name],
            "arm64_uefi_pe":True,
            "explicit_first_timer_address_16bit_le_hits":raw.count(
                struct.pack("<H",TIMER_ADDRESSES[0])),
            "explicit_first_timer_address_32bit_le_hits":raw.count(
                PATTERNS["first_timer_dword_le"]),
            "explicit_contiguous_four_timer_addresses_dword_le_hits":raw.count(
                PATTERNS["four_channel_dword_le"]),
        }
        require(image_result[name]["explicit_first_timer_address_16bit_le_hits"]==0 and
                image_result[name]["explicit_first_timer_address_32bit_le_hits"]==0 and
                image_result[name]["explicit_contiguous_four_timer_addresses_dword_le_hits"]==0,
                "original "+name+" actually has a literal timer address")
    pmic=module_path(modules,"PmicDxe").read_bytes()
    require(b"pm_pmicdxe_init" in pmic and
            b"pm_comm_spmi_lite.c" in pmic and
            b"SPMI_WR" in pmic and b"SPMI_RD" in pmic,
            "original PmicDxe does not contain expected actual PMIC/SPMI functionality")
    # The original capsule contains compressed/nested data and opcode bytes:
    # 16-bit 0xee3e alone is NOT discriminating, even near 0x93.
    occurrences={name:fw.count(pattern) for name,pattern in PATTERNS.items()}
    require(occurrences=={
        "four_channel_dword_le":0,
        "four_channel_word_le":0,
        "four_channel_byte_low_only":0,
        "first_timer_dword_le":0,
        "four_adjacent_0x93_bytes":0,
    },"original capsule's explicit literal timer-table signature changed")
    word16=struct.pack("<H",TIMER_ADDRESSES[0])
    sixteen_bit_hits=fw.count(word16)
    require(sixteen_bit_hits==95,
            "raw capsule 16-bit address-byte count no longer original")
    pe_hits={key:[] for key in PATTERNS}
    for path in modules:
        raw=path.read_bytes()
        for label,pattern in PATTERNS.items():
            count=raw.count(pattern)
            if count:
                pe_hits[label].append((path.parent.parent.name,count))
    require(len(pe_hits["first_timer_dword_le"])==0 and
            len(pe_hits["four_channel_dword_le"])==0 and
            len(pe_hits["four_channel_word_le"])==0 and
            len(pe_hits["four_adjacent_0x93_bytes"])==0 and
            len(pe_hits["four_channel_byte_low_only"])==2,
            "changed original firmware PE section literal count (NOT a writer inference)")
    require(set(name for name,_ in pe_hits["four_channel_byte_low_only"])==
            {"112 UsbKbDxe","20 HidKeyboardDxe"},
            "original incidental 4-byte low-sequence modules changed")
    return {
        "original_capsule_sha256":CAPSULE_SHA,
        "original_capsule_bytes":EXPECTED_CAPSULE_SIZE,
        "original_firmware_version":VERSION,
        "original_extracted_arm64_pe_image_count":EXPECTED_PE_COUNT,
        "original_pmic_spmi_uefi_modules":image_result,
        "pmic_dxe_contains_pmic_spmi_init_and_write_functionality_strings":True,
        "capsule_exact_literal_signature_occurrences":occurrences,
        "capsule_undifferentiated_two_byte_ee3e_hits":sixteen_bit_hits,
        "all_extracted_pe_exact_literal_hits":{
            label:[{"module":name,"occurrences":count} for name,count in hits]
            for label,hits in pe_hits.items()},
        "literal_16bit_ee3e_hits_prove_pmic_timer_access":False,
        "literal_table_absence_rules_out_computed_or_indirect_firmware_timer_writer":False,
        "archived_capsule_version_matches_current_running_bios_version_as_observed":True,
        "archived_capsule_bytes_equals_running_firmware_bytes_verified":False,
        "firmware_pmic_or_spmi_driver_initializes_timer_ee3e_in_actual_boot_proven":False,
        "original_first_0x93_timer_writer_identified":False,
        "actual_hw_reset_value_or_independent_led_cutoff_established":False,
    }

def prior():
    p=ROOT/"experiments/E004-front-ir-vd55g0/e004ht-common-spmi-controller-live-kd/evidence/RESULT.json"
    r=json.loads(p.read_text())
    require(r["status"]==
            "PASS_FRESH_EARLY_WINDOWS_COMMON_SPMI_CONTROLLER_READ_POSITIVE_PERSISTENT_FILTERED_WRITE_TIMER_NONHIT_GOLDEN_RETURN" and
            r["first_original_idle_timer_0x93_writer_identified"] is False and
            r["native_linux_ir_emitter_pam_or_login_modified"] is False,
            "original E004ht consumed runtime trace scope changed")
    return sha256(p.read_bytes()).hexdigest()

def main():
    import datetime
    require(Path("/sys/class/dmi/id/bios_version").read_text().strip()==VERSION,
            "SP11 current firmware version differs from the archived UEFI image")
    fw=CAPSULE.read_bytes()
    modules=sorted(p for p in DUMP.rglob("body.bin")
                   if "PE32 image section" in p.parent.name)
    record=scan(fw,modules)
    result={
        "experiment":"E004hu",
        "status":"PASS_CURRENT_VERSION_MATCHED_ARCHIVED_SP11_UEFI_PMIC_SPMI_EXPLICIT_TIMER_LITERAL_AUDIT_OFFLINE",
        "date":"2026-09-20",
        "source_checkpoint":"311aebe31836e64c9bebf7da7dd39f4f34fc793b",
        "live_sp11_golden_bios_version_at_audit":VERSION,
        "original_previous_e004ht_result_sha256":prior(),
        "original_uefi_firmware_bounded_audit":record,
        "new_windows_boot_or_kd_spmi_pmic_camera_led_login_activity":False,
        "firmware_flashing_or_uefi_mutation":False,
        "native_ir_emitter_authorized":False,
        "golden_modified":False,
        "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_firmware.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004HU_ACTUAL_RUNNING_BIOS_VERSION_MATCHED_ARCHIVED_175_222_235_CAPSULE=PASS")
    print("E004HU_ORIGINAL_UEFI_SPMI_AND_PMIC_DXE_ARM64_PE_PROVENANCE=PASS")
    print("E004HU_255_PE_NO_EXPLICIT_32BIT_TIMER_ADDRESS_OR_FOUR_CHANNEL_LITERAL_TABLE=PASS")
    print("E004HU_FIRST_0X93_WRITER_UNKNOWN_NO_RESET_VALUE_OR_HARDWARE_CUTOFF_PROOF=PASS")

if __name__=="__main__":main()
