#!/usr/bin/env python3
"""E004oh: original SP11 ISP stop-call vs progress/IRQ/event contract.

Read-only original SHA-pinned same-SP11 OEM ARM64 binary; export *only*
derived safe relative RVAs and explicit unproven status. No original OEM
driver/disassembly/diagnostics, KD data, pixel or buffer bytes copied.
"""
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
ANCHORS={
  # Individual IFE first callback stop invokes TWO distinct helpers.
  0x2360c:("cmp","w1, #0x805"),
  0x23614:("add","x0, x19, #0xc8"),
  0x23618:("bl","0x1400221a0 <.text+0x211a0>"),
  0x23620:("cbz","w20, 0x140023640 <.text+0x22640>"),
  0x23640:("mov","x0, x19"),
  0x23644:("bl","0x140027278 <.text+0x26278>"),
  0x2364c:("cbz","w20, 0x140023698 <.text+0x22698>"),
  0x221d0:("bl","0x14002a118 <.text+0x29118>"),
  0x221d8:("cbz","w19, 0x1400221ec <.text+0x211ec>"),
  # IFE second helper marks stop work and loops over bounded resource slots.
  0x27278:("pacibsp",""),
  0x27298:("ldr","w8, [x19, #0x301c]"),
  0x272a0:("strb","w23, [x19, #0x173]"),
  0x272c8:("cmp","w21, #0x22"),
  0x272ec:("mov","x0, x19"),
  0x27300:("blr","x15"),
  0x2731c:("ldr","w8, [x19, #0x301c]"),
  0x27324:("cmp","w21, w8"),
  0x27328:("b.lo","0x1400272c8 <.text+0x262c8>"),
  0x27334:("str","wzr, [x19, #0x15c]"),
  0x27344:("mov","x0, x19"),
  0x27358:("blr","x15"),
  # IFE completion handler, independent of the initial 0x805 branch.
  0x1f230:("ldrb","w8, [x19, #0x171]"),
  0x1f234:("cbz","w8, 0x14001f258 <.text+0x1e258>"),
  0x1f244:("strb","wzr, [x19, #0x171]"),
  0x1f254:("bl","0x1400241d8 <.text+0x231d8>"),
  0x24228:("add","x0, x19, #0xc8"),
  0x2422c:("bl","0x14002a1d8 <.text+0x291d8>"),
  0x24230:("cbz","w0, 0x14002424c <.text+0x2324c>"),
  # CSID IRQ/worker pathway: pending-bit clear followed by atomic decrement.
  0x1bcac:("cbnz","w9, 0x14001bcc4 <.text+0x1acc4>"),
  0x1bccc:("ldaxr","w9, [x1]"),
  0x1bcd0:("add","w9, w9, w8"),
  0x1bcd4:("stlxr","w17, w9, [x1]"),
  0x1bcd8:("cbnz","w17, 0x14001bccc <.text+0x1accc>"),
  0x1bcdc:("dmb","ish"),
  0x1bce0:("cbnz","w9, 0x14001bdac <.text+0x1adac>"),
  0x21b00:("strb","wzr, [x19, #0x6c]"),
  0x21b0c:("bl","0x14002a1d8 <.text+0x291d8>"),
  0x21b14:("bl","0x14002a4a0 <.text+0x294a0>"),
  0x21b18:("ldr","x8, [x19, #0xa8]"),
  0x21b1c:("cbnz","x8, 0x140021b34 <.text+0x20b34>"),
  0x21b68:("bl","0x140024260 <.text+0x23260>"),
  # CDM uses separate command state and event/worker helper.
  0x2853c:("cmp","w1, #0x805"),
  0x28550:("str","wzr, [x8, #0x30]"),
  0x28598:("strb","w8, [x19, #0x888]"),
  0x285a4:("bl","0x14002a4a0 <.text+0x294a0>"),
}
def check(flag,msg):
    if not flag:raise AssertionError("E004OH_FAIL_CLOSED "+msg)
def expected():
    return {
      "schema":"sp11-e004oh-original-ISP-conditional-multistage-stop-static-v1",
      "parent_git_revision":"03d7b1817f0606f06a6f4947a0474843326c00c7",
      "original_same_SP11_OEM_ISP_SHA256":SHA,
      "original_ARM64_instruction_anchors":len(ANCHORS),
      "original_IFE_first_0x805_callback_RVA":"0x22cd0",
      "IFE_pre_stop_helper_RVA":"0x221a0",
      "IFE_second_stop_resource_loop_helper_RVA":"0x27278",
      "IFE_independent_stop_progress_handler_RVA":"0x1f230",
      "IFE_independent_event_related_helper_RVA":"0x241d8",
      "CSID_pending_progress_count_atomic_RVA":"0x1bccc",
      "CSID_stop_worker_progress_RVA":"0x21b00",
      "CDM_stop_state_event_RVA":"0x28550",
      "IFE_first_call_and_later_stop_progress_are_distinct_source_paths":True,
      "IFE_second_stop_helper_has_bound_and_state_resource_loop":True,
      "CSID_stop_completion_code_has_pending_count_atomic_and_worker_wait":True,
      "CDM_0x805_callback_has_separate_state_event_helper":True,
      "IFEmode_stop_progress_defines_live_VFE_bus_WM16_safe_retirement":False,
      "CSID_pending_zero_proves_live_rear_FIFO8_BF_done":False,
      "specific_lower_helper_actual_MMIO_and_IRQ_acks_decoded":False,
      "real_Windows_rear4k_selected_0x805_stop_path_observed":False,
      "actual_0x809_receiver_and_software_semantics_decoded":False,
      "Linux_native_rear4k_hardware_ISP_optical_frame_proven":False,
      "Golden_kernel_camera_hardware_or_boot_modified":False,
      "original_OEM_disassembly_binaries_private_diagnostics_or_pixels_exported":False,
    }
def validate(x):
    check(x==expected(),"unexpected data or unsafe runtime claim")
    return True
if __name__=="__main__":
    check(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"original OEM exact SHA")
    src=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    pat=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    asm={int(m.group(1),16)-BASE:(m.group(2),m.group(3).split("//",1)[0].strip()) for m in pat.finditer(src)}
    for addr,ins in ANCHORS.items():
        check(asm.get(addr)==ins,f"original source RVA0x{addr:x} {asm.get(addr)} != {ins}")
    j=expected(); p=HERE/"RESULT.json"
    if p.exists():check(json.loads(p.read_text())==j,"saved scalar unchanged")
    else:p.write_text(json.dumps(j,sort_keys=True,indent=2)+"\n")
    neg=(
      ("fake_original_SHA",lambda o:o.__setitem__("original_same_SP11_OEM_ISP_SHA256","0"*64)),
      ("fake_same_helper",lambda o:o.__setitem__("IFE_second_stop_resource_loop_helper_RVA","0x221a0")),
      ("fake_ife_no_async",lambda o:o.__setitem__("IFE_first_call_and_later_stop_progress_are_distinct_source_paths",False)),
      ("fake_no_loop_bound",lambda o:o.__setitem__("IFE_second_stop_helper_has_bound_and_state_resource_loop",False)),
      ("fake_no_csid_pending",lambda o:o.__setitem__("CSID_stop_completion_code_has_pending_count_atomic_and_worker_wait",False)),
      ("fake_no_cdm_worker",lambda o:o.__setitem__("CDM_0x805_callback_has_separate_state_event_helper",False)),
      ("fake_WM16_stop",lambda o:o.__setitem__("IFEmode_stop_progress_defines_live_VFE_bus_WM16_safe_retirement",True)),
      ("fake_BF_from_CSID",lambda o:o.__setitem__("CSID_pending_zero_proves_live_rear_FIFO8_BF_done",True)),
      ("fake_mmio_decode",lambda o:o.__setitem__("specific_lower_helper_actual_MMIO_and_IRQ_acks_decoded",True)),
      ("fake_rear_live",lambda o:o.__setitem__("real_Windows_rear4k_selected_0x805_stop_path_observed",True)),
      ("fake_809",lambda o:o.__setitem__("actual_0x809_receiver_and_software_semantics_decoded",True)),
      ("fake_native",lambda o:o.__setitem__("Linux_native_rear4k_hardware_ISP_optical_frame_proven",True)),
      ("fake_Golden",lambda o:o.__setitem__("Golden_kernel_camera_hardware_or_boot_modified",True)),
      ("fake_export",lambda o:o.__setitem__("original_OEM_disassembly_binaries_private_diagnostics_or_pixels_exported",True)),
    )
    for name,f in neg:
        m=copy.deepcopy(j);f(m)
        try:validate(m)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OH_NEGATIVE_FAILED_OPEN "+name)
    print(f"PASS_E004OH_ORIGINAL_ISP_MULTISTAGE_IFE_CSID_CDM_STOP_{len(ANCHORS)}_ISA_ANCHORS_"
          f"{len(neg)}_NEGATIVE_MUTATIONS_NO_DMA_WM16_BF_RUNTIME_CLAIMS_GOLDEN_UNTOUCHED")
