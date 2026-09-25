#!/usr/bin/env python3
import hashlib
import json
import struct
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULT = json.loads((HERE / "RESULT.json").read_text())
WIN = Path("/mnt/sp11-win-ro")
DERIVED = WIN / "Users/Geoca/Documents/SP11-Camera-E005L-CompletedStreamHeader-20260925/E005L-DERIVED-SAFE-SCALARS.json"
KS = WIN / "Windows/System32/drivers/ks.sys"
AVS = WIN / "Windows/System32/DriverStore/FileRepository/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/surfacecamavs8380.sys"

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def disasm(path, start, stop):
    return subprocess.check_output(
        ["llvm-objdump", "-d", f"--start-address={start:#x}", f"--stop-address={stop:#x}", str(path)],
        text=True,
        stderr=subprocess.STDOUT,
    )

def sections(blob):
    pe = struct.unpack_from("<I", blob, 0x3C)[0]
    count = struct.unpack_from("<H", blob, pe + 6)[0]
    opt_size = struct.unpack_from("<H", blob, pe + 20)[0]
    sh = pe + 24 + opt_size
    out = []
    for i in range(count):
        off = sh + i * 40
        name = blob[off:off + 8].split(b"\0")[0].decode(errors="ignore")
        vsize, vaddr, raw_size, raw_ptr = struct.unpack_from("<IIII", blob, off + 8)
        out.append((name, vaddr, vsize, raw_ptr, raw_size))
    return out

def off_to_rva(sec, off):
    for name, vaddr, vsize, raw_ptr, raw_size in sec:
        if raw_ptr <= off < raw_ptr + raw_size:
            return name, vaddr + (off - raw_ptr)
    raise AssertionError(f"unmapped file offset {off:#x}")

def rva_to_off(sec, rva):
    for name, vaddr, vsize, raw_ptr, raw_size in sec:
        if vaddr <= rva < vaddr + max(vsize, raw_size):
            return raw_ptr + (rva - vaddr)
    raise AssertionError(f"unmapped RVA {rva:#x}")

assert sha256(DERIVED) == RESULT["e005l_derived_safe_scalars_sha256"]
assert sha256(KS) == RESULT["ks_sys_sha256"]
assert sha256(AVS) == RESULT["surfacecamavs8380_sha256"]

derived = json.loads(DERIVED.read_text(encoding="utf-8-sig"))
assert derived["rear_capture"]["format"] == "NV12 3840x2160"
assert derived["rear_capture"]["valid_frame_handles"] == 50
assert derived["rear_capture"]["elapsed_ms"] == 5032
assert derived["rear_capture"]["clean_start"] is True
assert derived["rear_capture"]["clean_stop"] is True

pin2 = derived["pin2_completion"]
assert pin2["samples"] == 24
assert pin2["header_size"] == 160
assert pin2["frame_extent"] == 12441600
assert pin2["data_used"] == 12441600
assert pin2["options_pre"] == "0x5000"
assert pin2["options_post"] == "0x25110"
assert pin2["frame_completion_min"] == 1
assert pin2["frame_completion_max"] == 24
assert pin2["frame_completion_unique"] == 24
assert pin2["metadata_buffer_size"] == 8130
assert pin2["metadata_used"] == 2224
assert pin2["drop_count"] == 0

pin3 = derived["pin3_completion"]
assert pin3["samples"] == 76
assert pin3["frame_extent"] == 1048576
assert pin3["data_used"] == 1048576
assert pin3["options_post"] == "0x25000"
assert pin3["frame_completion_min"] == 1
assert pin3["frame_completion_max"] == 76
assert pin3["frame_completion_unique"] == 76
assert pin3["metadata_used"] == 2224

ks_text = disasm(KS, 0x180007080, 0x180007120)
for needle in (
    "1800070bc:",
    "orr\tw9, w10, #0x20000",
    "1800070d4:",
    "ldr\tx9, [x22, #0x240]",
    "1800070d8:",
    "add\tx11, x9, #0x1",
    "1800070dc:",
    "str\tx11, [x22, #0x240]",
    "1800070e0:",
    "str\tx11, [x10, #0x40]",
):
    assert needle in ks_text, needle

complete = disasm(AVS, 0x140018D20, 0x140018D90)
for needle in (
    "140018d48:",
    "mov\tw8, #0x110",
    "140018d54:",
    "ldr\tw9, [x10, #0x30]",
    "140018d58:",
    "orr\tw8, w9, w8",
    "140018d5c:",
    "str\tw8, [x10, #0x30]",
    "140018d64:",
    "ldr\tx8, [x8, #0xc0]",
):
    assert needle in complete, needle
assert "#0x20000" not in complete

process = disasm(AVS, 0x140005720, 0x140005780)
assert "140005758:" in process
assert "ldr\tx8, [x8, #0xb8]" in process
assert "14000576c:" in process
assert "blr\tx15" in process

blob = AVS.read_bytes()
sec = sections(blob)
complete_ptr = struct.pack("<Q", 0x140018830)
refs = []
pos = 0
while True:
    pos = blob.find(complete_ptr, pos)
    if pos < 0:
        break
    refs.append(pos)
    pos += 1
assert len(refs) == 5, refs

vtable_rvas = []
for ref in refs:
    name, _ = off_to_rva(sec, ref)
    assert name == ".rdata"
    base = ref - 0xB8
    bname, brva = off_to_rva(sec, base)
    assert bname == ".rdata"
    assert struct.unpack_from("<Q", blob, base + 0xB8)[0] == 0x140018830
    vtable_rvas.append(brva)
assert 0x2FAB8 in vtable_rvas
video_ref = refs[vtable_rvas.index(0x2FAB8)]
video_base = video_ref - 0xB8
assert struct.unpack_from("<Q", blob, video_base + 0xC0)[0] == 0x140018EB0

parser = disasm(AVS, 0x140017880, 0x140017A64)
assert "cmp\tw8, #0x2" in parser
assert "cmp\tw8, #0x15" in parser
assert "cmp\tw8, #0x16" in parser
assert parser.count("bl\t0x140005c30") >= 2

jump_table = struct.unpack_from("<8i", blob, rva_to_off(sec, 0x1776C))
targets = [0x17614 + (entry << 2) for entry in jump_table]
assert targets[2] == 0x174E0, targets

worker = disasm(AVS, 0x1400174E0, 0x140017620)
assert worker.count("bl\t0x140005488") >= 4

assert RESULT["frame_completion_number_origin"] == "Microsoft KS stream bookkeeping"
assert RESULT["frame_completion_number_is_dma_fence"] is False
assert RESULT["surfacecamavs_complete_frame_adds_track_completion_numbers"] is False
assert RESULT["surfacecamavs_all_five_pin_vtables_slot_b8_complete_frame"] is True
assert RESULT["group0_image_normalized_notification_class"] == 2
assert RESULT["group0_class2_to_process_ife_frame_source_locked"] is True
assert RESULT["same_frame_fifo8_nonnull_wm16_match_proven"] is False
assert RESULT["independent_exact_wm16_irq_ack_dma_iommu_safe_stop_proven"] is False
assert RESULT["kernel_debugger_used"] is False
assert RESULT["native_rear_hardware_isp_runtime_authorized"] is False

print("PASS_E005K_COMPLETED_PIN2_HEADER_KS_GENERATED_FRAME_COMPLETION_NUMBER_GROUP0_CLASS2_PROCESSIFE_COMPLETEFRAME_REAR_DENIED")
