#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,subprocess,struct
from pathlib import Path
import pefile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
AVS=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/surfacecamavs8380.sys")
ISP_SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
AVS_SHA="b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed"
PARENT="29187cbea2f0e749d4773d97565e947a3e4c34fe"

def req(ok,msg):
    if not ok: raise AssertionError("E005L_FAIL_CLOSED "+msg)

def dis(path):
    out=subprocess.check_output(["llvm-objdump","-d",str(path)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):\s+[0-9a-f]{8}\s+([a-z.]+)\s*(.*)$",re.M)
    return {int(m.group(1),16)-0x140000000:(m.group(2),m.group(3).split("//",1)[0].strip()) for m in rx.finditer(out)}

def facts():
    return {
      "schema": "E005l-original-GROUP3-STAT-aggregate-key-tag-export-static-v1",
      "parent_git_revision": "29187cbea2f0e749d4773d97565e947a3e4c34fe",
      "evidence_class": "S_EXACT_OEM_ARM64_STATIC_NO_LIVE_CAMERA_NO_KERNEL_DEBUG",
      "qccamisp8380_sha256": "64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c",
      "surfacecamavs8380_sha256": "b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed",
      "group_ring_producer_rva": "0x26838",
      "group_ring_count": 13,
      "group4_name": "COMBO_STATS",
      "group4_queue_pointer_offset": "0x3378",
      "group8_name": "BF",
      "group8_queue_pointer_offset": "0x3398",
      "producer_uses_same_local_descriptor_source_for_each_selected_group": True,
      "producer_copy_source_is_stack_record": True,
      "producer_input_plus_0x08_diagnostic_name": "requestId",
      "group_ring_plus_0x08_is_direct_copy_of_input_requestId": False,
      "group_ring_plus_0x08_semantics": "opaque queue key",
      "group_ring_plus_0x16_semantics": "opaque 16-bit tag",
      "group4_and_group8_are_separate_rings": True,
      "group4_and_group8_same_descriptor_requires_each_independent_enqueue_success": True,
      "producer_checks_copy_helper_return_before_pending_increment": False,
      "bf_dispatch_group_index": 8,
      "bf_matcher_rva": "0x25078",
      "bf_match_key_offset": "0x08",
      "bf_match_tag_offset": "0x16",
      "group3_sender_rva": "0x26170",
      "group3_sender_pop_index": 4,
      "group3_aggregate_key_offset": "0x08",
      "group3_aggregate_tag_offset": "0x16",
      "group3_packet_key_offset": "0x28",
      "group3_packet_tag_offset": "0x38",
      "avstream_group3_raw_id": "0x19",
      "avstream_group3_normalized_type": 4,
      "avstream_group3_parser_uses_first_active_entry": True,
      "normalized_key_offset": "0x08",
      "normalized_tag_offset": "0x10",
      "stats_metadata_writer_rva": "0x91990",
      "stats_metadata_id": "0x8000000f",
      "stats_metadata_size": "0x8a0",
      "stats_metadata_key_low32_offset": "0x10",
      "stats_metadata_tag_offset": "0x18",
      "usermode_stat_metadata_can_expose_group4_aggregate_key_tag_without_kernel_debug": True,
      "usermode_stat_metadata_alone_proves_group8_bf_dequeue": False,
      "usermode_stat_metadata_key_is_source_proven_ife_requestId": False,
      "usermode_stat_metadata_alone_proves_nonnull_wm16_match": False,
      "same_frame_fifo8_nonnull_wm16_match_proven": False,
      "independent_exact_wm16_irq_ack_dma_iommu_safe_stop_proven": False,
      "native_rear_hardware_isp_runtime_authorized": False,
      "next_gate": "same_owner_frame_group8_FIFO8_nonnull_WM16_match_plus_independent_exact_hw_completion; aggregate STAT key/tag may be observed nonhalting but is not BF proof"
}

def main():
    req(hashlib.sha256(ISP.read_bytes()).hexdigest()==ISP_SHA,"ISP hash")
    req(hashlib.sha256(AVS.read_bytes()).hexdigest()==AVS_SHA,"AVS hash")
    i=dis(ISP); a=dis(AVS)

    # Common group producer: input requestId is logged from input+8, but each
    # ring receives the separately built stack record, source pointer x2=sp.
    for r,op,arg in [
      (0x26860,"mov","x22, x1"),(0x26868,"str","x22, [sp]"),
      (0x2688c,"ldr","x4, [x24, #0x8]"),
      (0x26b48,"strb","w23, [sp, #0x8]"),(0x26b50,"str","wzr, [sp, #0xc]"),
      (0x26f50,"mov","w21, #0x0"),(0x26f80,"add","x8, x21, #0x66b"),
      (0x26f84,"ldr","x22, [x20, x8, lsl #3]"),
      (0x26fb8,"mov","x2, sp"),(0x26fd0,"bl","0x14002c5b0 <.text+0x2b5b0>"),
      (0x26fd4,"ldr","w8, [x22, #0x18]"),(0x26fdc,"str","w8, [x22, #0x18]"),
      (0x27058,"cmp","w21, #0xd")]:
        req(i.get(r)==(op,arg),f"producer anchor {r:x}")
    pe=pefile.PE(str(ISP)); b=ISP.read_bytes()
    off=pe.get_offset_from_rva(0x3b480)
    s=b[off:off+160].split(b"\0",1)[0].decode(errors="replace")
    req("requestId %d" in s and "DAL_ife_process_iq_packet" in s,"producer input+8 requestId diagnostic")
    req(0x66b*8+4*8==0x3378 and 0x66b*8+8*8==0x3398,"group ring pointer arithmetic")

    # GROUP3 sender pops aggregate queue4, then uses aggregate +8/+16 as
    # matcher key/tag and packet fields +28/+38.
    for r,op,prefix in [
      (0x261a4,"mov","w1, #0x4"),(0x261ac,"bl","0x140026460"),
      (0x261b8,"ldrh","w2, [x22, #0x16]"),(0x261c0,"ldr","x1, [x22, #0x8]"),
      (0x261c4,"bl","0x140025078"),
      (0x26234,"ldr","x8, [x22, #0x8]"),(0x26238,"str","x8, [x10, #0x1a8]"),
      (0x2623c,"ldrh","w8, [x22, #0x16]"),(0x26240,"str","x8, [x10, #0x1b8]"),
      (0x262b8,"mov","w8, #0x19")]:
        got=i.get(r); req(got and got[0]==op and got[1].startswith(prefix),f"GROUP3 anchor {r:x}")

    # BF path is a different ring: index8, exact same offsets into its popped
    # entry, matcher 0x25078.
    for r,op,prefix in [
      (0x1fc8c,"mov","w1, #0x8"),(0x1fc94,"bl","0x140026460"),
      (0x1fcdc,"ldrh","w2, [x23, #0x16]"),(0x1fce0,"ldr","x1, [x23, #0x8]"),
      (0x1fce4,"bl","0x140025078")]:
        got=i.get(r); req(got and got[0]==op and got[1].startswith(prefix),f"BF anchor {r:x}")

    # AVStream raw25 first-active GROUP3 entry -> normalized fields.
    for r,op,prefix in [
      (0x8adb0,"ldrb","w8, [x21]"),(0x8adb4,"cmp","w8, #0x1"),
      (0x8adb8,"b.eq","0x14008add0"),
      (0x8addc,"ldr","x8, [x21, #0x28]"),(0x8ade0,"str","x8, [x19, #0x8]"),
      (0x8ade4,"ldr","w8, [x21, #0x38]"),(0x8ade8,"str","w8, [x19, #0x10]"),
      (0x8ae04,"cmp","w22, #0x6")]:
        got=a.get(r); req(got and got[0]==op and got[1].startswith(prefix),f"AVS group3 normalize {r:x}")

    # CompleteFrame preserves notification arg x2 in x24 and passes it as x3
    # to custom metadata writer. Writer exposes normalized key low32/tag.
    for r,op,prefix in [
      (0x18850,"mov","x24, x2"),(0x18b6c,"mov","x3, x24"),
      (0x18bb4,"bl","0x140091990"),
      (0x91a9c,"ldr","x8, 0x140091c80"),
      (0x91aa4,"ldr","x8, [x21]"),(0x91aac,"str","x8, [x19, #0x8]"),
      (0x91ab0,"ldr","w8, [x21, #0x8]"),(0x91ab4,"str","w8, [x19, #0x10]"),
      (0x91ac0,"ldr","w8, [x21, #0x10]"),(0x91ac4,"str","w8, [x19, #0x18]")]:
        got=a.get(r); req(got and got[0]==op and got[1].startswith(prefix),f"metadata anchor {r:x}")
    ap=pefile.PE(str(AVS)); ab=AVS.read_bytes()
    req(struct.unpack_from("<Q",ab,ap.get_offset_from_rva(0x91c80))[0]==0x000008A08000000F,"metadata id/size")

    # Parent source locks must remain conservative.
    pi=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e005i-original-group3-bf-stat-chain-static/RESULT.json").read_text())
    req(pi["group3_sender_uses_aggregate_software_queue_index"]==4,"parent GROUP3 queue4")
    req(pi["same_frame_fifo8_nonnull_wm16_match_proven"] is False,"parent no same-frame match")
    pu=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004pu-original-group8-ring-producer-capacity-static/RESULT.json").read_text())
    req(pu["original_producer_increments_count_after_copy_helper_call_without_result_guard"] is True,"parent unchecked copy return")

    saved=json.loads((HERE/"RESULT.json").read_text())
    req(saved==facts(),"saved conservative facts")
    req(saved["group_ring_plus_0x08_is_direct_copy_of_input_requestId"] is False,"no requestId shortcut")
    req(saved["usermode_stat_metadata_alone_proves_group8_bf_dequeue"] is False,"no BF shortcut")
    req(saved["native_rear_hardware_isp_runtime_authorized"] is False,"rear denied")
    print("PASS_E005L_GROUP3_STAT_EXPOSES_AGGREGATE_KEY_TAG_NOT_BF_QUEUE8_NOT_REQUESTID_NO_DMA_PROOF_REAR_DENIED")

if __name__=="__main__": main()
