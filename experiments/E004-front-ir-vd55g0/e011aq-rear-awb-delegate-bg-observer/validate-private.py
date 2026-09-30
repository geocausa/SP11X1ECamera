#!/usr/bin/env python3
"""Strict original same-SP11 delegate/retained BG audit; derived facts only."""
from pathlib import Path
import hashlib,json,re,struct,pefile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];P=ROOT.parent/"private/E011AQ-20260930-1740A";C=P/"capture"
def norm(p):return p.read_text(encoding="utf-8-sig").replace("\r\n","\n")
def u32(b,o=0):return struct.unpack_from("<I",b,o)[0]
def u64(b,o=0):return struct.unpack_from("<Q",b,o)[0]
def num(s):return int(s.replace("`",""),16)
def main():
    raw=(P/"cdb-observer.raw").read_text(errors="replace");hb=(P/"holder.log").read_bytes()
    h=hb.decode("utf-16" if hb.startswith((b"\xff\xfe",b"\xfe\xff")) else "utf-8-sig")
    for marker in ["E011AQ_HOLDER_BEGIN","INIT_BEGIN","INIT_PASS","START_BEGIN","START_STATUS=Success","STOP_BEGIN","STOP_PASS valid_4k_handles=711","E011AQ_HOLDER_END"]:
        assert h.count(marker)==1,marker
    run=json.loads(norm(P/"RUN-SAFE.json"))
    assert run["singleStart"] and run["cleanStop"] and run["taskRemoved"] and run["valid4kHandles"]==711
    assert run["explicitDetaches"]==1 and run["debuggerExitCode"]==0 and raw.count("Detached")==1
    assert run["fiveOuterResolvedBeforeStart"] and run["threeInnerResolvedBeforeCall"] and run["manualGet2Qualification"]
    assert len(re.findall(r'^\s*[01567]\s+e\s+[0-9a-f`]+\s+/1\s+0001',raw,re.M))>=5
    assert len(re.findall(r'^\s*[234]\s+e\s+[0-9a-f`]+\s+/1\s+0001',raw,re.M))==3
    assert raw.index("E011AQ_ARMED_5_OUTER_ONESHOT_BP")<raw.index("E011AQ_INIT tid=")
    assert raw.index("E011AQ_ARMED_3_INNER_ONESHOT_BP")<raw.index("E011AQ_DELEGATE tid=")
    tags=["INIT","BEFORE","DELEGATE","POPULATE","POP_RETURN","RETURN","PUBLISH","CONSUMER"]
    events=re.findall(r"^E011AQ_(INIT|BEFORE|DELEGATE|POPULATE|POP_RETURN|RETURN|PUBLISH|CONSUMER) tid=([0-9a-f]+)",raw,re.M)
    assert [a for a,b in events]==tags
    assert len({b for a,b in events[:7]})==1
    assert re.search(r'^E011AQ_DELEGATE tid=[0-9a-f]+ tidMatch=1 actorMatch=1 selector=2 rva=68e5a0$',raw,re.M)
    assert re.search(r'^E011AQ_POPULATE tid=[0-9a-f]+ tidMatch=1 actorMatch=1 payloadMatch=1 count=15$',raw,re.M)
    assert re.search(r'^E011AQ_POP_RETURN tid=[0-9a-f]+ tidMatch=1 result=0 rva=68e8d8$',raw,re.M)
    assert re.search(r'^E011AQ_RETURN tid=[0-9a-f]+ tidMatch=1 ownerMatch=1 result=0$',raw,re.M)
    assert re.search(r'^E011AQ_PUBLISH tid=[0-9a-f]+ property=5000001d size=80$',raw,re.M)
    assert re.search(r'^E011AQ_CONSUMER tid=[0-9a-f]+ req=1$',raw,re.M)
    # Preserve two failed pre-capture input-as-list qualification queries.
    diag=list(re.finditer(r'^.*(?:syntax error|memory access error|error at|No runnable debuggees).*$',
                          raw,re.M|re.I))
    assert len(diag)==2 and run["qualificationDiagnosticCount"]==2
    assert [x.group(0).split(" ",1)[0] for x in diag]==["E011AQ_QUALIFY","E011AQ_NESTED_SINGLE"]
    assert all(x.end()<raw.index("E011AQ_BEFORE tid=") for x in diag)
    assert run["captureDiagnosticCount"]==0
    assert re.search(r'^E011AQ_OUTPUT1_CHECK size=16 type=1 count=15 listOffset=2080$',raw,re.M)
    assert re.search(r'^E011AQ_OUTPUT_NESTED_QUALIFY bgMatch=1 bgSize=92 bgType=5$',raw,re.M)
    sizes={**{n+".bin":92 for n in ["INIT_BG","BEFORE_BG","RETAINED_BG","DELEGATE_BG","POP_SOURCE_BG","POP_BEFORE_BG","POP_AFTER_BG","POP_AFTER_SOURCE_BG","RETURN_BG"]},
      "BEFORE_PARAM.bin":40,"WRAPPER.bin":64,"ACTOR.bin":64,"VTABLE.bin":48,"CALLBACK_CODE.bin":128,
      "INPUT_LIST.bin":80,"OUTPUT_LIST.bin":264,"NESTED_OUTPUT_PAYLOAD.bin":16,"NESTED_DESCS.bin":360,
      "INPUT2_PAYLOAD.bin":12,"OUTPUT1_PAYLOAD.bin":16,"DELEGATE_PARAM.bin":40,"DELEGATE_CODE.bin":128,
      "POP_PAYLOAD.bin":16,"POP_DESCS.bin":360,"PUBLISH_REC.bin":128,"CONSUMER_REC.bin":128}
    assert {f.name for f in C.glob("*.bin")}==set(sizes)
    blobs={n:(C/n).read_bytes() for n in sizes}
    assert all(len(blobs[n])==size for n,size in sizes.items()) and sum(sizes.values())==2720
    before=re.search(r'^E011AQ_BEFORE tid=[0-9a-f]+ owner=([0-9a-f`]+) io=([0-9a-f`]+) wrapper=([0-9a-f`]+) target=([0-9a-f`]+) actor=([0-9a-f`]+) vtable=([0-9a-f`]+) callback=([0-9a-f`]+)',raw,re.M);assert before
    owner,io,wrapper,target,actor,vtable,callback=[num(x) for x in before.groups()]
    initial=re.search(r'^E011AQ_INIT tid=[0-9a-f]+ owner=([0-9a-f`]+) io=([0-9a-f`]+)',raw,re.M)
    assert initial and num(initial[1])==owner and num(initial[2])==io
    assert blobs["INIT_BG.bin"]==blobs["BEFORE_BG.bin"]==blobs["POP_BEFORE_BG.bin"]
    assert u32(blobs["INIT_BG.bin"],84)==0
    source=blobs["RETAINED_BG.bin"];assert u32(source,84)==1
    for n in ["DELEGATE_BG","POP_SOURCE_BG","POP_AFTER_BG","POP_AFTER_SOURCE_BG","RETURN_BG"]:
        assert blobs[n+".bin"]==source,n
    assert u32(blobs["PUBLISH_REC.bin"],76)==u32(blobs["CONSUMER_REC.bin"],76)==1
    assert u64(blobs["WRAPPER.bin"],8)==target and u64(blobs["WRAPPER.bin"],40)==actor
    assert u64(blobs["ACTOR.bin"])==vtable and u64(blobs["VTABLE.bin"],16)==callback
    param=blobs["BEFORE_PARAM.bin"];inp=blobs["INPUT_LIST.bin"];out=blobs["OUTPUT_LIST.bin"]
    assert param==blobs["DELEGATE_PARAM.bin"] and (u32(param),u32(param,16),u32(param,32))==(2,5,11)
    assert u64(param,8)==io+0x21e8 and u64(param,24)==io+0x2238
    assert (u64(inp,32),u32(inp,40),u32(inp,44))==(io+0xb70,12,2)
    assert (u32(out,32),u32(out,40))==(16,1)
    assert all(u64(out,i*24)!=io+0xcb4 for i in range(11))
    assert blobs["NESTED_OUTPUT_PAYLOAD.bin"]==blobs["OUTPUT1_PAYLOAD.bin"]==blobs["POP_PAYLOAD.bin"]
    nested=blobs["NESTED_OUTPUT_PAYLOAD.bin"]
    assert u64(nested)==io+0x2080 and u32(nested,8)==15
    assert blobs["NESTED_DESCS.bin"]==blobs["POP_DESCS.bin"]
    desc=blobs["NESTED_DESCS.bin"][120:144]
    assert (u64(desc),u32(desc,8),u32(desc,12),u32(desc,16),u32(desc,20))==(io+0xcb4,92,0,5,0)
    o=json.loads(norm(P/"OWNER-PRIVATE.json"));assert o["module"]=="QcDeviceMFT8380" and o["rva"]==0x68e5a0 and o["target"]==callback
    assert target-o["base"]==0x681b00 and vtable-o["base"]==0x133a390
    dll=ROOT.parents[1]/"00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"
    data=dll.read_bytes();assert hashlib.sha256(data).hexdigest()=="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
    pe=pefile.PE(data=data)
    assert blobs["CALLBACK_CODE.bin"]==blobs["DELEGATE_CODE.bin"]==pe.get_data(0x68e5a0,128)
    for i in range(6):
        assert u64(blobs["VTABLE.bin"],i*8)-o["base"]==u64(pe.get_data(0x133a390+i*8,8))-pe.OPTIONAL_HEADER.ImageBase
    generated=Path(str(P)+"-generated")
    for f in generated.glob("*.cmd"):assert norm(f)==norm(P/f.name),f.name
    for n in ["get2-before-active.cmd","populate-active.cmd","late-arm-active.cmd"]:assert norm(P/n)==norm(HERE/n),n
    assert norm(P/"holder.ps1")==norm(HERE/"holder.ps1")
    assert norm(P/"SCRIPT-ENTRY-CONSUMED.marker").startswith("E011AQ_ATOMIC_ENTRY_UTC=")
    copy=json.loads((HERE/"COPY-SAFE.json").read_text());assert copy["cases"]==140 and not copy["complete_function_return_verified"]
    (P/"VALIDATED-PRIVATE-MANIFEST.json").write_text(json.dumps({str(f.relative_to(P)):{"bytes":f.stat().st_size,"sha256":hashlib.sha256(f.read_bytes()).hexdigest()} for f in [*C.glob("*.bin"),*P.glob("*.cmd"),P/"holder.ps1",P/"holder.log",P/"cdb-observer.raw",P/"RUN-SAFE.json",P/"OWNER-PRIVATE.json"]},indent=2)+"\n")
    safe={"experiment":"E011AQ","status":"PASS_LIVE_DELEGATE_AND_RETAINED_BG_COPY",
      "attempt":"E011AQ-20260930-1740A","Windows_attempt_consumed":True,"single_start":True,"valid_4k_handles":711,
      "clean_stop":True,"task_removed":True,"explicit_detaches":1,"debugger_exit":0,"initial_outer_resolved_probes":5,
      "inner_probes_qualified_and_resolved_before_call":3,"manual_qualification":True,"events":8,"records":26,"bytes":2720,
      "pre_capture_qualification_memory_diagnostics":2,"capture_diagnostics":0,"nested_channel_corrected_while_same_call_held":True,
      "actual_original_callback_RVA":"0x68E5A0","actual_callback_method":"CamX::CAWBMain::AWBGetParameter",
      "two_callback_code_snapshots_128_bytes_each_match_original":True,"vtable_48_bytes_six_targets_match_original":True,
      "delegate_chain":"wrapper+0x28 -> object+0 -> vtable+0x10","retained_BG_actor_offset":"0xFB744",
      "retained_quad_actor_offset":"0xFB798","retained_quad_already_one_before_GetParam2":True,
      "retained_before_delegate_populate_and_after_92_bytes_exact":True,"PopulateOutput_copies_all_retained_92_bytes_to_IO":True,
      "before_output_quad":0,"after_output_quad":1,"publication_and_cold_request1_quad":1,
      "top_level_BG_output_present":False,"nested_BG_via_output1_type":1,"output1_container_bytes":16,
      "nested_descriptor_count":15,"nested_BG_index":5,"nested_BG_type":5,"nested_BG_bytes":92,
      "input2_type":2,"input2_separate_information_bytes":12,"input2_is_nested_output_list":False,
      "bounded_original_copy_slice_cases":140,"full_algorithm_emulation_return_claimed":False,
      "initial_value_policy_closed":False,"upstream_retained_record_initialization_open":True,
      "kernel_debugging":False,"Linux_camera_runtime":False,"private_payloads_exported":False,"native_rear_ISP_runtime_allowed":False}
    (HERE/"VALIDATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n");print(json.dumps(safe))
if __name__=="__main__":main()
