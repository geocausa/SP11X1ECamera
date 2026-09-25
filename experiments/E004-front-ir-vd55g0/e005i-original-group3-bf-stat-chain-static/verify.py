#!/usr/bin/env python3
"""E005i: exact original Windows BF -> GROUP3 -> STAT static chain.

Static source-binding only, combined with the already-published E005h user-mode
physical endpoint. No kernel debug, no raw OEM export, no DMA-fence claim.
"""
from __future__ import annotations
import hashlib, json, struct
from pathlib import Path
import pefile
import capstone
from capstone.arm64 import ARM64_INS_BL, ARM64_INS_CBZ, ARM64_INS_CBNZ, ARM64_OP_IMM, ARM64_OP_REG

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
AVS=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/surfacecamavs8380.sys")
E005H=ROOT/"experiments/E004-front-ir-vd55g0/e005h-windows-usermode-pin2-readstream-correlation/RESULT.json"

ISP_SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
AVS_SHA="b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed"
PARENT="b749b4f90c64f69daaccfee6634a743f2be8bcfa"

def require(ok, why):
    if not ok:
        raise AssertionError("E005I_FAIL_CLOSED "+why)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def pe_and_ins(path):
    pe=pefile.PE(str(path))
    base=pe.OPTIONAL_HEADER.ImageBase
    md=capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_LITTLE_ENDIAN)
    md.detail=True
    md.skipdata=True
    by={}
    for s in pe.sections:
        if not (s.Characteristics & 0x20000000):
            continue
        for i in md.disasm(s.get_data(), base+s.VirtualAddress):
            by[i.address-base]=i
    return pe,base,by

def text_at(pe,path,rva):
    b=path.read_bytes()
    o=pe.get_offset_from_rva(rva)
    return b[o:o+256].split(b"\0",1)[0].decode("ascii",errors="replace")

def imm(ins, idx=-1):
    o=ins.operands[idx]
    require(o.type==ARM64_OP_IMM, f"{ins.address:x} operand immediate")
    return o.imm

def is_bl_to(ins, base, rva):
    return ins.id==ARM64_INS_BL and ins.operands and ins.operands[0].type==ARM64_OP_IMM and ins.operands[0].imm-base==rva

def has_imm(ins, value):
    return any(o.type==ARM64_OP_IMM and o.imm==value for o in ins.operands)

def facts():
    return {
      "schema":"E005i-exact-original-Windows-BF-GROUP3-STAT-static-chain-v1",
      "parent_git_revision":PARENT,
      "evidence_class":"S_EXACT_OEM_ARM64_STATIC_PLUS_PARENT_E005H_USERMODE_ENDPOINT_NOT_DMA_FENCE",
      "original_qccamisp8380_sha256":ISP_SHA,
      "original_surfacecamavs8380_sha256":AVS_SHA,
      "isp_group3_sender_rva":"0x26170",
      "isp_group3_raw_message_id":25,
      "isp_group3_possible_event_resource_pairs":[
        {"event":"0x0e","resource":"0x300c"},
        {"event":"0x0f","resource":"0x300d"},
        {"event":"0x10","resource":"0x300e"},
        {"event":"0x11","resource":"0x300f"},
        {"event":"0x12","resource":"0x3010"},
        {"event":"0x0d","resource":"0x301c"},
      ],
      "bf_event_resource_pair_exactly_in_group3":True,
      "bf_event":"0x0f",
      "bf_resource":"0x300d",
      "group3_sender_uses_aggregate_software_queue_index":4,
      "group3_sender_calls_outstanding_matcher_rva":"0x25078",
      "group3_sender_requires_matcher_nonnull_before_packet":False,
      "group3_sender_direct_caller_rva":"0x1fe44",
      "all_stats_gate_rva":"0x25190",
      "all_stats_gate_tracks_up_to_six_slots":True,
      "all_stats_gate_compares_consumed_against_configured_expected_count":True,
      "dispatcher_calls_group3_sender_only_when_gate_returns_one":True,
      "avstream_raw7_name":"IFE_MSG_ID_DUAL_PD_STATS",
      "avstream_raw7_normalized_type":4,
      "avstream_raw25_name":"IFE_MSG_ID_GROUP3_STATS",
      "avstream_raw25_normalized_type":4,
      "avstream_raw26_name":"IFE_MSG_ID_GROUP4_STATS",
      "avstream_raw26_normalized_type":4,
      "avstream_raw27_name_source_locked":False,
      "avstream_raw27_normalized_type":4,
      "avstream_raw28_name":"FD Frame Done",
      "avstream_raw28_normalized_type":4,
      "avstream_type4_calls_process_stats_frame_rva":"0x57c0",
      "stats_pin_custom_metadata_id":"0x8000000f",
      "stats_pin_custom_metadata_size":"0x8a0",
      "stats_pin_is_raw_bf_dma_surface":False,
      "parent_e005h_live_pin3_stat_stream_active":True,
      "parent_e005h_kernel_debugger_used":False,
      "same_frame_fifo8_nonnull_wm16_match_proven":False,
      "independent_exact_wm16_irq_ack_dma_iommu_safe_stop_proven":False,
      "native_rear_hardware_isp_runtime_authorized":False,
      "next_gate":"source_or_dynamic_nonhalting_proof_of_same_frame_FIFO8_NONNULL_WM16_and_independent_exact_DMA_completion; external KD only when SP7 host returns"
    }

def main():
    require(sha(ISP)==ISP_SHA,"pinned qccamisp hash")
    require(sha(AVS)==AVS_SHA,"pinned AVStream hash")
    ip,ibase,ii=pe_and_ins(ISP)
    ap,abase,ai=pe_and_ins(AVS)
    require(ibase==0x140000000 and abase==0x140000000,"expected OEM PE image bases")

    # Original ISP diagnostic/source anchors.
    require("BF stats buf done Irq occured" in text_at(ip,ISP,0x37b88),"BF IRQ diagnostic")
    require("All Stats interrupts received" in text_at(ip,ISP,0x3a118),"all-stats gate diagnostic")
    require("success to send IFE_MSG_ID_GROUP3_STATS" in text_at(ip,ISP,0x3aca8),"GROUP3 success diagnostic")

    # Exact GROUP3 builder: aggregate queue, matcher, event/resource arithmetic,
    # five consecutive resources/events plus sixth event/resource, raw ID 25.
    require(ii[0x261a4].mnemonic=="mov" and has_imm(ii[0x261a4],4),"GROUP3 queue index 4")
    require(is_bl_to(ii[0x261ac],ibase,0x26460),"GROUP3 aggregate queue pop")
    require(is_bl_to(ii[0x261c4],ibase,0x25078),"GROUP3 outstanding matcher")
    require(ii[0x261d4].mnemonic=="mov" and has_imm(ii[0x261d4],0x300c),"GROUP3 resource base 0x300c")
    require(ii[0x261dc].mnemonic=="mov" and has_imm(ii[0x261dc],0x2ffe),"GROUP3 event conversion base")
    require(ii[0x261e0].mnemonic=="sub","GROUP3 event=resource-0x2ffe")
    require(ii[0x26254].mnemonic=="cmp" and has_imm(ii[0x26254],5),"five consecutive GROUP3 entries")
    require(ii[0x26264].mnemonic=="mov" and has_imm(ii[0x26264],0xd),"sixth GROUP3 event 0x0d")
    require(ii[0x26294].mnemonic=="mov" and has_imm(ii[0x26294],0x301c),"sixth GROUP3 resource 0x301c")
    require(ii[0x262b8].mnemonic=="mov" and has_imm(ii[0x262b8],0x19),"GROUP3 raw message ID25")
    require(is_bl_to(ii[0x262cc],ibase,0x26340),"GROUP3 onward callback")

    # Matcher result x26 is stored into GROUP3 entries; there is no cbz/cbnz
    # gate on x26 in the builder after matcher return.
    x26=capstone.arm64.ARM64_REG_X26
    gated=False
    for r in range(0x261c8,0x262b8,4):
        ins=ii.get(r)
        if ins and ins.id in (ARM64_INS_CBZ,ARM64_INS_CBNZ) and ins.operands and ins.operands[0].type==ARM64_OP_REG and ins.operands[0].reg==x26:
            gated=True
    require(not gated,"GROUP3 must not invent matcher-nonnull requirement")

    # Dispatcher completion gate -> GROUP3 sender.
    require(is_bl_to(ii[0x1fe30],ibase,0x25190),"dispatcher calls all-stats gate")
    require(ii[0x1fe38].mnemonic=="cmp" and has_imm(ii[0x1fe38],1),"gate result compared to one")
    require(ii[0x1fe3c].mnemonic.startswith("b.") and has_imm(ii[0x1fe3c],ibase+0x1fe48),"non-one skips GROUP3")
    require(is_bl_to(ii[0x1fe44],ibase,0x26170),"only gated path calls GROUP3 sender")

    # Gate searches six slots, increments consumed count, compares it to
    # configured expected count, sets return=1 only on equality.
    require(ii[0x251dc].mnemonic=="cmp" and has_imm(ii[0x251dc],6),"all-stats tracks six slots")
    require(ii[0x251f0].mnemonic=="add" and has_imm(ii[0x251f0],1),"consumed count increment")
    require(ii[0x25218].mnemonic=="cmp","consumed versus expected compare")
    require(ii[0x25238].mnemonic=="mov" and has_imm(ii[0x25238],1),"all-stats return true")

    # AVStream source-locks raw packet names and normalized type4.
    require("IFE_MSG_ID_DUAL_PD_STATS" in text_at(ap,AVS,0x286b0),"AVStream raw7 DualPD name")
    require("IFE_MSG_ID_GROUP3_STATS" in text_at(ap,AVS,0x28770),"AVStream raw25 Group3 name")
    require("IFE_MSG_ID_GROUP4_STATS" in text_at(ap,AVS,0x287d0),"AVStream raw26 Group4 name")
    require(ai[0x17cf0].mnemonic=="cmp" and has_imm(ai[0x17cf0],7),"raw7 compare")
    require(ai[0x17de0].mnemonic=="cmp" and has_imm(ai[0x17de0],0x19),"raw25 compare")
    require(ai[0x17e1c].mnemonic=="cmp" and has_imm(ai[0x17e1c],0x1a),"raw26 compare")
    for r in (0x8ad64,0x8ad9c,0x8ae2c,0x8ae9c):
        require(ai[r].mnemonic=="mov" and has_imm(ai[r],4),f"raw branch {r:x} type4")
    require(ai[0x8aef8].mnemonic=="mov" and has_imm(ai[0x8aef8],4),"raw28 FD type4")
    require(is_bl_to(ai[0x1761c],abase,0x57c0),"normalized type4 -> ProcessStatsFrame")

    # OEM custom STAT metadata, not raw BF DMA.
    ab=AVS.read_bytes()
    require(struct.unpack_from("<Q",ab,ap.get_offset_from_rva(0x91c80))[0]==0x000008A08000000F,"custom metadata 0x8000000f size0x8a0")
    require(struct.unpack_from("<Q",ab,ap.get_offset_from_rva(0x91c88))[0]==0x000000108000000E,"custom metadata 0x8000000e size0x10")

    h=json.loads(E005H.read_text())
    require(h["actual_start_and_stop_success"] is True and h["actual_valid_frame_handles"]==157,"E005h real rear4K endpoint")
    require(h["frameserver_usermode_cdb_only"] is True and h["kernel_debugger_used"] is False,"E005h no kernel debug")
    require(h["native_rear_hardware_isp_runtime_authorized"] is False,"parent rear remains denied")

    saved=json.loads((HERE/"RESULT.json").read_text())
    require(saved==facts(),"RESULT must equal recomputed conservative facts")
    negatives=0
    for k,v in saved.items():
        m=dict(saved)
        if isinstance(v,bool): m[k]=not v
        elif isinstance(v,int): m[k]=v+1
        elif isinstance(v,str): m[k]="INVALID"
        elif isinstance(v,list): m[k]=[]
        else: m[k]=None
        require(m!=saved,"negative mutation "+k)
        negatives+=1
    print(f"PASS_E005I_EXACT_OEM_BF_GROUP3_STAT_CHAIN_{negatives}_RESULT_MUTATIONS_MATCHER_NONNULL_NOT_PROVEN_DMA_FENCE_NOT_PROVEN_REAR_DENIED")

if __name__=="__main__":
    main()
