#!/usr/bin/env python3
"""E004oo: original IFE progress flag → event signal (not DMA retirement).

Only scalar driver-relative RVAs and independent OEM SHA/import mapping
are persisted. No private driver, raw bulk disassembly, DMA pointer,
KD material or optical image is exported.
"""
import copy,hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
1f230|ldrb|w8, [x19, #0x171]
1f234|cbz|w8, 0x14001f258 <.text+0x1e258>
1f238|ldr|w2, [x19, #0x120]
1f23c|adrp|x8, 0x140037000 <.text+0x36000>
1f240|add|x1, x8, #0x8a0
1f244|strb|wzr, [x19, #0x171]
1f248|add|x0, x21, #0x78
1f24c|bl|0x140029ad8 <.text+0x28ad8>
1f250|mov|x0, x19
1f254|bl|0x1400241d8 <.text+0x231d8>
241d8|pacibsp|
241dc|stp|x19, x20, [sp, #-0x10]!
241e0|stp|x29, x30, [sp, #-0x10]!
241e4|mov|x29, sp
241e8|mov|x19, x0
241ec|cbnz|x19, 0x14002420c <.text+0x2320c>
241f0|adrp|x8, 0x140038000 <.text+0x37000>
241f4|add|x1, x8, #0x9e0
241f8|adrp|x8, 0x140044000
241fc|add|x0, x8, #0x668
24200|mov|w2, #0x1d
24204|bl|0x140029ad8 <.text+0x28ad8>
24208|b|0x14002424c <.text+0x2324c>
2420c|adrp|x8, 0x140039000 <.text+0x38000>
24210|add|x1, x8, #0x778
24214|ldr|w2, [x19, #0x120]
24218|adrp|x8, 0x140044000
2421c|add|x20, x8, #0x668
24220|add|x0, x20, #0x6c0
24224|bl|0x140029ad8 <.text+0x28ad8>
24228|add|x0, x19, #0xc8
2422c|bl|0x14002a1d8 <.text+0x291d8>
24230|cbz|w0, 0x14002424c <.text+0x2324c>
24234|ldr|w2, [x19, #0x120]
24238|adrp|x8, 0x140039000 <.text+0x38000>
2423c|mov|w3, w0
24240|add|x1, x8, #0x7c0
24244|add|x0, x20, #0x210
24248|bl|0x140029ad8 <.text+0x28ad8>
2424c|ldp|x29, x30, [sp], #0x10
24250|ldp|x19, x20, [sp], #0x10
24254|autibsp|
24258|ret|
2a1d8|pacibsp|
2a1dc|stp|x29, x30, [sp, #-0x10]!
2a1e0|mov|x29, sp
2a1e4|mov|w8, #0x2c
2a1e8|cbz|x0, 0x14002a20c <.text+0x2920c>
2a1ec|ldr|x0, [x0]
2a1f0|cbz|x0, 0x14002a20c <.text+0x2920c>
2a1f4|adrp|x8, 0x14003f000
2a1f8|ldr|x8, [x8, #0x2e8]
2a1fc|mov|w2, #0x0
2a200|mov|w1, #0x0
2a204|blr|x8
2a208|mov|w8, #0x0
2a20c|mov|w0, w8
2a210|ldp|x29, x30, [sp], #0x10
2a214|autibsp|
2a218|ret|
"""
ANCHORS={int(a,16):(b,c) for a,b,c in (line.split("|",2) for line in SOURCE.strip().splitlines())}

def guard(ok,why):
    if not ok:raise AssertionError("E004OO_FAIL_CLOSED "+why)
def import_slot(source,name,dll):
    # llvm-readobj prints each original IMAGE_IMPORT_DESCRIPTOR and IAT base,
    # then the ordered symbols. Preserve only the scalar source-derived slot.
    inside=False; which=None; base=None; count=0; matches=[]
    for line in source.splitlines():
        line=line.strip()
        if line=="Import {":
            inside=True;which=None;base=None;count=0
        elif inside and line.startswith("Name: "):
            which=line[6:]
        elif inside and line.startswith("ImportAddressTableRVA: "):
            base=int(line.split(":",1)[1].strip(),16)
        elif inside and line.startswith("Symbol: "):
            guard(base is not None,"IAT base prior to symbol")
            if which==dll and line.split()[1]==name:
                matches.append(base+8*count)
            count+=1
        elif inside and line=="}":
            inside=False
    guard(len(matches)==1,"one exact imported symbol "+name)
    return matches[0]

def result():
    return {
        "schema":"sp11-e004oo-original-IFE-later-progress-KeSetEvent-not-WM16-DMA-ack-static-v1",
        "parent_git_revision":"45b1abd531bd980223734b849dd1c1b85acc6097",
        "same_SP11_original_ISP_sha256":SHA,
        "exact_original_ARM64_instruction_anchors":len(ANCHORS),
        "original_IFE_progress_flag_context_offset":"0x171",
        "original_flag_read_RVA":"0x1f230",
        "conditional_flag_clear_RVA":"0x1f244",
        "later_progress_event_helper_call_RVA":"0x1f254",
        "later_progress_event_helper_RVA":"0x241d8",
        "later_progress_event_helper_full_instructions":33,
        "later_progress_event_helper_event_wrapper_call_RVA":"0x2422c",
        "event_wrapper_RVA":"0x2a1d8",
        "event_wrapper_original_ntoskrnl_KeSetEvent_IAT_RVA":"0x3f2e8",
        "event_wrapper_checks_nonnull_wrapper_and_event_pointer":True,
        "event_wrapper_passes_zero_increment_and_wait_parameters_to_KeSetEvent":True,
        "event_helper_checks_wrapper_return_and_reports_error_without_MMIO_DMA_poll":True,
        "later_IFE_progress_flag_or_KeSetEvent_proves_HW_WM16_DMA_retirement":False,
        "all_other_IFE_IRQ_bus_WM16_stop_ack_paths_traced":False,
        "live_Windows_rear4k_selected_progress_flag_event_and_BF_proven":False,
        "Linux_native_rear_processed_ISP_4k_optical_frame_proven":False,
        "Golden_boot_or_camera_hardware_modified":False,
        "private_original_OEM_binary_raw_disassembly_DMA_KD_optical_exported":False,
    }
def strict(x):guard(x==result(),"result changed or physical claim promoted")
if __name__=="__main__":
    guard(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"original SP11 ISP SHA")
    assembly=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    orig={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(assembly)}
    for rva,instruction in ANCHORS.items():guard(orig.get(rva)==instruction,"original ISA RVA %x"%rva)
    # Entire bounded later-progress helper is checked, including the
    # non-null gate, single event-wrapper call, error branch and return.
    span=list(range(0x241d8,0x2425c,4))
    guard(len(span)==33 and all(i in ANCHORS for i in span),"complete original later helper")
    guard(all(ANCHORS[i][0] not in ("blr","br","wfe","wfi","dsb") for i in span),"helper contains untraced wait/indirect dispatch")
    imported=subprocess.check_output(["llvm-readobj","--coff-imports",str(ISP)],text=True)
    guard(import_slot(imported,"KeSetEvent","ntoskrnl.exe")==0x3f2e8,"exact original KeSetEvent slot")
    guard(import_slot(imported,"KeWaitForSingleObject","ntoskrnl.exe")==0x3f060,"distinguish wait IAT")
    guard(import_slot(imported,"KeClearEvent","ntoskrnl.exe")==0x3f250,"distinguish clear IAT")
    previous=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004oh-isp-multistage-stop-progress-static/RESULT.json").read_text())
    guard(previous["IFE_independent_stop_progress_handler_RVA"]=="0x1f230" and
          previous["IFE_independent_event_related_helper_RVA"]=="0x241d8" and
          previous["IFEmode_stop_progress_defines_live_VFE_bus_WM16_safe_retirement"] is False,
          "E004oh prior conservative source")
    facts=result();path=HERE/"RESULT.json"
    if path.exists():guard(json.loads(path.read_text())==facts,"saved original scalar result")
    else:path.write_text(json.dumps(facts,indent=2,sort_keys=True)+"\n")
    negatives=(
      ("fake_sha","same_SP11_original_ISP_sha256","0"*64),
      ("wrong_flag","original_IFE_progress_flag_context_offset","0x170"),
      ("fake_call","later_progress_event_helper_event_wrapper_call_RVA","0x24230"),
      ("fake_helper","event_wrapper_RVA","0x2a1e0"),
      ("fake_IAT","event_wrapper_original_ntoskrnl_KeSetEvent_IAT_RVA","0x3f060"),
      ("fake_wait","later_IFE_progress_flag_or_KeSetEvent_proves_HW_WM16_DMA_retirement",True),
      ("fake_remaining","all_other_IFE_IRQ_bus_WM16_stop_ack_paths_traced",True),
      ("fake_live","live_Windows_rear4k_selected_progress_flag_event_and_BF_proven",True),
      ("fake_4k","Linux_native_rear_processed_ISP_4k_optical_frame_proven",True),
      ("fake_golden","Golden_boot_or_camera_hardware_modified",True),
      ("fake_export","private_original_OEM_binary_raw_disassembly_DMA_KD_optical_exported",True),
    )
    for name,key,v in negatives:
        m=copy.deepcopy(facts);m[key]=v
        try:strict(m)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OO_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004OO_%d_EXACT_ORIGINAL_ARM64_ANCHORS_3_ORIGINAL_IAT_NAMES_%d_NEGATIVES_IFE_EVENT_SIGNAL_IS_NOT_DMA_ACK_GOLDEN_SAFE"%(len(ANCHORS),len(negatives)))
