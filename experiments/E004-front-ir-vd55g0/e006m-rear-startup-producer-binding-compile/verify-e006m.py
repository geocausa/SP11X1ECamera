#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, subprocess, sys

D=Path(__file__).resolve().parent
L=D.parent/"e006l-rear-startup-register-ownership"/"STARTUP-REGISTER-OWNER-MAP.json"
INC=D/"camss-e006m-rear-startup-bindings.inc"
j=json.loads(L.read_text())
s=INC.read_text()

rows=re.findall(r"\.reg = 0x([0-9a-f]+), \.source = (E006M_SOURCE_[A-Z_]+), \.owner = (E006M_OWNER_[A-Z0-9_]+)",s)
assert len(rows)==714,len(rows)
regs=[int(x[0],16) for x in rows]
assert regs==sorted(regs)
assert len(set(regs))==714

counts={}
for _,src,_ in rows: counts[src]=counts.get(src,0)+1
assert counts=={
 "E006M_SOURCE_STEADY_SINGLETON":468,
 "E006M_SOURCE_STEADY_DYNAMIC":25,
 "E006M_SOURCE_SHARED_STARTUP":35,
 "E006M_SOURCE_EXTRA_STARTUP":186,
},counts

assert any(r=="008c" and o=="E006M_OWNER_VFE680_PERIOD_CFG" for r,_,o in rows)
assert "e006j_rear_validate_scalar_contract(&b->steady)" in s
assert "e006j_rear_fill_scalar(&b->steady, ctx, reg, value)" in s
assert "There is deliberately no runtime caller" in s

h1=hashlib.sha256(INC.read_bytes()).hexdigest()
subprocess.run([sys.executable,str(D/"generate-e006m.py")],check=True,stdout=subprocess.DEVNULL)
h2=hashlib.sha256(INC.read_bytes()).hexdigest()
assert h1==h2,(h1,h2)

print("E006M_VERIFY_PASS")
print("registers=714 singleton=468 steady_dynamic=25 shared_startup=35 extra_startup=186")
print("period_cfg=explicit VFE680 callback runtime_wiring=none")
