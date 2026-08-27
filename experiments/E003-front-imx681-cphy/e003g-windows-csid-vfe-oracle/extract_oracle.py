#!/usr/bin/env python3
import argparse, csv, hashlib, json, re
from pathlib import Path

REGIONS = {
    "wrapper": (0x0ACB6000, 0x1000),
    "csid0": (0x0ACB7000, 0x2000),
    "vfe0": (0x0AC62000, 0x4000),
    "csiphy2": (0x0ACE8000, 0x2000),
}
PHASES = ("IDLE", "LIVE1", "POST", "LIVE2", "POST2")
LINE = re.compile(
    r"^([0-9a-f]{8})`([0-9a-f]{8})\s+"
    r"([0-9a-f]{8})\s+([0-9a-f]{8})\s+([0-9a-f]{8})\s+([0-9a-f]{8})\s*$",
    re.I | re.M,
)


def parse_dump(text: str, phase: str, region: str):
    begin = f"===E003G_{phase}_{region.upper()}_BEGIN==="
    end = f"===E003G_{phase}_{region.upper()}_END==="
    if begin not in text or end not in text:
        raise RuntimeError(f"missing marker pair: {begin} / {end}")
    body = text.rsplit(begin, 1)[1].split(end, 1)[0]
    out = {}
    for m in LINE.finditer(body):
        addr = int(m.group(1) + m.group(2), 16)
        for i in range(4):
            out[addr + 4 * i] = int(m.group(3 + i), 16)
    return out


def write_nonzero_csv(path: Path, base: int, live1: dict, live2: dict):
    with path.open("w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["offset", "address", "live1", "live2", "stable"])
        for addr in sorted(live1):
            if live1[addr] or live2[addr]:
                w.writerow([
                    f"0x{addr-base:04x}", f"0x{addr:08x}",
                    f"0x{live1[addr]:08x}", f"0x{live2[addr]:08x}",
                    int(live1[addr] == live2[addr]),
                ])


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser()
    ap.add_argument("raw", nargs="?", type=Path,
                    default=here / "raw" / "E003G_CSID_VFE_ORACLE_20260827.log")
    ap.add_argument("--out", type=Path, default=here)
    args = ap.parse_args()
    raw = args.raw.read_bytes()
    text = raw.decode("utf-16", errors="replace")
    outdir = args.out
    outdir.mkdir(parents=True, exist_ok=True)

    dumps = {phase: {} for phase in PHASES}
    for phase in PHASES:
        for region, (_base, size) in REGIONS.items():
            d = parse_dump(text, phase, region)
            expected = size // 4
            if len(d) != expected:
                raise RuntimeError(f"{phase}/{region}: {len(d)} dwords, expected {expected}")
            dumps[phase][region] = d

    summary = {
        "date": "2026-08-27",
        "device": "Surface Camera Front / Sony IMX681",
        "acquisition": "same-machine Windows 11; WinRT MediaCapture/MediaFrameReader; two StartAsync=Success live passes; clean StopAsync between/post passes; SP7 KDNET physical MMIO",
        "raw_file": args.raw.name,
        "raw_bytes": len(raw),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "regions": {},
        "notes": [
            "Idle/post 0x80000000 values are treated as powered-off/inaccessible MMIO sentinel observations, not decoded reset-register values.",
            "Register semantic labels beyond the physical block names remain intentionally unresolved unless mechanically mapped to X1E CSID/VFE680 source/register documentation.",
            "SP11 Denali baseline declares VFE0 size 0xf000; this raw oracle captured only the first 0x4000. Do not infer VFE write-master/mode state from the missing range.",
        ],
    }

    for region, (base, size) in REGIONS.items():
        idle = dumps["IDLE"][region]
        live1 = dumps["LIVE1"][region]
        post = dumps["POST"][region]
        live2 = dumps["LIVE2"][region]
        post2 = dumps["POST2"][region]
        live_mismatch = [a for a in live1 if live1[a] != live2[a]]
        post1_mismatch = [a for a in idle if idle[a] != post[a]]
        post2_mismatch = [a for a in idle if idle[a] != post2[a]]
        stable_nonzero = [a for a in live1 if live1[a] == live2[a] and live1[a] != 0]
        idle_80000000 = sum(1 for v in idle.values() if v == 0x80000000)
        summary["regions"][region] = {
            "base": f"0x{base:08x}",
            "size_bytes": size,
            "dwords": size // 4,
            "live1_live2_mismatches": len(live_mismatch),
            "idle_post1_mismatches": len(post1_mismatch),
            "idle_post2_mismatches": len(post2_mismatch),
            "stable_live_nonzero_dwords": len(stable_nonzero),
            "idle_0x80000000_dwords": idle_80000000,
            "volatile_live_offsets": [f"0x{a-base:04x}" for a in live_mismatch],
        }
        if region == "vfe0":
            summary["regions"][region].update({
                "platform_declared_size_bytes": 0xF000,
                "captured_size_bytes": 0x4000,
                "captured_offset_range": "0x0000..0x3fff",
                "missing_offset_range": "0x4000..0xefff",
                "capture_complete": False,
            })
        write_nonzero_csv(outdir / f"{region}-live-nonzero.csv", base, live1, live2)

    # Raw, unlabelled CSID0 offsets that are particularly useful for the next decode pass.
    csbase = REGIONS["csid0"][0]
    selected = [
        0x000, 0x080, 0x200, 0x204,
        0x24c, 0x250, 0x254, 0x258, 0x25c, 0x260, 0x264, 0x268,
        0x310, 0x328, 0x32c, 0x338, 0x33c, 0x340, 0x348, 0x35c, 0x360, 0x37c, 0x390,
        0x530, 0x534, 0x538, 0x548, 0x550, 0x554, 0x56c, 0x58c,
        0x630, 0x634, 0x638, 0x648, 0x650, 0x654, 0x66c, 0x68c,
        0x730, 0x734, 0x738, 0x748, 0x750, 0x754, 0x76c, 0x78c,
        0x830, 0x834, 0x838, 0x848, 0x850, 0x854, 0x86c, 0x88c,
        0x930, 0x934, 0x938, 0x948, 0x950, 0x954, 0x96c, 0x98c,
        0xa00, 0xa18, 0xa30, 0xa48, 0xa60, 0xa78, 0xa90,
        0xb10, 0xb38, 0xb3c, 0xb40, 0xb48, 0xb5c, 0xb60, 0xb7c, 0xb90,
    ]
    summary["csid0_selected_live_offsets"] = {
        f"0x{o:04x}": f"0x{dumps['LIVE1']['csid0'][csbase+o]:08x}" for o in selected
    }

    (outdir / "oracle-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
