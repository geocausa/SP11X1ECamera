#!/usr/bin/env python3
"""Strict same-SP11 audit. No original records, pointers or code leave SP11."""
from pathlib import Path
import hashlib,json,re,struct,pefile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
P=ROOT.parent/"private/E011AP-20260930-1640A";C=P/"capture"
def norm(f):return f.read_text(encoding="utf-8-sig").replace("\r\n","\n")
def u32(b,o):return struct.unpack_from("<I",b,o)[0]
def u64(b,o):return struct.unpack_from("<Q",b,o)[0]
def number(s):return int(s.replace("`",""),16)
def main():
    raw=(P/"cdb-observer.raw").read_text(errors="replace")
    hb=(P/"holder.log").read_bytes()
    h=hb.decode("utf-16" if hb.startswith((b"\xff\xfe",b"\xfe\xff")) else "utf-8-sig")
    for marker in ("E011AP_HOLDER_BEGIN","INIT_BEGIN","INIT_PASS","START_BEGIN","START_STATUS=Success","STOP_BEGIN","STOP_PASS valid_4k_handles=866","E011AP_HOLDER_END"):
        assert h.count(marker)==1,marker
    run=json.loads(norm(P/"RUN-SAFE.json"))
    assert run["singleStart"] and run["cleanStop"] and run["taskRemoved"]
    assert run["valid4kHandles"]==866 and run["debuggerExitCode"]==0
    assert run["allEightResolvedBeforeStart"] and run["manualGet2Qualification"]
    assert raw.count("Detached")==1 and run["diagnostics"]==0
    assert not re.search(r"syntax error|memory access error|error at|No runnable debuggees",raw,re.I)
    assert len(re.findall(r'^\s*[0-7]\s+e\s+[0-9a-f`]+\s+/1\s+0001',raw,re.M))==8
    tags=["INIT","SET_BEFORE","SET_AFTER","GET2_BEFORE","GET2_AFTER","GET12_BEFORE","PUBLISH","CONSUMER"]
    events=re.findall(r"^E011AP_(INIT|SET_BEFORE|SET_AFTER|GET2_BEFORE|GET2_AFTER|GET12_BEFORE|PUBLISH|CONSUMER) tid=([0-9a-f]+)",raw,re.M)
    assert [t for t,tid in events]==tags
    assert len({tid for t,tid in events[:7]})==1
    for tag in ["SET","GET2"]:
        assert re.search(r"^E011AP_"+tag+r"_AFTER tid=[0-9a-f]+ tidMatch=1 ownerMatch=1 result=0$",raw,re.M)
    assert re.search(r"^E011AP_GET2_CHECK rva=831920 wrapperMatch=1 selector=2 delegatePresent=1$",raw,re.M)
    assert re.search(r"^E011AP_GET2_LIST_COUNTS inputs=5 outputs=11$",raw,re.M)
    assert re.search(r"^E011AP_PUBLISH tid=[0-9a-f]+ property=5000001d size=80$",raw,re.M)
    assert re.search(r"^E011AP_CONSUMER tid=[0-9a-f]+ req=1$",raw,re.M)
    sizes={**{n+".bin":92 for n in ["INIT_BG","SET_BEFORE_BG","SET_AFTER_BG","GET2_BEFORE_BG","GET2_AFTER_BG","GET12_BG"]},
      "SET_PARAM.bin":16,"SET_WRAPPER.bin":64,"SET_TARGET.bin":128,
      "GET2_PARAM.bin":40,"GET2_WRAPPER.bin":64,"GET2_TARGET.bin":128,
      "DELEGATE_OBJECT.bin":64,"DELEGATE_TARGET.bin":128,
      "GET2_INPUT_LIST.bin":120,"GET2_OUTPUT_LIST.bin":264,"PUBLISH_REC.bin":128,"CONSUMER_REC.bin":128}
    assert {f.name for f in C.glob("*.bin")}==set(sizes)
    blobs={n:(C/n).read_bytes() for n in sizes}
    assert all(len(blobs[n])==size for n,size in sizes.items())
    assert sum(sizes.values())==1824
    def boundary(tag):
        m=re.search(r"^E011AP_"+tag+r" tid=[0-9a-f]+ owner=([0-9a-f`]+) io=([0-9a-f`]+) algo=([0-9a-f`]+) target=([0-9a-f`]+)",raw,re.M);assert m
        return [number(x) for x in m.groups()]
    so,si,sa,st=boundary("SET_BEFORE");go,gi,ga,gt=boundary("GET2_BEFORE")
    assert so==go and si==gi and sa==ga
    initial=re.search(r"^E011AP_INIT tid=[0-9a-f]+ owner=([0-9a-f`]+) io=([0-9a-f`]+)",raw,re.M)
    assert initial and number(initial[1])==so and number(initial[2])==si
    assert blobs["INIT_BG.bin"]==blobs["SET_BEFORE_BG.bin"]==blobs["SET_AFTER_BG.bin"]==blobs["GET2_BEFORE_BG.bin"]
    assert blobs["GET2_AFTER_BG.bin"]==blobs["GET12_BG.bin"]
    assert [u32(blobs[n+".bin"],84) for n in ["INIT_BG","SET_BEFORE_BG","SET_AFTER_BG","GET2_BEFORE_BG","GET2_AFTER_BG","GET12_BG"]]==[0,0,0,0,1,1]
    assert u32(blobs["PUBLISH_REC.bin"],76)==u32(blobs["CONSUMER_REC.bin"],76)==1
    param=blobs["GET2_PARAM.bin"];inp=blobs["GET2_INPUT_LIST.bin"];out=blobs["GET2_OUTPUT_LIST.bin"]
    assert (u32(param,0),u32(param,16),u32(param,32))==(2,5,11)
    assert u64(param,8)==gi+0x21e8 and u64(param,24)==gi+0x2238
    assert (u64(inp,32),u32(inp,40),u32(inp,44))==(gi+0xb70,12,2)
    assert all(u64(out,i*24)!=gi+0xcb4 for i in range(11))
    assert u64(blobs["SET_WRAPPER.bin"],16)==st and u64(blobs["GET2_WRAPPER.bin"],8)==gt
    delegate=re.search(r"^E011AP_DELEGATE object=([0-9a-f`]+) target=([0-9a-f`]+)",raw,re.M);assert delegate
    assert u64(blobs["GET2_WRAPPER.bin"],40)==number(delegate[1])
    # This direct object+0x10 read omitted the vtable indirection. It is not code.
    assert u64(blobs["DELEGATE_OBJECT.bin"],16)==number(delegate[2])
    owners=json.loads(norm(P/"OWNERS-PRIVATE.json"));assert len(owners)==3
    owner={o["role"]:o for o in owners}
    assert [(owner[t]["module"],owner[t]["rva"]) for t in ["SET","GET2"]]==[("QcDeviceMFT8380",0x681c40),("QcDeviceMFT8380",0x681b00)]
    assert owner["DELEGATE"]["module"] is None and owner["DELEGATE"]["rva"] is None
    dll=ROOT.parents[1]/"00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"
    data=dll.read_bytes();assert hashlib.sha256(data).hexdigest()=="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
    pe=pefile.PE(data=data)
    assert blobs["SET_TARGET.bin"]==pe.get_data(0x681c40,128)
    assert blobs["GET2_TARGET.bin"]==pe.get_data(0x681b00,128)
    assert u64(blobs["DELEGATE_OBJECT.bin"],0)==owner["GET2"]["base"]+0x133a390
    assert u64(pe.get_data(0x133a390+16,8),0)==pe.OPTIONAL_HEADER.ImageBase+0x68e5a0
    generated=Path(str(P)+"-generated")
    for f in generated.glob("*.cmd"):assert norm(f)==norm(P/f.name),f.name
    assert norm(P/"holder.ps1")==norm(HERE/"holder.ps1")
    assert norm(P/"get2-lists.cmd")==norm(HERE/"get2-lists.cmd")
    assert norm(P/"SCRIPT-ENTRY-CONSUMED.marker").startswith("E011AP_ATOMIC_ENTRY_UTC=")
    changed=[i for i,(a,b) in enumerate(zip(blobs["GET2_BEFORE_BG.bin"],blobs["GET2_AFTER_BG.bin"])) if a!=b]
    manifest={str(f.relative_to(P)):{"bytes":f.stat().st_size,"sha256":hashlib.sha256(f.read_bytes()).hexdigest()} for f in [*C.glob("*.bin"),*P.glob("*.cmd"),P/"holder.ps1",P/"holder.log",P/"cdb-observer.raw",P/"RUN-SAFE.json",P/"OWNERS-PRIVATE.json"]}
    (P/"VALIDATED-PRIVATE-MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    safe={"experiment":"E011AP","status":"PASS_LIVE_GETPARAM2_TRANSITION",
      "attempt":"E011AP-20260930-1640A","Windows_attempt_consumed":True,
      "single_start":True,"valid_4k_handles":866,"clean_stop":True,"task_removed":True,"explicit_detaches":1,"debugger_exit":0,
      "resolved_one_shot_probes_before_Start":8,"manual_GetParam2_target_qualification":True,"automatic_remaining_boundary_handlers_completed":True,
      "events":8,"captured_records":18,"captured_bytes":1824,"valid_source_records":17,"valid_source_bytes":1656,
      "excluded_records":["DELEGATE_TARGET.bin"],"excluded_tail_bytes":{"GET2_INPUT_LIST.bin":40},
      "SetParam_entire_BG_92_bytes_preserved":True,"quad_schedule":[0,0,0,0,1,1],"GetParam2_changed_BG_byte_count":len(changed),
      "GetParam2_same_thread_and_processor_return_zero":True,"GetParam2_caused_quad_transition_for_invocation":True,
      "GetParam2_after_equals_pre_GetParam12_92_bytes":True,"publication_and_cold_request1_quad":1,
      "SetParam_wrapper_RVA":"0x681C40","GetParam_wrapper_RVA":"0x681B00","two_original_targets_match_128_bytes_each":True,
      "GetParam2_top_level_BG_output_present":False,"GetParam2_input2_type":2,"GetParam2_input2_payload_bytes":12,
      "GetParam2_input2_payload_IO_offset":"0xB70","nested_payload_not_live_captured":True,
      "correct_delegate_chain":"wrapper+0x28 -> object+0 -> vtable+0x10",
      "captured_object_vtable_RVA":"0x133A390","original_vtable_GetParam_candidate_RVA":"0x68E5A0",
      "original_candidate_method":"CamX::CAWBMain::AWBGetParameter","live_vtable_callback_bytes_not_captured":True,
      "exact_numeric_value_policy_closed":False,"kernel_debugging":False,"Linux_camera_runtime":False,"private_payloads_exported":False,
      "native_rear_ISP_runtime_allowed":False}
    (HERE/"VALIDATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps(safe))
if __name__=="__main__":main()
