#!/usr/bin/env python3
"""E004nv read-only, same-SP11 OEM qccamisp8380.sys BF event/group proof.

No OEM driver bytes, Windows DMA addresses, optical pixels or raw logs
are exported. Source binary stays on the SAME SP11 private archive.
"""
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

DRIVER=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
RESULT=Path(__file__).resolve().parent/"BF-RESULT.json"
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
IMAGE=0x140000000

def required(condition,description):
    if not condition:
        raise SystemExit("E004NV_BF_STATIC_REJECT: "+description)

def mapped_string(data,text):
    pos=data.find(text)
    required(pos>=0,"missing OEM BF diagnostic")
    pe=struct.unpack_from("<I",data,0x3c)[0]
    n=struct.unpack_from("<H",data,pe+6)[0]
    opt=struct.unpack_from("<H",data,pe+20)[0]
    sh=pe+24+opt
    for i in range(n):
        o=sh+40*i
        vs,va,rs,raw=struct.unpack_from("<IIII",data,o+8)
        if raw<=pos<raw+rs:
            return va+pos-raw
    raise SystemExit("BF diagnostic not in a mapped PE section")

def disasm(start,end):
    text=subprocess.check_output(
        ["llvm-objdump","-d",
         f"--start-address=0x{IMAGE+start:x}",
         f"--stop-address=0x{IMAGE+end:x}",str(DRIVER)],
        text=True)
    result={}
    pattern=re.compile(r"^([0-9a-f]{9,}):\s+[0-9a-f]{8}\s+([a-z.]+)\s*(.*?)\s*$",re.M)
    for match in pattern.finditer(text):
        result[int(match.group(1),16)-IMAGE]=(
            match.group(2),match.group(3).split("//")[0].strip())
    return result

def anchor(ins,at,mn,operands):
    required(at in ins,f"RVA {at:x} missing")
    actual=ins[at]
    required(actual[0]==mn and actual[1]==operands,
             f"RVA {at:x}: expected {mn} {operands}, got {actual}")

def main():
    required(not RESULT.exists(),"scalar result already exists; never overwrite")
    data=DRIVER.read_bytes()
    required(len(data)==376560 and hashlib.sha256(data).hexdigest()==SHA,
             "original same-SP11 OEM driver identity")
    bf=b"IFE%d IFE BF stats buf done Irq occured.\0"
    required(mapped_string(data,bf)==0x37b88,"BF diagnostic RVA")
    ins=disasm(0x1fc58,0x1fd48)
    anchor(ins,0x1fc60,"cmp","w8, #0xf")
    anchor(ins,0x1fc64,"b.ne","0x14001fd48 <.text+0x1ed48>")
    anchor(ins,0x1fc6c,"adrp","x8, 0x140037000 <.text+0x36000>")
    anchor(ins,0x1fc70,"add","x1, x8, #0xb88")
    anchor(ins,0x1fc78,"bl","0x140029ad8 <.text+0x28ad8>")
    anchor(ins,0x1fc8c,"mov","w1, #0x8")
    anchor(ins,0x1fc90,"mov","x0, x19")
    anchor(ins,0x1fc94,"bl","0x140026460 <.text+0x25460>")
    anchor(ins,0x1fce8,"mov","w9, #0x300d")
    helper=disasm(0x26500,0x26528)
    anchor(helper,0x26500,"sxtw","x21, w1")
    anchor(helper,0x2650c,"add","x10, x21, #0x66b")
    anchor(helper,0x26514,"ldr","x9, [x8, x10, lsl #3]")
    # Front's five branches share the exact same FIFO helper.
    common=disasm(0x1f430,0x1fe28)
    for event_rva,event,group_rva,group in (
        (0x1f438,0x3,0x1f468,0),
        (0x1fd48,0xd,0x1fd64,5),
        (0x1fdc0,0xe,0x1fddc,6),
        (0x1fd84,0x10,0x1fda0,7),
        (0x1fdfc,0x12,0x1fe18,9),
    ):
        anchor(common,event_rva,"cmp",f"w8, #0x{event:x}")
        anchor(common,group_rva,"mov",f"w1, #0x{group:x}" if group else "w1, #0x0")
    report={
      "schema":"sp11-e004nv-same-sp11-oem-qccamisp8380-rear-BF-event-static-v1",
      "experiment":"E004nv",
      "driver":{"sha256":SHA,"bytes":len(data),"same_SP11_private_original_retained":True},
      "BF_static_dispatch":{
        "driver_event_id":"0x0f",
        "BF_diagnostic_RVA":"0x37b88",
        "BF_diagnostic":"IFE%d IFE BF stats buf done Irq occured.",
        "event_compare_RVA":"0x1fc60",
        "queue_group_index":8,
        "queue_group_argument_RVA":"0x1fc8c",
        "queue_pop_helper_RVA":"0x26460",
        "queue_pop_call_RVA":"0x1fc94",
        "BF_group_client_resource_port":"0x300d",
        "resource_port_stored_RVA":"0x1fce8",
        "independent_queue_index_arithmetic_RVA":"0x2650c",
        "independent_queue_pointer_load_RVA":"0x26514",
      },
      "front_proven_groups_in_same_driver":[
         {"event_id":"0x03","queue_group_index":0,"description":"VIDEO FULL+DS"},
         {"event_id":"0x0d","queue_group_index":5,"description":"AEC_BE_BHIST"},
         {"event_id":"0x0e","queue_group_index":6,"description":"TINTLESS_BG"},
         {"event_id":"0x10","queue_group_index":7,"description":"AWB_BG"},
         {"event_id":"0x12","queue_group_index":9,"description":"RS"},
      ],
      "rear_BF_WM16_BAF_static_association_corroborated_by_active_WM16_and_driver_BF_name":True,
      "BF_event_live_during_OEM_rear_recording_observed":False,
      "BF_event_has_independent_group_FIFO_in_same_driver":True,
      "all_six_rear_groups_live_confirmed":False,
      "Linux_rear_native_4k_ISP_optical_frame_proven":False,
      "no_driver_binary_or_DMACSV_or_optical_data_exported":True,
    }
    RESULT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("E004NV_STATIC_DRIVER_BF_EVENT_0F_GROUP8_FIFO_RVA26460_PORT300D_PROVED_LIVE_REAR_EVENT_UNPROVEN")

if __name__=="__main__":
    main()
