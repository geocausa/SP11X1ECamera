#!/usr/bin/env python3
"""E004hm: pinned original OEM SPMI software request -> MMIO command -> status.

Offline ARM64 PE instruction audit only. No physical PMIC readback, emitted IR
measurement, timer first-writer observation, or host-fault cutoff claim.
"""
from pathlib import Path
from hashlib import sha256
import json
import capstone
import pefile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ARCH=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
SPMI_SHA="b6a5868ec2450e713b9a5ada7b4e1a4a77c77427fedf0806fe3eb6541099523c"
PMIC_SHA="756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e"
BASE=0x140000000

def require(ok,why):
    if not ok:raise AssertionError("E004HM_FAIL_CLOSED "+why)

def original(name,sha):
    files=list(ARCH.glob(name+".inf_*/"+name+".sys"))
    require(len(files)==1,"ambiguous original OEM PE "+name)
    raw=files[0].read_bytes()
    require(sha256(raw).hexdigest()==sha,"original OEM PE hash changed "+name)
    pe=pefile.PE(data=raw)
    require(pe.FILE_HEADER.Machine==0xaa64 and
            pe.OPTIONAL_HEADER.ImageBase==BASE,"wrong original ARM64 PE")
    return pe

def instruction(pe,rva):
    c=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    ins=list(c.disasm(pe.get_data(rva,4),BASE+rva))
    require(len(ins)==1 and ins[0].address==BASE+rva,
            "invalid original instruction "+hex(rva))
    return ins[0].mnemonic,ins[0].op_str

# Every selected instruction is in the pinned OEM PE, not a decompiler guess
# or synthetic substitute. Distinct paths are checked around each branch.
SPMI_OPCODES=[
    (0x1688,"mov","w21, w2"),
    (0x168c,"mov","x27, x3"),
    (0x1690,"mov","w25, w4"),
    (0x1774,"ldr","w8, [x22, #0x18]"),
    (0x1778,"cbz","w8, #0x140001790"),
    (0x177c,"ubfx","w23, w21, #0x10, #4"),
    (0x1780,"ubfx","w19, w21, #8, #8"),
    (0x1784,"and","w20, w21, #0xff"),
    (0x1788,"ubfx","w21, w21, #0x14, #4"),
    (0x1790,"mov","w20, w21"),
    (0x1794,"ldp","w23, w19, [x22]"),
    (0x1798,"ldr","w21, [x22, #8]"),
    # SPMI callback supplies original buffer and count to controller helper.
    (0x17f4,"orr","w4, w20, w19, lsl #8"),
    (0x17f8,"mov","x7, #0"),
    (0x17fc,"mov","w6, w25"),
    (0x1804,"mov","x5, x27"),
    (0x180c,"mov","w3, w23"),
    (0x1810,"mov","w2, w21"),
    (0x1814,"mov","w1, w26"),
    (0x1818,"mov","w0, #0"),
    (0x1870,"bl","#0x1400064d8"),
    (0x1874,"mov","w23, w0"),
    (0x1878,"cbz","w23, #0x1400018b4"),
    (0x18e4,"mov","w0, w23"),
    # Controller helper captures request parameters, not known PMIC outcomes.
    (0x64d8,"pacibsp",""),
    (0x6500,"mov","w23, w2"),
    (0x6508,"mov","w22, w4"),
    (0x650c,"mov","x25, x5"),
    (0x6510,"mov","w26, w6"),
    (0x651c,"mov","w27, w0"),
    (0x6524,"mov","w24, w1"),
    (0x6528,"mov","x20, x7"),
    (0x652c,"cbnz","w8, #0x140006538"),
    (0x6530,"mov","w0, #0xe"),
    (0x6548,"mov","w0, #0x12"),
    (0x655c,"ldrb","w8, [x19, #8]"),
    (0x65b4,"strb","w23, [x9, x8]"),
    (0x65c8,"strb","w21, [x10, x8]"),
    (0x65d8,"strh","w22, [x10, x8]"),
    (0x65e8,"strb","w26, [x10, x8]"),
    # Branches before touching controller command: context/type checks.
    (0x6644,"bl","#0x140004780"),
    (0x664c,"cbnz","w21, #0x14000696c"),
    (0x6650,"ldr","x22, [x19]"),
    (0x665c,"cbz","x25, #0x140006968"),
    (0x6660,"cbz","w26, #0x140006968"),
    (0x668c,"mov","w21, #3"),
    (0x6694,"mov","w21, #1"),
    # Actual ORIGINAL memory-mapped data writes and command kickoff.
    # These are CPU stores to the driver's mapped peripheral registers.
    (0x674c,"str","w9, [x15, #0x10]"),
    (0x6788,"str","w8, [x9, #0x14]"),
    (0x67e0,"str","w9, [x8]"),
    # Status polling uses finite 0x190 iteration counter; progress depends
    # on host executing this code, not an independent PMIC light-off timer.
    (0x6818,"mov","w23, #0x190"),
    (0x6834,"sub","w23, w23, #1"),
    (0x6838,"cbz","w9, #0x14000685c"),
    (0x6840,"mov","w0, #1"),
    (0x6844,"blr","x8"),
    (0x684c,"ldr","w8, [x19, #8]"),
    (0x6854,"ldr","w8, [x24, #8]"),
    (0x6858,"cbz","w8, #0x140006830"),
    (0x6864,"tbnz","w8, #3, #0x140006954"),
    (0x6868,"tbz","w8, #0, #0x14000692c"),
    (0x6870,"mov","w8, #5"),
    (0x687c,"mov","w8, #6"),
    (0x6954,"mov","w8, #7"),
    (0x6958,"mov","w21, w8"),
    (0x6960,"mov","w21, #1"),
    (0x6968,"mov","w21, #0xf"),
    (0x6910,"ldr","w8, [x25]"),
    (0x691c,"str","w8, [x25]"),
    (0x6920,"cbnz","w26, #0x1400066b4"),
    (0x6924,"mov","w21, #0"),
    (0x6b54,"mov","w0, w21"),
]
PMIC_OPCODES=[
    (0x23ed8,"orr","w8, w20, w22, lsl #4"),
    (0x23edc,"orr","w2, w27, w8, lsl #16"),
    (0x23f18,"mov","w4, w24"),
    (0x23f20,"mov","x3, x26"),
    (0x23f24,"ldr","x8, [x25, #0x30]"),
    (0x23f3c,"blr","x15"),
]

def audit(spmi,pmic):
    for rva,mn,ops in SPMI_OPCODES:
        require(instruction(spmi,rva)==(mn,ops),
                "original SPMI branch/transport instruction drift "+hex(rva))
    for rva,mn,ops in PMIC_OPCODES:
        require(instruction(pmic,rva)==(mn,ops),
                "original PMIC raw-selector call instruction drift "+hex(rva))
    # 0x1660 is statically stored by original SPMI WDF interface provider,
    # established E004hl; 0x1870 is one ORIGINAL direct BL from that callback
    # into the controller helper but not necessarily the only caller.
    require(instruction(spmi,0x3e88)==("stp","x9, x8, [sp, #0x140]"),
            "original provider callback/neighbor table drift")
    require(instruction(spmi,0x3e74)==("add","x9, x8, #0x660"),
            "original SPMI +1660 callback pointer drift")
    return {
        "original_spmi_interface_write_callback_rva":"0x1660",
        "original_spmi_controller_helper_callsite_rva":"0x1870",
        "original_spmi_controller_helper_rva":"0x64d8",
        "original_spmi_selector_word_incoming":"w2",
        "original_spmi_input_payload_pointer":"x3",
        "original_spmi_input_byte_count":"w4",
        "original_spmi_controller_data_mmio_write_rvas":
            ["0x674c","0x6788"],
        "original_spmi_controller_command_mmio_write_rva":"0x67e0",
        "original_spmi_controller_status_read_rvas":["0x684c","0x6854"],
        "original_spmi_controller_poll_counter_initial_hex":"0x190",
        "original_spmi_controller_success_return_path_rvas":
            ["0x6924","0x6b54","0x1874","0x18e4"],
        "original_spmi_controller_failure_examples":{
            "not_initialized":"0x6530 -> w0=0x0e",
            "invalid_index":"0x6548 -> w0=0x12",
            "no_buffer_or_count":"0x6968 -> w21=0x0f",
            "status_bit3":"0x6864 -> 0x6954 -> w21=0x07",
            "status_not_complete":"0x6868 -> 0x692c (status-specific)",
        },
        "mmio_stores_guarantee_actual_physical_pmic_write":False,
        "finite_host_poll_counter_is_autonomous_emitter_watchdog":False,
        "real_windows_spmi_callback_hit_this_stage":False,
        "actual_controller_mmio_status_observed_this_stage":False,
        "first_writer_of_idle_timer_byte_0x93_identified":False,
        "real_light_pulse_current_irradiance_or_fault_off_measured":False,
    }

def prior():
    p=ROOT/"experiments/E004-front-ir-vd55g0/e004hl-original-spmi-raw-write-callback-identity/evidence/RESULT.json"
    d=json.loads(p.read_text())
    require(d["status"]==
            "PASS_ORIGINAL_SPMI_PROVIDER_PLUS_30_CALLBACK_1660_PMIC_INDIRECT_SLOT_IDENTITY_OFFLINE" and
            d["original_provider_consumer_slot"]["provider_original_callback_rva"]=="0x1660" and
            d["original_provider_consumer_slot"]["pmic_timer_byte_0x93_first_writer_identified"] is False,
            "prior original callback source/scope drift")
    return sha256(p.read_bytes()).hexdigest()

def result_data():
    spmi=original("qcspmi8380",SPMI_SHA)
    pmic=original("qcpmic8380",PMIC_SHA)
    return {
        "experiment":"E004hm",
        "status":"PASS_ORIGINAL_SPMI_RAW_CALLBACK_TO_MMIO_COMMAND_STATUS_AND_RETURN_OFFLINE",
        "date":"2026-09-20",
        "baseline_commit":"023636e138d1f8f355c756d40a05c3d3e347b95f",
        "original_binary_sha256":{"qcspmi8380":SPMI_SHA,"qcpmic8380":PMIC_SHA},
        "prior_e004hl_result_sha256":prior(),
        "original_spmi_controller_path":audit(spmi,pmic),
        "original_instruction_site_count":len(SPMI_OPCODES)+len(PMIC_OPCODES)+2,
        "new_windows_kd_camera_spmi_pmic_led_or_login_actions":False,
        "golden_modified":False,
        "native_ir_emitter_authorized":False,
        "verifier_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_controller.py").read_bytes()).hexdigest(),
    }

def main():
    out=result_data()
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(out,indent=2)+"\n")
    print("E004HM_ORIGINAL_SPMI_1660_TO_64D8_MMIO_COMMAND_POLL_AND_STATUS=PASS")
    print("E004HM_NO_ACTUAL_PHYSICAL_PMIC_WRITE_OR_TIMER_FIRST_WRITER_PROOF GOLDEN=UNCHANGED")
if __name__=="__main__":main()
