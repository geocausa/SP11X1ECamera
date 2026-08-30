#!/usr/bin/env python3
import argparse, hashlib, json, re
from pathlib import Path

EXPECTED_SHA256 = "c1afd89419c12ca093a7d3b1f80ef980723d78d3549ceb158b9ee1a1ca051846"
EXPECTED_BYTES = 53052

def die(msg):
    raise SystemExit("FAIL: " + msg)

def parse_map(lines, cb):
    prefix = f'HKR,0\\\\S2CB\\\\0x01\\\\0x04\\\\0x{cb:02X},"MAP"'
    line = next((x for x in lines if x.startswith(prefix)), None)
    if line is None:
        die(f"missing VFE S2CB CB{cb:02x}")
    vals = [int(x, 16) for x in re.findall(r'0x([0-9A-Fa-f]{2})', line.split('%REG_BINARY%',1)[1])]
    if len(vals) % 5:
        die(f"CB{cb:02x} MAP length not divisible by 5")
    return [
        {"entry": vals[i], "sid": (vals[i+1] << 8) | vals[i+2],
         "mask": (vals[i+3] << 8) | vals[i+4]}
        for i in range(0, len(vals), 5)
    ]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inf', type=Path)
    ap.add_argument('-o','--output', type=Path)
    a = ap.parse_args()
    raw = a.inf.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if len(raw) != EXPECTED_BYTES or sha != EXPECTED_SHA256:
        die(f"qcsmmu INF identity drift bytes={len(raw)} sha256={sha}")
    text = raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8')
    lines = text.splitlines()
    ctx = next((x for x in lines if x.startswith('HKR,0\\\\CTXI,"MAP"')), None)
    if ctx is None:
        die('missing SMMU0 CTXI map')
    vals = [int(x,16) for x in re.findall(r'0x([0-9A-Fa-f]{2})', ctx.split('%REG_BINARY%',1)[1])]
    if len(vals) % 3:
        die('CTXI map length not divisible by 3')
    triples = [vals[i:i+3] for i in range(0,len(vals),3)]
    if [1,0x10,4] not in triples or [1,0x11,4] not in triples:
        die('VFE HLOS/CDM context-bank assignment drift')
    cb16 = parse_map(lines,0x10)
    cb17 = parse_map(lines,0x11)
    if cb16 != [{"entry":255,"sid":0x800,"mask":0x60},{"entry":255,"sid":0x18a0,"mask":0}]:
        die('CB16 S1_IFE_HLOS mapping drift')
    if cb17 != [{"entry":255,"sid":0x1800,"mask":0x60},{"entry":255,"sid":0x1900,"mask":0},{"entry":255,"sid":0x1980,"mask":0x20}]:
        die('CB17 S1_ICP_IPE_BPS_CDM mapping drift')
    out = {
      "schema":"sp11-e003h-windows-qcsmmu-camera-sid-v1",
      "accepted":True,
      "source":{"file":"qcsmmu8380.inf","bytes":len(raw),"sha256":sha,"driver_version":"1.0.4160.6000"},
      "ctxi":{"client_0x01_cb16":{"vm":4,"name":"S1_IFE_HLOS"},"client_0x01_cb17":{"vm":4,"name":"S1_ICP_IPE_BPS_CDM"}},
      "cb16_s1_ife_hlos":cb16,
      "cb17_s1_icp_ipe_bps_cdm":cb17,
      "clean_room_consequence":"Same-machine Windows qcsmmu configuration places SID 0x18a0/mask0 in VFE client CB16 S1_IFE_HLOS. This establishes Windows SMMU grouping, not by itself which requester inside the group emits RT-CDM1 command fetches.",
      "runtime_authorized":False,
    }
    txt=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if a.output: a.output.write_text(txt)
    else: print(txt,end='')
    print('PASS: same-machine qcsmmu VFE CB16/CB17 SID maps pinned')
if __name__=='__main__': main()
