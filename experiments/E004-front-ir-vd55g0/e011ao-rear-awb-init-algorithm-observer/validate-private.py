#!/usr/bin/env python3
"""Strict same-SP11 observation audit; no private payload leaves this machine."""
from pathlib import Path
import hashlib,json,re,struct,pefile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
P=ROOT.parent/"private/E011AO-20260930-1250A";C=P/"capture"
def read(name,size):
    b=(C/name).read_bytes();assert len(b)==size,name;return b
def u32(b,o):return struct.unpack_from("<I",b,o)[0]
def norm(p):return p.read_text(encoding="utf-8-sig").replace("\r\n","\n")
def main():
    raw=(P/"cdb-observer.raw").read_text(errors="replace")
    hb=(P/"holder.log").read_bytes();h=hb.decode("utf-16" if hb.startswith((b"\xff\xfe",b"\xfe\xff")) else "utf-8-sig")
    for marker in ("E011AO_HOLDER_BEGIN","START_BEGIN","START_STATUS=Success","STOP_BEGIN","STOP_PASS valid_4k_handles=859","E011AO_HOLDER_END"):
        assert h.count(marker)==1,marker
    run=json.loads((P/"RUN-SAFE.json").read_text(encoding="utf-8-sig"))
    assert run["singleStart"] and run["cleanStop"] and run["taskRemoved"]
    assert run["oldDebuggerExitCode"]==run["actualDebuggerExitCode"]==0
    assert raw.count("Detached")==2 and run["valid4kHandles"]==859
    events=re.findall(r"^E011AO_(INIT|BEFORE|AFTER|PUBLISH|CONSUMER) n=(\d+) tid=([0-9a-f]+)",raw,re.M)
    assert [(t,int(n)) for t,n,tid in events]==[("INIT",1),("BEFORE",1),("AFTER",1),("PUBLISH",1),("CONSUMER",1),("INIT",2),("CONSUMER",2),("CONSUMER",3),("CONSUMER",4)]
    assert len({events[i][2] for i in (0,1,2,3)})==1
    assert re.search(r"^E011AO_CURRENT_RVA 831964\s*$",raw,re.M)
    assert re.search(r"^E011AO_FILTER selector=c size=5c outputMatch=1\s*$",raw,re.M)
    assert re.search(r"^E011AO_RETURN_CHECK rva=831968 tidMatch=1 ownerMatch=1 result=0\s*$",raw,re.M)
    assert re.search(r"^E011AO_FLOW rva=831e00 property=5000001d size=80\s*$",raw,re.M)
    # Initial obsolete owner had no events; its unresolved/load-gate diagnostic
    # is retained. Captured owner had five resolved probes before Start.
    captured=raw.split("E011AO_INIT n=1",1)[1]
    diagnostics=list(re.finditer(r"^.*(?:syntax error|memory access error|error at).*$",captured,re.M|re.I))
    assert len(diagnostics)==1
    assert diagnostics[0].group(0).startswith("E011AO_CONSUMER_SITE rva=Couldn't resolve error at")
    assert diagnostics[0].start()>captured.index("E011AO_CONSUMER n=4")
    # A queued informational query ran after DLL unload; capture commands succeeded.
    assert not re.search(r"^E011AO_(?:OVERLAP|INCOHERENT)_PAIR\s*$",captured,re.M)
    requests=[int(x) for x in re.findall(r"^E011AO_CONSUMER n=\d+ tid=[0-9a-f]+ req=(\d+)",raw,re.M)]
    assert requests==[1,1,2,3]
    sizes={"INIT01_BG.bin":92,"INIT02_BG.bin":92,"BEFORE01_BG.bin":92,"BEFORE01_PARAM.bin":40,
      "BEFORE01_BGDESC.bin":24,"BEFORE01_ALGO.bin":32,"BEFORE01_TARGET.bin":128,
      "AFTER01_BG.bin":92,"PUBLISH01_REC.bin":128,"PUBLISH01_BG.bin":92,
      **{f"CONSUMER{i:02}_REC.bin":128 for i in range(1,5)}}
    assert {f.name for f in C.glob("*.bin")}==set(sizes)
    blobs={name:read(name,size) for name,size in sizes.items()}
    assert sum(sizes.values())==1324
    before=re.search(r"^E011AO_BEFORE n=1 tid=([0-9a-f]+) selector=c target=([0-9a-f`]+) io=([0-9a-f`]+)",raw,re.M);assert before
    target=int(before[2].replace("`",""),16);io=int(before[3].replace("`",""),16)
    desc=blobs["BEFORE01_BGDESC.bin"];assert struct.unpack_from("<Q",desc)[0]==io+0xcb4
    assert struct.unpack_from("<4I",desc,8)==(92,0,10,0)
    assert u32(blobs["BEFORE01_PARAM.bin"],0)==12
    assert struct.unpack_from("<Q",blobs["BEFORE01_ALGO.bin"],8)[0]==target
    assert blobs["BEFORE01_BG.bin"]==blobs["AFTER01_BG.bin"]
    # Publish x0 is the node context, not AWB IO. Exclude the auxiliary BG read.
    assert u32(blobs["INIT01_BG.bin"],84)==0
    assert u32(blobs["BEFORE01_BG.bin"],84)==1
    assert u32(blobs["PUBLISH01_REC.bin"],76)==1
    assert all(u32(blobs[f"CONSUMER{i:02}_REC.bin"],76)==1 for i in range(1,5))
    owners=json.loads((P/"OWNER-TRANSCRIPT-PRIVATE.json").read_text(encoding="utf-8-sig"))
    owners=[owners] if isinstance(owners,dict) else owners
    assert len(owners)==1 and owners[0]["module"]=="QcDeviceMFT8380" and owners[0]["rva"]==0x681b00
    dll=ROOT.parents[1]/"00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"
    assert hashlib.sha256(dll.read_bytes()).hexdigest()=="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
    pe=pefile.PE(str(dll));assert blobs["BEFORE01_TARGET.bin"]==pe.get_data(0x681b00,128)
    generated=Path(str(P)+"-generated")
    for f in generated.glob("*.cmd"):assert norm(f)==norm(P/f.name),f.name
    assert norm(P/"holder.ps1")==norm(HERE/"holder.ps1")
    assert norm(P/"before-active.cmd")== "\n".join(norm(P/"before.cmd").split("\n")[1:])
    assert norm(P/"after-active.cmd")== "\n".join(norm(P/"after.cmd").split("\n")[1:])
    assert (P/"SCRIPT-ENTRY-CONSUMED.marker").read_text(encoding="utf-8-sig").startswith("E011AO_ATOMIC_ENTRY_UTC=")
    (P/"VALIDATED-PRIVATE-MANIFEST.json").write_text(json.dumps({str(f.relative_to(P)):{"bytes":f.stat().st_size,"sha256":hashlib.sha256(f.read_bytes()).hexdigest()} for f in [*C.glob("*.bin"),*P.glob("*.cmd"),P/"holder.ps1",P/"holder.log",P/"cdb-observer.raw",P/"RUN-SAFE.json",P/"OWNER-TRANSCRIPT-PRIVATE.json"]},indent=2)+"\n")
    safe={"experiment":"E011AO","status":"PASS_LIVE_SELECTOR12_EXCLUSION_AND_WRAPPER_IDENTITY",
      "attempt":"E011AO-20260930-1250A","Windows_attempt_consumed":True,
      "single_start":True,"valid_4k_handles":859,"clean_stop":True,"task_removed":True,
      "debugger_exits":[0,0],"explicit_detaches":2,"FrameServer_replaced_before_Start":True,
      "actual_owner_probes_resolved_before_Start":5,"manual_pair_and_publish_completion":True,"queued_post_stop_query_unresolved":True,
      "manual_pair_same_thread_and_processor":True,"input_records":14,"input_bytes":1324,"events":9,
      "consumer_request_ids":requests,"BG_before_after_bytes_exact":92,"excluded_auxiliary_records":["PUBLISH01_BG.bin"],"valid_source_records":13,"valid_source_bytes":1232,
      "quad_at_initial_helper_entry":0,"quad_before_selector12":1,"quad_after_selector12":1,
      "publication_and_four_consumers_quad_exact":True,
      "selector12_origin_excluded_for_this_invocation":True,"algorithm_wrapper_module":"QcDeviceMFT8380",
      "algorithm_wrapper_rva":"0x681B00","algorithm_wrapper_name":"CamX::AWBGetParam",
      "captured_target_bytes_match_unchanged_original":True,
      "wrapper_delegate_object_offset":"0x28","wrapper_delegate_GetParam_slot":"0x10",
      "exact_prior_writer_and_value_policy_closed":False,
      "next_boundary":"earlier SetParam at83180C/GetParam2 at831920 plus AWBGetParam delegate",
      "kernel_debugging_performed":False,"Linux_camera_runtime_performed":False,"private_bytes_exported":False,
      "native_rear_ISP_runtime_allowed":False}
    (HERE/"VALIDATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n");print(json.dumps(safe))
if __name__=="__main__":main()
