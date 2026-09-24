#!/usr/bin/env python3
"""E004oj: conditional original ISP BF port0x300D stop-zero register-offset math.

Original SHA-pinned private SP11 ARM64 binary is read-only. Export only
source-verified scalar RVAs and conditional arithmetic; not OEM bytes,
disassembly, optics, firmware, DMA pointers or KD material.
"""
import copy
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ISP=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
ANCHORS={
  # Instance window producer: generic IFE base x3 from +0x140, then source
  # chosen 0xC00 (zero mode) or 0x1200 (nonzero mode) bank offset.
 0x22440:("ldr","x3, [x20, #0x140]"),
 0x22444:("cbnz","x3, 0x140022464 <.text+0x21464>"),
 0x22464:("ldr","w8, [x20, #0x349c]"),
 0x2246c:("cmp","w24, w8"),
 0x22470:("add","x8, x20, #0x6b, lsl #12"),
 0x22474:("cset","w9, hs"),
 0x22478:("str","w9, [x8, #0x678]"),
 0x2247c:("mov","x9, #0xc00"),
 0x22480:("mov","x8, #0x1200"),
 0x22484:("csel","x8, x9, x8, lo"),
 0x22488:("add","x8, x8, x3"),
 0x2248c:("str","x8, [x20, #0x150]"),
  # Same 0/nonzero field installs corresponding IFE resource callback.
 0x19fac:("ldr","w8, [x8, #0x678]"),
 0x19fb0:("cmp","w8, #0x0"),
 0x19fd4:("add","x9, x8, #0xf0"),
 0x19fdc:("add","x8, x8, #0x830"),
 0x19fe0:("csel","x9, x9, x8, ne"),
 0x19fe8:("str","x9, [x8, #0x688]"),
  # IFE stop sequence reads the original selected callback and flags zero.
 0x272e4:("ldr","x8, [x25, #0x688]"),
 0x272e8:("mov","w2, #0x0"),
 0x27300:("blr","x15"),
  # In zero-mode original handler, BF port0x300D gets a special code path;
  # for the 0 stop flag w21 is zero independent of 0x300D special mask.
 0x1d850:("mov","w8, #0x300d"),
 0x1d854:("cmp","w8, w22"),
 0x1d860:("b.ne","0x14001d86c <.text+0x1c86c>"),
 0x1d884:("cmp","w23, #0x1"),
 0x1d888:("csel","w21, w8, wzr, eq"),
  # Exact bounded original resource jump table entry 13 (0x300D-0x3000)
  # yields target 0x1DA6C. Validate table bytes from ORIGINAL binary only.
 0x1d904:("sub","w10, w22, #0x3, lsl #12"),
 0x1d908:("cmp","w10, #0x1c"),
 0x1d910:("adr","x9, 0x14001dba4 <.text+0x1cba4>"),
 0x1d914:("ldrsw","x8, [x9, w10, uxtw #2]"),
 0x1d918:("adr","x9, 0x14001da6c <.text+0x1ca6c>"),
 0x1d920:("br","x8"),
 0x1da6c:("ldr","x8, [x19, #0x150]"),
 0x1da70:("mov","x1, #0x1200"),
 0x1da74:("str","w21, [x8, #0x1200]"),
}
def guard(ok,message):
    if not ok:raise AssertionError("E004OJ_FAIL_CLOSED "+message)
def original_file_rva(d,rva,n):
    pe=struct.unpack_from("<I",d,0x3c)[0]
    guard(d[pe:pe+4]==b"PE\0\0" and struct.unpack_from("<H",d,pe+4)[0]==0xaa64,"original ARM64 PE")
    sh=pe+24+struct.unpack_from("<H",d,pe+20)[0]
    for i in range(struct.unpack_from("<H",d,pe+6)[0]):
        o=sh+40*i
        virt,va,rawsize,raw=struct.unpack_from("<IIII",d,o+8)
        if va<=rva and rva+n<=va+rawsize:return d[raw+rva-va:raw+rva-va+n]
    raise AssertionError("original file RVA")
def expected():
    # For mode/state zero, original csel(lo) selects +0xC00, and the BF
    # resource branch writes +0x1200. That is a *register-relative write*,
    # not proof of physical DMA quiescence or even selected live rear mode.
    return {
     "schema":"sp11-e004oj-original-IFE-conditional-BF-port-zero-write-register-offset-static-v1",
     "parent_git_revision":"eae01b8655fb77c7bb3daa59ccd9f7f3fd37ff6c",
     "original_same_SP11_OEM_ISP_SHA256":SHA,
     "original_ARM64_instruction_anchors":len(ANCHORS),
     "IFE_original_base_pointer_context_offset":"0x140",
     "IFE_selected_resource_register_window_context_offset":"0x150",
     "IFE_zero_state_register_window_extra_offset":"0xc00",
     "IFE_nonzero_state_register_window_extra_offset":"0x1200",
     "IFE_selected_callback_zero_state_RVA":"0x1d830",
     "IFE_selected_callback_nonzero_state_RVA":"0x1c0f0",
     "IFE_stop_loop_zero_flag_instruction_RVA":"0x272e8",
     "BF_resource_ID":"0x300d",
     "BF_resource_switch_table_RVA":"0x1dba4",
     "BF_resource_switch_index":13,
     "BF_resource_switch_target_RVA":"0x1da6c",
     "BF_resource_target_window_register_offset":"0x1200",
     "BF_zero_state_total_original_IFE_base_relative_register_offset":"0x1e00",
     "BF_zero_stop_flag_register_value":0,
     "earlier_independent_static_BF_port_and_WM16_CFG0_offset_agree":True,
     "actual_Windows_rear_4k_selected_zero_state_handler_observed":False,
     "register_window_x3_exclusively_identified_as_live_rear_VFE1_MMIO_base":False,
     "static_zero_CFG0_write_proves_WM16_dma_legal_retirement":False,
     "BF_IRQ_event_0x0f_and_FIFO8_live_completion_observed":False,
     "Linux_native_rear_4k_processed_ISP_optical_frame_proven":False,
     "Golden_camera_hardware_or_boot_modified":False,
     "original_private_OEM_binaries_disassembly_DMAPTR_optical_KD_exported":False,
    }
def check_result(x):
    guard(x==expected(),"saved result vs strict static-boundary contract")
if __name__=="__main__":
    d=ISP.read_bytes()
    guard(hashlib.sha256(d).hexdigest()==SHA,"original private same-SP11 SHA")
    orig=subprocess.check_output(["llvm-objdump","-d",str(ISP)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    asm={int(m.group(1),16)-BASE:(m.group(2),m.group(3).split("//",1)[0].strip()) for m in rx.finditer(orig)}
    for rva,want in ANCHORS.items():
        guard(asm.get(rva)==want,"original ARM64 RVA0x%x %s != %s"%(rva,asm.get(rva),want))
    idx=0x300d-0x3000
    offset=struct.unpack("<i",original_file_rva(d,0x1dba4+idx*4,4))[0]
    guard(0x1da6c+offset*4==0x1da6c,"BF0x300D switch table selected target")
    prev=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004nv-rear-six-group-bf-static/BF-RESULT.json").read_text())
    guard(prev["BF_static_dispatch"]["BF_group_client_resource_port"]=="0x300d" and
          prev["BF_static_dispatch"]["driver_event_id"]=="0x0f" and
          prev["BF_event_live_during_OEM_rear_recording_observed"] is False,
          "independent original BF resource/source static")
    # Also original E004nv BF static source reported WINDOW=VFE+0xC00,
    # WM16 CFG0 at original VFE+0x1E00. Never equate CFG0 zero to DONE.
    guard(0xc00+0x1200==0x1e00,"source-derived conditional register window arithmetic")
    r=expected();p=HERE/"RESULT.json"
    if p.exists():guard(json.loads(p.read_text())==r,"saved scalar source mismatch")
    else:p.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    neg=(
      ("wrong_mode_base",lambda z:z.__setitem__("IFE_zero_state_register_window_extra_offset","0x1200")),
      ("wrong_handler",lambda z:z.__setitem__("IFE_selected_callback_zero_state_RVA","0x1c0f0")),
      ("wrong_port",lambda z:z.__setitem__("BF_resource_ID","0x300c")),
      ("wrong_jump_table",lambda z:z.__setitem__("BF_resource_switch_target_RVA","0x1da70")),
      ("wrong_register_offset",lambda z:z.__setitem__("BF_resource_target_window_register_offset","0x1e00")),
      ("wrong_total",lambda z:z.__setitem__("BF_zero_state_total_original_IFE_base_relative_register_offset","0x2400")),
      ("wrong_stop_zero",lambda z:z.__setitem__("BF_zero_stop_flag_register_value",1)),
      ("fake_proven_live_mode",lambda z:z.__setitem__("actual_Windows_rear_4k_selected_zero_state_handler_observed",True)),
      ("fake_MMIO_mapping",lambda z:z.__setitem__("register_window_x3_exclusively_identified_as_live_rear_VFE1_MMIO_base",True)),
      ("fake_safe_dma",lambda z:z.__setitem__("static_zero_CFG0_write_proves_WM16_dma_legal_retirement",True)),
      ("fake_live_BF",lambda z:z.__setitem__("BF_IRQ_event_0x0f_and_FIFO8_live_completion_observed",True)),
      ("fake_linux_rear",lambda z:z.__setitem__("Linux_native_rear_4k_processed_ISP_optical_frame_proven",True)),
      ("fake_golden",lambda z:z.__setitem__("Golden_camera_hardware_or_boot_modified",True)),
      ("fake_OEM_export",lambda z:z.__setitem__("original_private_OEM_binaries_disassembly_DMAPTR_optical_KD_exported",True)),
    )
    for name,fn in neg:
        m=copy.deepcopy(r);fn(m)
        try:check_result(m)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004OJ_NEGATIVE_FAILED_OPEN "+name)
    print(f"PASS_E004OJ_SOURCE_LOCKED_BF_0x300D_ZERO_WRITES_WM16_CFG0_MATCH_"
          f"{len(ANCHORS)}_ARM64_ANCHORS_{len(neg)}_NEGATIVE_TESTS_"
          "NO_LIVE_BF_DMA_STOP_OR_NATIVE_REAR4K_CLAIM_GOLDEN_SAFE")
