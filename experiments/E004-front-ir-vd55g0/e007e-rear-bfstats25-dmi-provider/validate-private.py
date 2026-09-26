#!/usr/bin/env python3
from pathlib import Path
import json, struct

D = Path(__file__).resolve().parent
REPO = D.parents[2]
SAFE = REPO / "experiments/E004-front-ir-vd55g0/e006b-windows-rear-dmi-source-payloads/PARTIAL-RESULT.json"
PRIVATE = REPO.parent / "private/e006b"
META = json.load(open(SAFE))

FILES = {
    "startup0": "E006B-START0-SOURCE.bin",
    "startup1": "E006B-START1-SOURCE.bin",
    "startup2": "E006B-START2-SOURCE.bin",
    "startup3": "E006B-START3-SOURCE.bin",
    "steady_ac8": "E006B-STEADY-AC8-SOURCE.bin",
}

def clamp_delta(d):
    return -8192 if d < -8192 else 8191 if d > 8191 else d

def pack_roi(r, eob):
    w0 = ((r["height"] & 0x1fff) |
          ((r["width"] & 0x0fff) << 14) |
          ((r["top"] & 0x1f) << 27))
    w1 = (((r["top"] >> 5) & 0x1ff) |
          ((r["left"] & 0x1fff) << 9) |
          ((r["rid"] & 0xff) << 23) |
          ((r["oid"] & 0x1) << 31))
    w2 = (((r["oid"] >> 1) & 0x7f) |
          ((r["merge"] & 1) << 7) |
          ((eob & 1) << 8) |
          ((r["type"] & 1) << 9))
    return struct.pack("<III", w0 & 0xffffffff, w1 & 0xffffffff, w2 & 0xffffffff)

def unpack_roi(b):
    w0, w1, w2 = struct.unpack("<III", b)
    top = ((w0 >> 27) & 0x1f) | ((w1 & 0x1ff) << 5)
    oid = ((w1 >> 31) & 0x1) | ((w2 & 0x7f) << 1)
    return {
        "height": w0 & 0x1fff,
        "width": (w0 >> 14) & 0x0fff,
        "top": top,
        "left": (w1 >> 9) & 0x1fff,
        "rid": (w1 >> 23) & 0xff,
        "oid": oid,
        "merge": (w2 >> 7) & 1,
        "eob": (w2 >> 8) & 1,
        "type": (w2 >> 9) & 1,
        "unknown_hi": w2 >> 10,
    }

def pack_gamma(samples):
    assert len(samples) == 32
    out = bytearray()
    for i, cur in enumerate(samples):
        assert 0 <= cur <= 0x3fff
        nxt = samples[i + 1] if i + 1 < 32 else 0x4000
        d = clamp_delta(nxt - cur)
        out += struct.pack("<I", (cur + ((d & 0xffffffff) << 14)) & 0xffffffff)
    return bytes(out)

captures = roi_records = gamma_words = 0
roi_payloads = gamma_payloads = 0
eob_checks = unknown_hi_checks = 0

for cap in META["captured"]["captures"]:
    label = cap["label"]
    if label not in FILES:
        continue
    blob = (PRIVATE / FILES[label]).read_bytes()
    base = int(cap["captured_source_window_base"], 16)
    found = False
    for item in cap["payloads"]:
        if item["dmi_register_offset"] != "0xbc08":
            continue
        sel = item["selector"]
        n = item["payload_bytes"]
        rel = int(item["source_offset"], 16) - base
        payload = blob[rel:rel+n]
        assert len(payload) == n
        found = True
        if sel == 1:
            assert n == 300
            records = [unpack_roi(payload[i:i+12]) for i in range(0, n, 12)]
            assert len(records) == 25
            assert all(r["unknown_hi"] == 0 for r in records)
            assert sum(r["eob"] for r in records) == 1
            assert records[-1]["eob"] == 1
            repacked = b"".join(pack_roi(r, i == len(records)-1)
                                for i, r in enumerate(records))
            assert repacked == payload
            roi_records += len(records)
            roi_payloads += 1
            eob_checks += 1
            unknown_hi_checks += len(records)
        elif sel == 2:
            assert n == 128
            words = list(struct.unpack("<32I", payload))
            samples = [w & 0x3fff for w in words]
            assert pack_gamma(samples) == payload
            gamma_words += len(words)
            gamma_payloads += 1
        else:
            raise AssertionError(sel)
    if found:
        captures += 1

assert captures >= 4
assert roi_payloads >= 4 and roi_records == roi_payloads * 25
assert gamma_payloads >= 3 and gamma_words == gamma_payloads * 32

safe = {
    "schema": "E007e-private-validation-safe-v2",
    "captures_with_bf_dmi": captures,
    "roi_payloads_checked": roi_payloads,
    "roi_records_checked": roi_records,
    "roi_compact_layout_exact_repack": True,
    "roi_eob_payload_checks": eob_checks,
    "roi_unknown_high_bits_zero_checks": unknown_hi_checks,
    "gamma_payloads_checked": gamma_payloads,
    "gamma_words_checked": gamma_words,
    "gamma_exact_repack": True,
    "raw_payload_values_emitted": False,
}
(D / "PRIVATE-VALIDATION-SAFE.json").write_text(
    json.dumps(safe, indent=2, sort_keys=True) + "\n"
)
print("E007E_PRIVATE_VALIDATION_PASS")
print(f"captures={captures} roi_payloads={roi_payloads} roi_records={roi_records} gamma_payloads={gamma_payloads} gamma_words={gamma_words}")
print("roi_compact_layout=true raw_payload_values_emitted=false")
