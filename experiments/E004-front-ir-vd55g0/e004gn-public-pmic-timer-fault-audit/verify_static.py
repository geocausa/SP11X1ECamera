#!/usr/bin/env python3
"""Offline reproducible audit of 4ch PM8550 timeout/fault register mapping.

Does not query a live PMIC or claim hardware cutoff/eye safety.
"""
from pathlib import Path
from hashlib import sha256
import json
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=ROOT/"experiments/E004-front-ir-vd55g0/e004fk-native-flash-disable-ordering/build/source/leds-qcom-flash.c"
SOURCE_SHA="cd1f98411545cdb4b679bb21c4c29076a88866517488d5b618c31485caa04727"
IDLE=ROOT/"experiments/E004-front-ir-vd55g0/e004fx-passive-golden-timer-read/evidence/RESULT.json"
IDLE_SHA="b2cbfeb4705937cca69609672fd1c4143135c82ee2aff8bcf82e33206daa093e"

def need(test,why):
    if not test:raise AssertionError("E004GN_FAIL_CLOSED "+why)

def local_contract(source, idle):
    start=source.index("static const struct reg_field mvflash_4ch_regs[")
    finish=source.index("\n};",start)
    four=source[start:finish]
    expected={
        "REG_STATUS3":("0x09","0","7"),
        "REG_CHAN_TIMER":("0x3e","0","7","4","1"),
        "REG_MODULE_EN":("0x46","7","7"),
        "REG_CHAN_STROBE":("0x4a","0","6","4","1"),
        "REG_CHAN_EN":("0x4e","0","3"),
    }
    for name,params in expected.items():
        line=re.search(r"^\s*\["+name+r"\]\s*=\s*(REG_FIELD(?:_ID)?)\(([^)]+)\)",four,re.M)
        need(line is not None and tuple(x.strip() for x in line.group(2).split(","))==params,
             "4ch register changed: "+name)
    need("#define FLASH_TIMER_EN_BIT\t\tBIT(7)" in source,"timer enable bit changed")
    need("#define FLASH_TIMER_STEP_MS\t\t10" in source,"timer 10ms step changed")
    read=source[source.index("static int qcom_flash_fault_get("):]
    for token in ("regmap_field_read(flash_data->r_fields[REG_STATUS3], &val)",
                  "shift = chan_id * 2;",
                  "if (val & BIT(shift))",
                  "fault_sts |= LED_FAULT_TIMEOUT;"):
        need(token in read,"4ch fault/status interpretation changed: "+token)
    need(idle["read_once_identity_consumed"] is True and
         set(idle["idle_timer_register_bytes"].values())=={"93"},
         "archived idle timer evidence changed")
    return {
        "four_channel_status3_offset":"0x09",
        "candidate_status3_address_if_mapped_flash_base_ee00":"0xee09",
        "status3_timeout_indication_bits_for_zero_based_channels_0_and_3":["0x01","0x40"],
        "four_channel_timer_offsets":["0x3e","0x3f","0x40","0x41"],
        "module_enable_offset":"0x46",
        "channel_enable_offset":"0x4e",
        "archived_idle_timer_bytes":["0x93"]*4,
        "idle_0x93_proves_runtime_timeout_enforcement":False,
        "fault_status_register_read_live":False,
        "fault_indicator_proves_led_off_when_trigger_stuck":False,
        "trigger_rearm_behavior_for_continuous_high_known":False,
        "physical_irradiance_or_led_current_measured":False,
        "native_ir_emitter_activation_authorized":False,
    }

def main():
    need(sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA,"isolated Linux driver source hash changed")
    need(sha256(IDLE.read_bytes()).hexdigest()==IDLE_SHA,"consumed idle register result changed")
    result=local_contract(SOURCE.read_text(),json.loads(IDLE.read_text()))
    result.update({
        "experiment":"E004gn",
        "status":"PASS_OFFLINE_PUBLIC_AND_LOCAL_FLASH_TIMER_FAULT_REGISTER_AUDIT",
        "source_sha256":SOURCE_SHA,
        "archived_idle_evidence_sha256":IDLE_SHA,
        "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_static.py").read_bytes()).hexdigest(),
        "external_sources":[
            "https://codebrowser.dev/linux/linux/drivers/leds/flash/leds-qcom-flash.c.html",
            "https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/qcom/pm8550.dtsi",
            "https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/leds/qcom,spmi-flash-led.yaml",
            "https://lkml.iu.edu/2302.0/02949.html",
            "https://www.spinics.net/lists/kernel/msg5785237.html",
        ],
        "public_datasheet_covering_exact_surface_led_and_wiring_found":False,
        "camera_or_pmic_hardware_accessed":False,
        "golden_modified":False,
    })
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004GN_FOUR_CHANNEL_FAULT_STATUS_TIMER_MAPPING=PASS STATUS3_CANDIDATE=0xee09")
    print("E004GN_TIMEOUT_STATUS_INDICATOR=IDENTIFIED LIVE_READ=NO RETRIGGER_BEHAVIOR=UNKNOWN")
    print("E004GN_EMITTER_OFF=YES PHYSICAL_CUTOFF_PROVEN=NO")

if __name__=="__main__":main()
