#!/usr/bin/env python3
"""Fail-closed proof of live IFELSC411 Titan680 staging -> wire packing.

The Windows producer session already captured the exact 0x18a0-byte IFELSC411
post-calculation staging object for requests 4/5/6.  This proof SHA-pins those
captures and the exact Surface DeviceMFT, asserts the ARM64 Titan680 packing
loop, and derives the same-stream LSC0/LSC1/LSC2 byte targets plus the already
proven Windows GIC wire alias.  Raw proprietary captures remain local/untracked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

try:
    import pefile
except Exception as exc:
    raise SystemExit(f"missing proof dependency pefile: {exc}")

DEVICE_MFT_SHA256 = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
PACKER_RVA = 0xB3D8A0
STAGING_BYTES = 0x18A0
MESH_POINTS = 221
WIRE_BYTES = MESH_POINTS * 4

STAGING_SHA256 = {
    4: "c67b893c5b32b6fdf343875cd4f2921f97429d98922d2b4d555c5bb36f4602bc",
    5: "5c07dca5e0e44e1fc3df026396643a255fc7fb1445a70e27934e9e6c6c49d766",
    6: "e8526f3f3676802b9596fadd0bc479df2a6e531bf587c9278e8729a10e2daa6e",
}
EXPECTED = {
    4: {
        "bank": 1,
        "lsc0": "d4a4a75ffe930e2af7186ab17a083e37de40e520b69db29cb798587774ced6f5",
        "lsc1": "f8d98429561f31e6fbbe351d320589192563673fae7c22d5646da723e0abeb43",
        "lsc2": "6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e",
        "gic_alias": "a0eafa31899484f9f584e9432ab3188407d4f4f6f53f6cd85c1331e1fd57caaa",
    },
    5: {
        "bank": 0,
        "lsc0": "e058fb6950db8b0f352c0feca2f38431f2d64ac51534a1703ee53b20707de6a2",
        "lsc1": "dc91ab40eca8ebe115341cd7b3bd2150251675f0ce23997484b47a42bb40f4af",
        "lsc2": "6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e",
        "gic_alias": "5309035131e7d2e0c1622ddbd2c506ab4bf81db9702a56a827c786b84730d31e",
    },
    6: {
        "bank": 1,
        "lsc0": "db9f60b5ffc8945c2b4772a3b0c0c7cad685408c2c3ee5c56f2f6e64f7421420",
        "lsc1": "52e3c4f0eb5c3cff0b45d097a5bede4f6c58fc03e446d8c4a3ea5ecaea545c27",
        "lsc2": "6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e",
        "gic_alias": "04c5a085d18362fc0b0dae0c6d2b62fb64447ff6242b2926f65ad0ac4be6c028",
    },
}

# Raw little-endian ARM64 bytes from exact DeviceMFT.  They pin the dimensions,
# bank addressing, LSC0/LSC1 14+14-bit packing, LSC2 12+18-bit packing, and
# output loop shape.  These are deliberately byte assertions, not decompiler
# assumptions.
CODE_BYTES = {
    0xB3D8A0: "7f2303d5",  # function entry, PackIQRegisterSetting
    0xB3DB94: "6aa64229",  # ldp w10,w9,[x19,#0x14] => cols-2, rows-2
    0xB3DB98: "4c090011",  # add w12,w10,#2
    0xB3DB9C: "2b090011",  # add w11,w9,#2
    0xB3DBA8: "8a0680d2",  # mov x10,#0x34 (two-bank mesh stride)
    0xB3DBB8: "a50180d2",  # mov x5,#0xd (LSC2 bank stride)
    0xB3DBBC: "6e124079",  # ldrh w14,[x19,#8] bank
    0xB3DBC4: "ce250a9b",  # madd x14,x14,x10,x9
    0xB3DBC8: "ce110e8b",  # *17 row stride
    0xB3DBD0: "eead0391",  # add +0xeb high LSC0 channel
    0xB3DBD4: "677a6e78",  # ldrh high LSC0
    0xB3DBD8: "ee390091",  # add +0x0e low LSC0 channel
    0xB3DBDC: "6e7a6e78",  # ldrh low LSC0
    0xB3DBE0: "cf350012",  # and low,#0x3fff
    0xB3DBE8: "ef341233",  # bfi high,#14,#14
    0xB3DBEC: "cf5928b8",  # store LSC0 dword
    0xB3DC00: "ee210791",  # add +0x1c8 high LSC1 channel
    0xB3DC04: "677a6e78",  # ldrh high LSC1
    0xB3DC08: "ee950a91",  # add +0x2a5 low LSC1 channel
    0xB3DC0C: "6e7a6e78",  # ldrh low LSC1
    0xB3DC10: "cf350012",  # and low,#0x3fff
    0xB3DC18: "ef341233",  # bfi high,#14,#14
    0xB3DC1C: "cf5928b8",  # store LSC1 dword
    0xB3DC24: "ce25059b",  # bank*0xd + row
    0xB3DC28: "ce110e8b",  # *17
    0xB3DC30: "ee212a91",  # add +0xa88 LSC2 low source
    0xB3DC34: "6e7a6e78",  # ldrh low source
    0xB3DC3C: "c72d0012",  # and low,#0xfff
    0xB3DC40: "ee290e91",  # add +0x38a LSC2 high source
    0xB3DC44: "6e7a6eb8",  # ldr w14,[x19,x14,lsl#2]
    0xB3DC48: "c7451433",  # bfi high,#12,#18
    0xB3DC50: "c75928b8",  # store LSC2 dword
    0xB3DC54: "08050011",  # output index++
    0xB3DC58: "26fbff35",  # inner loop
    0xB3DC60: "29050091",  # row++
    0xB3DC68: "2bfaff35",  # outer loop
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def u16(buf: bytes, off: int) -> int:
    return struct.unpack_from("<H", buf, off)[0]


def u32(buf: bytes, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def verify_code_bytes(dll: Path) -> dict[str, str]:
    if sha_file(dll) != DEVICE_MFT_SHA256:
        raise RuntimeError("DeviceMFT SHA-256 mismatch")
    pe = pefile.PE(str(dll), fast_load=True)
    raw = dll.read_bytes()
    result = {}
    for rva, expected in CODE_BYTES.items():
        off = pe.get_offset_from_rva(rva)
        actual = raw[off:off + 4].hex()
        if actual != expected:
            raise RuntimeError(f"DeviceMFT code mismatch at RVA 0x{rva:x}: {actual} != {expected}")
        result[f"0x{rva:x}"] = actual
    return result


def pack_live_staging(staging: bytes) -> tuple[dict, bytes, bytes, bytes]:
    if len(staging) != STAGING_BYTES:
        raise RuntimeError(f"staging size {len(staging):#x} != {STAGING_BYTES:#x}")

    bank = u16(staging, 0x08)
    cols = u32(staging, 0x14) + 2
    rows = u32(staging, 0x18) + 2
    if bank not in (0, 1):
        raise RuntimeError(f"unexpected LSC bank {bank}")
    if (cols, rows) != (17, 13):
        raise RuntimeError(f"unexpected LSC mesh dimensions {cols}x{rows}")
    if cols * rows != MESH_POINTS:
        raise RuntimeError("mesh point count mismatch")

    lsc0: list[int] = []
    lsc1: list[int] = []
    lsc2: list[int] = []
    for row in range(rows):
        for col in range(cols):
            idx = (row + bank * 0x34) * 0x11 + col

            lo0 = u16(staging, 2 * (idx + 0x0E))
            hi0 = u16(staging, 2 * (idx + 0x0EB))
            lsc0.append((lo0 & 0x3FFF) | ((hi0 & 0x3FFF) << 14))

            lo1 = u16(staging, 2 * (idx + 0x2A5))
            hi1 = u16(staging, 2 * (idx + 0x1C8))
            lsc1.append((lo1 & 0x3FFF) | ((hi1 & 0x3FFF) << 14))

            idx2 = (row + bank * 0x0D) * 0x11 + col
            lo2 = u16(staging, 2 * (idx2 + 0xA88))
            # Exact assembly is a 32-bit load with x14,lsl#2, not a halfword
            # load.  Keep this address expression separate to avoid silently
            # inheriting the decompiler's mixed pointer units.
            hi2 = u32(staging, 4 * (idx2 + 0x38A))
            lsc2.append((lo2 & 0x0FFF) | ((hi2 & 0x3FFFF) << 12))

    def emit(values: list[int]) -> bytes:
        return b"".join(struct.pack("<I", v) for v in values)

    return {"bank": bank, "cols": cols, "rows": rows, "points": cols * rows}, emit(lsc0), emit(lsc1), emit(lsc2)


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--device-mft",
        type=Path,
        default=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"),
    )
    parser.add_argument("--capture-dir", type=Path, default=here / "windows-adaptive-live-20260902")
    parser.add_argument("--out", type=Path, default=here / "lsc-live-staging-pack-oracle.json")
    args = parser.parse_args()

    code = verify_code_bytes(args.device_mft)
    requests = {}
    for request in (4, 5, 6):
        path = args.capture_dir / f"REQ{request}_LSC_STAGING.bin"
        staging = path.read_bytes()
        if sha(staging) != STAGING_SHA256[request]:
            raise RuntimeError(f"request{request}: staging SHA mismatch")
        geometry, lsc0, lsc1, lsc2 = pack_live_staging(staging)
        if len(lsc0) != WIRE_BYTES or len(lsc1) != WIRE_BYTES or len(lsc2) != WIRE_BYTES:
            raise RuntimeError(f"request{request}: wire LUT size mismatch")

        # GIC wire source 0x62e..0x82e aliases LSC0 source 0x400 and LSC1
        # source 0x774. Relative to LSC0||LSC1 that is [0x22e:0x42e].
        gic_alias = (lsc0 + lsc1)[0x22E:0x42E]
        if len(gic_alias) != 0x200:
            raise RuntimeError("GIC alias extraction size mismatch")

        observed = {
            "bank": geometry["bank"],
            "lsc0": sha(lsc0),
            "lsc1": sha(lsc1),
            "lsc2": sha(lsc2),
            "gic_alias": sha(gic_alias),
        }
        if observed != EXPECTED[request]:
            raise RuntimeError(f"request{request}: packed target mismatch: {observed!r}")
        if any(lsc2):
            raise RuntimeError(f"request{request}: expected zero LSC2 but packed output is nonzero")

        requests[f"request{request}"] = {
            "staging_sha256": sha(staging),
            "staging_bytes": len(staging),
            "bank": geometry["bank"],
            "mesh": {"cols": geometry["cols"], "rows": geometry["rows"], "points": geometry["points"]},
            "lsc0": {"bytes": len(lsc0), "sha256": sha(lsc0)},
            "lsc1": {"bytes": len(lsc1), "sha256": sha(lsc1)},
            "lsc2": {"bytes": len(lsc2), "sha256": sha(lsc2), "all_zero": True},
            "wire_gic_alias": {"bytes": len(gic_alias), "sha256": sha(gic_alias)},
        }

    oracle = {
        "schema": "sp11-e003h-lsc-live-staging-pack-oracle-v1",
        "accepted": True,
        "source_authority": {
            "device_mft_sha256": DEVICE_MFT_SHA256,
            "capture_session": "E003H_ADAPTIVE_0073_LIVE_20260902",
            "same_as_prior_matched_trigger_session": False,
        },
        "exact_function": {
            "name": "IFELSC411Titan680::PackIQRegisterSetting",
            "rva": f"0x{PACKER_RVA:x}",
            "capture_input": "IFELSC411 module+0xac post-calculation staging",
            "capture_bytes": f"0x{STAGING_BYTES:x}",
        },
        "capture_abi_code_byte_proofs": code,
        "packing_contract": {
            "bank_halfword_offset": "0x08",
            "cols_minus_2_dword_offset": "0x14",
            "rows_minus_2_dword_offset": "0x18",
            "mesh": "13x17 = 221 dwords per LUT",
            "lsc0": "14-bit + 14-bit channels, 0x374 bytes",
            "lsc1": "14-bit + 14-bit channels, 0x374 bytes",
            "lsc2": "12-bit + 18-bit fields, 0x374 bytes; exact high source uses a 32-bit scaled-by-4 load",
            "gic_alias": "wire source 0x62e..0x82e = 0x200 bytes from concatenated LSC0||LSC1 offsets 0x22e..0x42e",
        },
        "requests": requests,
        "classification": "CLOSED LIVE/OFFLINE POST-CALCULATION WIRE TARGET: exact Surface Titan680 packing converts the captured same-stream request4/5/6 LSC staging into deterministic LSC0/LSC1/LSC2 and derived GIC wire targets. This closes staging-to-wire, not the upstream Tintless producer.",
        "next_gate": "Reproduce the captured 0x18a0 LSC staging (and therefore LSC0/LSC1) from same-device calibration/config plus sequential validated Tintless inputs/state in the same atomic Windows stream. GTM and post-LSC packing are already closed. Linux request6 remains forbidden.",
        "safety": {
            "linux_camera_runtime": False,
            "linux_request6_executed": False,
            "raw_windows_captures_committed": False,
        },
    }
    args.out.write_text(json.dumps(oracle, indent=2) + "\n")
    print("PASS exact live LSC staging pack")
    for req, data in requests.items():
        print(f"  {req}: bank={data['bank']} 13x17 LSC0={data['lsc0']['sha256']} LSC1={data['lsc1']['sha256']} LSC2=zero")
    print(f"  oracle: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
