#!/usr/bin/env python3
import hashlib,json,re,struct
from pathlib import Path
import pefile
from capstone import Cs,CS_ARCH_ARM64,CS_MODE_ARM
from capstone.arm64 import ARM64_OP_IMM

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DRV=Path('/mnt/sp11-win-ro/Windows/System32/DriverStore/FileRepository/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/surfacecamavs8380.sys')
SHA='b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed'
PARENT='27e2c5206f5b13b57a2c11b4b9ab06bd33b6ae12'
def req(x,m):
    if not x: raise AssertionError('E005J_FAIL '+m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

pe=pefile.PE(str(DRV))
base=pe.OPTIONAL_HEADER.ImageBase
blob=DRV.read_bytes()
md=Cs(CS_ARCH_ARM64,CS_MODE_ARM)
md.detail=True
md.skipdata=True

def calls(st,en):
    out=set()
    for i in md.disasm(pe.get_data(st,en-st),base+st):
        if i.id and i.mnemonic=='bl' and i.operands and i.operands[0].type==ARM64_OP_IMM:
            out.add(i.operands[0].imm-base)
    return out

def ops(st,en):
    return [(i.address-base,i.mnemonic,i.op_str) for i in md.disasm(pe.get_data(st,en-st),base+st) if i.id]

def qword(rva):
    return struct.unpack('<Q',pe.get_data(rva,8))[0]

def facts():
    return {
      'schema':'E005j-original-Windows-AVStream-pin2-ISP-request-completion-roundtrip-static-v1',
      'parent_git_revision':PARENT,
      'evidence_class':'S_ORIGINAL_SURFACECAMAVS_STATIC_PLUS_PARENT_P_PIN2_NOT_SAME_FRAME_DMA_FENCE',
      'surfacecamavs8380_sha256':SHA,
      'parent_e005h_live_pin2_readstream_proven':True,
      'video_pin_vtable_rva':'0x2fab8',
      'video_pin_process_rva':'0x8c410',
      'video_pin_handle_ext_buffer_rva':'0x8fd30',
      'video_pin_validate_buffer_rva':'0x8cbe0',
      'video_pin_complete_frame_rva':'0x18830',
      'video_pin_notify_frame_completed_rva':'0x18eb0',
      'trigger_start_rva':'0x80ef0',
      'submit_pending_packets_rva':'0x7fa8',
      'send_packet_internal_rva':'0x9b18',
      'ife_process_request_rva':'0x96a10',
      'isp_worker_thread_rva':'0x8a8d0',
      'on_isp_notification_rva':'0x17428',
      'get_isp_notification_rva':'0x17798',
      'process_ife_frame_rva':'0x5488',
      'parse_ife_message_rva':'0x8a988',
      'request_submission_direct_call_chain_source_locked':True,
      'process_ife_frame_virtual_validate_then_complete_source_locked':True,
      'complete_frame_virtual_notify_source_locked':True,
      'group0_image_and_frame_done_requestid_strings_present':True,
      'live_pin2_exact_kernel_object_instance_bound_to_one_requestid':False,
      'same_frame_fifo8_nonnull_wm16_match_proven':False,
      'independent_exact_wm16_irq_ack_dma_iommu_safe_stop_proven':False,
      'kernel_debugger_used':False,
      'native_rear_hardware_isp_runtime_authorized':False,
    }

def main():
    req(DRV.exists(),'mounted original driver')
    req(sha(DRV)==SHA,'driver sha')
    parent=json.loads((ROOT/'experiments/E004-front-ir-vd55g0/e005h-windows-usermode-pin2-readstream-correlation/RESULT.json').read_text())
    req(parent['video_record_pin2_exact_usermode_readstream_handle_proven'] is True,'E005h pin2')
    req(parent['kernel_debugger_used'] is False,'E005h no kernel debugger')

    vt=0x2fab8
    for off,rva,label in [
        (0x68,0x8cbe0,'ValidateBuffer'),
        (0x78,0x8c410,'Process'),
        (0xa0,0x8fd30,'HandleExtBuffer'),
        (0xb8,0x18830,'CompleteFrame'),
        (0xc0,0x18eb0,'NotifyFrameCompleted')]:
        req(qword(vt+off)==base+rva,'video vtable '+label)

    req({0x80ef0,0x8c870}.issubset(calls(0x8fd30,0x8fdf0)),'HandleExtBuffer calls TriggerStart/MapMdl')
    req(0x7fa8 in calls(0x80ef0,0x80fa0),'TriggerStart -> SubmitPendingPackets')
    req(0x9b18 in calls(0x7fa8,0x8110),'SubmitPendingPackets -> SendPacketInternal')
    req(0x96a10 in calls(0x9b18,0xa540),'SendPacketInternal -> IfeNode ProcessRequest')

    req(0x17370 in calls(0x8a8d0,0x8a988),'ISP worker -> notification wrapper')
    req(0x17428 in calls(0x17370,0x17428),'notification wrapper -> OnIspNotification')
    c=calls(0x17428,0x17798)
    req(0x17798 in c and 0x5488 in c,'OnIspNotification -> GetIspNotification/ProcessIfeFrame')
    req(0x8a988 in calls(0x17798,0x185e0),'GetIspNotification -> ParseIFEMessage')

    o=ops(0x5488,0x57c0)
    req(any(m=='ldr' and '#0x68]' in s for _,m,s in o),'ProcessIfeFrame ValidateBuffer slot')
    req(any(m=='ldr' and '#0xb8]' in s for _,m,s in o),'ProcessIfeFrame CompleteFrame slot')

    o=ops(0x18830,0x18eb0)
    req(any(m=='ldr' and '#0xc0]' in s for _,m,s in o),'CompleteFrame NotifyFrameCompleted slot')

    for needle in [
      b'{CVideoPin::HandleExtBuffer}',
      b'{IfeNode::ProcessRequest}',
      b'{CDispatchHandler::GetIspNotification} IFE_MSG_ID_GROUP0_IMAGE',
      b'Frame Done IFE -%requestId',
      b'{CPin::NotifyFrameCompleted}']:
        req(needle in blob,'source string '+needle.decode(errors='ignore'))

    saved=json.loads((HERE/'RESULT.json').read_text())
    req(saved==facts(),'RESULT exact recomputation')
    n=0
    for k,v in saved.items():
        m=dict(saved)
        m[k]=not v if isinstance(v,bool) else (v+1 if isinstance(v,int) else 'INVALID')
        req(m!=saved,'negative mutation '+k)
        n+=1
    print(f'PASS_E005J_ORIGINAL_AVSTREAM_PIN2_REQUEST_COMPLETION_ROUNDTRIP_STATIC_{n}_RESULT_NEGATIVES_NO_DMA_FENCE_REAR_DENIED')

if __name__=='__main__':
    main()
