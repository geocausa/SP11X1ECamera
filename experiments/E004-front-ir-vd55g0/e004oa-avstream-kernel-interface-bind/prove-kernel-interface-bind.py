#!/usr/bin/env python3
"""E004oa: read-only SP11 AVStream engine -> kernel interface acquisition.

Pins one private original OEM ARM64 PE by SHA, validates exact instruction
edges, IAT import symbols, shared dispatch vtable and IOCTL scalar, exports
only safe *relative* code offsets and booleans. No driver/firmware/raw
memory/pixel data leaves the original host.
"""
from pathlib import Path
import hashlib
import json
import re
import struct
import subprocess
import copy

HERE=Path(__file__).resolve().parent
OEM=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/"
         "surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/surfacecamavs8380.sys")
EXPECTED_SHA="b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed"
BASE=0x140000000

# Exact ARM64 source anchors: device-specific engine register/lookup, selection
# of the interface GUID; IoGetDeviceInterfaces/IoGetDeviceObjectPointer,
# IRP request with 8-byte output; storing selected interface record; common
# dispatcher; invoking vtable or alternate function pointer.
ANCHORS={
  0x1ec08:("ldr","x0, [x19, #0x48]"),
  0x1ec14:("add","x2, x8, #0x1d8"),
  0x1ec18:("bl","0x140020b60 <.text+0x1fb60>"),
  0x1f674:("ldr","x0, [x9, #0x1d8]"),
  0x20b74:("mov","x20, x2"),
  0x20bbc:("umaddl","x21, w8, w10, x0"),
  0x20bc0:("ldr","w11, [x21, #0x8]"),
  0x20bc8:("cmp","w1, w11"),
  0x20be4:("ldr","x0, [x21, #0x10]"),
  0x20bfc:("ldr","x8, [x8, #0x260]"),
  0x20c04:("blr","x8"),
  0x20c0c:("ldr","x1, [sp, #0x10]"),
  0x20c14:("ldr","x8, [x8, #0x2b8]"),
  0x20c1c:("blr","x8"),
  0x20c28:("add","x3, x21, #0x18"),
  0x20c2c:("add","x2, x21, #0x20"),
  0x20c24:("ldr","x8, [x8, #0x2a0]"),
  0x20c38:("blr","x8"),
  0x20c64:("add","x9, x21, #0x8"),
  0x20c88:("ldr","x0, [x9, #0x10]"),
  0x20c98:("ldr","x1, [x9, #0x18]"),
  0x20c9c:("mov","w6, #0x8"),
  0x20ca0:("add","x5, x9, #0x28"),
  0x20ca4:("mov","w4, #0x0"),
  0x20ca8:("mov","x3, #0x0"),
  0x20cac:("ldr","w2, 0x140020da0 <.text+0x1fda0>"),
  0x20cb0:("bl","0x140020a50 <.text+0x1fa50>"),
  0x20ce8:("str","x22, [x20]"),
  0x20ac0:("ldr","x8, [x8, #0x2a8]"),
  0x20ae0:("mov","w0, w24"),
  0x20ae4:("blr","x8"),
  0x20b00:("ldr","x8, [x8, #0x288]"),
  0x20b04:("blr","x8"),
  0x20db4:("mov","x9, x0"),
  0x20dc8:("ldr","x10, [x9, #0x10]"),
  0x20dd0:("ldr","x0, [x9, #0x28]"),
  0x20dd8:("ldrb","w10, [x9, #0x30]"),
  0x20de0:("ldr","x8, [x0]"),
  0x20df4:("blr","x15"),
  0x20dfc:("ldr","x10, [x9, #0x40]"),
  0x20e1c:("ldr","x1, [x9, #0x38]"),
  0x20e30:("blr","x15"),
}
# NT kernel import address-table entries, NOT named Linux calls:
IAT={
 "IoGetDeviceInterfaces":0x2c260,
 "IoGetDeviceObjectPointer":0x2c2a0,
 "RtlInitUnicodeString":0x2c2b8,
 "IoBuildDeviceIoControlRequest":0x2c2a8,
 "IofCallDriver":0x2c288,
}
VIRTUAL={
 "engine_OnStart":(0x2fd68+3*8,0x1efd0),
 "engine_OnStop":(0x2fd68+4*8,0x1f130)
}
EXPECTED_IOCTL=0x002326ab

def must(ok,why):
    if not ok:raise AssertionError("E004OA_FAIL_CLOSED "+why)

def sections(data):
    pe=struct.unpack_from("<I",data,0x3c)[0]
    must(data[pe:pe+4]==b"PE\0\0" and struct.unpack_from("<H",data,pe+4)[0]==0xaa64,
         "exact ARM64 OEM PE required")
    count=struct.unpack_from("<H",data,pe+6)[0]
    sh=pe+24+struct.unpack_from("<H",data,pe+20)[0]
    return [struct.unpack_from("<IIII",data,sh+40*i+8)[1:] for i in range(count)]

def rva_bytes(data,sec,rva,num):
    for va,length,raw in sec:
        if va<=rva and rva+num<=va+length:
            return data[raw+rva-va:raw+rva-va+num]
    raise AssertionError("non-file-backed OEM PE RVA")

def static_imports():
    text=subprocess.check_output(["llvm-readobj","--coff-imports",str(OEM)],text=True)
    m=re.search(r"Import \{\s+Name: ntoskrnl\.exe\s+ImportLookupTableRVA: 0x[0-9A-Fa-f]+\s+ImportAddressTableRVA: (0x[0-9A-Fa-f]+)(.*?)\n\}",text,re.S)
    must(m is not None,"missing Windows kernel IAT")
    base=int(m.group(1),16)
    symbols=re.findall(r"^\s+Symbol: (\w+) \(\d+\)",m.group(2),re.M)
    for name,rva in IAT.items():
        must((rva-base)%8==0 and symbols[(rva-base)//8]==name,
             f"AVStream OEM IAT {name} changed")
    return True

def verify_record(r):
    must(r["schema"]=="sp11-e004oa-private-OEM-AVStream-internal-interface-bind-v1","schema")
    must(r["parent_git_revision"]=="9cc697e7da1ed32d4595a537bddef53892d63380","parent")
    must(r["OEM_AVStream_sha256"]==EXPECTED_SHA,"OEM identity")
    must(r["source_locked_ARM64_instruction_anchor_count"]==len(ANCHORS),"instruction count")
    must(r["Windows_device_interface_enumeration_import_RVA"]=="0x2c260","interface enumeration")
    must(r["Windows_device_object_access_import_RVA"]=="0x2c2a0","device object")
    must(r["Windows_device_control_request_import_RVA"]=="0x2c2a8","device control")
    must(r["Windows_device_control_dispatch_import_RVA"]=="0x2c288","device dispatch")
    must(r["internal_interface_request_code_UNDECODED"]==hex(EXPECTED_IOCTL),"interface code")
    must(r["interface_request_result_length_bytes"]==8,"interface length")
    must(r["AVStream_backend_binding_RVA"]=="0x20b60","binding")
    must(r["interface_request_IRP_builder_RVA"]=="0x20a50","IRP")
    must(r["engine_selected_interface_record_lookup_RVA"]=="0x1f620","interface lookup")
    must(r["engine_common_indirect_dispatch_RVA"]=="0x20da8","common dispatch")
    must(r["engine_OnStart_virtual_table_RVA"]=="0x2fd80","vtable start")
    must(r["engine_OnStop_virtual_table_RVA"]=="0x2fd88","vtable stop")
    for key in ("OEM_backend_device_interface_acquired_statically",
                "OEM_backend_device_control_returns_interface_pointer_statically",
                "OEM_engine_calls_selected_interface_indirectly_statically",
                "OEM_engine_OnStart_OnStop_share_dispatch_helper_statically",
                "no_OEM_binary_optical_data_DMA_pointers_exported"):
        must(r[key] is True,key)
    for key in ("interface_request_code_mapped_to_specific_platform_sensor_or_ISP_driver",
                "active_rear_Windows_session_selected_backing_interface_captured",
                "numeric_engine_start_stop_selector_semantics_proven",
                "native_Linux_rear_4k_ISP_optical_frame_proven",
                "camera_hardware_or_Golden_modified"):
        must(r[key] is False,key)
    return True

def build():
    data=OEM.read_bytes()
    must(len(data)==547192 and hashlib.sha256(data).hexdigest()==EXPECTED_SHA,
         "private exact same-SP11 OEM driver")
    sec=sections(data)
    for rva,target in VIRTUAL.values():
        addr=struct.unpack("<Q",rva_bytes(data,sec,rva,8))[0]
        must(addr==BASE+target,f"engine vtable at RVA {rva:x}")
    literal=struct.unpack("<I",rva_bytes(data,sec,0x20da0,4))[0]
    must(literal==EXPECTED_IOCTL,"expected camera interface request scalar")
    dis=subprocess.check_output(["llvm-objdump","-d",str(OEM)],text=True)
    pattern=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    ins={int(m.group(1),16)-BASE:(m.group(2),m.group(3).split("//")[0].strip())
         for m in pattern.finditer(dis)}
    for rva,want in ANCHORS.items():
        must(ins.get(rva)==want,f"instruction RVA 0x{rva:x}, got {ins.get(rva)}")
    static_imports()
    r={
      "schema":"sp11-e004oa-private-OEM-AVStream-internal-interface-bind-v1",
      "parent_git_revision":"9cc697e7da1ed32d4595a537bddef53892d63380",
      "OEM_AVStream_sha256":EXPECTED_SHA,
      "source_locked_ARM64_instruction_anchor_count":len(ANCHORS),
      "Windows_device_interface_enumeration_import_RVA":hex(IAT["IoGetDeviceInterfaces"]),
      "Windows_device_object_access_import_RVA":hex(IAT["IoGetDeviceObjectPointer"]),
      "Windows_device_control_request_import_RVA":hex(IAT["IoBuildDeviceIoControlRequest"]),
      "Windows_device_control_dispatch_import_RVA":hex(IAT["IofCallDriver"]),
      "internal_interface_request_code_UNDECODED":hex(EXPECTED_IOCTL),
      "interface_request_result_length_bytes":8,
      "AVStream_backend_binding_RVA":"0x20b60",
      "interface_request_IRP_builder_RVA":"0x20a50",
      "engine_selected_interface_record_lookup_RVA":"0x1f620",
      "engine_common_indirect_dispatch_RVA":"0x20da8",
      "engine_OnStart_virtual_table_RVA":"0x2fd80",
      "engine_OnStop_virtual_table_RVA":"0x2fd88",
      "OEM_backend_device_interface_acquired_statically":True,
      "OEM_backend_device_control_returns_interface_pointer_statically":True,
      "OEM_engine_calls_selected_interface_indirectly_statically":True,
      "OEM_engine_OnStart_OnStop_share_dispatch_helper_statically":True,
      "no_OEM_binary_optical_data_DMA_pointers_exported":True,
      "interface_request_code_mapped_to_specific_platform_sensor_or_ISP_driver":False,
      "active_rear_Windows_session_selected_backing_interface_captured":False,
      "numeric_engine_start_stop_selector_semantics_proven":False,
      "native_Linux_rear_4k_ISP_optical_frame_proven":False,
      "camera_hardware_or_Golden_modified":False
    }
    verify_record(r)
    return r

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--write-new",action="store_true")
    a=p.parse_args()
    r=build()
    f=HERE/"RESULT.json"
    if a.write_new:
        must(not f.exists(),"one-use output already exists")
        f.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    else:
        must(f.exists() and json.loads(f.read_text())==r,"saved proof differs")
    muts=(
      ("fabricated_recipient",lambda t:t.__setitem__("interface_request_code_mapped_to_specific_platform_sensor_or_ISP_driver",True)),
      ("fabricated_live_bind",lambda t:t.__setitem__("active_rear_Windows_session_selected_backing_interface_captured",True)),
      ("fabricated_selector",lambda t:t.__setitem__("numeric_engine_start_stop_selector_semantics_proven",True)),
      ("fabricated_frame",lambda t:t.__setitem__("native_Linux_rear_4k_ISP_optical_frame_proven",True)),
      ("false_Golden_mutation",lambda t:t.__setitem__("camera_hardware_or_Golden_modified",True)),
      ("wrong_request_code",lambda t:t.__setitem__("internal_interface_request_code_UNDECODED","0x2326aa")),
      ("wrong_interface_reply_size",lambda t:t.__setitem__("interface_request_result_length_bytes",16)),
      ("wrong_dispatcher",lambda t:t.__setitem__("engine_common_indirect_dispatch_RVA","0x20db0")),
      ("wrong_engine_start_vtable",lambda t:t.__setitem__("engine_OnStart_virtual_table_RVA","0x2fd88")),
      ("remove_interface_acquire",lambda t:t.__setitem__("OEM_backend_device_interface_acquired_statically",False)),
      ("remove_request_to_interface_link",lambda t:t.__setitem__("OEM_backend_device_control_returns_interface_pointer_statically",False)),
      ("wrong_IAT",lambda t:t.__setitem__("Windows_device_control_request_import_RVA","0x2c260")),
    )
    for name,mut in muts:
        copyr=copy.deepcopy(r);mut(copyr)
        try:verify_record(copyr)
        except (KeyError,AssertionError):continue
        raise SystemExit("E004OA_FAIL_OPEN_NEGATIVE_MUTANT "+name)
    print("PASS_E004OA_SAME_SP11_OEM_AVSTREAM_KERNEL_INTERFACE_BIND_"
          f"{len(ANCHORS)}_ARM64_INSTRUCTION_ANCHORS_"
          "5_NT_IAT_NAMES_2_ENGINE_VTABLE_ENTRIES_"
          f"{len(muts)}_FAIL_CLOSED_NEGATIVE_TESTS_"
          "BACKEND_RECIPIENT_SELECTOR_SEMANTICS_AND_LIVE_BF_UNPROVEN")
