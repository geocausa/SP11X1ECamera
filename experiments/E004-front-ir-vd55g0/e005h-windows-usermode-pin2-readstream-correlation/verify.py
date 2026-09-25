#!/usr/bin/env python3
import collections, hashlib, json, re
from pathlib import Path

HERE=Path(__file__).resolve().parent
PRIV=Path("/mnt/sp11-win-ro/Users/Geoca/Documents/SP11-Camera-E005H-UserMode-PinCorrelation-20260925")
EXPECTED={
    "E005H-FrameServer-CDB-PRIVATE.log":"8a6aa06fac11f30a8b80105bf32be6e2eea34b3371b6c4e5f60fc6a4ab4972fe",
    "E005H-CAPTURE-SCALARS.txt":"c2a99087bef8ba2ca050934e3d55bd5a3b9f89ec1dbd8ff306f5ed645dc7715d",
    "E005H-rear4k-once.ps1":"3fdf8fb612578d205a0ed7f212f725809a8890a244c40766128bf7503aa90c55",
}
def req(v,m):
    if not v: raise AssertionError("E005H_FAIL "+m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

saved=json.loads((HERE/"RESULT.json").read_text())
ksuser=Path("/mnt/sp11-win-ro/Windows/System32/ksuser.dll")
req(ksuser.exists() and sha(ksuser)=="00baa6d3ad353ceb1547da8bd1e1aa913a7a26b27c0cf8deaed3adf4521bd369","ksuser source lock")
for n,h in EXPECTED.items():
    p=PRIV/n; req(p.exists(),"missing "+n); req(sha(p)==h,"hash "+n)
cap=(PRIV/"E005H-CAPTURE-SCALARS.txt").read_text(errors="ignore")
for token in ("StartAsync=Success","StopAsync=Success","elapsed_ms=15055","valid_frame_handles=157"):
    req(token in cap,"capture "+token)

pins=[]
reads=collections.Counter()
for l in (PRIV/"E005H-FrameServer-CDB-PRIVATE.log").read_text(errors="ignore").splitlines():
    m=re.match(r"E005H_PIN api=(\S+) status=([0-9a-f]+) pin=(\d+) handle=([0-9a-f]+) filter=([0-9a-f]+)",l)
    if m: pins.append((m.group(1),m.group(2),int(m.group(3)),m.group(4),m.group(5)))
    m=re.match(r"E005H_IOCTL h=([0-9a-f]+) code=002f4017",l)
    if m: reads[m.group(1)]+=1

success=[x for x in pins if x[1]=="00000000"]
req(sorted(x[2] for x in success)==[0,1,2,3],"successful pin IDs")
req(sum(reads.values())==1449 and len(reads)==2,"read stream total/handles")
by_pin={x[2]:reads[x[3]] for x in success}
req(by_pin=={0:0,1:0,2:361,3:1088},"pin to read-stream counts")
req(saved["video_record_pin2_exact_usermode_readstream_handle_proven"] is True,"pin2 proof")
req(saved["raw_usermode_handles_exported"] is False,"no raw handle export")
req(saved["kernel_debugger_used"] is False and saved["kernel_breakpoint_used"] is False,"no kernel debug")
req(saved["same_frame_fifo8_nonnull_wm16_match_proven"] is False,"FIFO8 WM16 still open")
req(saved["independent_exact_wm16_irq_ack_dma_iommu_safe_stop_proven"] is False,"DMA fence still open")
req(saved["native_rear_hardware_isp_runtime_authorized"] is False,"rear denied")
print("PASS_E005H_REAL_REAR4K_PIN2_EXACT_KS_READSTREAM_HANDLE_361_CALLS_PIN3_1088_NO_KERNEL_DEBUG_REAR_DENIED")
