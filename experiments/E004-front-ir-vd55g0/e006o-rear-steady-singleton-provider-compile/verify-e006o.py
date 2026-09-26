#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,sys

D=Path(__file__).resolve().parent
R=D.parents[2]
H=R/"experiments/E004-front-ir-vd55g0/e006h-rear-steady-main-symbolic-recipe/STEADY-SYMBOLIC-RECIPE.json"
L=R/"experiments/E004-front-ir-vd55g0/e006l-rear-startup-register-ownership/STARTUP-REGISTER-OWNER-MAP.json"
INC=D/"camss-e006o-rear-steady-singletons.inc"

h=json.loads(H.read_text()); l=json.loads(L.read_text()); s=INC.read_text()
want={int(x,16) for x in l["reusable_steady_singleton_offsets"]}
vals={}
for v in h["variants"].values():
    for c in v["commands"]:
        if c["command"]!="REG_CONT": continue
        for x in c["values"]:
            if x["source"]!="STABLE_OBSERVED": continue
            r=int(x["register_offset"],16); val=int(x["value"],16)
            vals.setdefault(r,set()).add(val)

expected=[(r,next(iter(vals[r]))) for r in sorted(want)]
got=[(int(a,16),int(b,16)) for a,b in
     re.findall(r"\.reg = 0x([0-9a-f]+), \.value = 0x([0-9a-f]+)",s)]
assert len(expected)==468==len(got)
assert got==expected
assert len({r for r,_ in got})==468
assert "e006o_rear_steady_singleton_lookup" in s
assert "e006o_rear_steady_singleton_recipe" in s

h1=hashlib.sha256(INC.read_bytes()).hexdigest()
subprocess.run([sys.executable,str(D/"generate-e006o.py")],check=True,stdout=subprocess.DEVNULL)
h2=hashlib.sha256(INC.read_bytes()).hexdigest()
assert h1==h2

print("E006O_VERIFY_PASS")
print("safe_singletons=468 exact_e006h_values=true")
print("private_input=false runtime_wiring=none")
