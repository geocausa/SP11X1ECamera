#!/usr/bin/env python3
"""Verify source-locked scalar handoff and frame-query metadata; no raw export."""
from pathlib import Path
import hashlib,json,struct
import pefile,capstone
from capstone.arm64 import ARM64_OP_MEM,ARM64_OP_IMM
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
DLL=ROOT.parents[1]/"00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"
SHA="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
def main():
    blob=DLL.read_bytes();assert hashlib.sha256(blob).hexdigest()==SHA
    p=pefile.PE(data=blob);cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);cs.detail=True
    decode=lambda r,n:list(cs.disasm(p.get_data(r,n),r))
    sequence=decode(0x83e01c,24);assert len(sequence)==6
    for lane in range(3):
        read,write=sequence[lane*2:lane*2+2]
        assert read.mnemonic=="ldr" and write.mnemonic=="str"
        a,b=read.operands[1],write.operands[1]
        assert a.type==b.type==ARM64_OP_MEM
        assert (cs.reg_name(a.mem.base),a.mem.disp)==("x21",0x1ec+lane*4)
        assert (cs.reg_name(b.mem.base),b.mem.disp)==("x19",0x30+lane*4)
        assert cs.reg_name(read.operands[0].reg)==cs.reg_name(write.operands[0].reg)=="s16"
    q=decode(0x8528b4,60);setup={}
    for ins in q:
        if ins.mnemonic in ("add","mov") and ins.operands[-1].type==ARM64_OP_IMM:
            setup[ins.address]=(cs.reg_name(ins.operands[0].reg),ins.operands[-1].imm)
    assert setup[0x8528c0]==("w8",10)
    assert setup[0x8528c8]==("x9",0x1a8)
    assert setup[0x8528cc]==("x8",92)
    assert setup[0x8528e4]==("w1",12)
    call=next(x for x in q if x.address==0x8528ec)
    assert call.mnemonic=="bl" and call.operands[0].imm==0x852668
    names={}
    for selector in (12,20):
        ptr=struct.unpack("<Q",p.get_data(0x1048110+selector*8,8))[0]
        names[selector]=p.get_data(ptr-p.OPTIONAL_HEADER.ImageBase,100).split(b"\0")[0].decode()
    assert names[12]=="AECAlgoGetParamBGStatsConfig" and names[20]=="AECAlgoGetParamBEStatsConfig"
    copy=decode(0x73c090,4)[0]
    assert copy.mnemonic=="bl" and copy.operands[0].imm==0xf5d480
    assert any(x.mnemonic=="mov" and cs.reg_name(x.operands[0].reg)=="w2" and x.operands[-1].type==ARM64_OP_IMM and x.operands[-1].imm==0x818 for x in decode(0x73c074,28))
    safe={"experiment":"E011AW","status":"PASS_SOURCE_LOCKED_STATIC_HANDOFF",
        "original_DLL_sha256":SHA,"static_primary_frame_query_selector":12,"static_primary_frame_query_output_type":10,
        "static_primary_frame_query_output_bytes":92,"static_frame_query_output_offset":424,
        "static_frame_query_call_rva":"0x8528EC","static_GetParam_wrapper_rva":"0x852668",
        "primary_scalar_handoff_range":["0x83E01C","0x83E034"],
        "primary_frame_weight_offsets":[492,496,500],"primary_statistics_weight_offsets":[48,52,56],
        "IFE_default_AEC_copy_call_rva":"0x73C090","IFE_default_AEC_copy_bytes":2072,
        "GetParam_selector_names":names,"live_cold_selector_and_cache_lineage_proven":False,
        "cold_weight_numeric_policy_closed":False,"source_profile_independent_materialization_closed":False,
        "runtime_actions_performed":False,"private_bytes_exported":False}
    (HERE/"SOURCE-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps(safe,indent=2))
if __name__=="__main__":main()
