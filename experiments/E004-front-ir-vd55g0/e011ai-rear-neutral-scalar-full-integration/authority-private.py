#!/usr/bin/env python3
"""Recover only independently recorded semantic inputs; outputs are not authority."""
from pathlib import Path
import hashlib,json,re,struct
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PRIVATE=ROOT.parent/"private"
RECOVERED=PRIVATE/"E011X-source-recovered"
def f32(word):return struct.unpack("<f",struct.pack("<I",word))[0]
def get_inputs():
    meta=json.loads((HERE.parent/"e011x-rear-neutral-3a-scalar-source-recon/LIVE-VALIDATION-SAFE.json").read_text())
    raw=(RECOVERED/"cdb-transcript.raw").read_bytes()
    assert hashlib.sha256(raw).hexdigest()==meta["private_transcript_sha256"]
    assert hashlib.sha256((RECOVERED/"holder.log").read_bytes()).hexdigest()==meta["private_holder_log_sha256"]
    samples=json.loads((RECOVERED/"samples.json").read_text(encoding="utf-8-sig"))["samples"]
    original=(RECOVERED/"e006a-compare.json")
    order=json.loads(original.read_text())["event_order"]
    text=raw.decode();events=list(re.finditer(r"E011X_(DEMUX|PDPC|WB|TRIGGER) n=([0-9]+)[^\n]*",text))
    assert len(events)==32
    grouped={tag:{} for tag in ("DEMUX","PDPC","WB","TRIGGER")}
    observed=[]
    for i,e in enumerate(events):
        tag,n=e.group(1),int(e.group(2));assert n not in grouped[tag]
        block=text[e.end():events[i+1].start() if i+1<len(events) else len(text)]
        words=[]
        for line in block.splitlines():
            if len(words)=={"DEMUX":16,"PDPC":5,"WB":4,"TRIGGER":6}[tag]:break
            m=re.match(r"^[0-9a-f]{8}`[0-9a-f]{8}\s+(.+)$",line)
            if m:
                tokens=m.group(1).split()
                assert all(re.fullmatch(r"[0-9a-f]{8}(?:`[0-9a-f]{8})?",x) for x in tokens)
                words.extend(int(x.replace("`",""),16) for x in tokens)
        assert len(words)=={"DEMUX":16,"PDPC":5,"WB":4,"TRIGGER":6}[tag]
        grouped[tag][n]=words
        observed.append([tag,n,words[0] if tag=="TRIGGER" else None])
    assert observed==order
    assert [x for x in observed[:12]]==[
        ["DEMUX",0,None],["PDPC",0,None],["WB",0,None],["TRIGGER",0,1],
        ["DEMUX",1,None],["PDPC",1,None],["WB",1,None],["TRIGGER",1,2],
        ["DEMUX",2,None],["PDPC",2,None],["WB",2,None],["TRIGGER",2,3]]
    # No scalar recalc between source request3 and4: explicit hold of source2.
    assert observed[12]==["TRIGGER",3,4]
    inputs=[]
    for n in range(8):
        sample=samples[n];assert sample["n"]==n
        demux,pdpc,wb,trigger=(grouped[tag][n] for tag in ("DEMUX","PDPC","WB","TRIGGER"))
        assert sample["bayer"]==(demux[0]&255)==2
        assert sample["demux_gain"]==f32(demux[3])
        assert sample["bls"]==[f32(x) for x in demux[8:12]]
        assert sample["channel"]==[f32(x) for x in demux[12:16]]
        assert sample["pdpc_floats"]==[f32(x) for x in pdpc]
        assert sample["wb"]==[f32(x) for x in wb]
        assert sample["request_id"]==trigger[0]==n+1
        assert sample["trigger_dgain"]==f32(trigger[1])
        assert sample["trigger"]==[f32(x) for x in trigger[2:]]
        assert pdpc[2:5]==wb[:3], "same common-calculation AWB tuple required"
        # Strict original bit patterns, not formatted decimal log calibration.
        inputs.append({"bayer":2,"demux_gain":f32(demux[3]),
            "bls":[f32(x) for x in demux[8:12]],"channel":[f32(x) for x in demux[12:16]],
            "awb_g":f32(wb[0]),"awb_b":f32(wb[1]),"awb_r":f32(wb[2]),
            "predictive_gain":f32(wb[3])})
    assert all(x["predictive_gain"]==1.0 for x in inputs)
    assert all(x["bls"]==inputs[0]["bls"] for x in inputs)
    assert all(x["channel"]==inputs[0]["channel"] for x in inputs)
    return inputs,{"input_sample_count":8,"numeric_events":32,"source_schedule":[0,1,2,2],
        "trace_sha256_verified":True,"holder_sha256_verified":True,
        "original_trace_bit_patterns_equal_archived_samples":True,
        "pdpc_wb_awb_inputs_coherent":True,"predictive_gain_all_one":True,
        "event_order_and_request3_hold_verified":True,
        "cold_source_input_is_observed_pre_request1_not_assumed_zero":True}
if __name__=="__main__":
    _,safe=get_inputs();print(json.dumps(safe,indent=2))
