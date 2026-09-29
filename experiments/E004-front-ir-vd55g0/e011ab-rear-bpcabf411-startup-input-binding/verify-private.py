#!/usr/bin/env python3
"""Validate private common inputs against live output; emit aggregate facts."""
import argparse, importlib.util, json, re, struct, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("producer",HERE.parent/"e011aa-rear-bpcabf411-common-producer"/"producer.py")
P=importlib.util.module_from_spec(s);s.loader.exec_module(P)
def main():
    a=argparse.ArgumentParser();a.add_argument("private",type=Path);a.add_argument("--log",default="cdb-observer.raw");a.add_argument("--request-limit",type=int,default=16);a.add_argument("--startup-corpus",type=Path);args=a.parse_args()
    text=(args.private/args.log).read_text(errors="replace")
    events=[(m[1],int(m[2]),int(m[3])) for m in re.finditer(r"E011AB_(REQ|COMMON|PACK) n=(\d+) req=(\d+)",text)]
    requests=[req for typ,n,req in events if typ=="REQ"]
    assert requests==list(range(1,args.request_limit+1)), "request coverage/order incomplete"
    commons=[(n,req) for typ,n,req in events if typ=="COMMON"]
    packs=[(n,req) for typ,n,req in events if typ=="PACK"]
    assert len(commons)==len(packs)==8, "eight common and output samples required"
    assert commons==packs, "common/packer ordering not aligned"
    assert not re.search(r"Memory access error|Syntax error|Unable to read",text), "observer errors"
    selected_match=0;states=[];semantic_inputs=[]
    for n,req in commons:
        c=args.private/"capture"
        r=(c/f"COMMON{n:02}_REGION.bin").read_bytes()
        reserve=(c/f"COMMON{n:02}_RESERVE.bin").read_bytes()
        out=(c/f"PACK{n:02}_OUT.bin").read_bytes()
        assert len(r)==428 and len(reserve)==24 and len(out)==144
        vals=struct.unpack("<107f",r);anchors=list(struct.unpack("<6f",reserve)[1:])
        inputs=(list(vals[82:84]),[[vals[84],vals[86]],[vals[85],vals[87]]],
                [list(vals[88:93]),list(vals[93:98])],anchors)
        semantic_inputs.append(inputs);state=P.calculate(*inputs);states.append(P.pack(state))
        def hs(start,num):return list(struct.unpack_from("<"+str(num)+"H",out,start))
        def ss(start,num):return list(struct.unpack_from("<"+str(num)+"h",out,start))
        live={"signed10":ss(0x50,2),"unsigned9":hs(0x4c,2),"nibble4":hs(0x54,2),
              "byte_group0":[hs(0x60,4),hs(0x68,4)],
              "byte_group1":[hs(0x70,4),hs(0x78,4)],
              "nibble_group":[hs(0x80,4),hs(0x88,4)]}
        assert live==state,f"live common output mismatch sample {n}"
        selected_match+=1
    report={"status":"LIVE_COMMON_ARITHMETIC_CLOSED","common_samples_exact":selected_match,
            "output_scalar_matches":selected_match*30,"request_ids":requests,
            "common_request_tags":[req for n,req in commons],"events":events,
            "selected_semantic_input_binding":True,"runtime_tuning_root_selection":False,
            "complete_four_packet_composition":False,"native_rear_runtime_allowed":False}
    report["distinct_startup_selected_inputs"]=len({repr(x) for x in semantic_inputs[:3]})
    report["distinct_startup_seven_word_states"]=len({repr(x) for x in states[:3]})
    assert [req for n,req in commons]==[0,1,2,4,5,6,7,8], "sampled startup schedule changed"
    report["pre_first_request_tag_zero_is_phase_marker"]=True
    report["request_3_common_and_packer_hold"]=True
    if args.startup_corpus:
        path=HERE.parents[2]/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py"
        spec=importlib.util.spec_from_file_location("decoder",path);decoder=importlib.util.module_from_spec(spec);spec.loader.exec_module(decoder)
        records=json.loads(args.startup_corpus.read_text(encoding="utf-8-sig"))["records"]
        phases=[]
        for rec in records:
            if rec.get("idx")!=1 or not rec.get("complete") or rec["n"]>=4:continue
            values={reg:val for reg,val,offset,kind in decoder.decode(bytes.fromhex(rec["hex"]))["writes"] if reg in P.REGS}
            if len(values)!=7:continue
            assert rec["n"]<3 and values==states[rec["n"]], "startup phase BPC seven-word mismatch"
            phases.append(rec["n"])
        assert phases==[0,1,2], "three startup records required"
        report["private_startup_packet_phases_exact"]=phases
        report["private_startup_register_matches"]=21
        report["bpc_seven_word_startup_phase_binding"]=True
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
