#!/usr/bin/env python3
"""Same-SP11 OEM platform+ISP comparison of an opaque AVStream interface code.

Read-only original private ARM64 .sys files. Emits only derived code RVAs and
boolean distinctions; does NOT infer a unique or live recipient from code
number equality. No OEM binaries/disassembly/pointers/image bytes exported.
"""
import copy
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
R=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
OEM={
 "platform":(R/"qccamplatform8380.inf_arm64_16d44e9aca3becfb/qccamplatform8380.sys",
             "836714ec41f92f45af363d7bf3c9b9cfc2cccdbd19a1c57f355b471068648049",
             144584,0x6490,0x6334,0x6364),
 "ISP":(R/"qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys",
        "64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c",
        376560,0x5784,0x5638,0x566c)
}
AVSTREAM=HERE.parent/"e004oa-avstream-kernel-interface-bind/RESULT.json"
CODE=0x002326ab
BASE=0x140000000
ANCHORS={
 "platform":{
  0x6334:("ldr","w8, 0x140006490 <.text+0x5490>"),
  0x6338:("cmp","w19, w8"),
  0x633c:("b.eq","0x140006364 <.text+0x5364>"),
  0x6364:("ldr","x8, [sp, #0x10]"),
  0x6368:("cbz","x8, 0x14000637c <.text+0x537c>"),
  0x636c:("strb","wzr, [x8, #0x8]"),
  0x6370:("mov","w19, #0x0"),
  0x6374:("stp","xzr, xzr, [x8, #0x10]"),
 },
 "ISP":{
  0x5638:("ldr","w8, 0x140005784 <.text+0x4784>"),
  0x563c:("cmp","w24, w8"),
  0x5640:("b.eq","0x14000566c <.text+0x466c>"),
  0x566c:("ldr","x8, [sp, #0x18]"),
  0x5670:("cbz","x8, 0x140005694 <.text+0x4694>"),
  0x5674:("ldr","x9, [x22, #0x10]"),
  0x5678:("str","x9, [x8]"),
  0x567c:("mov","w9, #0x1"),
  0x5680:("strb","w9, [x8, #0x8]"),
  0x5684:("adrp","x9, 0x140004000 <.text+0x3000>"),
  0x5688:("add","x9, x9, #0xe30"),
  0x568c:("stp","x22, x9, [x8, #0x10]"),
 }
}

def must(ok,msg):
    if not ok:raise AssertionError("E004OB_FAIL_CLOSED "+msg)

def file_rva(data,rva,length):
    pe=struct.unpack_from("<I",data,0x3c)[0]
    must(data[pe:pe+4]==b"PE\0\0" and struct.unpack_from("<H",data,pe+4)[0]==0xaa64,
         "OEM ARM64 PE")
    sh=pe+24+struct.unpack_from("<H",data,pe+20)[0]
    for i in range(struct.unpack_from("<H",data,pe+6)[0]):
        o=sh+40*i
        va,sz,raw=struct.unpack_from("<III",data,o+12)
        if va<=rva and rva+length<=va+sz:
            return data[raw+rva-va:raw+rva-va+length]
    raise AssertionError("OEM literal RVA not file backed")

def verify_record(r):
    must(r["schema"]=="sp11-e004ob-two-OEM-camera-backends-same-opaque-control-v1","schema")
    must(r["parent_git_revision"]=="e75dfd6f00e1581b2ad89a42765d9d5e0558aae9","parent")
    must(r["opaque_internal_interface_request_code"]==hex(CODE),"opaque request")
    must(set(r["matched_OEM_components"])=={"platform","ISP"},"dual candidate components")
    must(r["platform_verified_literal_RVA"]=="0x6490" and r["ISP_verified_literal_RVA"]=="0x5784","two code constants")
    must(r["platform_branch_RVA"]=="0x6364" and r["ISP_branch_RVA"]=="0x566c","branch locations")
    must(r["platform_direct_match_zeroes_flag_and_two_state_fields"] is True,"platform state clear")
    must(r["ISP_direct_match_populates_pointer_flag_and_callback_fields"] is True,"ISP state populate")
    must(r["source_locked_ARM64_instruction_anchors"]==20,"exact instruction count")
    for k in ("OEM_AVStream_iface_same_request_code_source_verified",
              "platform_and_ISP_private_orig_OEM_SHA_validated",
              "no_private_OEM_binary_or_optical_pixels_exported"):
        must(r[k] is True,k)
    for k in ("platform_or_ISP_uniquely_established_as_live_rear_camera_receiver",
              "matched_request_code_proves_identical_platform_and_ISP_semantics",
              "engine_numeric_selectors_decoded_into_verified_sensor_or_ISP_commands",
              "native_Linux_rear_4k_ISP_optical_frame_proven",
              "camera_hardware_or_Golden_modified"):
        must(r[k] is False,k)
    return True

def build():
    from_adapter=json.loads(AVSTREAM.read_text())
    must(from_adapter["internal_interface_request_code_UNDECODED"]==hex(CODE),"AVStream sender code changed")
    results={}
    for name,(path,sha,size,lit,source,branch) in OEM.items():
        data=path.read_bytes()
        must(len(data)==size and hashlib.sha256(data).hexdigest()==sha,
             "exact OEM image identity "+name)
        must(struct.unpack("<I",file_rva(data,lit,4))[0]==CODE,
             "OEM request code changed "+name)
        instr=subprocess.check_output(["llvm-objdump","-d",str(path)],text=True)
        pat=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
        asm={int(m.group(1),16)-BASE:(m.group(2),m.group(3).split("//")[0].strip())
             for m in pat.finditer(instr)}
        for rva,want in ANCHORS[name].items():
            must(asm.get(rva)==want,f"{name} instruction RVA 0x{rva:x}, actual {asm.get(rva)}")
        results[name]=(lit,source,branch)
    r={
       "schema":"sp11-e004ob-two-OEM-camera-backends-same-opaque-control-v1",
       "parent_git_revision":"e75dfd6f00e1581b2ad89a42765d9d5e0558aae9",
       "opaque_internal_interface_request_code":hex(CODE),
       "matched_OEM_components":["platform","ISP"],
       "platform_verified_literal_RVA":hex(results["platform"][0]),
       "ISP_verified_literal_RVA":hex(results["ISP"][0]),
       "platform_branch_RVA":hex(results["platform"][2]),
       "ISP_branch_RVA":hex(results["ISP"][2]),
       "platform_direct_match_zeroes_flag_and_two_state_fields":True,
       "ISP_direct_match_populates_pointer_flag_and_callback_fields":True,
       "source_locked_ARM64_instruction_anchors":sum(map(len,ANCHORS.values())),
       "OEM_AVStream_iface_same_request_code_source_verified":True,
       "platform_and_ISP_private_orig_OEM_SHA_validated":True,
       "no_private_OEM_binary_or_optical_pixels_exported":True,
       "platform_or_ISP_uniquely_established_as_live_rear_camera_receiver":False,
       "matched_request_code_proves_identical_platform_and_ISP_semantics":False,
       "engine_numeric_selectors_decoded_into_verified_sensor_or_ISP_commands":False,
       "native_Linux_rear_4k_ISP_optical_frame_proven":False,
       "camera_hardware_or_Golden_modified":False
    }
    verify_record(r)
    return r

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--write-new",action="store_true")
    args=ap.parse_args()
    r=build()
    f=HERE/"RESULT.json"
    if args.write_new:
        must(not f.exists(),"single use result already exists")
        f.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    else:
        must(f.exists() and json.loads(f.read_text())==r,"saved proof not equal to same SP11 source")
    corruptions=(
      ("fake_unique_receiver",lambda z:z.__setitem__("platform_or_ISP_uniquely_established_as_live_rear_camera_receiver",True)),
      ("fake_identical_semantics",lambda z:z.__setitem__("matched_request_code_proves_identical_platform_and_ISP_semantics",True)),
      ("fake_engine_selector",lambda z:z.__setitem__("engine_numeric_selectors_decoded_into_verified_sensor_or_ISP_commands",True)),
      ("fake_Linux_optical",lambda z:z.__setitem__("native_Linux_rear_4k_ISP_optical_frame_proven",True)),
      ("fake_Golden_change",lambda z:z.__setitem__("camera_hardware_or_Golden_modified",True)),
      ("wrong_platform_branch",lambda z:z.__setitem__("platform_branch_RVA","0x6388")),
      ("wrong_ISP_branch",lambda z:z.__setitem__("ISP_branch_RVA","0x56b8")),
      ("wrong_request_code",lambda z:z.__setitem__("opaque_internal_interface_request_code","0x2326aa")),
      ("wrong_component_count",lambda z:z["matched_OEM_components"].pop()),
      ("wrong_platform_state",lambda z:z.__setitem__("platform_direct_match_zeroes_flag_and_two_state_fields",False)),
      ("wrong_ISP_state",lambda z:z.__setitem__("ISP_direct_match_populates_pointer_flag_and_callback_fields",False)),
      ("unverified_private_images",lambda z:z.__setitem__("platform_and_ISP_private_orig_OEM_SHA_validated",False)),
    )
    for name,mut in corruptions:
        x=copy.deepcopy(r);mut(x)
        try:verify_record(x)
        except (AssertionError,KeyError,IndexError):continue
        raise AssertionError("E004OB_FAIL_OPEN_NEGATIVE_MUTANT "+name)
    print("PASS_E004OB_SAME_SP11_PLATFORM_AND_ISP_OPAQUE_INTERFACE_CONTROL_"
          "20_ARM64_SOURCE_ANCHORS_2_OEM_IMAGE_SHA_12_FAIL_CLOSED_MUTATIONS_"
          "REAR_ACTIVE_RECEIVER_AND_SELECTOR_SEMANTICS_STILL_UNPROVEN")
