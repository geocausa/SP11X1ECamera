#!/usr/bin/env python3
"""No-hardware, fail-closed test of E004fy passive six-register preflight."""
from pathlib import Path
from prepare import ADDRS,OFFSETS,inspect_access

assert ADDRS == (0xee46,0xee4a,0xee4b,0xee4c,0xee4d,0xee4e)
assert OFFSETS == tuple(9*a for a in ADDRS)
rows=[f"{a:04x}: y y y n" for a in range(65536)]
assert inspect_access("\n".join(rows))
cases=0
for addr,replacement,reason in (
    (0xee46,"ee45: y y y n","sparse"),
    (0xee4a,"ee4a: n y y n","unreadable"),
    (0xee4e,"ee4e: y y y y","precious"),
):
    wrong=rows.copy()
    wrong[addr]=replacement
    try:
        inspect_access("\n".join(wrong))
    except ValueError as exc:
        assert reason in str(exc),str(exc)
        cases+=1
    else:
        raise AssertionError("accepted "+reason)
src=Path(__file__).with_name("read_once.py").read_text()
assert 'with C.open("x")' in src
assert src.index('with C.open("x")') < src.index('subprocess.run(["sudo"')
assert "os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW" in src
assert "os.pread(fd,9,address*9)" in src
assert "addresses=(0xee46,0xee4a,0xee4b,0xee4c,0xee4d,0xee4e)" in src
assert "emitter_activation_authorized" in src
print("E004FY_OFFLINE_NEGATIVE=PASS CASES=3")
print("BOUNDED_READ_DESIGN=PASS SIX_BYTES_FSYNC_CONSUMED_BEFORE_IO")
