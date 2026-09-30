#!/usr/bin/env python3
"""Validate same-SP11 AEC/context -> shared object -> source BPC startup chain."""
from pathlib import Path
import importlib.util,json,re,struct,subprocess,tempfile,hashlib
import pefile,capstone
HERE=Path(__file__).resolve().parent
PRIVATE=HERE.parents[2].parent/"private"/"E011AF-20260930-0535B"
CORPUS=HERE.parents[2].parent/"private/e006a/E006A-PRIVATE-RECORDS-v2.json"
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
P=load("request_live_af",HERE.parent/"e011ae-rear-request-generic-trigger-producer"/"producer.py")
A=load("authority_live_af",HERE.parent/"e011ac-rear-bpcabf411-tuning-selection"/"authority.py")
TUNE=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin")
def bits(v):return struct.pack("<f",v)
def parse(text):
    # CDB can concatenate command text and event output on a physical line.
    # Parse the exact numeric event grammar, never a whole-line key dictionary.
    pointer=r"[0-9a-f`]+"
    patterns={
        "GAIN":r"n=(?P<n>\d+) req=(?P<req>\d+) isp=(?P<isp>"+pointer+r") tid=(?P<tid>"+pointer+r")",
        "GEN":r"n=(?P<n>\d+) req=(?P<req>\d+) isp=(?P<isp>"+pointer+r") shared=(?P<shared>"+pointer+r") vector=(?P<vector>"+pointer+r") tid=(?P<tid>"+pointer+r") bytes=(?P<bytes>\d+)",
        "CALC":r"n=(?P<n>\d+) req=(?P<req>\d+) shared=(?P<shared>"+pointer+r") vector=(?P<vector>"+pointer+r") tid=(?P<tid>"+pointer+r") caller_rva=(?P<caller_rva>"+pointer+r") bytes=(?P<bytes>\d+)",
        "COMMON":r"n=(?P<n>\d+) req=(?P<req>\d+) root=(?P<root>"+pointer+r") caller_rva=(?P<caller_rva>"+pointer+r") tid=(?P<tid>"+pointer+r")",
        "INTERP":r"n=(?P<n>\d+) req=(?P<req>\d+) caller_rva=(?P<caller_rva>"+pointer+r") tid=(?P<tid>"+pointer+r")",
        "PACK":r"n=(?P<n>\d+) req=(?P<req>\d+)",
        "REQ":r"n=(?P<n>\d+) req=(?P<req>\d+)",
        "SNAPSHOT":r"stage=(?P<stage>\d+) req=(?P<req>\d+) isp=(?P<isp>"+pointer+r") tid=(?P<tid>"+pointer+r") context=(?P<context>\d+)"}
    events=[]
    for kind,pattern in patterns.items():
        for m in re.finditer("E011AF_"+kind+" "+pattern,text,re.I):
            event={"event":kind,"pos":m.start()}
            for key,value in m.groupdict().items():
                event[key]=int(value.replace("`",""),16 if key in ("isp","shared","vector","tid","caller_rva","root") else 10)
            events.append(event)
    return sorted(events,key=lambda e:e["pos"])

def source_anchors():
    dll=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll")
    blob=dll.read_bytes();assert hashlib.sha256(blob).hexdigest()=="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
    pe=pefile.PE(data=blob);cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
    anchors={0xa08dc8:("bl","#0x890208"),0xa08df8:("blr","x15"),0xa08e34:("blr","x15"),
        0x897d68:("bl","#0x76e198"),0x897d6c:("ldp","x29, x30, [sp], #0x10"),
        0x746e6c:("bl","#0x88a4e8"),0x746f4c:("bl","#0x897b78")}
    for rva,expected in anchors.items():
        ins=next(cs.disasm(pe.get_data(rva,4),rva));assert (ins.mnemonic,ins.op_str)==expected
    return len(anchors)

def main():
    anchor_count=source_anchors()
    cap=PRIVATE/"capture";text=(PRIVATE/"cdb-observer.raw").read_text(errors="replace")
    safe=json.loads((PRIVATE/"RUN-SAFE.json").read_text(encoding="utf-8-sig"))
    assert safe["start_stop"]=="PASS" and safe["valid_4k_handles"]>=10
    assert safe["capture_files"]==250 and safe["concrete_breakpoints_verified_before_start"]==11
    assert safe["task_removed"] and not safe["camera_retry"]
    assert safe["observer_repair_in_same_held_session"] and not safe["observer_errors_after_repair"]
    repair=text.index("E011AF_REGISTER_ALIAS_REPAIRED_SAME_HELD_SESSION")
    assert not re.search(r"register error|Syntax error|Numeric expression missing|Unable to read",text[repair:])
    events=parse(text)
    def ev(kind):return [e for e in events if e["event"]==kind]
    assert [e["req"] for e in ev("REQ")]==list(range(1,9))
    for kind in ("COMMON","INTERP","PACK"):
        assert [(e["n"],e["req"]) for e in ev(kind)]==[(1,0),(2,1),(3,2)]
    assert len(ev("CALC"))==len(ev("GEN"))==len(ev("GAIN"))==16
    def raw(e,label):
        return (cap/f'{e["event"]}{e["n"]:02}_{label}.bin').read_bytes()
    gain_cases={};gain_fields=sensitivity_fields=metadata_returns=unused_metadata=0
    for e in ev("GAIN"):
        prior=[g for g in ev("GAIN") if g["pos"]<e["pos"] and (g["isp"],g["tid"])==(e["isp"],e["tid"])]
        begin=prior[-1]["pos"] if prior else -1
        snaps=[g for g in ev("SNAPSHOT") if begin<g["pos"]<e["pos"] and (g["isp"],g["tid"])==(e["isp"],e["tid"])]
        head=raw(e,"HEAD");ctx=raw(e,"CTX");node=raw(e,"NODE");aec=raw(e,"AEC")
        assert len(head)==0x108 and len(ctx)==32 and len(node)==12 and len(aec)==0xc4
        override=struct.unpack_from("<I",head,0xf4)[0]==1
        if snaps:
            values={s["context"] for s in snaps};assert len(values)==1
            snapshot=next(iter(values));metadata_returns+=len(snaps)
        else:
            # Canonical unused input, not a claim that metadata returned zero.
            assert override or node[0]==3
            snapshot=0;unused_metadata+=1
        case=dict(gains={name:struct.unpack_from("<f",aec,offset)[0] for name,offset in (("short",8),("mid",0x20),("long",0x38))},
            sensitivities={name:struct.unpack_from("<f",aec,offset)[0] for name,offset in (("short",0xc),("mid",0x24))},
            drc_gain=struct.unpack_from("<f",aec,0x78)[0],sensor_mid_override=override,
            node_context=node[0],snapshot_context=snapshot,input_context=ctx[0xc],request_id=e["req"])
        slot=P.gain_slot(override,node[0],snapshot,ctx[0xc])
        fixed=raw(e,"FIXED");assert fixed[0x30:0x34]==bits(case["gains"][slot]);gain_fields+=1
        denominator=case["sensitivities"]["short"]
        ratio=1.0 if abs(denominator)<1e-6 else P.f32(case["sensitivities"]["mid"]/denominator)
        assert fixed[0x2c:0x30]==bits(ratio);sensitivity_fields+=1
        gain_cases[e["n"]]=case
    gen_cases={};generic_fields=source_object_pairs=preceding_atomic_tags=0
    for e in ev("GEN"):
        prior=[g for g in ev("GAIN") if g["pos"]<e["pos"] and (g["isp"],g["tid"])==(e["isp"],e["tid"])]
        assert prior,"GEN has no observed selected-gain producer"
        gain=prior[-1];case=gain_cases[gain["n"]]
        assert e["req"]>=1
        # IQSetup executes before the primary atomic hook; the observer's global
        # tag there can still name the preceding request. Bind to the actual
        # GEN request only with an intervening observed atomic event.
        if case["request_id"] != e["req"]:
            between=[q for q in ev("REQ") if gain["pos"]<q["pos"]<e["pos"]]
            assert e["req"]==case["request_id"]+1 and len(between)==1 and between[0]["req"]==e["req"]
            preceding_atomic_tags+=1
        case=dict(case,request_id=e["req"])
        assert raw(e,"HEAD")[:8]==raw(gain,"HEAD")[:8]
        assert raw(e,"HEAD")[0xf4:0xf8]==raw(gain,"HEAD")[0xf4:0xf8]
        assert raw(e,"CTX")[0xc]==raw(gain,"CTX")[0xc]
        aec=raw(e,"AEC");gain_aec=raw(gain,"AEC")
        for offset in (8,0x20,0x38,0xc,0x24,0x78):
            assert aec[offset:offset+4]==gain_aec[offset:offset+4],"AEC semantic input changed between producer and generic setup"
        result=P.produce_triggers(**case)
        current=raw(e,"CURRENT");desc=struct.unpack("<3Q",raw(e,"VECTOR"))
        assert desc[0]==e["vector"] and desc[1]-desc[0]==len(current)==e["bytes"]==168
        assert desc[2]>=desc[1] and e["shared"]==e["isp"]+0x17190
        fixed=raw(e,"FIXED")
        for (index,value),offset in zip(result["typed"],(0x74,0x2c,0x30)):
            assert current[index*4:index*4+4]==bits(value)==fixed[offset:offset+4]
            generic_fields+=1
        gen_cases[e["n"]]=case;source_object_pairs+=1
    # Independent original-source membership was obtained from Ghidra on SP11.
    membership=json.loads((HERE/"CALLER-SOURCE-SAFE.json").read_text())
    assert membership["actual_bpc_function_rva"]=="0xa08850"
    assert membership["builder_caller_rva"]=="0xa08dcc"
    assert membership["interpolation_caller_rva"]=="0xa08dfc"
    assert membership["common_caller_rva"]=="0xa08e38"
    modes=[]
    for n in (1,2):
        b=(cap/f"SELECT{n:02}_MODES.bin").read_bytes()
        assert len(b)%8==0;modes.append([struct.unpack_from("<2I",b,i) for i in range(0,len(b),8)])
    t=A.Authority(TUNE);states=[];cases_by_req={};objects=typed=regions=common=anchors=0
    for interp in ev("INTERP"):
        assert interp["caller_rva"]==0xa08dfc
        corresponding=next(e for e in ev("COMMON") if e["n"]==interp["n"])
        assert corresponding["caller_rva"]==0xa08e38 and corresponding["tid"]==interp["tid"]
        choices=[e for e in ev("CALC") if e["pos"]<interp["pos"] and e["caller_rva"]==0xa08dcc and e["tid"]==interp["tid"] and e["req"]==interp["req"]]
        assert len(choices)==1,"startup BPC input builder is not uniquely observed"
        calc=choices[0];current=raw(calc,"CURRENT");desc=struct.unpack("<3Q",raw(calc,"VECTOR"))
        assert desc[0]==calc["vector"] and desc[1]-desc[0]==len(current)==168
        assert struct.unpack("<3I",raw(calc,"TYPES"))==(2,5,1)
        if interp["req"]==0:
            result=P.S.AC.cold_seed(t)
        else:
            candidates=[e for e in ev("GEN") if e["pos"]<calc["pos"] and e["shared"]==calc["shared"] and e["vector"]==calc["vector"] and e["tid"]==calc["tid"]]
            assert candidates,"BPC shared object has no observed generic producer"
            gen=candidates[-1]
            assert gen["req"]==calc["req"] and current==raw(gen,"CURRENT")
            case=gen_cases[gen["n"]];cases_by_req[calc["req"]]=case
            result=P.produce_bpc(t,modes[1],**case);objects+=1
        assert result["root"]==corresponding["root"]
        for level,index in enumerate((2,5,1),1):
            b=raw(interp,f"LEVEL{level}");kind,value=struct.unpack("<2f",b)
            assert kind==index and b[4:]==current[index*4:index*4+4];typed+=2
        assert struct.pack("<107f",*result["region"])==raw(corresponding,"REGION");regions+=107
        root=raw(corresponding,"ROOT");reserve=raw(corresponding,"RESERVE")
        assert reserve==root[0xa0:0xb8] and list(struct.unpack_from("<5f",reserve,4))==t.anchors(result["root"]);anchors+=5
        out=raw(next(e for e in ev("PACK") if e["n"]==interp["n"]),"OUT")
        def hs(start,n):return list(struct.unpack_from("<"+str(n)+"H",out,start))
        def ss(start,n):return list(struct.unpack_from("<"+str(n)+"h",out,start))
        native={"signed10":ss(0x50,2),"unsigned9":hs(0x4c,2),"nibble4":hs(0x54,2),
            "byte_group0":[hs(0x60,4),hs(0x68,4)],"byte_group1":[hs(0x70,4),hs(0x78,4)],
            "nibble_group":[hs(0x80,4),hs(0x88,4)]}
        assert result["state"]==native;common+=30;states.append(result["registers"])
    source=P.startup_common(t,modes[1],cases_by_req[1],cases_by_req[2])
    assert source["source_request_id"]==(0,1,2)
    assert [P.S.AC.P.pack(state) for state in source["common"]]==states
    semantic_wire=bytearray()
    for state in source["common"]:
        values=state["signed10"]+state["unsigned9"]+state["nibble4"]
        for key in ("byte_group0","byte_group1","nibble_group"):
            values.extend(state[key][0]+state[key][1])
        semantic_wire.extend(struct.pack("<2h2H26B",*values))
    expected=bytearray()
    for state in (states[0],states[1],states[2],states[2]):
        expected.extend(struct.pack("<7I",*[state[reg] for reg in P.S.AC.P.REGS]))
    with tempfile.TemporaryDirectory(prefix="e011af-private-binding-") as directory:
        binary=str(Path(directory)/"binder-check")
        subprocess.run(["cc","-std=c11","-Wall","-Wextra","-Werror",str(HERE.parent/"e011ae-rear-request-generic-trigger-producer"/"compile-check.c"),"-o",binary],check=True)
        actual=subprocess.run([binary,"bind-source"],input=bytes(semantic_wire),capture_output=True,check=True)
        assert actual.stdout==bytes(expected),"source-produced startup common states changed across C packet binding"
    decoder=load("commands_live_af",HERE.parent/"e006a-windows-rear-rtcdm-targeted-corpus"/"decode_rear_rtcdm.py")
    phases=[]
    for record in json.loads(CORPUS.read_text(encoding="utf-8-sig"))["records"]:
        if record.get("idx")!=1 or not record.get("complete") or record["n"]>=4:continue
        values={reg:val for reg,val,offset,kind in decoder.decode(bytes.fromhex(record["hex"]))["writes"] if reg in P.S.AC.P.REGS}
        if len(values)!=7:continue
        assert record["n"]<3 and values==states[record["n"]];phases.append(record["n"])
    assert phases==[0,1,2]
    report={"experiment":"E011AF","identity":safe["identity"],
        "status":"LIVE_AEC_CONTEXT_SHARED_OBJECT_TO_SOURCE_BPC_STARTUP_PASS",
        "original_source_instruction_anchors":anchor_count,
        "primary_ife_source_order_iqsetup_atomic_generic_proven":True,
        "valid_windows_rear_4k_handles":safe["valid_4k_handles"],"capture_files":250,
        "source_gain_field_matches":gain_fields,"source_sensitivity_field_matches":sensitivity_fields,
        "snapshot_metadata_returns_bound_to_gain_records":metadata_returns,
        "snapshot_metadata_not_read_canonical_inputs":unused_metadata,
        "selected_gain_to_generic_object_pairs":source_object_pairs,
        "gain_observer_tag_preceded_atomic_request":preceding_atomic_tags,
        "gain_global_log_tag_is_not_source_request_identity":True,"generic_produced_scalar_matches":generic_fields,
        "actual_bpc_startup_input_builders_unique":3,"active_same_request_shared_object_lineage_matches":objects,
        "ordinary_typed_vector_field_matches":typed,"source_live_region_fields_exact":regions,
        "source_live_common_selected_scalars_exact":common,"source_reserve_anchor_matches":anchors,
        "retained_startup_packet_phases_exact":phases,"retained_startup_register_word_matches":21,
        "startup_common_states_generated_from_source_and_live_AEC_semantics":3,
        "source_common_to_c_packet_binding_phases_checked":4,
        "source_common_to_c_provider_word_matches":28,
        "c_binding_phase3_is_held_semantics_not_new_captured_words":True,
        "c_materializer_ids_are_explicit_host_fixture":[4,5,6,7],
        "full_e008o_recursive_dmi_validation_exercised":False,
        "live_startup_aec_context_to_bpc_binding_closed":True,
        "cold_bpc_seed_uses_source_invariant_default":True,"cold_zero_vector_producer_policy_inferred":False,
        "full_AEC_algorithm_or_snapshot_metadata_lookup_ported":False,
        "source_phase3_hold_authority":"E011AB; host binding E011AE [0,1,2,2]",
        "repair_in_same_held_session":True,"camera_retry":False,
        "complete_e008o_composition_closed":False,"wm16_retirement_closed":False,
        "native_rear_linux_runtime_allowed":False,"raw_source_or_capture_values_exported":False}
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
