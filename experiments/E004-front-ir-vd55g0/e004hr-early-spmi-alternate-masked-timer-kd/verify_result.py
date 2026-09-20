#!/usr/bin/env python3
"""E004hr original immutable SP7 KD alternate RMW non-hit, direct positive control."""
from pathlib import Path
from hashlib import sha256
import json,re,zipfile,capstone,pefile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ZIP=HERE/"evidence/ORIGINAL-SP7-EARLY-ALTERNATE-SPMI-MASKED-KD-20260920.zip"
RAW_SHA="70bbb26c0b13ea575d88c6954ad9eeb909ef2bcabd98fbfe8ae3b97886a8000f"
ZIP_SHA="a445f4e059e2feb58d6d990412430e71b755f9b821c70d554c85ff7b4611cfd3"
SPMI_SHA="b6a5868ec2450e713b9a5ada7b4e1a4a77c77427fedf0806fe3eb6541099523c"

def need(ok,reason):
    if not ok:raise AssertionError("E004HR_FAIL_CLOSED "+reason)

def marker(raw,name):
    matches=list(re.finditer(rb"(?m)^"+re.escape(name)+rb"\r?$",raw))
    need(len(matches)==1,"missing/duplicate original SP7 event "+name.decode())
    return matches[0]

def between(raw,a,b):
    start=marker(raw,a).end()
    end=marker(raw,b).start()
    need(start<end,"original KD event order changed")
    return raw[start:end]

def verify_log(raw):
    need(len(raw)==10047 and sha256(raw).hexdigest()==RAW_SHA,
         "original SP7 KD trace byte identity changed")
    need(re.search(rb"(?i)key=[A-Za-z0-9.]{8,}",raw) is None,
         "KDNET credential may not appear in original trace")
    # Simplify WinDbg printed 64-bit addresses without losing original hash.
    norm=raw.replace(bytes([96]),b"")
    pre=between(norm,b"E004HR_FIRST_PRELOAD",b"E004HR_SPMI_LOAD_WATCH_ARMED")
    need(b"System Uptime: 0 days 0:00:10.969" in pre and
         b"qcspmi8380   (deferred)" not in pre,
         "initial SP7 breakpoint was after driver module load")
    loaded=between(norm,b"E004HR_SPMI_LOAD_STOP",b"E004HR_SPMI_LOAD_CHECK_DONE")
    need(b"System Uptime: 0 days 0:00:11.792" in loaded and
         b"Last event: Load module qcspmi8380.sys at fffff8037e280000" in loaded and
         b"fffff8037e280000 fffff8037e292000   qcspmi8380" in loaded and
         b"fffff8037e220000 fffff8037e279000   qcpmic8380" in loaded,
         "original SPMI/PMIC Windows live bases or load event unverified")
    armed=between(norm,b"E004HR_ARMING_DISTINCT_MASKED_TIMER_FILTER",
                  b"E004HR_BOTH_EARLY_CONTROLS_ARMED")
    need(b"fffff8037e281920 d503237f pacibsp" in norm and
         b"fffff8037e281924 a9bb53f3 stp" in norm and
         b"qcspmi8380+0x1920 (Condition: ((@w2 & 0xffff) >= 0xee3e) && ((@w2 & 0xffff) <= 0xee41))" in armed and
         b"/1 0001 (0001) qcspmi8380+0x1924" in armed and
         b"/1 0001 (0001) qcspmi8380+0x1664" in armed and
         b"r x2; r x3; r x4; r lr; gc" in armed,
         "early masked single-register selector filter/controls not armed")
    direct=between(norm,b"E004HR_DIRECT_WRITE_CONTROL",
                   b"E004HR_FINAL_BOUNDED_ALTERNATE_OBSERVER_CHECK")
    need(b"System Uptime: 0 days 0:00:15.973" in direct and
         b"x2=0000000000019246" in direct and
         b"x4=0000000000000001" in direct,
         "same-session natural non-timer direct-write positive control missing")
    need(not re.search(rb"(?m)^E004HR_ALT_RMW_ENTRY_CONTROL\r?$",norm) and
         not re.search(rb"(?m)^E004HR_ALT_TIMER_ADDR_ENTRY\r?$",norm),
         "actual alternate callback/timer hit misreported as absent")
    end=between(norm,b"E004HR_FINAL_BOUNDED_ALTERNATE_OBSERVER_CHECK",
                b"E004HR_ALL_EARLY_OBSERVERS_CLEARED")
    need(b"System Uptime: 0 days 0:01:06.474" in end and
         b"Last event: Break instruction exception" in end and
         b"0 e fffff8037e281920" in end and
         b"qcspmi8380+0x1920 (Condition: ((@w2 & 0xffff) >= 0xee3e) && ((@w2 & 0xffff) <= 0xee41))" in end and
         b"1 e fffff8037e281924" in end and
         b"/1 0001 (0001) qcspmi8380+0x1924" in end,
         "final unconsumed original alternate one-shot and active filter missing")
    need(b"bc *; sxd ld:qcspmi8380; bl" in norm and
         b"Closing open log file " in norm,
         "breakpoints or debugger log left active")

def verify_result(r,p):
    need(p["status"]=="PREPARED_FRESH_WINDOWS_ALT_SPMI_MASKED_RMW_EARLY_OBSERVER_NOT_EXECUTED" and
         p["baseline_commit"]=="2a617add2109219bc397fb54a9996ee9d9f48609" and
         p["golden_preboot_id"]=="e32d34ba-a422-44cb-a60b-4ff28b583bab" and
         p["new_windows_boot_consumed"] is False and
         p["native_ir_emitter_enabled"] is False,
         "original one-time Windows preboot baseline drift")
    need(r["experiment"]=="E004hr" and
         r["status"]=="PASS_FRESH_EARLY_WINDOWS_ALTERNATE_MASKED_SPMI_CALLBACK_BOUNDED_NONHIT_WITH_DIRECT_POSITIVE_GOLDEN_RETURN" and
         r["prepared_commit"]=="24d0e69ddc1b53cb32229b7cf992d463850d5547" and
         r["fresh_windows_boots_consumed"]==1 and
         r["original_spmi_live_base"]=="fffff8037e280000" and
         r["original_pmic_live_base"]=="fffff8037e220000" and
         r["original_alt_masked_spmi_callback_rva"]=="0x1920" and
         r["direct_positive_control_hit_kernel_uptime_seconds"]==15.973 and
         r["direct_positive_control_selector"]=="0x00019246" and
         r["direct_positive_control_byte_count"]==1 and
         r["final_manual_pause_kernel_uptime_seconds"]==66.474 and
         r["golden_return_boot_id"]=="a668186f-df85-4238-9983-f7b28455ec84" and
         r["golden_kernel"]=="7.1.5-sp11-render-parity-v4+" and
         r["saved_grub_entry"]=="sp11-audio-fullio-v19c" and
         r["original_sp7_kd_raw_bytes"]==10047 and
         r["original_sp7_kd_raw_sha256"]==RAW_SHA and
         r["original_sp7_kd_zip_sha256"]==ZIP_SHA,
         "original trace/Golden return result identity changed")
    for key in ("direct_write_positive_control_hit",
                "persistent_alt_masked_timer_breakpoint_active_at_final_manual_pause",
                "one_shot_alt_masked_control_still_armed_at_final_manual_pause",
                "timer_filter_compares_w2_low16_single_register_ee3e_through_ee41",
                "alternate_masked_w4_is_mask_not_byte_count",
                "all_debugger_breakpoints_load_events_cleared_log_closed_kd_stopped",
                "temporary_software_code_breakpoints_used_then_cleared",
                "no_windows_camera_preview_manual_pmic_spmi_flash_command_or_debugger_data_write",
                "windows_normally_rebooted_to_golden","efi_bootorder_unchanged",
                "efi_bootnext_empty","golden_camera_idle"):
        need(r[key] is True,"positive control/cleanup claim changed "+key)
    for key in ("alt_masked_positive_control_hit","alt_masked_timer_address_filtered_hit",
                "alternate_masked_path_full_bus_sid_or_legacy_real_address_observed",
                "alternate_masked_path_comprehensive_absence_proven",
                "first_original_idle_timer_byte_0x93_writer_identified",
                "physical_silicon_write_current_pulse_autonomous_fault_off_proven",
                "native_ir_emitter_or_login_modified"):
        need(r[key] is False,"fabricated alternate/timer/physical result "+key)

def static_original():
    paths=list(Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump").glob(
        "qcspmi8380.inf_*/qcspmi8380.sys"))
    need(len(paths)==1,"original SPMI OEM PE unavailable or ambiguous")
    data=paths[0].read_bytes()
    need(sha256(data).hexdigest()==SPMI_SHA,"original OEM SPMI PE hash changed")
    pe=pefile.PE(data=data)
    need(pe.FILE_HEADER.Machine==0xaa64 and pe.OPTIONAL_HEADER.ImageBase==0x140000000,
         "wrong original OEM ARM64 PE")
    cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    for rva,mn,ops in (
       (0x1920,"pacibsp",""),(0x1924,"stp","x19, x20, [sp, #-0x50]!"),
       (0x194c,"mov","w20, w2"),(0x1950,"mov","w27, w3"),
       (0x1954,"mov","w26, w4"),(0x1664,"stp","x19, x20, [sp, #-0x50]!"),
       (0x1b38,"bl","#0x1400064d8"),(0x1b70,"bl","#0x1400064d8")):
        ins=list(cs.disasm(pe.get_data(rva,4),0x140000000+rva))
        need(len(ins)==1 and (ins[0].mnemonic,ins[0].op_str)==(mn,ops),
             "original callback/one-byte RMW controller disassembly changed")
    hq=ROOT/"experiments/E004-front-ir-vd55g0/e004hq-spmi-masked-rmw-alternate-timer-bus-path/evidence/RESULT.json"
    prior=json.loads(hq.read_text())
    need(prior["original_spmi_provider_alt_callback"]["provider_original_masked_rmw_callback_rva"]=="0x1920" and
         prior["original_spmi_provider_alt_callback"]["alternate_rmw_writes_without_direct_call_to_spmi_plus1660"] is True and
         prior["original_idle_0x93_first_writer_identified"] is False,
         "prior original alternate callback code findings changed")

def main():
    need(sha256(ZIP.read_bytes()).hexdigest()==ZIP_SHA,"original KD ZIP drift")
    with zipfile.ZipFile(ZIP) as archive:
        need(archive.namelist()==["ORIGINAL-SP7-EARLY-ALTERNATE-SPMI-MASKED-KD.log"],
             "original SP7 archive contains unknown members")
        raw=archive.read(archive.namelist()[0])
    verify_log(raw)
    verify_result(json.loads((HERE/"evidence/RESULT.json").read_text()),
                  json.loads((HERE/"evidence/PREPARED.json").read_text()))
    static_original()
    print("E004HR_EARLY_ORIGINAL_ALTERNATE_RMW_BOUNDED_NO_HIT=PASS")
    print("E004HR_DIRECT_ONE_SHOT_POSITIVE_AND_ACTIVE_ALTERNATE_FILTER_VERIFIED=PASS")
    print("E004HR_TIMER_FIRST_WRITER_UNKNOWN_GOLDEN_RETURN_NATIVE_IR_OFF=PASS")

if __name__=="__main__":main()
