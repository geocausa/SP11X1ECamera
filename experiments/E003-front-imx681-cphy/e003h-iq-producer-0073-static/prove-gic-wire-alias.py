#!/usr/bin/env python3
"""Fail-closed proof of the Surface 10.9 GIC311 DMI offset anomaly and wire alias.

Windows parity is the policy boundary: this proves what the exact Surface
DeviceMFT submits to PacketBuilder/Packet, and what bytes the captured Windows
DMI source therefore feeds to VFE GIC, independently of the logical GIC311
calculation output location.
"""
from __future__ import annotations
import argparse, hashlib, json, struct
from pathlib import Path

DEVICEMFT_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
REQ5_SHA = "fb172ee2e4e407d823a255e84427e68f1c3ef6a985ba2e00f32c4c4dea4997f8"
REQ6_SHA = "ff5f0f04bee8491c76451838743a28e3793ee5d2a0ecbff8f6589dca5c92f955"

# Exact Surface DeviceMFT RVAs, pinned by SHA above.
RVA = {
    "lsc_create": 0xB3CDA0,
    "gic_create": 0xB4AB10,
    "gtm_create": 0xB5A970,
    "packet_write_dmi": 0x85F108,
    "cmd_add_nested": 0x5E3180,
    "packet_add_cmd_buffer_reference": 0x5E35D0,
}

# Exact instruction bytes establishing byte scaling at the module boundary.
# LSC: lsl w23,w8,#2 ; GIC: ldr w23,[x2] then later mov w4,w23 ;
# GTM: lsl w4,w22,#2. Packet serialization adds child CmdBuffer +0x60 to
# the nested offset but performs no x4 scaling.
CODE_PROOFS = {
    0xB3CDE0: bytes.fromhex("17751e53"),
    0xB4AB28: bytes.fromhex("570040b9"),
    0xB4AB84: bytes.fromhex("e403172a"),
    0xB5A9C0: bytes.fromhex("c4761e53"),
    0x5E3A10: bytes.fromhex("893140f9"),  # child CmdBuffer +0x60
    0x5E3A18: bytes.fromhex("2b01080b"),  # add w11,w9,w8 (base + raw nested offset)
    0x5E3A50: bytes.fromhex("0b7d00b9"),  # serialized child offset field
}

LSC0 = (0x400, 0x374)
LSC1 = (0x774, 0x374)
LSC2 = (0xAE8, 0x374)
GIC_WIRE = (0x62E, 0x200)
GIC_LOGICAL = (0x18B8, 0x200)
BPC = (0x1AB8, 0x100)
GTM = (0x34CC, 0x800)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def rva_to_off(pe: bytes, rva: int) -> int:
    if pe[:2] != b"MZ":
        raise ValueError("not PE/MZ")
    peoff = struct.unpack_from("<I", pe, 0x3C)[0]
    if pe[peoff:peoff+4] != b"PE\0\0":
        raise ValueError("bad PE signature")
    nsec = struct.unpack_from("<H", pe, peoff + 6)[0]
    optsz = struct.unpack_from("<H", pe, peoff + 20)[0]
    sh = peoff + 24 + optsz
    for i in range(nsec):
        o = sh + i * 40
        vsize, va, rawsz, raw = struct.unpack_from("<IIII", pe, o + 8)
        span = max(vsize, rawsz)
        if va <= rva < va + span:
            return raw + (rva - va)
    raise ValueError(f"RVA 0x{rva:x} not mapped")


def assert_code(pe: bytes) -> dict[str, str]:
    out = {}
    for rva, want in CODE_PROOFS.items():
        off = rva_to_off(pe, rva)
        got = pe[off:off+len(want)]
        if got != want:
            raise ValueError(f"code proof mismatch RVA 0x{rva:x}: {got.hex()} != {want.hex()}")
        out[f"0x{rva:x}"] = got.hex()
    return out


def slice_info(a: bytes, b: bytes, off: int, n: int) -> dict:
    x, y = a[off:off+n], b[off:off+n]
    if len(x) != n or len(y) != n:
        raise ValueError(f"short DMI source slice 0x{off:x}+0x{n:x}")
    return {
        "offset": f"0x{off:x}", "bytes": n,
        "request5_sha256": sha(x), "request6_sha256": sha(y),
        "identical": x == y,
        "changed_byte_count": sum(p != q for p, q in zip(x, y)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--devicemft", type=Path, required=True)
    ap.add_argument("--request5-dmi", type=Path, required=True)
    ap.add_argument("--request6-dmi", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    pe = args.devicemft.read_bytes()
    r5 = args.request5_dmi.read_bytes()
    r6 = args.request6_dmi.read_bytes()
    if sha(pe) != DEVICEMFT_SHA:
        raise SystemExit("exact Surface DeviceMFT SHA mismatch")
    if sha(r5) != REQ5_SHA:
        raise SystemExit("request5 DMI source SHA mismatch")
    if sha(r6) != REQ6_SHA:
        raise SystemExit("matched request6 DMI source SHA mismatch")
    if len(r5) != 0x8000 or len(r6) != 0x8000:
        raise SystemExit("unexpected steady DMI source size")

    code = assert_code(pe)

    # The logical GIC producer starts at dword offset 0x62e, hence byte offset
    # 0x62e*4 == 0x18b8. Unlike LSC and GTM, exact GIC311 CreateCmdList passes
    # the dword offset raw to WriteDMI. Packet patch serialization adds the
    # CmdBuffer base offset only; it never scales it. Thus Windows wire address
    # uses source +0x62e, while the actual GIC calculation output lives +0x18b8.
    if GIC_WIRE[0] * 4 != GIC_LOGICAL[0]:
        raise SystemExit("internal GIC dword/byte relation failed")
    if GIC_LOGICAL[0] + GIC_LOGICAL[1] != BPC[0]:
        raise SystemExit("logical GIC is not immediately before BPC as expected")

    wire_start, wire_n = GIC_WIRE
    wire_end = wire_start + wire_n
    l0s, l0n = LSC0; l1s, l1n = LSC1
    l0e, l1e = l0s+l0n, l1s+l1n
    overlap0 = max(0, min(wire_end, l0e) - max(wire_start, l0s))
    overlap1 = max(0, min(wire_end, l1e) - max(wire_start, l1s))
    if (overlap0, overlap1, overlap0 + overlap1) != (0x146, 0xBA, 0x200):
        raise SystemExit("unexpected GIC/LSC alias geometry")
    if r5[wire_start:wire_end] != r5[wire_start:l0e] + r5[l1s:wire_end]:
        raise SystemExit("request5 alias concatenation failed")
    if r6[wire_start:wire_end] != r6[wire_start:l0e] + r6[l1s:wire_end]:
        raise SystemExit("request6 alias concatenation failed")

    slices = {
        "lsc0": slice_info(r5, r6, *LSC0),
        "lsc1": slice_info(r5, r6, *LSC1),
        "lsc2": slice_info(r5, r6, *LSC2),
        "gic_wire_alias": slice_info(r5, r6, *GIC_WIRE),
        "gic_logical_output": slice_info(r5, r6, *GIC_LOGICAL),
        "bpc": slice_info(r5, r6, *BPC),
        "gtm": slice_info(r5, r6, *GTM),
    }
    if slices["gic_logical_output"]["identical"] is not True:
        raise SystemExit("logical GIC output unexpectedly changes request5->6")
    if slices["gic_wire_alias"]["identical"] is not False:
        raise SystemExit("wire GIC alias unexpectedly static request5->6")

    result = {
        "schema": "sp11-e003h-gic-wire-alias-v1",
        "status": "PASS",
        "policy": "Same-machine Windows wire behavior is authoritative for Linux parity.",
        "surface_devicemft_sha256": DEVICEMFT_SHA,
        "request5_dmi_sha256": REQ5_SHA,
        "request6_matched_dmi_sha256": REQ6_SHA,
        "exact_rvas": {k: f"0x{v:x}" for k,v in RVA.items()},
        "code_byte_proofs": code,
        "offset_semantics": {
            "ife_node_gic_offset_unit": "UINT32/dword",
            "gic_offset_dwords": "0x62e",
            "gic_logical_output_byte_offset": "0x18b8",
            "gic_create_cmd_list_write_dmi_offset": "0x62e raw (no x4)",
            "lsc_create_cmd_list": "converts dword offset to bytes with x4",
            "gtm_create_cmd_list": "converts dword offset to bytes with <<2",
            "packet_patch_serialization": "adds child CmdBuffer base offset to raw nested offset; no scaling",
        },
        "wire_alias": {
            "gic_register": "0x4708",
            "selector": 1,
            "payload_bytes": 512,
            "windows_source_offset": "0x62e",
            "logical_gic_source_offset": "0x18b8",
            "overlaps": [
                {"module": "LSC0", "bytes": overlap0, "source_range": "0x62e..0x774"},
                {"module": "LSC1", "bytes": overlap1, "source_range": "0x774..0x82e"},
            ],
            "conclusion": "Windows VFE GIC DMI consumes a 512-byte alias spanning the tail of LSC0 and head of LSC1; the separately calculated GIC311 table at 0x18b8 is not the wire payload for this path.",
        },
        "request5_to_request6": slices,
        "producer_reduction": {
            "independent_dynamic_wire_lut_producers_remaining": ["LSC", "GTM"],
            "gic_wire_payload_dependency": "derived automatically from the LSC source bytes through the exact Windows alias",
            "logical_unused_gic_table_changed": False,
        },
        "runtime_authorized": False,
    }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status":result["status"], "wire_alias":result["wire_alias"], "producer_reduction":result["producer_reduction"]}, indent=2))

if __name__ == "__main__":
    main()
