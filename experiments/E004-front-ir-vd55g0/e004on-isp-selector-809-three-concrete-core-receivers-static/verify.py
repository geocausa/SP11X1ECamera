#!/usr/bin/env python3
"""E004on: conditional original CSID/IFE/CDM first-callback 0x809 paths.

Source-only original-SP11 ARM64, never a live rear-session or physical
stop/WM16 DMA acknowledgement. No original OEM binaries/raw disassembly,
optical pixels, addresses or KD logs are saved to Git.
"""
import copy,hashlib,json,re,subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
211b0|pacibsp|
211dc|mov|w20, #0x0
211e0|cbz|x0, 0x140021b98 <.text+0x20b98>
211e4|ldr|x19, [x0, #0x20]
211e8|cbz|x19, 0x140021b98 <.text+0x20b98>
2120c|cmp|w1, #0x803
21210|b.hi|0x1400218d8 <.text+0x208d8>
218d8|cmp|w1, #0x804
218dc|b.eq|0x140021b4c <.text+0x20b4c>
218e0|cmp|w1, #0x805
218e4|b.eq|0x140021904 <.text+0x20904>
218e8|mov|w2, w1
218ec|adrp|x8, 0x140038000 <.text+0x37000>
218f0|add|x1, x8, #0x768
218f4|adrp|x8, 0x140044000
218f8|add|x8, x8, #0xb0
218fc|add|x0, x8, #0x2e8
21900|b|0x14002139c <.text+0x2039c>
2139c|bl|0x140029ad8 <.text+0x28ad8>
213a0|b|0x140021b90 <.text+0x20b90>
21b90|mov|w0, w20
22cd0|pacibsp|
22cf4|mov|w20, #0x0
22cf8|cbz|x0, 0x1400236a0 <.text+0x226a0>
22cfc|ldr|x19, [x0, #0x20]
22d00|cbz|x19, 0x1400236a0 <.text+0x226a0>
22d24|cmp|w1, #0x803
22d28|b.hi|0x140023604 <.text+0x22604>
23604|cmp|w1, #0x804
23608|b.eq|0x14002366c <.text+0x2266c>
2360c|cmp|w1, #0x805
23610|b.ne|0x140023698 <.text+0x22698>
23614|add|x0, x19, #0xc8
23618|bl|0x1400221a0 <.text+0x211a0>
23640|mov|x0, x19
23644|bl|0x140027278 <.text+0x26278>
23698|mov|w0, w20
28480|pacibsp|
284b4|mov|w20, #0x0
284b8|cbz|x0, 0x140028a2c <.text+0x27a2c>
284bc|ldr|x19, [x0, #0x20]
284c0|cbz|x19, 0x140028a2c <.text+0x27a2c>
28518|cbz|w1, 0x140028a14 <.text+0x27a14>
2851c|cmp|w1, #0x1
28520|b.eq|0x14002898c <.text+0x2798c>
28524|cmp|w1, #0x2
28528|b.eq|0x140028664 <.text+0x27664>
2852c|cmp|w1, #0x3
28530|b.eq|0x1400285ec <.text+0x275ec>
28534|cmp|w1, #0x804
28538|b.eq|0x1400285c8 <.text+0x275c8>
2853c|cmp|w1, #0x805
28540|b.eq|0x14002854c <.text+0x2754c>
28544|mov|w20, #0xe
28548|b|0x14002865c <.text+0x2765c>
2865c|mov|w0, w20
28660|b|0x140028a30 <.text+0x27a30>
"""
ANCHORS={int(a,16):(b,c) for a,b,c in (line.split("|",2) for line in SOURCE.strip().splitlines())}
def must(ok,why):
    if not ok:raise AssertionError("E004ON_FAIL_CLOSED "+why)
def result():
    return {
      "schema":"sp11-e004on-original-ISP-CSID-IFE-CDM-conditional-0x809-first-callback-dispatch-v1",
      "parent_git_revision":"e9bfeeda8a3a56b94e346060065fb7001478e3b4",
      "same_SP11_original_OEM_ISP_sha256":SHA,
      "exact_original_ARM64_instruction_anchors":len(ANCHORS),
      "installed_first_callback_entries":{"CSID":"0x211b0","IFE":"0x22cd0","CDM":"0x28480"},
      "0x809_selector_forwards_to_first_callback_only_if_manager_list_selects_this_core":True,
      "CSID_0x809_default_branch_RVA":"0x218e8",
      "CSID_0x809_default_branch_diagnostic_then_return_RVA":"0x2139c",
      "CSID_0x809_status_zero_if_valid_inputs_and_no_other_early_failure":True,
      "IFE_0x809_default_branch_return_RVA":"0x23698",
      "IFE_0x809_status_zero_if_valid_inputs_and_no_other_early_failure":True,
      "CDM_0x809_unrecognized_selector_branch_RVA":"0x28544",
      "CDM_0x809_return_status_decimal_if_valid_inputs":14,
      "CDM_0x809_return_status_hex_if_valid_inputs":"0x0e",
      "CSID_IFE_default_status_zero_is_hardware_stop_or_WM16_DMA_completion_ack":False,
      "CDM_0x809_equivalent_to_CDM_0x805_stop":False,
      "every_0x809_possible_configured_core_receiver_identified":False,
      "live_windows_rear4k_0x809_call_count_selection_and_results_observed":False,
      "BF_0x0f_WM16_IRQ_or_DMA_retirement_proven":False,
      "Linux_native_rear_4k_processed_ISP_optical_frame_proven":False,
      "Golden_boot_or_camera_hardware_modified":False,
      "private_OEM_binary_disassembly_DMA_KD_or_optical_data_exported":False,
    }
def conservative(x):must(x==result(),"saved schema or unverified claim")
if __name__=="__main__":
    must(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"original same-SP11 ISP SHA")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    orig={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for rva,want in ANCHORS.items():must(orig.get(rva)==want,"original ISA RVA %x"%rva)
    must(0x809>0x803 and 0x809 not in (0x804,0x805),"independent 809 branch arithmetic")
    old=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004og-original-isp-three-core-callback-implementations-static/RESULT.json").read_text())
    for name,rva in (("CSID","0x211b0"),("IFE","0x22cd0"),("CDM","0x28480")):
        must(old["specific_original_per_core_provider_functions"][name]["first_callback_entry_RVA"]==rva,
             "verified original installed first callback "+name)
    old809=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004ol-isp-selector-809-independent-dispatch-static/RESULT.json").read_text())
    must(old809["selector_0x809_reaches_generic_default_branch_RVA"]=="0x1932c" and
         old809["default_dispatch_forwards_original_selector_in_w1_RVA"]=="0x193b4","original 809 forwarding")
    facts=result();file=HERE/"RESULT.json"
    if file.exists():must(json.loads(file.read_text())==facts,"saved same-source result")
    else:file.write_text(json.dumps(facts,sort_keys=True,indent=2)+"\n")
    mutants=(
      ("fake_sha","same_SP11_original_OEM_ISP_sha256","0"*64),
      ("fake_csid","CSID_0x809_default_branch_RVA","0x21904"),
      ("fake_ife","IFE_0x809_default_branch_return_RVA","0x23614"),
      ("fake_cdm","CDM_0x809_return_status_decimal_if_valid_inputs",0),
      ("fake_cdmhex","CDM_0x809_return_status_hex_if_valid_inputs","0x00"),
      ("fake_csid_dma","CSID_IFE_default_status_zero_is_hardware_stop_or_WM16_DMA_completion_ack",True),
      ("fake_cdm_stop","CDM_0x809_equivalent_to_CDM_0x805_stop",True),
      ("fake_all","every_0x809_possible_configured_core_receiver_identified",True),
      ("fake_live","live_windows_rear4k_0x809_call_count_selection_and_results_observed",True),
      ("fake_bf","BF_0x0f_WM16_IRQ_or_DMA_retirement_proven",True),
      ("fake_linux4k","Linux_native_rear_4k_processed_ISP_optical_frame_proven",True),
      ("fake_golden","Golden_boot_or_camera_hardware_modified",True),
      ("fake_oem_export","private_OEM_binary_disassembly_DMA_KD_or_optical_data_exported",True),
    )
    for name,key,v in mutants:
        fake=copy.deepcopy(facts);fake[key]=v
        try:conservative(fake)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004ON_NEGATIVE_FAILED_OPEN "+name)
    print("PASS_E004ON_%d_EXACT_ORIGINAL_ARM64_INSTRUCTIONS_%d_NEGATIVES_THREE_CONDITIONAL_809_CALLBACK_PATHS_NOT_PHYSICAL_STOP_GOLDEN_SAFE"%(len(ANCHORS),len(mutants)))
