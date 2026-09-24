#!/usr/bin/env python3
"""E004py: compare ORIGINAL physical Windows front/rear CSID1 snapshots.

Read original front raw from SAME SP11 repo; read verified rear scalar
evidence from E004pi. Never write/export raw MMIO, OEM files, IOVAs or pixels.
P = existing original snapshot at two historical capture windows per mode.
NOT frame-by-frame identity, IRQ causality or WM16 DMA/IOMMU completion.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
FRONT=ROOT/"experiments/E003-front-imx681-cphy/e003g-windows-csid-vfe-oracle"
REAR=ROOT/"experiments/E004-front-ir-vd55g0/e004pi-original-live-rear-csid-bf-bit7-wm16-fence-offline"
RAW_SHA="fd8edcee46e794dffa0e2305331f19d4e9d2cd5b9ba5197484aa1cc7fa6c6fca"
PARSER_SHA="e45c28890f1c1025321b4b4240b8305f18b2f9a1bee3a580bb4bbd8e23873aab"
REAR_RESULT_SHA="2d674a58e860aa9fb7adbdb2ad2747ec1a072376b1ad26e9a2f7b63edb319c47"
PARENT="521b7cbe6e90e64b0f0c15e8d6de315b21075add"

def require(ok, why):
    if not ok: raise AssertionError("E004PY_FAIL_CLOSED "+why)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def measured():
    raw=FRONT/"raw/E003G_ROUTE_ORACLE_20260828.log"
    parser=FRONT/"extract_route_oracle.py"
    require(digest(raw)==RAW_SHA,"front original raw physical source digest")
    require(digest(parser)==PARSER_SHA,"front original physical source parser digest")
    spec=importlib.util.spec_from_file_location("E004PY_front_source_readonly",parser)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    text=raw.read_bytes().decode("utf-16",errors="replace")
    front=[]
    for phase in mod.PHASES:
        csid=mod.parse_dump(text,phase,"csid1")
        vfe=mod.parse_dump(text,phase,"vfe1")
        require(len(csid)==2048 and len(vfe)==4096,"complete original physical regions "+phase)
        def reg(d,base,offset):
            return d[base+offset]
        status=reg(csid,0x0acb9000,0x8c)
        mask=reg(csid,0x0acb9000,0x90)
        if phase in ("LIVE1","LIVE2"):
            require((status,mask)==(0x271,0x1ffff),"front live mode status and mask "+phase)
            require(reg(vfe,0x0ac71000,0x1e00)==0x10,"front WM16 disabled "+phase)
            require(reg(vfe,0x0ac71000,0xc28)==0 and
                    reg(vfe,0x0ac71000,0xc2c)==0,"front sampled BUS IRQ status "+phase)
            require(reg(vfe,0x0ac71000,0xc18)==0xd0000000,"front sampled BUS IRQ mask "+phase)
            front.append({
                "phase":phase,
                "csid1_buf_done_status":f"0x{status:08x}",
                "csid1_buf_done_mask":f"0x{mask:08x}",
                "csid1_bf_bit7_set":bool(status&0x80),
                "vfe1_wm16_cfg0":"0x00000010",
                "vfe1_wm16_enabled":False,
                "vfe1_bus_status0":"0x00000000",
                "vfe1_bus_status1":"0x00000000",
            })
        else:
            require(status==mask==0x80000000,
                    "front inactive phase sentinel must NOT be interpreted as IRQ "+phase)
    require(len(front)==2,"two distinct front original live phases")
    d=REAR/"RESULT.json"
    require(digest(d)==REAR_RESULT_SHA,"earlier verified rear Windows physical scalar evidence unchanged")
    rear=json.loads(d.read_text())
    require(rear["physical_evidence_class"]==
            "P_existing_original_Windows_REGISTER_SNAPSHOTS_NOT_EVENT_OR_DMA_FENCE",
            "rear original physical scope")
    require(rear["original_per_frame_FIFO8_group8_matching_WM16_DMA_completion_observed"] is False,
            "rear earlier evidence does not prove WM16 DMA")
    require(len(rear["live_snapshots"])==2,"two separately captured rear live windows")
    measurements=[]
    for f,r in zip(front,rear["live_snapshots"]):
        require(f["phase"]==r["phase"],"front/rear correspond to same NAMED phase not same session")
        fs=int(f["csid1_buf_done_status"],16)
        rs=int(r["csid1_buf_done_status"],16)
        fm=int(f["csid1_buf_done_mask"],16)
        rm=int(r["csid1_buf_done_mask"],16)
        require((fs,rs,fs^rs)==(0x271,0x2f1,0x80),"only CSID1 BF bit7 differs in sampled statuses")
        require(fm==rm==0x1ffff and bool(fm&0x80),"same bit7 unmasked in both modes")
        require(not f["csid1_bf_bit7_set"] and r["csid1_buf_done_status_bit7_set"] is True,
                "front sampled BF bit clear; rear sampled BF bit set")
        require(f["vfe1_wm16_enabled"] is False and
                r["vfe1_wm16_enabled"] is True and
                int(r["vfe1_wm16_cfg0"],16)==0x20001,
                "WM16 enabled only in both rear samples")
        require(f["vfe1_bus_status0"]==r["vfe1_bus_status0"]=="0x00000000" and
                f["vfe1_bus_status1"]==r["vfe1_bus_status1"]=="0x00000000",
                "BUS IRQ zeros at sample instants not verified all-frame completion")
        measurements.append({
            "named_phase":f["phase"],
            "front_original_camera":"IMX681_FRONT",
            "rear_original_camera":"OV13858_REAR",
            "front_csid1_buf_done_status":f["csid1_buf_done_status"],
            "rear_csid1_buf_done_status":r["csid1_buf_done_status"],
            "xor_front_rear_csid1_buf_done_status":"0x00000080",
            "both_csid1_buf_done_mask":"0x0001ffff",
            "front_vfe1_wm16_cfg0":f["vfe1_wm16_cfg0"],
            "rear_vfe1_wm16_cfg0":r["vfe1_wm16_cfg0"],
            "both_vfe1_bus_status0_at_sample":"0x00000000",
            "both_vfe1_bus_status1_at_sample":"0x00000000",
        })
    require(len(measurements)==2,"two real source-measured per-camera phase comparisons")
    return measurements

def facts(m):
    return {
       "schema":"E004py-SP11-original-Windows-front-rear-physical-CSID1-BF-bit7-comparison-v1",
       "parent_git_revision":PARENT,
       "evidence_tier":"P_ORIGINAL_TWO_FRONT_AND_TWO_REAR_PHYSICAL_SNAPSHOTS_NOT_PER_FRAME_IRQ_DMA",
       "front_original_windows_physical_capture_date":"2026-08-28",
       "rear_original_windows_physical_capture_date":"2026-09-23",
       "front_private_original_KD_snapshot_SHA256":RAW_SHA,
       "rear_existing_verified_scalar_RESULT_sha256":REAR_RESULT_SHA,
       "same_SP11_CSID1_and_VFE1_shared_by_front_and_rear":True,
       "front_and_rear_snapshots_are_same_session_or_same_frame":False,
       "front_live_snapshots":2,
       "rear_live_snapshots":2,
       "sampled_front_BF_bit7_clear_rear_BF_bit7_set_with_both_masks_enabled":True,
       "sampled_front_WM16_disabled_rear_WM16_enabled":True,
       "only_bit7_differs_between_front_and_rear_recorded_CSID_BUF_DONE_status_words":True,
       "physical_snapshot_proves_all_front_BF_bit7_events_are_always_absent":False,
       "physical_snapshot_proves_BF_IRQ_same_frame_WM16_buffer_completed":False,
       "physical_snapshot_proves_FIFO8_nonnull_outstanding_WM16_buffer_match":False,
       "physical_snapshot_proves_HW_BUS_DMA_IOMMU_quiescence":False,
       "per_owner_dynamic_native_BF_mode_evidence_producer_implemented":False,
       "native_rear_hardware_ISP_runtime_authorized":False,
       "Golden_kernel_or_accepted_CAMSS_modified":False,
       "private_original_KD_logs_OEM_binaries_frame_pixels_exported_in_this_stage":False,
       "physical_register_phase_comparisons":m,
       "next_gate":"owner_frame_bound_true_native_BF_IRQ_event_FIFO8_NONNULL_WM16_match_and_independent_exact_DMA_IOMMU_safe_stop"
    }

def main():
    m=measured()
    parent=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004px-bf-owner-handoff-token-uniqueness-isolated/RESULT.json").read_text())
    require(parent["native_rear_hardware_ISP_runtime_authorized"] is False,
            "last native ring remains unarmed")
    saved=json.loads((HERE/"RESULT.json").read_text())
    result=facts(m)
    require(saved==result,"result facts must be mechanically recomputed from original capture")
    negatives=0
    for k,v in saved.items():
        mutant=copy.deepcopy(saved)
        if isinstance(v,bool): mutant[k]=not v
        elif isinstance(v,int): mutant[k]=v+1
        elif isinstance(v,str): mutant[k]="INVALID_MUTATION"
        elif isinstance(v,list): mutant[k]=[{"invalid":"mutation"}]
        else: mutant[k]={}
        try:require(mutant==result,"mutant "+k)
        except AssertionError: negatives+=1
        else:raise AssertionError("E004PY_MUTATION_FAIL_OPEN "+k)
    print("PASS_E004PY_2_FRONT_2_REAR_ORIGINAL_PHYSICAL_WINDOWS_CSID_BF_BIT7_ONLY_STATUS_DIFFERENCE_WM16_DISABLED_VS_ENABLED_%d_RESULT_MUTANTS_NO_SAME_FRAME_DMA_PROOF_REAR_DENIED"%negatives)

if __name__=="__main__":main()
