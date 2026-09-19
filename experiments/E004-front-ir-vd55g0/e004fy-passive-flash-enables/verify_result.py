#!/usr/bin/env python3
"""Offline reconciliation of the consumed E004fy read; NO additional PMIC IO."""
from pathlib import Path
from hashlib import sha256
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
E=HERE/"evidence"
PINNED={
    "PREPARED.json":"b3230c7c0aeb8181be0d78a8807b2e478212626fd9694ebee8d5cbaac9e30846",
    "CONSUMED.json":"a38f42f52c9e2136dc11b03539d54c56ee7318926746ac1de988d5435957bbd3",
    "RESULT.json":"814a80e5761ef6f4bbb2d241da78389c3aa64136d22d3302dbee4a7cddc46217",
    "POSTREAD.txt":"2fe786c3910479b7cec03397c50c64270de71bb2a99dd41430ef2eb91bc9f1f6",
}
DRIVER=ROOT/"experiments/E004-front-ir-vd55g0/e004fk-native-flash-disable-ordering/build/source/leds-qcom-flash.c"
FP=ROOT/"experiments/E004-front-ir-vd55g0/e004fp-windows-pmic-register-trace-corrected/evidence/RESULT.json"

def need(ok,reason):
    if not ok: raise ValueError("E004FY_VERIFICATION_FAIL_CLOSED "+reason)

def main():
    for name,digest in PINNED.items():
        f=E/name
        need(f.is_file() and sha256(f.read_bytes()).hexdigest()==digest,"evidence drift "+name)
    need(sha256(DRIVER.read_bytes()).hexdigest()=="cd1f98411545cdb4b679bb21c4c29076a88866517488d5b618c31485caa04727","driver drift")
    need(sha256(FP.read_bytes()).hexdigest()=="b94a5997ecfb27f8f87527b2099763416cae390abf03e90d909b11efd2deac86","Windows parsed evidence drift")
    pre=json.loads((E/"PREPARED.json").read_text())
    consumed=json.loads((E/"CONSUMED.json").read_text())
    result=json.loads((E/"RESULT.json").read_text())
    post=(E/"POSTREAD.txt").read_text()
    fp=json.loads(FP.read_text())
    boot="c4172e14-03ca-4e99-adbb-ddfb102cbe27"
    need(pre["boot"]==consumed["golden_boot"]==result["boot"]==boot
         and boot in post,"Golden identity mismatch")
    need(consumed["prepared_sha256"]==PINNED["PREPARED.json"] and consumed["attempts"]==1
         and consumed["status"]=="CONSUMED_BEFORE_REGISTER_IO","single-use marker invalid")
    need(result["status"]=="PASS_SINGLE_PASSIVE_IDLE_FLASH_ENABLE_TRIGGER_READ" and
         result["identity_consumed"] is True and result["read_only_register_bytes_requested"]==54,
         "actual bounded six-byte result missing")
    addresses=["0xee46","0xee4a","0xee4b","0xee4c","0xee4d","0xee4e"]
    need(pre["addresses"]==result["register_addresses"]==consumed["read_only_addresses"]==addresses,
         "target address mapping changed")
    observed=result["idle_register_bytes"]
    need(list(observed)==addresses,"unexpected register value fields")
    expected={"0xee46":"00","0xee4a":"01","0xee4b":"01","0xee4c":"01","0xee4d":"01","0xee4e":"00"}
    need(observed==expected,"actual idle module, channel or trigger register differs")
    need(result["conditional_module_enable_bit7"] is False and
         result["conditional_channel_enable_mask_low4"]==0,
         "reported enable decode differs from read values")
    need(all(result[k] is False for k in (
         "register_writes_requested","emitter_activation_requested",
         "independent_physical_shutoff_verified","safe_current_or_irradiance_verified",
         "emitter_activation_authorized")),"unsupported safety or activation claim")
    for marker in (boot,"FLASH_DT_STATUS=disabled",
                   "saved_entry=sp11-audio-fullio-v19c","next_entry=\n",
                   "BootCurrent: 0005","BootOrder: 0005,0004,0000,0001,0002,0006",
                   "nodes=no modules=none active_processes=no","OVERLAP_GUARD=PASS"):
        need(marker in post,"Golden return/idle evidence missing: "+marker)
    src=DRIVER.read_text()
    for expected_line in (
        "[REG_MODULE_EN]\t\t= REG_FIELD(0x46, 7, 7)",
        "[REG_CHAN_STROBE]\t= REG_FIELD_ID(0x4a, 0, 6, 4, 1)",
        "[REG_CHAN_EN]\t\t= REG_FIELD(0x4e, 0, 3)",
        "#define FLASH_STROBE_HW_SW_SEL_BIT\tBIT(2)",
        "#define FLASH_HW_STROBE_TRIGGER_SEL_BIT\tBIT(1)",
        "#define FLASH_STROBE_POLARITY_BIT\tBIT(0)",
    ):
        need(expected_line in src,"driver bit layout changed")
    need(fp.get("status")=="PASS_BOUNDED_WINDOWS_PMIC_REGISTER_TRACE", "Windows trace state changed")
    verified={
        "experiment":"E004fy",
        "status":"PASS_SINGLE_IDLE_FLASH_ENABLE_AND_TRIGGER_SNAPSHOT",
        "identity_consumed":True,
        "pmic_spmi":"0-01",
        "idle_config_bytes":observed,
        "idle_module_enable_bit7":False,
        "idle_channel_enable_mask_low4":0,
        "idle_trigger_fields":"0x01 on all four channels: per isolated Linux source SW (bit2=0), level (bit1=0), active-high polarity (bit0=1)",
        "golden_flash_node_status":"disabled",
        "windows_streaming_trigger_config_not_remeasured_here":True,
        "windows_trace_distinct_bounded_session":True,
        "physical_light_output_or_optical_power_measured":False,
        "hardware_timer_cutoff_or_independent_fault_shutdown_verified":False,
        "emitter_activation_authorized":False,
        "spmi_register_reads_during_offline_verification":0,
        "golden_postread":"PASS",
        "evidence_sha256":PINNED,
        "next_gate":"Independent electrical/optical shutoff and current limits; optionally separate fresh Windows KDNET session for live trigger/timer source cross-check."
    }
    (E/"VERIFIED.json").write_text(json.dumps(verified,indent=2)+"\n")
    print("E004FY_OFFLINE=PASS MODULE=OFF CHANNELS=OFF TRIGGER_BYTES=01x4 GOLDEN=PASS")
    print("WINDOWS_COMPARISON=SEPARATE_SESSION PHYSICAL_OFF_AUTHORITY=NOT_PROVEN IR_EMITTER=BLOCKED")

if __name__=="__main__":
    main()
