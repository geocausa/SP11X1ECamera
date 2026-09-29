#!/usr/bin/env python3
"""SP11-private startup scalar -> source interval -> region/common/packet bridge."""
from pathlib import Path
import importlib.util,json,math,re,struct
HERE=Path(__file__).resolve().parent
PRIVATE=HERE.parents[2].parent/"private"/"E011AD-20260929-2245B"
CORPUS=HERE.parents[2].parent/"private"/"e006a"/"E006A-PRIVATE-RECORDS-v2.json"
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
V=load("private_verify",HERE/"verify-private.py");S=V.S;A=V.A
def main():
    t=A.Authority(V.TUNE);native=V.native();cap=PRIVATE/"capture"
    safe=json.loads((PRIVATE/"RUN-SAFE.json").read_text(encoding="utf-8-sig"))
    assert safe["start_stop"]=="PASS" and safe["valid_4k_handles"]>=10
    assert safe["capture_files"]==26 and safe["concrete_breakpoints_verified_before_start"]==6
    assert safe["task_removed"] and not safe["camera_retry"]
    text=(PRIVATE/"cdb-observer.raw").read_text(errors="replace")
    assert not re.search(r"Syntax error|Numeric expression missing|E011AD_BOUND_REJECT",text)
    requests=[int(m[1]) for m in re.finditer(r"E011AD_REQ n=\d+ req=(\d+)",text)]
    assert requests==list(range(1,9))
    for event in ("COMMON","INTERP","PACK"):
        assert [(int(m[1]),int(m[2])) for m in re.finditer(rf"E011AD_{event} n=(\d+) req=(\d+)",text)]==[(1,0),(2,1),(3,2)]
    modes=[]
    for n in (1,2):
        b=(cap/f"SELECT{n:02}_MODES.bin").read_bytes()
        assert len(b)%8==0
        modes.append([struct.unpack_from("<2I",b,o) for o in range(0,len(b),8)])
    states=[];region_matches=scalar_matches=anchors=decisions=0;types=[]
    for n in range(1,4):
        rootbytes=(cap/f"COMMON{n:02}_ROOT.bin").read_bytes()
        assert len(rootbytes)==184
        root=struct.unpack_from("<I",rootbytes)[0]
        path=modes[0 if n==1 else 1];assert t.resolve(path)==root
        rows,leaves,prefix=S.source_intervals(t,root,with_prefix=True)
        outer=(cap/f"INTERP{n:02}_VECTOR.bin").read_bytes();assert len(outer)==72
        vectors=[]
        for level in range(1,4):
            raw=(cap/f"INTERP{n:02}_LEVEL{level}.bin").read_bytes()
            assert len(raw)==8
            begin,end,capacity=struct.unpack_from("<3Q",outer,(level-1)*24)
            assert capacity>=end>begin>0 and end-begin==len(raw)
            values=struct.unpack("<2f",raw)
            assert all(math.isfinite(x) for x in values)
            vectors.append((raw,values))
        assert [values[0] for raw,values in vectors]==[2,5,1]
        types.append([int(values[0]) for raw,values in vectors])
        for row,(raw,values),mode in zip(prefix,vectors[:2],("outer","nested")):
            assert S.select([row],values[1])==(0,0,0.0)
            assert native([row],values[1],mode,raw)==(0,0,struct.pack("<f",0))
            decisions+=1
        raw,values=vectors[2]
        lower,upper,ratio=S.select(rows,values[1])
        assert native(rows,values[1],"terminal",raw)==(lower,upper,struct.pack("<f",ratio))
        decisions+=1
        # Actual exposure scalar is verification input; live regions/outputs are not producer input.
        result=S.produce(t,path,values[1])
        assert struct.pack("<107f",*result["region"])==(cap/f"COMMON{n:02}_REGION.bin").read_bytes()
        region_matches+=107
        reserve=(cap/f"COMMON{n:02}_RESERVE.bin").read_bytes()
        assert reserve==rootbytes[0xa0:0xb8]
        assert list(struct.unpack_from("<5f",reserve,4))==t.anchors(root);anchors+=5
        out=(cap/f"PACK{n:02}_OUT.bin").read_bytes();assert len(out)==144
        def hs(start,count):return list(struct.unpack_from("<"+str(count)+"H",out,start))
        def ss(start,count):return list(struct.unpack_from("<"+str(count)+"h",out,start))
        original={"signed10":ss(0x50,2),"unsigned9":hs(0x4c,2),"nibble4":hs(0x54,2),
                  "byte_group0":[hs(0x60,4),hs(0x68,4)],
                  "byte_group1":[hs(0x70,4),hs(0x78,4)],
                  "nibble_group":[hs(0x80,4),hs(0x88,4)]}
        assert result["state"]==original;scalar_matches+=30
        states.append(result["registers"])
    decoder=load("rtcdm",HERE.parent/"e006a-windows-rear-rtcdm-targeted-corpus"/"decode_rear_rtcdm.py")
    records=json.loads(CORPUS.read_text(encoding="utf-8-sig"))["records"];phases=[]
    for record in records:
        if record.get("idx")!=1 or not record.get("complete") or record["n"]>=4:continue
        values={reg:val for reg,val,offset,kind in decoder.decode(bytes.fromhex(record["hex"]))["writes"] if reg in S.AC.P.REGS}
        if len(values)!=7:continue
        assert record["n"]<3 and values==states[record["n"]]
        phases.append(record["n"])
    assert phases==[0,1,2]
    assert len({repr(x) for x in states})==2
    report={"experiment":"E011AD","identity":safe["identity"],
            "status":"LIVE_STARTUP_SCALAR_TO_SOURCE_INTERVAL_REGION_COMMON_PACKET_BRIDGE_PASS",
            "valid_windows_rear_4k_handles":safe["valid_4k_handles"],"capture_files":26,
            "common_request_tags":[0,1,2],"live_root_ids":["0x1a","0x100","0x100"],
            "live_trigger_type_vectors":types,"observed_numeric_trigger_vectors":9,
            "native_source_decisions_on_live_inputs_exact":decisions,
            "source_produced_live_region_field_matches":region_matches,
            "source_produced_live_selected_scalar_matches":scalar_matches,
            "serialized_runtime_anchor_matches":anchors,
            "private_startup_packet_phases_exact":phases,"private_startup_register_matches":21,
            "distinct_startup_seven_word_states":2,
            "startup_scalar_to_source_selection_bridge_closed":True,
            "actual_runtime_leaf_ordinal_directly_observed":False,
            "upstream_exposure_scalar_producer_closed":False,
            "live_scalar_input_validation_only":True,
            "captured_regions_or_registers_used_as_producer_input":False,
            "complete_e008o_composition_closed":False,
            "vfe1_wm16_same_generation_retirement_gate_open":True,
            "native_rear_linux_runtime_allowed":False,"raw_runtime_bytes_exported":False}
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
