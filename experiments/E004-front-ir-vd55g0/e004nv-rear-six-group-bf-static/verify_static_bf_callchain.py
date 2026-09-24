#!/usr/bin/env python3
"""Read-only exact-OEM BF ISR status/producer/consumer proof, same SP11 only.

Disassembles ONLY a SHA-pinned private same-machine OEM driver. Emits no
binary bytes, image/DMA addresses, pointer values or optical data.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
DRIVER=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/"
            "qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
KERNEL=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/"
            "sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/"
            "camss-vfe-680.c")
WM=HERE.parent/"e004nr-rear-pix-kernel-source-profile/WM-RESULT.json"
WINDOWS=HERE.parent/"e004ny-rear4k-live-control/RESULT.json"
DRIVER_SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
IMAGE_BASE=0x140000000

def fail(test: bool, message: str):
    if not test:
        raise AssertionError("E004NV_BF_CALLCHAIN_FAIL_CLOSED: "+message)

def selected_instructions(start: int,stop: int):
    s=subprocess.check_output([
        "llvm-objdump","-d",f"--start-address={IMAGE_BASE+start:#x}",
        f"--stop-address={IMAGE_BASE+stop:#x}",str(DRIVER)],text=True)
    rows={}
    pattern=re.compile(r"^([0-9a-f]{9,}):\s+[0-9a-f]{8}\s+([a-z.]+)\s*(.*?)\s*$",re.M)
    for m in pattern.finditer(s):
        rows[int(m.group(1),16)-IMAGE_BASE]=(m.group(2),m.group(3).split("//")[0].strip())
    return rows

def actual_at(ins: dict, rva: int, mn: str, operand: str):
    fail(ins.get(rva)==(mn,operand),
         f"RVA{rva:x}: expected {mn} {operand}, observed {ins.get(rva)}")

def read_pe_rva(data: bytes, rva: int, count: int):
    pe=struct.unpack_from("<I",data,0x3c)[0]
    sections=struct.unpack_from("<H",data,pe+6)[0]
    opt=struct.unpack_from("<H",data,pe+20)[0]
    for i in range(sections):
        sec=pe+24+opt+40*i
        vs,va,raw_len,raw_off=struct.unpack_from("<IIII",data,sec+8)
        if va<=rva and rva+count<=va+raw_len:
            return data[raw_off+rva-va:raw_off+rva-va+count]
    raise AssertionError(f"private driver RVA {rva:x} not file-backed")

def verify():
    data=DRIVER.read_bytes()
    fail(len(data)==376560 and hashlib.sha256(data).hexdigest()==DRIVER_SHA,
         "same-SP11 exact OEM driver hash")
    windows=[
        (0x19fa8,0x1a110),
        (0x1efb8,0x1f19c),
        (0x1fc60,0x1fd2c),
        (0x1d620,0x1d730),
        (0x22298,0x22490),
        (0x23998,0x239c0),
        (0x250a8,0x25174),
        (0x26500,0x265a8),
        (0x27fa8,0x27fcf),
    ]
    instructions={}
    for start,stop in windows:
        chunk=selected_instructions(start,stop)
        fail(not any(addr in instructions for addr in chunk),"overlapping disassembly chunks")
        instructions.update(chunk)
    anchor={
        0x222a0:("mov","w24, w2"),
        0x22384:("str","w8, [x20, #0x349c]"),
        0x2246c:("cmp","w24, w8"),
        0x22474:("cset","w9, hs"),
        0x22478:("str","w9, [x8, #0x678]"),
        0x2247c:("mov","x9, #0xc00"),
        0x22480:("mov","x8, #0x1200"),
        0x22484:("csel","x8, x9, x8, lo"),
        0x1a0a4:("csel","x9, x9, x8, ne"),
        0x1a0ac:("str","x9, [x8, #0x6c0]"),
        0x1a0f4:("add","x8, x8, #0xf90"),
        0x1a0f8:("csel","x9, x9, x8, ne"),
        0x1a100:("str","x9, [x8, #0x6d8]"),
        0x239a0:("ldr","x8, [x24, #0x6d8]"),
        0x239bc:("blr","x15"),
        0x1efe8:("ldr","x23, [x20, #0x8]"),
        0x1eff0:("ldp","w8, w2, [x23, #0x4]"),
        0x1f048:("ubfx","w15, w2, #7, #1"),
        0x1f188:("cbz","w15, 0x14001f19c <.text+0x1e19c>"),
        0x1f190:("mov","w15, #0xf"),
        0x1fc60:("cmp","w8, #0xf"),
        0x1fc8c:("mov","w1, #0x8"),
        0x1fc94:("bl","0x140026460 <.text+0x25460>"),
        0x1fc9c:("cbz","x23, 0x14001fe48 <.text+0x1ee48>"),
        0x1fca4:("mov","w2, #0xf"),
        0x1fcac:("ldr","x8, [x8, #0x6c0]"),
        0x1fcc4:("blr","x15"),
        0x1fcc8:("ldrb","w8, [x19, #0x1c0]"),
        0x1fcdc:("ldrh","w2, [x23, #0x16]"),
        0x1fce0:("ldr","x1, [x23, #0x8]"),
        0x1fce4:("bl","0x140025078 <.text+0x24078>"),
        0x1fce8:("mov","w9, #0x300d"),
        0x1fd14:("mov","w8, #0x1a"),
        0x1fd18:("str","x23, [x19, #0x6a8]"),
        0x1fd20:("str","w8, [x19, #0x520]"),
        0x1fd28:("bl","0x140026340 <.text+0x25340>"),
        0x1d634:("adr","x9, 0x14001d7f8 <.text+0x1c7f8>"),
        0x1d638:("ldrsb","x8, [x9, w2, uxtw]"),
        0x1d710:("ldr","x8, [x0, #0x150]"),
        0x1d714:("ldr","w8, [x8, #0x1270]"),
        0x1d718:("str","w8, [x1, #0x4c]"),
        0x1d720:("ldr","w8, [x8, #0x1200]"),
        0x1d724:("and","w8, w8, #0x1"),
        0x1d728:("strb","w8, [x1, #0x48]"),
        0x2650c:("add","x10, x21, #0x66b"),
        0x26514:("ldr","x9, [x8, x10, lsl #3]"),
        0x27fb0:("mov","w24, #0x300d"),
    }
    for rva,(mn,operands) in anchor.items():
        actual_at(instructions,rva,mn,operands)
    mode0_handler_rva=0x1e000+0xf90
    mode1_handler_rva=0x1c000+0x9d0
    fail(mode0_handler_rva==0x1ef90 and mode1_handler_rva==0x1c9d0,
         "mode-dependent dispatched callback address")
    mode0_event_callback_rva=0x1d000+0x620
    fail(mode0_event_callback_rva==0x1d620,"mode0 per-event status callback")
    jump=read_pe_rva(data,0x1d7f8,25)
    target=0x1d7f8+struct.unpack("<b",jump[15:16])[0]*4
    fail(target==0x1d710,"BF event15 jump table target")
    for name,expected,observed in (
        ("mode0_window",0xc00,0xc00),
        ("client16_CFG0",0xe00+0x100*16,0xc00+0x1200),
        ("client16_ADDR_STATUS0",0xe70+0x100*16,0xc00+0x1270),
        ("scratch_enabled_gate",0x178+0x48,0x1c0),
        ("BF_queued_item",0xf,15),
        ("BF_outstanding_record_port",0x300d,0x300d),
    ):
        fail(expected==observed,name)
    source=KERNEL.read_text()
    for key in (
        "#define VFE680_X1E_BUS_CLIENT_BASE\t\t0x0e00",
        "#define VFE680_X1E_BUS_CLIENT_STRIDE\t\t0x0100",
        "#define VFE680_X1E_BUS_CFG\t\t\t0x00",
        "#define VFE_BUS_ADDR_STATUS0(vfe, c)",
        "(vfe_is_lite(vfe) ? 0x470 : 0xe70) + (c) * 0x100",
        "STATS_BAF\t\t16",
    ):
        fail(key in source,"independent Linux VFE680 BUS register field "+key)
    wm=json.loads(WM.read_text())
    fail(wm["phases"][0]["write_masters"]==wm["phases"][1]["write_masters"],
         "OEM static rear WM config mismatch between live captures")
    for phase in wm["phases"]:
        w=phase["write_masters"][8]
        fail(w["wm"]==16 and w["wm_config"]=="0x00020001",
             "OEM rear WM16 CFG0 not enabled")
    prior=json.loads((HERE/"BF-RESULT.json").read_text())
    win=json.loads(WINDOWS.read_text())
    fail(prior["BF_event_live_during_OEM_rear_recording_observed"] is False,
         "prior BF-event-live evidence falsely promoted")
    fail(win["BF_event_0x0f_live_recording_observed"] is False,
         "Windows 4K frame-handle controls promoted to BF-event proof")
    print("PASS_E004NV_BF_EXACT_OEM_CALLBACK_REGISTRATION_AND_INDIRECT_CALL")
    print("PASS_E004NV_BF_MODE0_INPUT_STATUS_WORD2_BIT7_GENERATES_EVENT0F_FIFO_GROUP8")
    print("PASS_E004NV_BF_MODE0_EVENT_CALLBACK_DIRECT_WM16_CFG0_AND_ADDR_STATUS0")
    print("PASS_E004NV_BF_WM16_CFG0_BIT0_GATES_OUTSTANDING_ITEM_MATCH_PORT300D_NOTIFY")
    print(f"PASS_E004NV_BF_{len(anchor)}_SOURCE_LOCKED_ARM64_INSTRUCTION_ANCHORS")
    print("E004NV_LIVE_REAR_DISPATCH_MODE_AND_BF_EVENT_AND_WM16_DMA_RETIRE_STILL_UNPROVEN")

if __name__=="__main__":
    verify()
