#!/usr/bin/env python3
"""Source-locked static E004oe Windows ISP CDM/IFE/CSID dispatch order.

No kernel camera access, Windows session, image, private OEM code, secrets or
MMIO; this source verifies original SHA-pinned SP11 OEM driver and only exports
relative RVAs, original diagnostic hashes and explicit static-vs-live flags.
"""
import copy
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000

# The source diagnostics and their checked code references jointly identify
# each callsite's CDM / IFE / CSID role. Store diagnostic SHA only, NOT OEM
# literal diagnostics or original code.
STAGES={
 "0x804":{
 "CDM":(0x15f3c,0x15f50,0x15f5c,0x15f60,0x33fd8,"aab0f8a5597a7726ebd2f819e0189b678777e326f371d44281054308e23c67d5"),
 "IFE":(0x15fd8,0x15fec,0x16234,0x16238,0x34018,"cce31a89fbe1bbb1007cf137d206d990678164b837de1fee74bff1c15f45fa64"),
 "CSID":(0x161ec,0x16208,0x162ac,0x162b0,0x34100,"153bf5f953826750d0562d6ed62ebae9e27d45e68e55d86e825db68b28574914"),
 },
 "0x805":{
 "CSID":(0x163ac,0x163c8,0x163d8,0x163dc,0x34200,"219884eb5ea238e2b7749f45c793a324af0a35267a5d5a41b449b8fbe54cea4f"),
 "IFE":(0x16414,0x16434,0x16448,0x1644c,0x34240,"74799d36b5a4d27b7ecaae96aa8a7a0ef56af28fe6c5e398d25ff25deb0c4e73"),
 "CDM":(0x164a0,0x164b4,0x164c8,0x164cc,0x34280,"9ec5dab0d49a04a2edbfdd7a0eb9cbeb6b6d8a9f885b31e750b768ce6e605835"),
 },
}

OTHER={
 0x15d70:("pacibsp",""),
 0x15db4:("mov","w24, w1"),
 0x15ee0:("cmp","w24, #0x804"),
 0x15ee4:("b.ne","0x140016300 <.text+0x15300>"),
 0x15f58:("cbz","w19, 0x140015f78 <.text+0x14f78>"),
 0x15ff0:("cbnz","w0, 0x140016228 <.text+0x15228>"),
 0x1620c:("cbnz","w0, 0x1400162ac <.text+0x152ac>"),
 0x16300:("cmp","w24, #0x805"),
 0x16304:("b.ne","0x140016504 <.text+0x15504>"),
 0x1631c:("strb","wzr, [x21, #0x510]"),
 0x163cc:("cmp","w0, #0x0"),
 0x163d0:("ccmp","w0, #0x1a, #0x4, ne"),
 0x16438:("mov","w19, w0"),
 0x1643c:("cmp","w19, #0x0"),
 0x16440:("ccmp","w19, #0x1a, #0x4, ne"),
 0x164b8:("mov","w19, w0"),
 0x164bc:("cmp","w19, #0x0"),
 0x164c0:("ccmp","w19, #0x1a, #0x4, ne"),
 0x164f4:("ldr","w8, [x8, #0x24]"),
 0x164f8:("cmp","w24, w8"),
 0x164fc:("b.lo","0x140016360 <.text+0x15360>"),
  # The start-like branch uses multiple arrays and source-dependent fanout;
  # the stop-like branch follows a distinct first-call and extra calls.
  0x15f14:("ldr","x8, [x8, x9]"),
  0x15fac:("mov","x8, #0x30"),
  0x15fb0:("umaddl","x9, w19, w8, x9"),
  0x161c0:("ldr","x8, [x9, #0x30]"),
  0x16380:("ldr","x8, [x10, #0x30]"),
  0x16408:("ldr","x8, [x8, #0x30]"),
  0x1647c:("ldr","x8, [x8, x9]"),
  0x1586c:("str","x0, [x8, #0x30]"),
  0x15888:("str","x0, [x8, #0x40]"),
  0x158a8:("str","x0, [x20, x21]"),
}

def demand(b,why):
    if not b:raise AssertionError("E004OE_FAIL_CLOSED "+why)

def read_rva(data,rva,n):
    pe=struct.unpack_from("<I",data,0x3c)[0]
    demand(data[pe:pe+4]==b"PE\0\0" and struct.unpack_from("<H",data,pe+4)[0]==0xaa64,
           "original ARM64 PE")
    sh=pe+24+struct.unpack_from("<H",data,pe+20)[0]
    for i in range(struct.unpack_from("<H",data,pe+6)[0]):
        p=sh+i*40
        virtual_size,va,raw_size,raw=struct.unpack_from("<IIII",data,p+8)
        if va<=rva and rva+n<=va+raw_size:
            return data[raw+rva-va:raw+rva-va+n]
    raise AssertionError("missing original PE RVA")

def original_instructions():
    s=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    pattern=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    return {int(m.group(1),16)-BASE:(m.group(2),m.group(3).split("//",1)[0].strip())
            for m in pattern.finditer(s)}

def canonical():
    return {
     "schema":"sp11-e004oe-original-oem-isp-manager-core-fanout-order-static-v1",
     "parent_git_revision":"d3ce9c8a953295daeaaeaa404df9ffadeaa03546",
     "original_same_SP11_OEM_ISP_SHA256":SHA,
     "original_ARM64_instruction_anchors":len(OTHER)+len(STAGES["0x804"])*4+len(STAGES["0x805"])*4,
     "source_checked_dispatch_order":{
       key:[{"core":core,"call_selector_RVA":f"0x{v[0]:x}",
              "indirect_callback_RVA":f"0x{v[1]:x}",
              "failure_diagnostic_code_RVA":f"0x{v[2]:x}",
              "original_diagnostic_RVA":f"0x{v[4]:x}",
              "original_diagnostic_SHA256":v[5]}
            for core,v in group.items()] for key,group in STAGES.items()},
     "start_branch":"0x15ee0","stop_branch":"0x16300",
     "start_call_stage_order_is_CDM_IFE_CSID_statical_code":True,
     "stop_call_stage_order_is_CSID_IFE_CDM_static_code":True,
     "per_core_entry_fanout_and_guarded_failures_present":True,
     "original_ISP_manager_init_allocates_separate_per_core_interface_arrays":True,
     "ISP_0x809_effects_decoded":False,
     "actual_per_core_indirect_callback_bodies_and_MMIO_effects_proven":False,
     "live_rear_Windows_4k_recording_took_this_ISP_route_proven":False,
     "physical_stop_drained_DMA_WM16_and_BF_irq_proven":False,
     "Linux_native_rear_processed_4k_optical_frame_proven":False,
     "camera_hardware_Golden_kernel_or_boot_modified":False,
     "original_OEM_driver_bytes_optical_images_or_KD_secrets_exported":False,
    }

def validate(j):
    expect=canonical()
    demand(j==expect,"saved scalar/negative guard changed")
    demand([v["core"] for v in j["source_checked_dispatch_order"]["0x804"]]==["CDM","IFE","CSID"],"start stage order")
    demand([v["core"] for v in j["source_checked_dispatch_order"]["0x805"]]==["CSID","IFE","CDM"],"stop stage order")
    demand(j["actual_per_core_indirect_callback_bodies_and_MMIO_effects_proven"] is False,
           "unsafe hardware claim")
    return True

def verify_original():
    b=ISP.read_bytes()
    demand(hashlib.sha256(b).hexdigest()==SHA,"same-SP11 exact private OEM ISP SHA")
    ins=original_instructions()
    for rva,inst in OTHER.items():
        demand(ins.get(rva)==inst,"OEM source anchor OTHER "+hex(rva))
    for selector,group in STAGES.items():
        for core,(call,indirect,log,add,diag,diag_hash) in group.items():
            demand(ins.get(call)==("mov","w1, #"+selector),
                   "numeric selector source "+selector+"/"+core)
            demand(ins.get(indirect)==("blr","x15"),
                   "separate per-core callback "+selector+"/"+core)
            demand(ins.get(log)==("adrp","x8, 0x140033000 <.text+0x32000>")
                   if selector=="0x804" and core=="CDM" else
                   ins.get(log)==("adrp","x8, 0x140034000 <.text+0x33000>") ,
                   "diagnostic page xref "+selector+"/"+core)
            demand(ins.get(add)==("add","x1, x8, #0x%x"%(diag&0xfff)),
                   "diagnostic exact address xref "+selector+"/"+core)
            # Read *only* the original null-terminated private diagnostic and
            # verify its SHA-256; do not serialize the original OEM diagnostic.
            original=read_rva(b,diag,120).split(b"\x00",1)[0]
            demand(hashlib.sha256(original).hexdigest()==diag_hash,
                   "diagnostic proves CDM/IFE/CSID role "+selector+"/"+core)
            demand(call<indirect<log and add==log+4,
                   "conditional call precedes its matching failure path")
    return canonical()

if __name__=="__main__":
    actual=verify_original()
    p=HERE/"RESULT.json"
    if not p.exists():
        p.write_text(json.dumps(actual,indent=2,sort_keys=True)+"\n")
        print("E004OE_SCALAR_EVIDENCE_CREATED")
    else:
        demand(json.loads(p.read_text())==actual,"scalar persistence mismatch")
    neg=[
      ("fake_branch",lambda q:q.__setitem__("start_branch","0x16300")),
      ("fake_source_sha",lambda q:q.__setitem__("original_same_SP11_OEM_ISP_SHA256","0"*64)),
      ("fake_start_stage",lambda q:q["source_checked_dispatch_order"]["0x804"][0].__setitem__("core","IFE")),
      ("fake_stop_order",lambda q:q["source_checked_dispatch_order"]["0x805"].reverse()),
      ("fake_start_log",lambda q:q["source_checked_dispatch_order"]["0x804"][2].__setitem__("original_diagnostic_RVA","0x34200")),
      ("fake_stop_log",lambda q:q["source_checked_dispatch_order"]["0x805"][1].__setitem__("original_diagnostic_SHA256","0"*64)),
      ("fake_register_meaning",lambda q:q.__setitem__("actual_per_core_indirect_callback_bodies_and_MMIO_effects_proven",True)),
      ("fake_windows_video_route",lambda q:q.__setitem__("live_rear_Windows_4k_recording_took_this_ISP_route_proven",True)),
      ("fake_809",lambda q:q.__setitem__("ISP_0x809_effects_decoded",True)),
      ("fake_physical_stop",lambda q:q.__setitem__("physical_stop_drained_DMA_WM16_and_BF_irq_proven",True)),
      ("fake_native_4k",lambda q:q.__setitem__("Linux_native_rear_processed_4k_optical_frame_proven",True)),
      ("fake_golden_mutation",lambda q:q.__setitem__("camera_hardware_Golden_kernel_or_boot_modified",True)),
      ("fake_private_export",lambda q:q.__setitem__("original_OEM_driver_bytes_optical_images_or_KD_secrets_exported",True)),
    ]
    for name,change in neg:
        mutant=copy.deepcopy(actual);change(mutant)
        try:validate(mutant)
        except (AssertionError,KeyError,TypeError):
            continue
        raise AssertionError("FAIL_OPEN_E004OE_NEGATIVE_TEST "+name)
    print("PASS_E004OE_SAME_SP11_ORIGINAL_ISP_"
          f"{actual['original_ARM64_instruction_anchors']}_ARM64_ANCHORS_"
          "ORIGINAL_DIAGNOSTIC_SHA_XREFS_"
          "START_CDM_IFE_CSID_STOP_CSID_IFE_CDM_"
          f"{len(neg)}_FAIL_CLOSED_NEGATIVE_TESTS_GOLDEN_UNTOUCHED")
