#!/usr/bin/env python3
import argparse, hashlib, struct
from pathlib import Path

MASK34 = 0x3FFFFFFFF
RAW_STRIDE = 0x50
PARSED_STRIDE = 0x70
REGIONS = 1024
PARSED_BYTES = 0x70008
ACTIVE_BYTES = 8 + REGIONS * PARSED_STRIDE


def replay(raw: bytes) -> bytes:
    if len(raw) != REGIONS * RAW_STRIDE:
        raise ValueError(f"expected {REGIONS * RAW_STRIDE:#x} raw bytes, got {len(raw):#x}")
    out = bytearray(PARSED_BYTES)
    struct.pack_into('<II', out, 0, 3, REGIONS)
    for i in range(REGIONS):
        ro = i * RAW_STRIDE
        po = 8 + i * PARSED_STRIDE
        q = [struct.unpack_from('<Q', raw, ro + 8*j)[0] for j in range(10)]
        sums = [q[0] & MASK34, q[3] & MASK34, q[1] & MASK34, q[2] & MASK34, q[4] & MASK34,
                q[5] & MASK34, q[8] & MASK34, q[6] & MASK34, q[7] & MASK34, q[9] & MASK34]
        for j, value in enumerate(sums[:5]):
            struct.pack_into('<Q', out, po + 8*j, value)
        counts = [struct.unpack_from('<H', raw, ro + off)[0] for off in (0x06, 0x1e, 0x0e, 0x16, 0x26)]
        for j, value in enumerate(counts):
            struct.pack_into('<H', out, po + 0x28 + 2*j, value)
        for j, value in enumerate(sums[5:]):
            struct.pack_into('<Q', out, po + 0x38 + 8*j, value)
        counts2 = [struct.unpack_from('<H', raw, ro + off)[0] for off in (0x2e, 0x46, 0x36, 0x3e, 0x4e)]
        for j, value in enumerate(counts2):
            struct.pack_into('<H', out, po + 0x60 + 2*j, value)
    return bytes(out)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('raw', type=Path)
    ap.add_argument('--expected', type=Path)
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    raw = args.raw.read_bytes()
    got = replay(raw)
    print(f'raw_bytes={len(raw)} raw_sha256={sha(raw)}')
    print(f'parsed_bytes={len(got)} active_bytes={ACTIVE_BYTES:#x} parsed_sha256={sha(got)}')
    if args.expected:
        exp = args.expected.read_bytes()
        print(f'expected_bytes={len(exp)} expected_sha256={sha(exp)}')
        print(f'byte_exact={got == exp}')
        if got != exp:
            for i, (a, b) in enumerate(zip(got, exp)):
                if a != b:
                    print(f'first_mismatch={i:#x} got={a:#04x} expected={b:#04x}')
                    return 1
            if len(got) != len(exp):
                return 1
    if args.out:
        args.out.write_bytes(got)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
