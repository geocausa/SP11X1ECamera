#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

RAW_SHA256 = "8ccb149a22dddf21edb3b7115493a9000368a29c132f9dcfddc4867070c1e9cc"
EXPECTED_ADDRS = [
    0x0AC74D08, 0x0AC75308, 0x0AC75708, 0x0AC75908, 0x0AC76408,
    0x0AC76A08, 0x0AC76F08, 0x0AC7B008, 0x0AC7B208, 0x0AC7C208,
]
LINE_RE = re.compile(r"^#\s+([0-9a-fA-F]+)\s+((?:[0-9a-fA-F]{8}(?:\s+|$))+)")

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def block(lines: list[str], begin: str, end: str) -> list[str]:
    try:
        a = lines.index(begin)
        b = lines.index(end, a + 1)
    except ValueError as e:
        raise SystemExit(f"missing marker: {e}")
    return lines[a + 1:b]

def reads(lines: list[str]) -> list[dict]:
    out=[]
    for line in lines:
        m=LINE_RE.match(line.strip())
        if not m:
            continue
        out.append({
            "address": int(m.group(1),16),
            "values": [int(x,16) for x in m.group(2).split()],
        })
    return out

def phase_map(rs: list[dict]) -> dict[int,list[int]]:
    return {r["address"]: r["values"] for r in rs}

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("raw", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args=ap.parse_args()
    raw=args.raw.read_bytes()
    got=sha256(raw)
    if got != RAW_SHA256:
        raise SystemExit(f"raw SHA mismatch: {got}")
    text=raw.decode("utf-16")
    lines=text.splitlines()

    idle=phase_map(reads(block(lines,"===E003H_DMI_IDLE===","===E003H_DMI_IDLE_DONE===")))
    live=phase_map(reads(block(lines,"===E003H_DMI_LIVE===","===E003H_DMI_LIVE_DONE===")))
    post=phase_map(reads(block(lines,"===E003H_DMI_POST===","===E003H_DMI_POST_DONE===")))
    for name, phase, expected in (
        ("idle", idle, 0x80000000), ("live", live, 0), ("post", post, 0x80000000)
    ):
        if sorted(phase) != sorted(EXPECTED_ADDRS):
            raise SystemExit(f"{name}: address set mismatch")
        for addr in EXPECTED_ADDRS:
            if phase[addr] != [expected]*4:
                raise SystemExit(f"{name}: unexpected values at 0x{addr:08x}: {phase[addr]}")

    diag=reads(block(lines,"===E003H_DMI_READ4708_BEGIN===","===E003H_DMI_READ4708_DONE==="))
    # Exact observed order: initial quartet, selected cfg/addr pair, three data-port reads
    # interleaved with address reads, then restored quartet.
    if not diag or diag[0] != {"address":0x0AC75708,"values":[0,0,0,0]}:
        raise SystemExit("diagnostic initial quartet mismatch")
    selected_idx=lines.index("===E003H_DMI_READ4708_SELECTED===")
    restored_idx=lines.index("===E003H_DMI_READ4708_RESTORED===")
    selected=reads(lines[selected_idx+1:restored_idx])
    restored=reads(lines[restored_idx+1:lines.index("===E003H_DMI_READ4708_DONE===",restored_idx+1)])
    if selected[0] != {"address":0x0AC75708,"values":[1,0]}:
        raise SystemExit(f"selector readback mismatch: {selected[0] if selected else None}")
    data_reads=[r for r in selected if r["address"] in (0x0AC75710,0x0AC75714)]
    if not data_reads or any(any(v != 0 for v in r["values"]) for r in data_reads):
        raise SystemExit("diagnostic data-port result mismatch")
    if restored != [{"address":0x0AC75708,"values":[0,0,0,0]}]:
        raise SystemExit(f"diagnostic restore mismatch: {restored}")

    summary={
        "status":"PASS",
        "policy":"Same-machine Windows is behavioral oracle. The bounded selector/address writes were diagnostic only and were restored before native StopAsync.",
        "raw":{"bytes":len(raw),"sha256":got,"encoding":"UTF-16LE KD text log"},
        "dmi_quartets":{
            "addresses":[f"0x{x:08x}" for x in EXPECTED_ADDRS],
            "idle":"all four dwords 0x80000000 at all ten blocks",
            "native_live":"all four dwords 0x00000000 at all ten blocks",
            "post":"all four dwords 0x80000000 at all ten blocks",
        },
        "bounded_4708_diagnostic":{
            "physical_block":"0x0ac75708 (VFE1 + 0x4708)",
            "write_sequence":["DMI_CFG <= 0x00000101","DMI_ADDR <= 0x00000000"],
            "cfg_readback":"0x00000001",
            "candidate_data_ports":["+0x10","+0x14"],
            "candidate_data_reads":"all zero",
            "restore":["DMI_CFG <= 0","DMI_ADDR <= 0"],
            "restored_quartet":"all zero while native stream remained live",
            "conclusion":"The older Qualcomm VFE17x LUT-dump recipe is not accepted as a VFE680 DMI read mechanism on this SP11; it did not expose the known nonzero Windows payload at +0x4708 selector 1.",
        },
        "native_holder":"Surface Camera Front WinRT reader StartAsync=Success; normal StopAsync/Dispose after diagnostic",
        "golden_return":"rebooted to 7.1.5-sp11-render-parity-v4+; protected kernel/initrd/DTB hashes reverified; saved GRUB default unchanged and next_entry empty",
        "next_required_oracle":"Prove native SW_CDM=0 / hardware-CDM branch and resolve RT_CDM_0/RT_CDM_1 mapped and physical bases/version before any Linux DMI execution design.",
    }
    args.out.write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__ == "__main__":
    main()
