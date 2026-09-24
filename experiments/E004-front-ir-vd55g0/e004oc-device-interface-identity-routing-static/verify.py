#!/usr/bin/env python3
"""Read-only same-SP11 OEM AVStream -> real camera device-interface identity map.

No Windows session, camera access, KD credential, binary export or pointer dump.
All matching binary identities and instruction anchors are private, SHA pinned.
"""
import copy
import hashlib
import json
import re
import struct
import subprocess
import uuid
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ORIGINAL=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
AVS=ORIGINAL/"surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/surfacecamavs8380.sys"
PARENT=HERE.parent/"e004ob-dual-backend-ioctl-static/RESULT.json"
AVS_SHA="b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed"
BASE=0x140000000
# This ORIGINAL same-device AVStream .rdata table is nine 0x48-byte rows,
# each containing a 32-bit matching key, owner/status, GUID pointer, and
# dynamically populated state. Do not serialize original pointer/state bytes.
TABLE_RVA=0x2ece0
TABLE_ROWS=9
TABLE_STRIDE=0x48
IDS=(
 ("flash","d2ff3f74-880f-4858-841c-fb0bc634676c",0x2efb8),
 ("rear_sensor","5e34e1c5-c5bc-4c7f-b6fc-e2443e45be67",0x2ef78),
 ("front_sensor","f27170b8-7b88-4f4a-b505-1d065616aadc",0x2efd8),
 ("aux_sensor","65528936-042e-4693-bb4f-96c419453ccb",0x2ef98),
 ("ISP","3e9c0fdb-cef9-4c4a-8e85-36e4a82eb80f",0x2ef68),
 ("platform_common","8d73ce35-93cf-4795-8db9-40bbe130d859",0x2efa8),
 ("unresolved_6","91761a61-b864-4cd3-bcdd-4afaf16dd2c0",0x2efc8),
 ("unresolved_7","23a032e0-11af-460b-bac1-400da39b428e",0x2efe8),
 ("secure_ISP","2a851ba1-8248-4567-b61a-f279610b248c",0x2ef88),
)
# Each unique provider takes the address of precisely the matching GUID,
# supplies it as the device-interface creation call's x2 argument, and invokes
# the framework slot at +0x268. These are REGISTERING CODE PATHS, not proof
# the relevant interface was enabled or selected in the actual live rear session.
# provider SHA, GUID RVA, (ADRP RVA, ADD/MOV-to-x2 RVA, WDF slot-load RVA).
PROVIDERS={
 "flash":("qccamflash8380","6bc1d698bc3b6da16974cd6f3ea89dc1ba6a8ea102eebe1a5d41129b4eb9ba2b",0xc4f0,(0x2cba4,0x2cba8,0x2cbb8)),
 "rear_sensor":("surfacecamrearsensor8380","b7d7a278c5e7b92ebf35f870a7e06cbad670ffb35bfaf40106e27b09bf33fabb",0x1b4e0,(0x3d240,0x3d244,0x3d258)),
 "front_sensor":("surfacecamfrontsensor8380","80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03",0x16398,(0x38248,0x3824c,0x38274)),
 "aux_sensor":("surfacecamauxsensor8380","e5b6b064f39cf239ab07e22ca2434e3c08c93b691dc7d27cebb90861226efa75",0x15490,(0x372b4,0x372b8,0x372cc)),
 "ISP":("qccamisp8380","64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c",0x3f6d0,(0x6acfc,0x6ad00,0x6ad14)),
 "platform_common":("qccamplatform8380","836714ec41f92f45af363d7bf3c9b9cfc2cccdbd19a1c57f355b471068648049",0x19568,(0x3b264,0x3b268,0x3b278)),
 "secure_ISP":("qccamsecureisp8380","47c944fa497477751073ec79a27a589a55e884178c1859d6f27388ec7af2ad53",0x10468,(0x312d4,0x312d8,0x312ec)),
}
def require(ok,reason):
    if not ok:raise AssertionError("E004OC_FAIL_CLOSED "+reason)

def file_rva(data,rva,n):
    pe=struct.unpack_from("<I",data,0x3c)[0]
    require(data[pe:pe+4]==b"PE\0\0","PE signature")
    require(struct.unpack_from("<H",data,pe+4)[0]==0xaa64,"ARM64 image type")
    count=struct.unpack_from("<H",data,pe+6)[0]
    sh=pe+24+struct.unpack_from("<H",data,pe+20)[0]
    for i in range(count):
        p=sh+i*40
        vs,va,rs,raw=struct.unpack_from("<IIII",data,p+8)
        if va<=rva and rva+n<=va+rs:return data[raw+rva-va:raw+rva-va+n]
    raise AssertionError(f"rva not filebacked {rva:x}")

def asm_at(p,start,stop):
    txt=subprocess.check_output([
        "llvm-objdump","-d",f"--start-address={BASE+start:#x}",
        f"--stop-address={BASE+stop:#x}",str(p)],text=True)
    pat=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    return {int(m.group(1),16)-BASE:(m.group(2),m.group(3).split("//")[0].strip())
            for m in pat.finditer(txt)}

def verify_record(r):
    require(r["schema"]=="sp11-e004oc-sha-locked-OEM-nine-device-interface-routing-static-v1","schema")
    require(r["parent_git_revision"]=="e90eee9cb7daa6b121f7444df212377009f1efe3","parent")
    require(r["AVStream_nine_entry_device_interface_table_RVA"]=="0x2ece0","table")
    require(len(r["identity_map"])==9,"nine distinct entries")
    require([(x["slot"],x["component"],x["device_interface_GUID"])
            for x in r["identity_map"]]==[(i,n,g) for i,(n,g,_) in enumerate(IDS)],"identity map exact")
    require(set(r["registering_provider_matches"])==set(PROVIDERS),"provider keys")
    for name,(_,sha,rva,anchors) in PROVIDERS.items():
        x=r["registering_provider_matches"][name]
        require(x["sha256"]==sha,"provider exact identity "+name)
        require(x["GUID_RVA"]==f"0x{rva:x}","provider GUID RVA "+name)
        require(x["registration_callsite_ADRP_RVA"]==f"0x{anchors[0]:x}","provider reg RVA "+name)
        require(x["WDF_interface_create_slot_load_RVA"]==f"0x{anchors[2]:x}","provider callback anchor "+name)
    require(r["unknown_identity_slots"]==[6,7],"unresolved slots")
    require(r["original_same_SP11_OEM_driver_archive_sys_count"]==102,"original archive scan scope")
    require(r["platform_common_identity_registered_by_platform_and_queried_by_ISP_rear_front"] is True,"common registration and access")
    for k in ("AVStream_real_session_rear_selected_device_interface_identified",
              "OEM_interface_selector_values_decoded_into_native_hardware_commands",
              "Windows_live_rear_BF_event_observed",
              "Linux_native_rear_4k_ISP_optical_frame_proven",
              "camera_hardware_or_Golden_modified"):
        require(r[k] is False,"unproven fact "+k)
    require(r["no_private_original_OEM_driver_bytes_or_optical_pixels_exported"] is True,"no private data")
    return True

def generate():
    av=AVS.read_bytes()
    require(hashlib.sha256(av).hexdigest()==AVS_SHA,"AVS exact same-SP11 SHA")
    avasm=asm_at(AVS,0x208b8,0x208e0)
    require(avasm[0x208c8]==("umaddl","x9, w8, w23, x21"),"selected row = 0x48 * dynamic slot")
    require(avasm[0x208d0]==("str","x8, [x9, #0x8]"),"row identity key copied")
    sel=asm_at(AVS,0x20bbc,0x20c10)
    require(sel[0x20bbc]==("umaddl","x21, w8, w10, x0"),"binder uses same row stride")
    require(sel[0x20bc0]==("ldr","w11, [x21, #0x8]"),"binder compares row key")
    require(sel[0x20bc8][0]=="cmp" and sel[0x20bc8][1]=="w1, w11","interface type key compare")
    require(sel[0x20be4]==("ldr","x0, [x21, #0x10]"),"interface identity argument")
    require(sel[0x20c04]==("blr","x8"),"interface enumeration dispatched")
    mapped=[]
    for i,(name,guid,rva) in enumerate(IDS):
        b=file_rva(av,TABLE_RVA+i*TABLE_STRIDE,16)
        key,flag,ptr=struct.unpack_from("<IIQ",b)
        require(key==uuid.UUID(guid).time_low,"AVS matching key differs "+name)
        require(flag==({"flash":1,"rear_sensor":2,"front_sensor":2,"aux_sensor":2,"ISP":3,"platform_common":4,"unresolved_6":2,"unresolved_7":2,"secure_ISP":3}[name]),"AVS per-interface selector flag "+name)
        require(ptr-BASE==rva,"GUID record pointer RVA differs "+name)
        require(uuid.UUID(bytes_le=file_rva(av,rva,16))==uuid.UUID(guid),
                "AVS table GUID bytes differ "+name)
        mapped.append({"slot":i,"component":name,"device_interface_GUID":guid,
                       "AVStream_identity_RVA":f"0x{rva:x}","AVStream_identity_type_key":f"0x{key:08x}",
                       "AVStream_source_row_RVA":f"0x{TABLE_RVA+i*TABLE_STRIDE:x}"})
    provider={}
    for name,(stem,sha,rva,anchors) in PROVIDERS.items():
        orig=next(ORIGINAL.glob(stem+".inf_arm64_*"))/(stem+".sys")
        data=orig.read_bytes()
        require(hashlib.sha256(data).hexdigest()==sha,"provider SHA mismatch "+name)
        guid=dict((k,(g,v)) for k,g,v in IDS)[name][0]
        require(uuid.UUID(bytes_le=file_rva(data,rva,16))==uuid.UUID(guid),
                "provider actual GUID differs "+name)
        a,b,c=anchors
        src=asm_at(orig,a,c+8)
        ra=src[a]
        require(ra[0]=="adrp","provider GUID address taken "+name)
        require(src[b][0]=="add" and (src[b][1].startswith("x2, ") or name in ("ISP","secure_ISP") and src[b][1].startswith("x19, ")),
                "provider GUID address prepared "+name)
        if name in ("ISP","secure_ISP"):
            move=0x6ad10 if name=="ISP" else 0x312e8
            m=asm_at(orig,move,move+4)
            require(m[move]==("mov","x2, x19"),"provider identity actually passed as x2 "+name)
        require(src[c][0]=="ldr" and src[c][1].endswith(", #0x268]"),
                "device-interface registration framework slot "+name)
        provider[name]={"sha256":sha,"GUID_RVA":f"0x{rva:x}",
                        "registration_callsite_ADRP_RVA":f"0x{a:x}",
                        "WDF_interface_create_slot_load_RVA":f"0x{c:x}",
                        "original_same_device_identity_source_checked":True}
    # The shared platform GUID has a distinct registration path in platform
    # and separately a *query* path in ISP/rear/front (not their own identities).
    for stem,rva,adr,add in (
       ("qccamisp8380",0x478d8,0x2b1d8,0x2b1dc),
       ("surfacecamrearsensor8380",0x1bb78,0x6e50,0x6e54),
       ("surfacecamfrontsensor8380",0x16780,0x3810,0x3814)):
        f=next(ORIGINAL.glob(stem+".inf_arm64_*"))/(stem+".sys")
        data=f.read_bytes()
        require(uuid.UUID(bytes_le=file_rva(data,rva,16))==uuid.UUID(IDS[5][1]),
                "platform common lookup GUID "+stem)
        source=asm_at(f,adr,add+8)
        require(source[adr][0]=="adrp" and source[add][0]=="add" and
                source[add][1].startswith("x0, "),
                "client queries platform interface "+stem)
    # Scan all 102 original OEM SYS files, not only camera-named drivers.
    all_sys=list(ORIGINAL.glob("*/*.sys"))
    require(len(all_sys)==102,"original installed OEM driver archive inventory changed")
    for slot in (6,7):
        needle=uuid.UUID(IDS[slot][1]).bytes_le
        hits=[p for p in all_sys if needle in p.read_bytes()]
        require(hits==[AVS],"unresolved GUID unexpectedly has a matching OEM SYS provider")
    r={"schema":"sp11-e004oc-sha-locked-OEM-nine-device-interface-routing-static-v1",
       "parent_git_revision":"e90eee9cb7daa6b121f7444df212377009f1efe3",
       "AVStream_original_same_SP11_sha256":AVS_SHA,
       "AVStream_nine_entry_device_interface_table_RVA":"0x2ece0",
       "AVStream_device_identity_record_stride_bytes":0x48,
       "AVStream_backend_binder_RVA":"0x20b60",
       "AVStream_binder_interface_GUID_argument_RVA":"0x20be4",
       "AVStream_binder_matches_32bit_key_before_IoGetDeviceInterfaces":True,
       "identity_map":mapped,"registering_provider_matches":provider,
       "unknown_identity_slots":[6,7],
       "original_same_SP11_OEM_driver_archive_sys_count":len(all_sys),
       "platform_common_identity_registered_by_platform_and_queried_by_ISP_rear_front":True,
       "OEM_shared_opaque_request_0x2326ab_does_not_uniquely_select_provider":True,
       "AVStream_real_session_rear_selected_device_interface_identified":False,
       "OEM_interface_selector_values_decoded_into_native_hardware_commands":False,
       "Windows_live_rear_BF_event_observed":False,
       "Linux_native_rear_4k_ISP_optical_frame_proven":False,
       "no_private_original_OEM_driver_bytes_or_optical_pixels_exported":True,
       "camera_hardware_or_Golden_modified":False}
    verify_record(r)
    return r

if __name__=="__main__":
    actual=generate()
    p=HERE/"RESULT.json"
    if not p.exists():
        p.write_text(json.dumps(actual,indent=2,sort_keys=True)+"\n")
        print("E004OC_SAFE_SCALAR_RESULT_CREATED")
    else:
        require(json.loads(p.read_text())==actual,"saved result does not match original driver evidence")
    earlier=json.loads(PARENT.read_text())
    require(earlier["matched_OEM_components"]==["platform","ISP"] and
            earlier["platform_or_ISP_uniquely_established_as_live_rear_camera_receiver"] is False,
            "E004ob original request dual-receiver fact lost")
    negative=(
     ("fake_ISP_GUID",lambda x:x["identity_map"][4].__setitem__("device_interface_GUID","0"*36)),
     ("fake_rear_identity",lambda x:x["identity_map"][1].__setitem__("component","front_sensor")),
     ("fake_provider",lambda x:x["registering_provider_matches"]["ISP"].__setitem__("GUID_RVA","0x0")),
     ("wrong_table",lambda x:x.__setitem__("AVStream_nine_entry_device_interface_table_RVA","0x2ec00")),
     ("pretend_common_GUID_unique",lambda x:x.__setitem__("platform_common_identity_registered_by_platform_and_queried_by_ISP_rear_front",False)),
     ("fake_known_unresolved",lambda x:x.__setitem__("unknown_identity_slots",[])),
     ("fake_runtime_selection",lambda x:x.__setitem__("AVStream_real_session_rear_selected_device_interface_identified",True)),
     ("fake_semantic_selector",lambda x:x.__setitem__("OEM_interface_selector_values_decoded_into_native_hardware_commands",True)),
     ("fake_live_BF",lambda x:x.__setitem__("Windows_live_rear_BF_event_observed",True)),
     ("fake_linux_4K",lambda x:x.__setitem__("Linux_native_rear_4k_ISP_optical_frame_proven",True)),
     ("fake_golden_mutation",lambda x:x.__setitem__("camera_hardware_or_Golden_modified",True)),
     ("fake_image_export",lambda x:x.__setitem__("no_private_original_OEM_driver_bytes_or_optical_pixels_exported",False)),
    )
    for name,mutation in negative:
        mutant=copy.deepcopy(actual)
        mutation(mutant)
        try:verify_record(mutant)
        except (AssertionError,KeyError,TypeError):
            continue
        raise AssertionError("E004OC_FAIL_OPEN_NEGATIVE_CASE "+name)
    print("PASS_E004OC_AVSTREAM_NINE_GUID_BACKEND_LOOKUP_SEVEN_DISTINCT_REGISTERING_OEM_PROVIDERS")
    print("PASS_E004OC_COMMON_PLATFORM_PROVIDER_QUERIED_BY_ISP_REAR_FRONT_TWO_UNRESOLVED_IDENTITIES")
    print("PASS_E004OC_12_FAIL_CLOSED_NEGATIVES_NO_LIVE_PROFILE_OR_SELECTOR_SEMANTICS_CLAIMED")
