#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import json

D = Path(__file__).resolve().parent
REPO = D.parents[2]
PRIVATE = REPO.parent / "private" / "e006a" / "E006A-PRIVATE-RECORDS-v2.json"
DECODER = D.parent / "e006a-windows-rear-rtcdm-targeted-corpus" / "decode_rear_rtcdm.py"

spec = importlib.util.spec_from_file_location("e006a_decode", DECODER)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
records = json.load(open(PRIVATE, encoding="utf-8-sig"))

regular = {
    0x3d58, 0x3d5c, 0x4758, 0x475c, 0x4958, 0x495c,
    0xa058, 0xa05c, 0xa258, 0xa25c,
}
inverse = {0x4358, 0x435c, 0x5a58, 0x5a5c, 0x5f58, 0x5f5c}

def decode(n):
    rec = next(x for x in records["records"] if x["n"] == n and x["idx"] == 1)
    parsed = mod.decode(bytes.fromhex(rec["hex"]))
    return rec, {r: v for r, v, _off, _kind in parsed["writes"]}

startup_bank_checks = 0
scalar_repack_checks = 0
for n in range(4):
    _rec, vals = decode(n)
    for reg in regular | inverse:
        if reg in vals:
            assert vals[reg] == (n & 1)
            startup_bank_checks += 1

    if 0x3b70 in vals and 0x3b74 in vals:
        q0 = (vals[0x3b70] >> 16) & 0x7fff
        q1 = vals[0x3b70] & 0x7fff
        q2 = vals[0x3b74] & 0x7fff
        q3 = (vals[0x3b74] >> 16) & 0x7fff
        assert ((q0 << 16) | q1) == vals[0x3b70]
        assert ((q3 << 16) | q2) == vals[0x3b74]
        scalar_repack_checks += 2

    for reg in (0x3d78, 0x3d7c, 0x3d80, 0x3d84):
        if reg in vals:
            assert 0 <= vals[reg] <= 0x3ffff
            scalar_repack_checks += 1

    for reg in (0x456c, 0x4570):
        if reg in vals:
            q = vals[reg] >> 17
            assert q <= 0x7fff and (q << 17) == vals[reg]
            scalar_repack_checks += 1

steady_records = 0
steady_bank_checks = 0
for n in sorted({x["n"] for x in records["records"] if x["n"] >= 4}):
    _rec, vals = decode(n)
    seen = False
    for reg in regular:
        if reg in vals:
            assert vals[reg] == ((n + 1) & 1)
            steady_bank_checks += 1
            seen = True
    for reg in inverse:
        if reg in vals:
            assert vals[reg] == (n & 1)
            steady_bank_checks += 1
            seen = True
    if seen:
        steady_records += 1

assert startup_bank_checks >= 30
assert scalar_repack_checks >= 20
assert steady_records >= 20
assert steady_bank_checks >= 100

safe = {
    "schema": "E006z-private-validation-safe-v1",
    "startup_bank_rule_exact": True,
    "steady_regular_rule_exact": True,
    "steady_inverse_rule_exact": True,
    "startup_scalar_pack_roundtrip_exact": True,
    "startup_bank_checks": startup_bank_checks,
    "steady_records_checked": steady_records,
    "steady_bank_checks": steady_bank_checks,
    "scalar_repack_checks": scalar_repack_checks,
    "raw_register_values_emitted": False,
    "raw_packet_bytes_emitted": False,
}
(D / "PRIVATE-VALIDATION-SAFE.json").write_text(
    json.dumps(safe, indent=2, sort_keys=True) + "\n"
)

print("E006Z_PRIVATE_VALIDATION_PASS")
print(f"startup_bank_checks={startup_bank_checks} steady_records={steady_records} steady_bank_checks={steady_bank_checks}")
print(f"scalar_repack_checks={scalar_repack_checks} raw_values_emitted=false")
