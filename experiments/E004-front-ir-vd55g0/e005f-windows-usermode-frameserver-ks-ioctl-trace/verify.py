#!/usr/bin/env python3
import collections, hashlib, json, re
from pathlib import Path

HERE=Path(__file__).resolve().parent
PRIV=Path("/mnt/sp11-win-ro/Users/Geoca/Documents/SP11-Camera-E005F-UserMode-Trace-20260925")
EXPECTED={
    "E005F-FrameServer-CDB-PRIVATE.log":"d8859976d0b1f1a5ed9dfd8760dc485656c8bd225872a2aded7053075fdb6d75",
    "E005F-CAPTURE-SCALARS.txt":"68012b3527b4b8b5c301936049f42f8956627df7c3de42801780460e2ccb6690",
    "E005F-rear4k-once.ps1":"085d143179c57ff6d04db82f5bfb91980fa18ec6f4c1bf83e775cc87239698bd",
}
def req(v,m):
    if not v: raise AssertionError("E005F_FAIL "+m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

saved=json.loads((HERE/"RESULT.json").read_text())
for n,h in EXPECTED.items():
    p=PRIV/n
    req(p.exists(),"private evidence missing "+n)
    req(sha(p)==h,"private hash "+n)
cap=(PRIV/"E005F-CAPTURE-SCALARS.txt").read_text(errors="ignore")
for token in ("StartAsync=Success","StopAsync=Success","rear4k_valid_frame_handles=203","elapsed_ms=20049"):
    req(token in cap,"capture scalar "+token)
log=(PRIV/"E005F-FrameServer-CDB-PRIVATE.log").read_text(errors="ignore").splitlines()
ctr=collections.Counter(); handles=collections.defaultdict(set); per=collections.Counter()
for l in log:
    m=re.match(r"E005F_IOCTL h=([0-9a-f]+) code=([0-9a-f]+)",l)
    if not m: continue
    h,code=m.group(1),"0x"+m.group(2).lower()
    ctr[code]+=1; handles[code].add(h)
    if code=="0x002f4017": per[h]+=1
req(sum(ctr.values())==4598,"total ioctl")
req(ctr["0x002f0003"]==1599,"KS property count")
req(ctr["0x002f4017"]==1225,"KS read stream count")
req(len(handles["0x002f4017"])==2,"two read stream handles")
req(sorted(per.values(),reverse=True)==[922,303],"read stream per handle counts")
req(ctr["0x002f0007"]==18 and ctr["0x002f000b"]==4 and ctr["0x002f000f"]==2,"event/method counts")
text="\n".join(log).lower()
req("qcom_avstream_8380" in text,"QCOM filter open")
req("qcdevicemft8380.dll" in text,"DeviceMFT load")
req("ksuser.dll" in text,"ksuser load")
req(saved["frameserver_usermode_debugger_only"] is True and saved["kernel_debugger_used"] is False,"no KD")
req(saved["specific_4k_pin_id_to_read_stream_handle_mapping_proven"] is False,"pin mapping still open")
req(saved["same_frame_fifo8_nonnull_wm16_match_proven"] is False,"WM16 still open")
req(saved["native_rear_hardware_isp_runtime_authorized"] is False,"rear denied")
print("PASS_E005F_USERMODE_ONLY_REAR4K_203_FRAMES_4598_IOCTL_1225_READSTREAM_TWO_HANDLES_NO_KERNEL_DEBUG_REAR_DENIED")
