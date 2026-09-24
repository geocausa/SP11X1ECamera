#!/usr/bin/env python3
"""E004os: original SP11 ISP IFE base lookup is populated by MmMapIoSpaceEx.

Offline SHA-locked OEM ISA and import-table tests; no private driver,
bulk disassembly, physical/DMA addresses, image or KD data in the repo.
"""
import copy,hashlib,json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
2b1c|adrp|x8, 0x14004a000
2b20|add|x20, x8, #0xee0
2c64|ldr|x8, [x20, #0x50]
2c68|cbnz|x8, 0x140002cc0 <.text+0x1cc0>
2c70|lsl|w1, w0, #3
2c74|mov|w0, #0x3e
2c78|bl|0x14002a260 <.text+0x29260>
2c84|str|x0, [x20, #0x50]
2cc0|ldr|x8, [x20, #0x20]
2cc4|cbnz|x8, 0x140002d3c <.text+0x1d3c>
2ce8|mov|w0, #0x3e
2cf4|bl|0x14002a260 <.text+0x29260>
2d00|str|x0, [x20, #0x20]
2f14|ldr|w8, [x26]
2f18|mov|w24, #0x0
2f1c|cbz|w8, 0x140003370 <.text+0x2370>
2f20|adrp|x8, 0x14004a000
2f24|add|x20, x8, #0x720
2f30|mov|x8, #0x38
2f34|umaddl|x19, w24, w8, x25
2f40|add|x0, x19, #0x24
2f44|bl|0x14002dae8 <.text+0x2cae8>
31ac|adrp|x8, 0x14002f000 <.text+0x2e000>
31b0|add|x1, x8, #0xfe8
31b4|add|x0, x19, #0x24
31b8|bl|0x14002dae8 <.text+0x2cae8>
31bc|cbnz|w0, 0x1400031e4 <.text+0x21e4>
31c0|ldr|w1, [x19, #0x20]
31c4|mov|w2, #0x4
31c8|ldr|x0, [x19, #0x18]
31cc|adrp|x8, 0x14003f000
31d0|ldr|x8, [x8, #0x170]
31d4|blr|x8
31d8|ldr|x8, [x20, #0x810]
31dc|str|x0, [x8]
31e4|adrp|x8, 0x140030000 <.text+0x2f000>
31e8|add|x1, x8, #0x10
31ec|add|x0, x19, #0x24
31f0|bl|0x14002dae8 <.text+0x2cae8>
31f4|cbnz|w0, 0x14000323c <.text+0x223c>
31f8|ldr|w1, [x19, #0x20]
31fc|mov|w2, #0x4
3200|ldr|x0, [x19, #0x18]
3204|adrp|x8, 0x14003f000
3208|ldr|x8, [x8, #0x170]
320c|blr|x8
3210|ldr|x8, [x20, #0x810]
3214|str|x0, [x8, #0x8]
323c|adrp|x8, 0x140030000 <.text+0x2f000>
3240|add|x1, x8, #0x18
3244|add|x0, x19, #0x24
3248|bl|0x14002dae8 <.text+0x2cae8>
324c|cbnz|w0, 0x140003280 <.text+0x2280>
3250|ldr|w1, [x19, #0x20]
3254|mov|w2, #0x4
3258|ldr|x0, [x19, #0x18]
325c|adrp|x8, 0x14003f000
3260|ldr|x8, [x8, #0x170]
3264|blr|x8
3268|ldr|x8, [x20, #0x7e0]
3270|str|x0, [x8]
3280|adrp|x8, 0x140030000 <.text+0x2f000>
3284|add|x1, x8, #0x48
3288|add|x0, x19, #0x24
328c|bl|0x14002dae8 <.text+0x2cae8>
3290|cbnz|w0, 0x1400032c0 <.text+0x22c0>
32d4|ldr|w1, [x19, #0x20]
32d8|mov|w2, #0x4
32dc|ldr|x0, [x19, #0x18]
32e0|adrp|x8, 0x14003f000
32e4|ldr|x8, [x8, #0x170]
32e8|blr|x8
32ec|ldr|x8, [x20, #0x7e0]
32f4|str|x0, [x8, #0x8]
3358|ldr|w8, [x26]
335c|add|w24, w24, #0x1
3360|cmp|w24, w8
3364|b.lo|0x140002f30 <.text+0x1f30>
2b590|adrp|x8, 0x14004a000
2b594|add|x8, x8, #0xee0
2b598|ldr|x8, [x8, #0x50]
2b59c|ldr|x0, [x8]
2b5b8|adrp|x8, 0x14004a000
2b5bc|add|x8, x8, #0xee0
2b5c0|ldr|x8, [x8, #0x20]
2b5c4|b|0x14002b59c <.text+0x2a59c>
2b5c8|adrp|x8, 0x14004a000
2b5cc|add|x8, x8, #0xee0
2b5d0|ldr|x8, [x8, #0x20]
2b5d4|b|0x14002b5b0 <.text+0x2a5b0>
2b5b0|ldr|x0, [x8, #0x8]
22408|bl|0x14002b568 <.text+0x2a568>
22410|str|x0, [x20, #0x140]
22440|ldr|x3, [x20, #0x140]
22484|csel|x8, x9, x8, lo
22488|add|x8, x8, x3
2248c|str|x8, [x20, #0x150]
"""
ANCHORS={int(a,16):(b,c) for a,b,c in (line.split("|",2) for line in SOURCE.strip().splitlines())}
def need(ok,why):
    if not ok:raise AssertionError("E004OS_FAIL_CLOSED "+why)
def iat_slot(source,name):
    inside=False;which=None;base=None;index=0;out=[]
    for s in source.splitlines():
        s=s.strip()
        if s=="Import {":inside=True;which=None;base=None;index=0
        elif inside and s.startswith("Name: "):which=s[6:]
        elif inside and s.startswith("ImportAddressTableRVA: "):base=int(s.split(":",1)[1],16)
        elif inside and s.startswith("Symbol: "):
            need(base is not None,"symbol before IAT base")
            if which=="ntoskrnl.exe" and s.split()[1]==name:out.append(base+8*index)
            index+=1
        elif inside and s=="}":inside=False
    need(len(out)==1,"unique imported "+name)
    return out[0]
def result():
    return {
      "schema":"sp11-e004os-original-IFE-global-resource-MMIO-map-arrays-producer-static-v1",
      "parent_git_revision":"1746a5c8cef093e731c0ab94472a8d8fa71fb6bc",
      "same_SP11_original_OEM_ISP_sha256":SHA,
      "original_exact_ARM64_instruction_anchors":len(ANCHORS),
      "original_ntoskrnl_MmMapIoSpaceEx_IAT_RVA":"0x3f170",
      "original_ntoskrnl_MmUnmapIoSpace_IAT_RVA":"0x3f328",
      "original_resource_descriptor_physical_start_field_offset":"0x18",
      "original_resource_descriptor_length_field_offset":"0x20",
      "source_original_global_resource_array_table_RVA":"0x4aee0",
      "producer_original_global_resource_loop_base_RVA":"0x4a720",
      "resource_array_plus_0x50_allocation_store_RVA":"0x2c84",
      "resource_array_plus_0x20_allocation_store_RVA":"0x2d00",
      "resource_global_0x4a720_plus_0x810_equals_0x4aee0_plus_0x50":True,
      "resource_global_0x4a720_plus_0x7e0_equals_0x4aee0_plus_0x20":True,
      "conditional_resource_field_0x50_first_MMIO_mapping_store_RVA":"0x31dc",
      "conditional_resource_field_0x50_second_MMIO_mapping_store_RVA":"0x3214",
      "conditional_resource_field_0x20_first_MMIO_mapping_store_RVA":"0x3270",
      "conditional_resource_field_0x20_second_MMIO_mapping_store_RVA":"0x32f4",
      "resource_selector_zero_reads_0x50_first_entry":True,
      "resource_selector_two_reads_0x20_first_entry":True,
      "resource_selector_three_reads_0x20_second_entry":True,
      "IFE_init_selected_base_from_resource_lookup_RVA":"0x22410",
      "IFE_init_selected_register_window_from_base_RVA":"0x2248c",
      "each_conditional_mapping_call_independently_source_identified_as_MmMapIoSpaceEx":True,
      "actual_live_Windows_rear4k_selected_MMIO_resource_entry_and_physical_IFE_instance_known":False,
      "original_resource_mapping_success_and_nonnull_each_entry_verified_live":False,
      "original_resource_mapping_implies_WM16_IRQ_bus_DMA_retirement":False,
      "live_Windows_BF_0x0f_FIFO8_completion_observed":False,
      "Linux_native_rear_processed_hardware_ISP_4k_optical_frame_proven":False,
      "Golden_boot_or_camera_hardware_modified":False,
      "private_OEM_binary_bulk_disassembly_dma_physical_KD_optical_exported":False,
    }
def strict(x):need(x==result(),"result mutated or false physical claim")
if __name__=="__main__":
    need(hashlib.sha256(ISP.read_bytes()).hexdigest()==SHA,"original-SP11 OEM ISP SHA")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    asm={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for rva,ins in ANCHORS.items():need(asm.get(rva)==ins,"original ISA RVA %x"%rva)
    imports=subprocess.check_output(["llvm-readobj","--coff-imports",str(ISP)],text=True)
    need(iat_slot(imports,"MmMapIoSpaceEx")==0x3f170 and iat_slot(imports,"MmUnmapIoSpace")==0x3f328,"independent MMIO IAT identity")
    need(0x4a720+0x810==0x4aee0+0x50 and 0x4a720+0x7e0==0x4aee0+0x20,"global resource array alias arithmetic")
    prior=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004or-ife-register-window-provenance-static/RESULT.json").read_text())
    need(prior["source_global_table_original_RVA"]=="0x4aee0" and
         prior["global_resource_pointer_proven_physically_mapped_VFE1_for_live_rear4k"] is False,
         "E004or source-only original lookup")
    facts=result();saved=HERE/"RESULT.json"
    if saved.exists():need(json.loads(saved.read_text())==facts,"saved scalar mismatch")
    else:saved.write_text(json.dumps(facts,indent=2,sort_keys=True)+"\n")
    muts=(
      ("fake_SHA","same_SP11_original_OEM_ISP_sha256","0"*64),
      ("fake_import","original_ntoskrnl_MmMapIoSpaceEx_IAT_RVA","0x3f328"),
      ("fake_descriptor","original_resource_descriptor_physical_start_field_offset","0x20"),
      ("fake_length","original_resource_descriptor_length_field_offset","0x18"),
      ("fake_resource_global","source_original_global_resource_array_table_RVA","0x4a720"),
      ("fake_alias","resource_global_0x4a720_plus_0x810_equals_0x4aee0_plus_0x50",False),
      ("fake_first","conditional_resource_field_0x50_first_MMIO_mapping_store_RVA","0x3214"),
      ("fake_second","conditional_resource_field_0x20_second_MMIO_mapping_store_RVA","0x3270"),
      ("fake_unmapped","each_conditional_mapping_call_independently_source_identified_as_MmMapIoSpaceEx",False),
      ("fake_live","actual_live_Windows_rear4k_selected_MMIO_resource_entry_and_physical_IFE_instance_known",True),
      ("fake_success","original_resource_mapping_success_and_nonnull_each_entry_verified_live",True),
      ("fake_dma","original_resource_mapping_implies_WM16_IRQ_bus_DMA_retirement",True),
      ("fake_bf","live_Windows_BF_0x0f_FIFO8_completion_observed",True),
      ("fake_rear","Linux_native_rear_processed_hardware_ISP_4k_optical_frame_proven",True),
      ("fake_Golden","Golden_boot_or_camera_hardware_modified",True),
      ("fake_private","private_OEM_binary_bulk_disassembly_dma_physical_KD_optical_exported",True),
    )
    for name,k,v in muts:
        m=copy.deepcopy(facts);m[k]=v
        try:strict(m)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OS_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004OS_%d_EXACT_ORIGINAL_ARM64_INSTRUCTIONS_2_ORIGINAL_MMIO_IAT_IMPORTS_%d_NEGATIVES_ORIGINAL_RESOURCE_MMIO_PRODUCER_NOT_LIVE_REAR_DMA_PROOF_GOLDEN_SAFE"%(len(ANCHORS),len(muts)))
