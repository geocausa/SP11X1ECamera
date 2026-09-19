#!/usr/bin/env python3
"""Offline predicate and bounded-capture preflight, not proof of KD MASM semantics."""
from pathlib import Path
import hashlib
import re
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OLD=ROOT/"experiments/E004-front-ir-vd55g0/e004ga-windows-flash-module-enable-trace"
import generate_kd as g

assert len(g.TARGET_REGISTERS)==11 and len(g.SKIP_REGISTERS)==8
assert len(set(g.TARGET_REGISTERS))==11
assert not set(g.TARGET_REGISTERS)&set(g.SKIP_REGISTERS)
assert {0xee46,0xee4e}.issubset(g.TARGET_REGISTERS)
for expr_input in ("@w24","(@w27 & 0xffff)","0xee46"):
    expr=g.expr(expr_input)
    assert ">=" not in expr and "<=" not in expr
    for reg in g.TARGET_REGISTERS:
        assert f"({expr_input} == 0x{reg:04x})" in expr
    # All equality atoms are individually parenthesized to avoid MASM precedence.
    atoms=re.findall(r"\((?:@w24|\(@w27 & 0xffff\)|0xee46) == 0x([0-9a-f]{4})\)",expr)
    assert [int(a,16) for a in atoms]==list(g.TARGET_REGISTERS)
def evaluate_equivalence(value):
    atoms=[int(x,16) for x in re.findall(r"0xee46 == 0x([0-9a-f]{4})",g.expr("0xee46"))]
    assert len(atoms)==11
    return value in g.TARGET_REGISTERS
assert all(evaluate_equivalence(value) for value in g.TARGET_REGISTERS)
assert not any(evaluate_equivalence(value) for value in g.SKIP_REGISTERS)

assert (HERE/"capture.ps1").read_text()==(OLD/"capture.ps1").read_text().replace("E004GA","E004GB")
capture=(HERE/"capture.ps1").read_text()
for marker in ("frames -lt 12","AddSeconds(5)","TryAcquireLatestFrame"):
    assert marker in capture
for blocked in ("TrySet","SetValue","FlashControl","ExposureControl.Set","SoftwareBitmap.CopyToBuffer"):
    assert blocked not in capture

ps=(HERE/"generate-kd.ps1").read_text()
assert "Get-ExactPredicate" in ps
assert ">= 0xee" not in ps and "<= 0xee" not in ps
assert "ee46" in ps and "ee4e" in ps
assert "E004GB_ARMED_STAY_BROKEN" in ps
assert 'db 0x' not in ps  # KD dry run must not read a dummy address
assert 'E004GB_DRY_TARGET reg=%x\\n' in ps
parser=(HERE/"validate-dry.ps1").read_text()
assert "TARGETS=11 SKIPS=8" in parser and "E004GB_ARM_BEGIN" in parser
assert '$s.Replace("`r`n","`n").Replace("`r","`n")' in parser
for x in ("ee46","ee4e"):
    assert x in parser

with tempfile.TemporaryDirectory(prefix="sp11-e004gb-static-") as directory:
    r=subprocess.run(["python3",str(HERE/"generate_kd.py"),
                      "--pmic-base","fffff80012345000","--output",directory],
                     text=True,capture_output=True,timeout=15)
    assert r.returncode==0,r.stderr
    arm=(Path(directory)/"arm.kd").read_text()
    dry=(Path(directory)/"validate.kd").read_text()
    assert "fffff80012368af8" in arm and "fffff80012368bec" in arm
    assert "E004GB_ARMED_STAY_BROKEN" in arm and not re.search(r"(?m)^g\s*$",arm)
    assert "(@w24 == 0xee46)" in arm and "(@w24 == 0xee4e)" in arm
    assert "((@w27 & 0xffff) == 0xee46)" in arm
    assert "((@w27 & 0xffff) == 0xee4e)" in arm
    assert "E004GB_DRY_BEGIN" in dry and "E004GB_DRY_END_STAY_BROKEN" in dry
    lines=[line for line in dry.splitlines() if line.startswith(".if (") and "E004GB_DRY_TARGET" in line]
    assert len(lines)==19
    assert "db 0x" not in dry
    for line in lines:
        assert ">= 0xee" not in line and "<= 0xee" not in line
    for reg in g.TARGET_REGISTERS:
        assert f'0x{reg:04x} ' in dry
    for reg in g.SKIP_REGISTERS:
        assert f'0x{reg:04x} }}' in dry

assert not (HERE/"evidence/CONSUMED.json").exists()
print("E004GB_OFFLINE_STATIC=PASS ELEVEN_EXACT_TARGETS EIGHT_NEGATIVE_CASES")
print("ACTUAL_MASM_INTERPRETER=STILL_REQUIRES_LIVE_KD_DRY_GATE NO_BOOT_OR_CAMERA_STARTED")
print("GENERATOR_SHA256="+hashlib.sha256((HERE/"generate_kd.py").read_bytes()).hexdigest())
