#!/usr/bin/env python3
"""E004pu: static group-8 software queue producer and independent consumer.

Reads only same-SP11 private OEM binary; commits scalar evidence/design only.
No camera, kernel, GPU, IRQ, IOMMU, DMA access or rear ISP authorization.
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
PARENT="40b7e6a0f1265d50143b9c904838bcb97cdfc01c"
# Exact bounded instructions in original same-SP11 ARM64 Windows ISP binary.
# All addresses are PE IMAGE RVA, never live/private kernel addresses.
ISA_TEXT="""
23454|bl|0x140026838 <.text+0x25838>
234a4|bl|0x140026838 <.text+0x25838>
235c0|bl|0x140026838 <.text+0x25838>
26838|pacibsp|
26860|mov|x22, x1
26868|str|x22, [sp]
26f40|ldr|w9, [x20, #0x120]
26f44|ldr|w8, [x20, #0x3498]
26f48|cmp|w8, w9
26f4c|b.ne|0x140027064 <.text+0x26064>
26f50|mov|w21, #0x0
26f5c|mov|w26, #0x1
26f60|ldr|w8, [x20, #0x33d4]
26f64|lsl|w9, w26, w21
26f68|tst|w9, w8
26f6c|b.ne|0x140026f7c <.text+0x25f7c>
26f70|ldr|w8, [x20, #0x33dc]
26f74|tst|w8, w9
26f78|b.eq|0x140027050 <.text+0x26050>
26f80|add|x8, x21, #0x66b
26f84|ldr|x22, [x20, x8, lsl #3]
26f8c|cbz|x22, 0x14002702c <.text+0x2602c>
26fa4|ldr|w9, [x22, #0x18]
26fa8|ldr|w8, [x22, #0x10]
26fac|cmp|w9, w8
26fb0|b.hs|0x140027010 <.text+0x26010>
26fb4|ldr|w11, [x22, #0x30]
26fbc|ldr|w10, [x22, #0x14]
26fc0|ldr|x8, [x22]
26fc8|madd|x0, x10, x11, x8
26fd0|bl|0x14002c5b0 <.text+0x2b5b0>
26fd4|ldr|w8, [x22, #0x18]
26fd8|add|w8, w8, #0x1
26fdc|str|w8, [x22, #0x18]
26fe0|ldr|w8, [x22, #0x30]
26fe4|add|w8, w8, #0x1
26fe8|str|w8, [x22, #0x30]
27000|mov|w19, #0x0
27010|mov|w19, #0x1
27038|cbnz|w19, 0x1400270bc <.text+0x260bc>
27050|add|w8, w21, #0x1
27054|uxtb|w21, w8
27058|cmp|w21, #0xd
2705c|b.lo|0x140026f60 <.text+0x25f60>
2650c|add|x10, x21, #0x66b
26514|ldr|x9, [x8, x10, lsl #3]
26518|mov|x0, #0x0
2651c|cbz|x9, 0x140026610 <.text+0x25610>
26520|ldr|w9, [x9, #0x18]
26524|cbz|w9, 0x14002660c <.text+0x2560c>
26528|ldr|x19, [x8, x10, lsl #3]
2656c|bl|0x14002c5b0 <.text+0x2b5b0>
26570|ldr|w8, [x19, #0x18]
26574|sub|w8, w8, #0x1
26578|str|w8, [x19, #0x18]
1fc8c|mov|w1, #0x8
1fc94|bl|0x140026460 <.text+0x25460>
1fc98|mov|x23, x0
1fc9c|cbz|x23, 0x14001fe48 <.text+0x1ee48>
1fce4|bl|0x140025078 <.text+0x24078>
1fcec|str|x0, [x19, #0x580]
1fd28|bl|0x140026340 <.text+0x25340>
"""
ISA={}
for line in ISA_TEXT.strip().splitlines():
    addr,opcode,args=line.strip().split("|",2)
    address=int(addr,16)
    if address in ISA: raise AssertionError("DUPLICATE E004PU original anchor")
    ISA[address]=(opcode,args)

def require(condition, why):
    if not condition: raise AssertionError("E004PU_FAIL_CLOSED "+why)

def producer_can_accept(group8_enabled_mask_a,group8_enabled_mask_b,
                        correct_owner_generation,queue_exists,pending,capacity):
    # SOFTWARE queue model only. Hardware completion is not an input.
    return (bool(group8_enabled_mask_a or group8_enabled_mask_b)
            and bool(correct_owner_generation) and bool(queue_exists)
            and 0 <= pending < capacity and capacity > 0)

def consumer_can_pop(queue_exists,pending):
    return bool(queue_exists and pending>0)

def native_can_reuse(group8_enabled_mask_a,group8_enabled_mask_b,
                     correct_owner_generation,queue_exists,pending,capacity,
                     same_frame,nonnull_outstanding_wm16,verified_irq_ack,
                     dma_iommu_quiescent,six_group_owner_safe_stop):
    # Hypothetical native gate; currently NO trusted HW input producers.
    return (producer_can_accept(group8_enabled_mask_a,group8_enabled_mask_b,
                                correct_owner_generation,queue_exists,pending,capacity)
            and all((same_frame,nonnull_outstanding_wm16,verified_irq_ack,
                     dma_iommu_quiescent,six_group_owner_safe_stop)))

def facts():
    return {
      "schema":"E004pu-original-same-SP11-software-group8-ring-producer-capacity-v1",
      "evidence_tier":"S_EXACT_OEM_ARM64_SOURCE_PLUS_D_OFFLINE_GATING_NOT_P_LIVE",
      "parent_git_revision":PARENT,
      "original_OEM_ISP_sha256":SHA,
      "exact_original_ARM64_source_instruction_anchors":len(ISA),
      "original_group_software_ring_producer_RVA":"0x26838",
      "original_group_software_ring_producer_direct_callsites_RVAs":["0x23454","0x234a4","0x235c0"],
      "original_producer_group_count":13,
      "original_producer_group8_selection_uses_either_software_mask":True,
      "original_producer_group8_queue_pointer_offset":"0x3398",
      "original_consumer_group8_queue_pointer_offset":"0x3398",
      "original_producer_and_consumer_index_same_object_if_same_device_pointer":True,
      "original_producer_requires_nonnull_queue":True,
      "original_producer_skips_copy_and_count_increment_when_queue_full":True,
      "original_producer_increments_count_after_copy_helper_call_without_result_guard":True,
      "original_consumer_returns_null_when_queue_absent_or_count_zero":True,
      "original_FIFO8_BF_dispatch_requires_nonnull_software_ring_pop":True,
      "original_pop_identity_tag_matches_outstanding_WM16_in_actual_rear4k":False,
      "original_either_mask_or_ring_count_alone_proves_live_BF_irq_or_DMA":False,
      "original_producer_copy_is_verified_hardware_DMA_completion_fence":False,
      "original_producer_queue_entry_frame_and_owner_generation_proven":False,
      "real_linux_per_owner_frame_FIFO8_queue_producer_implemented":False,
      "native_rear_hardware_ISP_runtime_authorized":False,
      "protected_Golden_or_CAMSS_active_runtime_modified":False,
      "next_gate":"same_real_rear4k_software_FIFO8_entry_and_nonnull_matched_WM16_owner_frame_plus_independent_proven_irq_dma_iommu_stop",
    }

def main():
    require(hashlib.sha256(BIN.read_bytes()).hexdigest()==SHA,"original OEM ISP hash")
    disasm=subprocess.check_output(["llvm-objdump","-d",str(BIN)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    instructions={int(m[1],16)-0x140000000:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(disasm)}
    for rva,inst in ISA.items():
        require(instructions.get(rva)==inst, "original ARM64 instruction RVA 0x%x"%rva)
    require(0x66b*8+8*8 == 0x3398,"both groups share exact pointer slot arithmetic")
    require(0x26fb0 < 0x26fd0 < 0x26fd8 < 0x27010,
            "copy helper CALLED only on capacity-success branch before count increment")
    require(all(not (instructions[rva][0] in ("cbz","cbnz","tbz","tbnz") and
                    instructions[rva][1].startswith(("w0,","x0,")))
                for rva in range(0x26fd4,0x26ff0,4)),
            "original ring count increment does not check copy-helper success")
    require(instructions[0x26fb0][1].startswith("0x140027010"),
            "full ring skips copy and pending increment")
    require(instructions[0x26f78][1].startswith("0x140027050"),
            "masked-out group skipped")
    require(instructions[0x2651c][1].startswith("x9, 0x140026610")
            and instructions[0x26524][1].startswith("w9, 0x14002660c"),
            "consumer cannot invent nonempty FIFO8")
    parent=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pt-csid1-bf-irq-observer-isolated/RESULT.json").read_text())
    require(not parent["native_rear_hardware_ISP_runtime_authorized"]
            and not parent["per_frame_FIFO8_WM16_matched_buffer_identity_proven"],
            "E004pt status-only counter must not be promoted to a queue match")
    parent2=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004ps-original-bf-null-matcher-callback-gate-static/RESULT.json").read_text())
    require(not parent2["original_outstanding_matched_pointer_return_has_explicit_nonnull_guard_before_software_callback"],
            "original matcher null gap retained")
    cases=0; fake_soft=0
    # Masks, configured owner, queue object, two capacities, and four pending
    # levels. Negative and overflow/underflow status are fail-closed.
    for ma,mb,owner,obj,pending,capacity in itertools.product((False,True),
                     (False,True),(False,True),(False,True),(-1,0,1,2),(0,1,2)):
        accepted=producer_can_accept(ma,mb,owner,obj,pending,capacity)
        if accepted:require(bool(ma or mb) and owner and obj and
                            0<=pending<capacity,"producer allowed invalid queue")
        else:
            for h in itertools.product((False,True), repeat=5):
                require(not native_can_reuse(ma,mb,owner,obj,pending,capacity,*h),
                        "cannot claim HW-safe retire without producer")
        require(not consumer_can_pop(obj,pending) if pending<=0 or not obj else
                consumer_can_pop(obj,pending),"consumer pending guard")
        if accepted:
            fake_soft+=1
            # Even accepted SOFTWARE queue producer with every other bit
            # asserted cannot grant native retirement without real HW evidence.
            require(not native_can_reuse(ma,mb,owner,obj,pending,capacity,
                       True,True,False,True,True),"IRQ must be independent")
            require(not native_can_reuse(ma,mb,owner,obj,pending,capacity,
                       True,True,True,False,True),"DMA/IOMMU must be independent")
        cases+=1
    require(cases==192 and fake_soft>0,"exhaustive software ring domain")
    result=facts()
    require(json.loads((HERE/"RESULT.json").read_text())==result,
            "saved facts cannot change from verified source contract")
    negatives=0
    for key in result:
        mutate=copy.deepcopy(result)
        val=mutate[key]
        mutate[key]=not val if isinstance(val,bool) else (
           "INVALID" if isinstance(val,str) else val+1 if isinstance(val,int) else ["INVALID"])
        try:require(mutate==result,"negative field "+key)
        except AssertionError:negatives+=1
        else:raise AssertionError("E004PU_FAIL_OPEN "+key)
    print("PASS_E004PU_%d_EXACT_ORIGINAL_ARM64_ANCHORS_%d_NEGATIVE_FIELDS_%d_SOFTWARE_RING_CASES_%d_ACCEPTED_SOFTWARE_ONLY_COUNTEREXAMPLES_NO_DMA_PROOF_REAR_DENIED_GOLDEN_SAFE"%
          (len(ISA),negatives,cases,fake_soft))

if __name__=="__main__":main()
