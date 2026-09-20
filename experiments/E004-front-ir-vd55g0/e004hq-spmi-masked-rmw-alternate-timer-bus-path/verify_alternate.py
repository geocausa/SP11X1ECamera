#!/usr/bin/env python3
"""E004hq: original SPMI provider +0x38 masked read-modify-write is NOT +0x30.

Offline, pinned original ARM64 PE and already consumed original live KD
interface dump. This demonstrates a blind spot of previous +0x1660 entry
observer without asserting +0x1920 was actually called, nor first 0x93 writer.
"""
from pathlib import Path
from hashlib import sha256
import json
import re
import zipfile
import capstone
import pefile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ARCH=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
BASE=0x140000000
SPMI_SHA="b6a5868ec2450e713b9a5ada7b4e1a4a77c77427fedf0806fe3eb6541099523c"
PMIC_SHA="756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e"
HN=ROOT/"experiments/E004-front-ir-vd55g0/e004hn-readonly-live-spmi-interface"
HP=ROOT/"experiments/E004-front-ir-vd55g0/e004hp-early-spmi-timer-span-kd"
GUID="72c96e71-eb2d-48e3-99ac-9894a59f9c4c"

def require(ok,why):
    if not ok:raise AssertionError("E004HQ_FAIL_CLOSED "+why)

def original(name,digest):
    files=list(ARCH.glob(name+".inf_*/"+name+".sys"))
    require(len(files)==1,"original Windows OEM image ambiguity "+name)
    raw=files[0].read_bytes()
    require(sha256(raw).hexdigest()==digest,"original OEM image SHA changed "+name)
    p=pefile.PE(data=raw)
    require(p.FILE_HEADER.Machine==0xaa64 and p.OPTIONAL_HEADER.ImageBase==BASE,
            "unexpected OEM PE image arch/base "+name)
    return p

def instruction(pe,rva):
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    ins=list(cs.disasm(pe.get_data(rva,4),BASE+rva))
    require(len(ins)==1,"original OEM ARM64 instruction missing "+hex(rva))
    return ins[0].mnemonic,ins[0].op_str

PROVIDER=(
    # Original provider constructs both separate callback pointers in
    # successive slots within SAME published 0x70-byte output interface.
    (0x3e70,"adrp","x8, #0x140001000"),
    (0x3e74,"add","x9, x8, #0x660"),
    (0x3e80,"adrp","x8, #0x140001000"),
    (0x3e84,"add","x8, x8, #0x920"),
    (0x3e88,"stp","x9, x8, [sp, #0x140]"),
    (0x3f00,"add","x9, sp, #0x110"),
    (0x3f10,"stp","x9, x8, [sp, #0x78]"),
    # The alternate callback loads caller-provided 32-bit packed selector
    # w2 and the two masked-write 32-bit fields w3/w4.
    (0x1920,"pacibsp",""),
    (0x1944,"mov","w25, w1"),
    (0x194c,"mov","w20, w2"),
    (0x1950,"mov","w27, w3"),
    (0x1954,"mov","w26, w4"),
    (0x1a38,"ldr","w8, [x22, #0x18]"),
    (0x1a3c,"cbz","w8, #0x140001a54"),
    (0x1a40,"ubfx","w23, w20, #0x10, #4"),
    (0x1a44,"ubfx","w21, w20, #8, #8"),
    (0x1a48,"and","w19, w20, #0xff"),
    (0x1a4c,"ubfx","w20, w20, #0x14, #4"),
    # First controller request: read one byte into temporary SP+0x30.
    (0x1ab8,"mov","x7, #0"),
    (0x1abc,"mov","w6, #1"),
    (0x1ac4,"add","x5, sp, #0x30"),
    (0x1ad8,"mov","w0, #1"),
    (0x1b38,"bl","#0x1400064d8"),
    (0x1b3c,"cbnz","w0, #0x140001b78"),
    # Read succeeded: original mask/update before a distinct write
    # controller helper call; NEVER calls SPMI+0x1660 here.
    (0x1b40,"ldrb","w8, [sp, #0x30]"),
    (0x1b44,"mov","x7, #0"),
    (0x1b48,"mov","w6, #1"),
    (0x1b4c,"add","x5, sp, #0x30"),
    (0x1b54,"bic","w9, w8, w26"),
    (0x1b58,"and","w8, w27, w26"),
    (0x1b5c,"orr","w8, w9, w8"),
    (0x1b64,"strb","w8, [sp, #0x30]"),
    (0x1b70,"bl","#0x1400064d8"),
    (0x1b74,"cbz","w0, #0x140001bb8"),
    (0x1b78,"mov","w23, w0"),
)
CONSUMER=(
    (0x393c,"add","x3, x8, #0x10"),
    (0x3948,"add","x2, x8, #0x58"),
    (0x395c,"mov","w4, #0x70"),
    (0x3974,"blr","x15"),
    (0x23ec4,"add","x25, x8, #0x10"),
    (0x23f24,"ldr","x8, [x25, #0x30]"),
    (0x23f3c,"blr","x15"),
)
def no_spmi_1660_call(spmi):
    # This isn't a full indirect-call graph exclusion; the original
    # RMW block has two *direct* calls to +0x64d8, no direct BL +0x1660.
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    ins=list(cs.disasm(spmi.get_data(0x1920,0x1bb8-0x1920),BASE+0x1920))
    calls=[(i.address-BASE,int(i.op_str[1:],16)-BASE)
           for i in ins if i.mnemonic=="bl" and i.op_str.startswith("#")]
    require((0x1b38,0x64d8) in calls and (0x1b70,0x64d8) in calls,
            "alternate RMW lost its two distinct original controller calls")
    require(all(target!=0x1660 for at,target in calls),
            "alternate original RMW gained direct +0x1660 call")
    return [(hex(at),hex(target)) for at,target in calls]

def audit(spmi,pmic):
    import uuid
    require(spmi.get_data(0xa1d8,16)==uuid.UUID(GUID).bytes_le and
            pmic.get_data(0x37058,16)==uuid.UUID(GUID).bytes_le,
            "original SPMI/PMIC shared GUID changed")
    for rva,mn,ops in PROVIDER:
        require(instruction(spmi,rva)==(mn,ops),
                "original provider or alternate RMW instruction drift "+hex(rva))
    for rva,mn,ops in CONSUMER:
        require(instruction(pmic,rva)==(mn,ops),
                "original PMIC consumer interface instruction drift "+hex(rva))
    calls=no_spmi_1660_call(spmi)
    # The callback's computed one-byte output is (prior & ~mask) | (new&mask),
    # *not* evidence of a true Windows 0x93 timer payload.
    synthetic=(0x10 & (~0xff & 0xff)) | (0x93 & 0xff)
    require(synthetic==0x93,"synthetic RMW arithmetic fixture altered")
    return {
        "provider_original_guid":GUID,
        "provider_original_interface_size_bytes":112,
        "provider_original_interface_stack_base_hex":"0x110",
        "provider_original_direct_write_slot_offset":"0x30",
        "provider_original_direct_write_callback_rva":"0x1660",
        "provider_original_masked_rmw_slot_offset":"0x38",
        "provider_original_masked_rmw_callback_rva":"0x1920",
        "provider_original_callback_pair_store_rva":"0x3e88",
        "consumer_original_wdf_interface_size_bytes":112,
        "consumer_original_interface_struct_rva":"0x3d010",
        "consumer_original_direct_write_pointer_rva":"0x3d040",
        "consumer_original_masked_rmw_pointer_rva":"0x3d048",
        "alternate_callback_selector_argument":"w2",
        "alternate_callback_requested_value_argument":"w3",
        "alternate_callback_mask_argument":"w4",
        "alternate_controller_read_rva":"0x1b38",
        "alternate_masked_byte_composition_rvas":["0x1b54","0x1b58","0x1b5c","0x1b64"],
        "alternate_controller_write_rva":"0x1b70",
        "alternate_rmw_original_direct_calls":calls,
        "alternate_rmw_writes_without_direct_call_to_spmi_plus1660":True,
        "synthetic_0x93_possible_if_caller_supplies_mask_ff_value_93":True,
        "real_timer_caller_supplied_value_or_mask_identified":False,
        "real_rmw_callback_entry_ever_observed":False,
        "original_idle_0x93_first_writer_identified":False,
        "silicon_bus_completion_or_independent_emitter_cutoff_measured":False,
    }

def verify_prior(hnraw,hp):
    hnresult=json.loads((HN/"evidence/RESULT.json").read_text())
    require(hnresult["status"]==
            "PASS_FRESH_READ_ONLY_WINDOWS_LIVE_PMIC_SPMI_INTERFACE_CALLBACK_1660_GOLDEN_RETURN_IDLE_NONHIT" and
            hnresult["pmic_live_base"]=="fffff8033de40000" and
            hnresult["spmi_live_base"]=="fffff8033dea0000" and
            hnresult["original_spmi_live_callback_resolved_rva"]=="0x1660",
            "consumed E004hn real original PMIC/SPMI image bases or callback changed")
    # The same historical READ-ONLY KD dump ALSO contains +0x38 neighbor.
    # This is archived original evidence, NOT a NEW Windows boot.
    pattern=(b"fffff803"+bytes([96])+b"3de7d040  "
             b"fffff803"+bytes([96])+b"3dea1660 "
             b"fffff803"+bytes([96])+b"3dea1920")
    require(pattern in hnraw,"original live second SPMI callback pointer unobserved")
    require(hp["status"]==
            "PASS_FRESH_EARLY_SPMI_TIMER_SPAN_WATCH_WITH_NONTIMER_CALLBACK_CONTROL_NO_MATCH_GOLDEN_RETURN" and
            hp["original_filtered_spmi_entry_rva"]=="0x1660" and
            hp["actual_timer_address_span_callback_hit_markers"]==0 and
            hp["original_raw_lowlevel_timer_callback_complete_absence_proven"] is False and
            hp["independent_early_callback_positive_control_hit"] is True,
            "original consumed +0x1660 early timer watch not scoped correctly")
    return {
        "e004hn_original_kd_log_sha256":sha256(hnraw).hexdigest(),
        "e004hn_original_result_sha256":sha256((HN/"evidence/RESULT.json").read_bytes()).hexdigest(),
        "e004hp_original_result_sha256":sha256((HP/"evidence/RESULT.json").read_bytes()).hexdigest(),
        "live_pmic_plus_3d048_points_to_original_spmi_plus_1920":True,
        "e004hp_watched_spmi_plus_1660_not_plus_1920":True,
    }

def main():
    archive=next((HN/"evidence").glob("ORIGINAL-SP7-READONLY-SPMI-LIVE-INTERFACE-KD-*.zip"))
    with zipfile.ZipFile(archive) as z:
        require(z.namelist()==["ORIGINAL-SP7-READONLY-SPMI-LIVE-INTERFACE-KD.log"],
                "original SP7 KD trace zip members changed")
        live=z.read(z.namelist()[0])
    require(sha256(live).hexdigest()==
            "81cf7b9e0655a98902e3f54a1973a1d3a8134077b6a6065a469c96148f059643",
            "consumed original live interface evidence changed")
    hp=json.loads((HP/"evidence/RESULT.json").read_text())
    result={
        "experiment":"E004hq",
        "status":"PASS_ALTERNATE_ORIGINAL_SPMI_MASKED_RMW_PLUS38_LIVE_PUBLISHED_SEPARATE_UNWATCHED_WRITE_PATH_OFFLINE",
        "date":"2026-09-20",
        "baseline_commit":"60f458c2381923ff1e07aad6b850f7e6e0727548",
        "original_windows_oem_sha256":{"qcspmi8380":SPMI_SHA,"qcpmic8380":PMIC_SHA},
        "archived_live_source_and_prior_scope":verify_prior(live,hp),
        "original_spmi_provider_alt_callback":audit(original("qcspmi8380",SPMI_SHA),
                                                     original("qcpmic8380",PMIC_SHA)),
        "second_callback_written_0x93_to_real_timer_verified":False,
        "original_idle_0x93_first_writer_identified":False,
        "fresh_windows_kd_camera_spmi_pmic_led_or_login_actions":False,
        "physical_current_irradiance_pulse_or_autonomous_host_fault_off_proven":False,
        "native_linux_emitter_or_pam_enabled":False,
        "golden_modified":False,
        "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_alternate.py").read_bytes()).hexdigest(),
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004HQ_LIVE_ORIGINAL_SPMI_MASKED_RMW_SLOT_PLUS38_TO_CALLBACK_PLUS1920=PASS")
    print("E004HQ_ORIGINAL_PLUS1920_READ_MODIFY_WRITE_BYPASSES_PLUS1660_BREAKPOINT=PASS")
    print("E004HQ_FIRST_TIMER_0X93_WRITER_UNOBSERVED GOLDEN_UNCHANGED NATIVE_IR_OFF")
if __name__=="__main__":main()
