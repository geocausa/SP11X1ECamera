#!/usr/bin/env python3
"""Offline consistency checks for E003i-AR static AEC exposure-coordinate proof."""
from __future__ import annotations
import json, math, struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
AQ = HERE.parent / "aq-windows-aec-arbitration-table" / "TABLE681.fixture.json"

def f32(x: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(x)))[0]

def u32f(bits: int) -> float:
    return struct.unpack("<f", struct.pack("<I", bits))[0]

def frinta_positive(x: float) -> int:
    # All checked exposure quantities are positive; ties-away == floor(x+0.5).
    return math.floor(x + 0.5)

def main() -> None:
    fixture = json.loads(AQ.read_text())
    assert fixture["device_mft"]["sha256"] == "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
    knees = fixture["decoded_knees"]
    assert knees[0] == {"increment_priority": 1, "gain_f32": 1.0, "exposure_time_ns": 37516}
    assert fixture["tuned_blob"]["correction_factor_f32"] == 1.0

    base = frinta_positive(knees[0]["gain_f32"] * knees[0]["exposure_time_ns"] * fixture["tuned_blob"]["correction_factor_f32"])
    assert base == 37516

    one03 = u32f(0x3F83D70A)
    assert one03 == f32(1.03)
    reciprocal_log = f32(1.0 / f32(math.log(one03)))

    # Address/layout identities proven by disassembly.
    assert 0xD0 + 0x198 == 0x268
    assert 0xD0 + 0x138 == 0x208
    assert 0xD0 + 0x160 == 0x230
    assert [0x688 + 0x50*i for i in range(7)] == [0x688,0x6D8,0x728,0x778,0x7C8,0x818,0x868]

    pair = fixture["corroborative_pair"]
    gain = u32f(int(pair["gain_f32_bits"], 16))
    assert gain == pair["gain"]
    pair_product = frinta_positive(gain * pair["exposure_time_ns"])
    assert pair_product == 241_379_204
    assert pair_product != base

    # Analytic coordinate only: actual DeviceMFT stores a float32 coordinate and
    # uses its own log/pow implementations, so this is deliberately not an exact
    # hidden-qword reconstruction claim.
    analytic_coord = math.log(pair_product / base) / math.log(one03)
    analytic_rebuild = base * math.pow(one03, analytic_coord)
    assert abs(analytic_rebuild - pair_product) < 1e-5

    print(f"T681_BASE={base}")
    print(f"ONE03_F32={one03:.17g} bits=0x3f83d70a")
    print(f"RECIP_LOG_F32_APPROX={reciprocal_log:.9f}")
    print(f"CORROBORATIVE_PAIR_FRINTA_PRODUCT={pair_product}")
    print(f"ANALYTIC_COORD_FOR_PAIR_PRODUCT={analytic_coord:.12f}")
    print("LAYOUT input+0x198=child+0x268 input+0x138=child+0x208 input+0x160=child+0x230")
    print("AR_VERIFY=PASS")

if __name__ == "__main__":
    main()
