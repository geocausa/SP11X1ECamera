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

REGS = (0x49b8, 0x49bc, 0x49d0, 0x49d4, 0x49d8, 0x49dc, 0x49e0)

def sx10(v):
    v &= 0x3ff
    return v - 0x400 if v & 0x200 else v

def bytes4(v):
    return [(v >> (8 * i)) & 0xff for i in range(4)]

def repack(vals):
    a, b = vals[0x49b8], vals[0x49bc]
    signed10 = [sx10(a), sx10(b)]
    unsigned9 = [(a >> 16) & 0x1ff, (b >> 16) & 0x1ff]
    nibble4 = [(a >> 28) & 0xf, (b >> 28) & 0xf]
    g0 = [bytes4(vals[0x49d0]), bytes4(vals[0x49d4])]
    g1 = [bytes4(vals[0x49d8]), bytes4(vals[0x49dc])]
    e = vals[0x49e0]
    ng = [
        [(e >> (4 * i)) & 0xf for i in range(4)],
        [(e >> (4 * (i + 4))) & 0xf for i in range(4)],
    ]
    out = {}
    for i, reg in enumerate((0x49b8, 0x49bc)):
        out[reg] = ((signed10[i] & 0x3ff) |
                    (unsigned9[i] << 16) |
                    (nibble4[i] << 28))
    for reg, group in ((0x49d0, g0[0]), (0x49d4, g0[1]),
                       (0x49d8, g1[0]), (0x49dc, g1[1])):
        out[reg] = sum(v << (8 * i) for i, v in enumerate(group))
    out[0x49e0] = sum(ng[0][i] << (4 * i) for i in range(4)) |                   sum(ng[1][i] << (4 * (i + 4)) for i in range(4))
    return out

records_checked = 0
register_checks = 0
startup_records = 0
steady_records = 0
for rec in records["records"]:
    if rec.get("idx") != 1 or not rec.get("complete"):
        continue
    parsed = mod.decode(bytes.fromhex(rec["hex"]))
    vals = {r: v for r, v, _off, _kind in parsed["writes"] if r in REGS}
    if not all(r in vals for r in REGS):
        continue
    out = repack(vals)
    assert all(out[r] == vals[r] for r in REGS)
    records_checked += 1
    register_checks += len(REGS)
    if rec["n"] < 4:
        startup_records += 1
    else:
        steady_records += 1

assert records_checked >= 20
assert register_checks == records_checked * len(REGS)
safe = {
    "schema": "E007a-private-validation-safe-v1",
    "records_checked": records_checked,
    "startup_records_checked": startup_records,
    "steady_records_checked": steady_records,
    "register_roundtrip_checks": register_checks,
    "all_seven_words_exact": True,
    "raw_register_values_emitted": False,
    "raw_packet_bytes_emitted": False,
}
(D / "PRIVATE-VALIDATION-SAFE.json").write_text(
    json.dumps(safe, indent=2, sort_keys=True) + "\n"
)
print("E007A_PRIVATE_VALIDATION_PASS")
print(f"records={records_checked} startup={startup_records} steady={steady_records} register_checks={register_checks}")
print("raw_values_emitted=false")
