#!/usr/bin/env python3
"""Validate private common inputs against live output; emit aggregate facts."""
import argparse, importlib.util, json, re, struct, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location("producer",HERE.parent/"e011aa-rear-bpcabf411-common-producer"/"producer.py")
P=importlib.util.module_from_spec(s);s.loader.exec_module(P)
def main():
    a=argparse.ArgumentParser();a.add_argument("private",type=Path);a.add_argument("--log",default="cdb-observer.raw");args=a.parse_args()
    text=(args.private/args.log).read_text(errors="replace")
    events=[(m[1],int(m[2]),int(m[3])) for m in re.finditer(r"E011AB_(REQ|COMMON|PACK) n=(\d+) req=(\d+)",text)]
    requests=[req for typ,n,req in events if typ=="REQ"]
    assert requests==list(range(1,17)), "request coverage/order incomplete"
    commons=[(n,req) for typ,n,req in events if typ=="COMMON"]
    packs=[(n,req) for typ,n,req in events if typ=="PACK"]
    assert len(commons)==len(packs)==8, "eight common and output samples required"
    assert commons==packs, "common/packer ordering not aligned"
    assert not re.search(r"Memory access error|Syntax error|Unable to read",text), "observer errors"
    selected_match=0
    for n,req in commons:
        c=args.private/"capture"
        r=(c/f"COMMON{n:02}_REGION.bin").read_bytes()
        reserve=(c/f"COMMON{n:02}_RESERVE.bin").read_bytes()
        out=(c/f"PACK{n:02}_OUT.bin").read_bytes()
        assert len(r)==428 and len(reserve)==24 and len(out)==144
        vals=struct.unpack("<107f",r);anchors=list(struct.unpack("<6f",reserve)[1:])
        state=P.calculate(list(vals[82:84]),[[vals[84],vals[86]],[vals[85],vals[87]]],
                          [list(vals[88:93]),list(vals[93:98])],anchors)
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
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
