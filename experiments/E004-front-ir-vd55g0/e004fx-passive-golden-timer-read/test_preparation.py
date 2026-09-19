#!/usr/bin/env python3
"""Offline tests of four-register offset calculation and one-shot source guard."""
from pathlib import Path
import copy
from prepare import ADDRS, LINE_BYTES, access_offset

rows = [f"{address:04x}: y y y n" for address in range(65536)]
clean = "\n".join(rows) + "\n"
assert ADDRS == (0xee3e, 0xee3f, 0xee40, 0xee41)
assert LINE_BYTES == 9
assert access_offset(clean) == 548910

def reject(text, reason):
    try:
        access_offset(text)
    except ValueError as exc:
        assert reason in str(exc), str(exc)
    else:
        raise AssertionError("preflight accepted " + reason)

reject("\n".join(rows[:-1])+"\n", "count")
for label, line in (
    ("wrong address", "ee3d: y y y n"),
    ("unreadable", "ee3e: n y y n"),
    ("precious", "ee3e: y y y y"),
):
    wrong = rows.copy()
    wrong[0xee3e] = line
    reject("\n".join(wrong)+"\n", "metadata" if label == "wrong address" else "unreadable or precious")
source = Path(__file__).with_name("read_once.py").read_text()
assert "os.pread(fd,length,offset)" in source
assert "ONE_PASSIVE_READ_CONSUMED_BEFORE_IO" in source
assert source.index('with CONSUMED.open("x")') < source.index('subprocess.run(["sudo"')
assert '"w"' not in source.split("ROOT_READ =",1)[1].split('"""',1)[0]
assert "os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW" in source
assert "length=36" in source and "offset=548910" in source
print("E004FX_PREPARE_NEGATIVE=PASS CASES=4")
print("READ_ONCE_STATIC=PASS ONLY_FOUR_READONLY_REGISTERS CONSUMED_BEFORE_IO")
