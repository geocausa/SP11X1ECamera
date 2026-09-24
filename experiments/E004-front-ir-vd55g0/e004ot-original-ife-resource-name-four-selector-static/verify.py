#!/usr/bin/env python3
"""E004ot: four original resource labels, mapped entries and IFE lookup cases.

Static original same-SP11 OEM ISA, original short descriptor-label bytes
and pre-existing E004nq P evidence; not proof of live callback selection.
No private OEM image/disassembly, physical/DMA addresses, KD or optical data
exported into this repository.
"""
import copy,hashlib,json,re,struct,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
SOURCE="""
22370|cmp|w24, #0x4
22374|csel|w24, w24, wzr, lo
2237c|str|w24, [x20, #0x120]
223c4|mov|w0, w24
223c8|b|0x140022408 <.text+0x21408>
22408|bl|0x14002b568 <.text+0x2a568>
22410|str|x0, [x20, #0x140]
31ac|adrp|x8, 0x14002f000 <.text+0x2e000>
31b0|add|x1, x8, #0xfe8
31b4|add|x0, x19, #0x24
31b8|bl|0x14002dae8 <.text+0x2cae8>
31bc|cbnz|w0, 0x1400031e4 <.text+0x21e4>
31d0|ldr|x8, [x8, #0x170]
31d4|blr|x8
31d8|ldr|x8, [x20, #0x810]
31dc|str|x0, [x8]
31e4|adrp|x8, 0x140030000 <.text+0x2f000>
31e8|add|x1, x8, #0x10
31ec|add|x0, x19, #0x24
31f0|bl|0x14002dae8 <.text+0x2cae8>
31f4|cbnz|w0, 0x14000323c <.text+0x223c>
3208|ldr|x8, [x8, #0x170]
320c|blr|x8
3210|ldr|x8, [x20, #0x810]
3214|str|x0, [x8, #0x8]
323c|adrp|x8, 0x140030000 <.text+0x2f000>
3240|add|x1, x8, #0x18
3244|add|x0, x19, #0x24
3248|bl|0x14002dae8 <.text+0x2cae8>
324c|cbnz|w0, 0x140003280 <.text+0x2280>
3260|ldr|x8, [x8, #0x170]
3264|blr|x8
3268|ldr|x8, [x20, #0x7e0]
3270|str|x0, [x8]
3280|adrp|x8, 0x140030000 <.text+0x2f000>
3284|add|x1, x8, #0x48
3288|add|x0, x19, #0x24
328c|bl|0x14002dae8 <.text+0x2cae8>
3290|cbnz|w0, 0x1400032c0 <.text+0x22c0>
32e4|ldr|x8, [x8, #0x170]
32e8|blr|x8
32ec|ldr|x8, [x20, #0x7e0]
32f4|str|x0, [x8, #0x8]
2b578|cmp|w0, #0x18
2b57c|b.hi|0x14002b70c <.text+0x2a70c>
2b580|adr|x9, 0x14002b734 <.text+0x2a734>
2b584|ldrsb|x8, [x9, w0, uxtw]
2b588|add|x8, x9, x8, lsl #2
2b58c|br|x8
2b590|adrp|x8, 0x14004a000
2b594|add|x8, x8, #0xee0
2b598|ldr|x8, [x8, #0x50]
2b59c|ldr|x0, [x8]
2b5a4|adrp|x8, 0x14004a000
2b5a8|add|x8, x8, #0xee0
2b5ac|ldr|x8, [x8, #0x50]
2b5b0|ldr|x0, [x8, #0x8]
2b5b8|adrp|x8, 0x14004a000
2b5bc|add|x8, x8, #0xee0
2b5c0|ldr|x8, [x8, #0x20]
2b5c4|b|0x14002b59c <.text+0x2a59c>
2b5c8|adrp|x8, 0x14004a000
2b5cc|add|x8, x8, #0xee0
2b5d0|ldr|x8, [x8, #0x20]
2b5d4|b|0x14002b5b0 <.text+0x2a5b0>
22440|ldr|x3, [x20, #0x140]
22474|cset|w9, hs
22478|str|w9, [x8, #0x678]
2247c|mov|x9, #0xc00
22480|mov|x8, #0x1200
22484|csel|x8, x9, x8, lo
22488|add|x8, x8, x3
2248c|str|x8, [x20, #0x150]
"""
ANCHORS={int(a,16):(b,c) for a,b,c in (row.split("|",2) for row in SOURCE.strip().splitlines())}
LABELS={0x2ffe8:"IFE0",0x30010:"IFE1",0x30018:"IFELITE0",0x30048:"IFELITE_CDM0"}
def need(ok,why):
    if not ok:raise AssertionError("E004OT_FAIL_CLOSED "+why)
def rva_at(image,target):
    pe=struct.unpack_from("<I",image,0x3c)[0]
    need(image[pe:pe+4]==b"PE\0\0" and struct.unpack_from("<H",image,pe+4)[0]==0xaa64,"original ARM64 PE")
    sh=pe+24+struct.unpack_from("<H",image,pe+20)[0]
    for i in range(struct.unpack_from("<H",image,pe+6)[0]):
        o=sh+40*i;size,rv,rawsize,raw=struct.unpack_from("<IIII",image,o+8)
        if rv<=target<rv+rawsize:return raw+target-rv
    raise AssertionError("source RVA not mapped %x"%target)
def original_label(image,rva):
    pos=rva_at(image,rva);end=image.find(b"\0",pos,pos+32)
    need(end>pos,"bounded original descriptor string")
    return image[pos:end].decode("ascii")
def lookup_branch(image,index):
    v=image[rva_at(image,0x2b734+index)]
    return 0x2b734+4*(v if v<128 else v-256)
def facts():
    return {
      "schema":"sp11-e004ot-original-ISP-IFE0-IFE1-IFELITE-resource-descriptors-and-four-selectors-static-v1",
      "parent_git_revision":"572dffb31238265c1fba12d4604764ce4939ff89",
      "same_SP11_original_OEM_ISP_sha256":SHA,
      "original_exact_ARM64_instruction_anchors":len(ANCHORS),
      "original_exact_PE_resource_label_strings_checked":len(LABELS),
      "original_exact_PE_jump_table_selector_entries_checked":4,
      "original_descriptor_resource_names":["IFE0","IFE1","IFELITE0","IFELITE_CDM0"],
      "selector_0_original_lookup_branch_RVA":"0x2b590",
      "selector_1_original_lookup_branch_RVA":"0x2b5a4",
      "selector_2_original_lookup_branch_RVA":"0x2b5b8",
      "selector_3_original_lookup_branch_RVA":"0x2b5c8",
      "selector_0_original_resource_array":"0x50:first:IFE0",
      "selector_1_original_resource_array":"0x50:second:IFE1",
      "selector_2_original_resource_array":"0x20:first:IFELITE0",
      "selector_3_original_resource_array":"0x20:second:IFELITE_CDM0",
      "original_0x22b_type_branch_allows_instance_selector_1":True,
      "previous_source_checks_of_selectors_0_2_3_do_not_exclude_selector_1":True,
      "previous_E004nq_windows_rear4k_physical_VFE1_active":True,
      "previous_E004nq_windows_rear4k_physical_VFE0_inactive":True,
      "original_live_Windows_rear4k_callback_selected_lookup_selector_1_proven":False,
      "original_descriptor_label_IFE1_alone_proves_live_selected_VFE1_mapping":False,
      "actual_live_rear4k_callback_dispatch_mode_and_BF_event_0x0f_proven":False,
      "BF_WM16_bus_IRQ_DMA_retirement_proven":False,
      "native_Linux_rear_processed_hardware_ISP_4k_optical_frame_proven":False,
      "Golden_boot_or_camera_hardware_modified":False,
      "private_OEM_binary_bulk_disassembly_DMA_physical_KD_optical_exported":False,
    }
def strict(x):need(x==facts(),"invalid source claim")
if __name__=="__main__":
    image=ISP.read_bytes()
    need(hashlib.sha256(image).hexdigest()==SHA,"original same-SP11 ISP SHA")
    raw=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    asm={int(m[1],16)-BASE:(m[2],m[3].split("//",1)[0].strip()) for m in rx.finditer(raw)}
    for rva,ins in ANCHORS.items():need(asm.get(rva)==ins,"original ARM64 anchor %x"%rva)
    for rva,name in LABELS.items():need(original_label(image,rva)==name,"original short descriptor label RVA %x"%rva)
    for selector,expected in enumerate((0x2b590,0x2b5a4,0x2b5b8,0x2b5c8)):
        need(lookup_branch(image,selector)==expected,"original signed-byte jump selector %d"%selector)
    prior=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004os-ife-original-mmio-map-resource-array-producer-static/RESULT.json").read_text())
    need(prior["original_ntoskrnl_MmMapIoSpaceEx_IAT_RVA"]=="0x3f170" and
         prior["actual_live_Windows_rear4k_selected_MMIO_resource_entry_and_physical_IFE_instance_known"] is False,
         "E004os original mapper conservative")
    physical=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004nq-rear-physical-mmio-5phase/RESULT.json").read_text())
    need(physical["rear_OEM_Windows_VFE1_PIX_3840x2160_confirmed_across_two_live_passes"] is True and
         physical["Linux_rear_native_4k_ISP_optical_frame_proven"] is False,"E004nq P vs native Linux not proven")
    vfe={r["region"]:r for r in physical["region_stats"]}
    need(vfe["VFE1"]["LIVE1_nonzero_nonsentinel_dwords"]>0 and vfe["VFE0"]["LIVE1_nonzero_nonsentinel_dwords"]==0 and
         vfe["VFE1"]["LIVE2_nonzero_nonsentinel_dwords"]>0 and vfe["VFE0"]["LIVE2_nonzero_nonsentinel_dwords"]==0,
         "preexisting Windows physical rear session route")
    result=facts();path=HERE/"RESULT.json"
    if path.exists():need(json.loads(path.read_text())==result,"saved scalar differs")
    else:path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    mutants=(
       ("fake_SHA","same_SP11_original_OEM_ISP_sha256","0"*64),
       ("fake_labels","original_descriptor_resource_names",["IFE0","IFE1","IFELITE1","IFELITE_CDM0"]),
       ("fake_selector1","selector_1_original_lookup_branch_RVA","0x2b590"),
       ("fake_IFE1","selector_1_original_resource_array","0x20:second:IFE1"),
       ("fake_IFELITE","selector_3_original_resource_array","0x50:second:IFELITE_CDM0"),
       ("fake_0x22b","original_0x22b_type_branch_allows_instance_selector_1",False),
       ("fake_old","previous_source_checks_of_selectors_0_2_3_do_not_exclude_selector_1",False),
       ("fake_P","previous_E004nq_windows_rear4k_physical_VFE1_active",False),
       ("fake_P0","previous_E004nq_windows_rear4k_physical_VFE0_inactive",False),
       ("fake_selected","original_live_Windows_rear4k_callback_selected_lookup_selector_1_proven",True),
       ("fake_physical_identity","original_descriptor_label_IFE1_alone_proves_live_selected_VFE1_mapping",True),
       ("fake_mode","actual_live_rear4k_callback_dispatch_mode_and_BF_event_0x0f_proven",True),
       ("fake_DMA","BF_WM16_bus_IRQ_DMA_retirement_proven",True),
       ("fake_Linux","native_Linux_rear_processed_hardware_ISP_4k_optical_frame_proven",True),
       ("fake_Golden","Golden_boot_or_camera_hardware_modified",True),
       ("fake_private","private_OEM_binary_bulk_disassembly_DMA_physical_KD_optical_exported",True),
    )
    for name,k,v in mutants:
        f=copy.deepcopy(result);f[k]=v
        try:strict(f)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OT_NEGATIVE_FAIL_OPEN "+name)
    print("PASS_E004OT_%d_ORIGINAL_ARM64_INSTRUCTIONS_4_ORIGINAL_PE_LABELS_4_ORIGINAL_PE_JUMP_SELECTORS_%d_NEGATIVES_PRIOR_WINDOWS_REAR_VFE1_P_DISTINGUISHED_FROM_UNPROVEN_CALLBACK_GOLDEN_SAFE"%(len(ANCHORS),len(mutants)))
