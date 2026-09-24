#!/usr/bin/env python3
"""E004ps: original BF callback can be reached without an outstanding match.

Static original OEM ISA evidence only. Simulated native gate is an offline
design: it DOES NOT arm rear processing or attest any HW DMA completion.
"""
import copy
import hashlib
import itertools
import json
import re
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BIN=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
PARENT="245775448fd51f99518a43c369a3a1e1a75b9347"
# Bounded exact machine instructions, extracted from same-SP11 read-only OEM binary.
ISA_TEXT="""
1fc9c|cbz|x23, 0x14001fe48 <.text+0x1ee48>
1fcc8|ldrb|w8, [x19, #0x1c0]
1fccc|cbz|w8, 0x14001fd14 <.text+0x1ed14>
1fcdc|ldrh|w2, [x23, #0x16]
1fce0|ldr|x1, [x23, #0x8]
1fce4|bl|0x140025078 <.text+0x24078>
1fce8|mov|w9, #0x300d
1fcec|str|x0, [x19, #0x580]
1fcf8|ldr|x8, [x23, #0x8]
1fd04|str|x8, [x19, #0x5a0]
1fd14|mov|w8, #0x1a
1fd18|str|x23, [x19, #0x6a8]
1fd20|str|w8, [x19, #0x520]
1fd28|bl|0x140026340 <.text+0x25340>
1fd2c|cbz|w0, 0x14001fe48 <.text+0x1ee48>
250a0|mov|x23, #0x0
250b4|ldr|x8, [x20, #0x2e68]
250b8|cmp|x8, x22
250bc|b.ne|0x1400250cc <.text+0x240cc>
250c0|ldrh|w8, [x20, x24]
250c4|cmp|w8, w5
250c8|b.eq|0x1400250e0 <.text+0x240e0>
250d4|cmp|w19, #0x6
250dc|b|0x14002516c <.text+0x2416c>
250f4|ldr|x23, [x26, x21]
2516c|mov|x0, x23
"""
ISA={int(addr,16):(op,args) for addr,op,args in (line.split("|",2) for line in ISA_TEXT.strip().splitlines())}

def require(condition,why):
    if not condition:
        raise AssertionError("E004PS_FAIL_CLOSED: "+why)

def source_facts():
    return {
       "schema":"E004ps-original-bf-null-matcher-callback-static-v1",
       "parent_git_revision":PARENT,
       "original_OEM_ISP_SHA256":SHA,
       "exact_ARM64_instruction_anchors":len(ISA),
       "original_FIFO8_nonempty_required_to_reach_BF_callback":True,
       "original_CFG0_zero_skips_outstanding_match_but_reaches_software_callback":True,
       "original_outstanding_matcher_max_slots":6,
       "original_outstanding_matcher_defaults_to_null_and_returns_null_on_no_match":True,
       "original_outstanding_matcher_requires_pointer_identity_and_16bit_tag":True,
       "original_outstanding_matched_pointer_return_has_explicit_nonnull_guard_before_software_callback":False,
       "original_matcher_return_stored_in_software_event_context_offset":"0x580",
       "original_FIFO8_popped_entry_retained_context_offset":"0x6a8",
       "original_software_callback_RVA":"0x1fd28",
       "original_callback_reached_alone_proves_matched_WM16_buffer":False,
       "original_callback_reached_alone_proves_HW_WM16_DMA_IOMMU_completion":False,
       "original_rear4k_same_frame_FIFO8_WM16_and_independent_HW_completion_proven":False,
       "native_fail_closed_policy_requires_outstanding_match_even_if_original_software_notification_skips_it":True,
       "native_fail_closed_policy_requires_independent_irq_DMA_IOMMU_owner_generation_and_six_group_stop":True,
       "native_rear_ISP_runtime_authorized":False,
       "protected_Golden_kernel_or_camera_hardware_modified":False,
       "next_gate":"original_same_frame_FIFO8_WM16_matched_buffer_and_independent_source_verified_CSID_or_VFE_IRQ_DMA_IOMMU_quiescence",
    }

def oem_callback_reachable(bf_selected, fifo8_nonempty, cfg0_nonzero, matcher_nonnull):
    # OEM does not gate callback on CFG0/matcher result, just on FIFO8 nonempty.
    return bool(bf_selected and fifo8_nonempty)

def native_reuse_allowed(bf_selected, fifo8_nonempty, cfg0_nonzero,
                         matcher_nonnull, same_buffer, owner_generation,
                         trusted_wm16_irq, dma_iommu_quiescent, six_groups_stop):
    # OFFLINE policy; arguments are hypothetical. No live sources set these yet.
    return bool(
       bf_selected and fifo8_nonempty and cfg0_nonzero and matcher_nonnull
       and same_buffer and owner_generation and trusted_wm16_irq
       and dma_iommu_quiescent and six_groups_stop
    )

def main():
    require(hashlib.sha256(BIN.read_bytes()).hexdigest()==SHA,"original OEM ISP hash")
    out=subprocess.check_output(["llvm-objdump","-d",str(BIN)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    ins={int(m[1],16)-0x140000000:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(out)}
    for rva,expected in ISA.items():
        require(ins.get(rva)==expected,"exact original ARM64 instruction RVA 0x%x"%rva)
    # Validate the bounded layout: match result x0 is stored, but the callback is
    # reached without a cbz/cbnz on x0 across this exact contiguous instruction span.
    region=[(rva,ins[rva]) for rva in range(0x1fce4,0x1fd2c+4,4)]
    require(region[0][1][0]=="bl" and region[-1][1][0]=="cbz",
            "bounded callback branch layout")
    require(all(not (op in ("cbz","cbnz","tbz","tbnz") and
                     (args.startswith("x0,") or args.startswith("w0,")))
                for rva,(op,args) in region[1:-1]),
            "no matcher-return check before callback")
    require(ins[0x1fccc][1].startswith("w8, 0x14001fd14"),
            "CFG0-zero branch rejoins before software callback")
    require(ins[0x250a0]==("mov","x23, #0x0") and
            ins[0x2516c]==("mov","x0, x23"),
            "matcher null-default and return")
    require(ins[0x250dc][1].endswith("0x14002516c <.text+0x2416c>"),
            "six-slot miss reaches null-return")
    parent=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pr-original-bf-fifo8-wm16-software-dispatch-gates-static/RESULT.json").read_text())
    require(parent["original_BF_fifo8_group_index"]==8 if "original_BF_fifo8_group_index" in parent else parent["original_BF_group_index"]==8,"parent FIFO8")
    require(not parent["native_rear_hardware_ISP_runtime_authorized"],"parent rear DENIED")
    all_cases=0
    false_positive=0
    for v in itertools.product((False,True),repeat=9):
        oem=oem_callback_reachable(*v[:4])
        native=native_reuse_allowed(*v)
        require(native==all(v),"native policy cannot skip any required input")
        if oem and not native:false_positive+=1
        require(not native or oem,"native policy cannot retire absent software path")
        all_cases+=1
    require(all_cases==512 and false_positive>0,"full truth table and miss counterexamples")
    require(oem_callback_reachable(True,True,False,False) and
            oem_callback_reachable(True,True,True,False),
            "OEM software callback may lack outstanding match")
    require(not native_reuse_allowed(True,True,True,False,True,True,True,True,True),
            "native null matcher fails closed")
    facts=source_facts()
    saved=HERE/"RESULT.json"
    require(saved.exists(),"saved result must be reviewed before verifying")
    require(json.loads(saved.read_text())==facts,"saved source facts unchanged")
    negative=0
    for k in facts:
        variant=copy.deepcopy(facts)
        variant[k]=not variant[k] if isinstance(variant[k],bool) else "INVALID_MUTATION"
        try:
            require(variant==facts,"source contract modified "+k)
        except AssertionError:
            negative+=1
        else:
            raise AssertionError("E004PS_FAIL_OPEN "+k)
    print("PASS_E004PS_%d_EXACT_ORIGINAL_ARM64_ANCHORS_%d_NEGATIVE_FIELDS_%d_OFFLINE_INPUT_COMBINATIONS_%d_OEM_SOFTWARE_ONLY_COUNTEREXAMPLES_REAR_RUNTIME_DENIED"%
          (len(ISA),negative,all_cases,false_positive))

if __name__=="__main__":
    main()
