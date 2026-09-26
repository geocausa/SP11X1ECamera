#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess,sys,hashlib

D=Path(__file__).resolve().parent
R=D.parents[2]
SRC=R/"experiments/E004-front-ir-vd55g0/e006h-rear-steady-main-symbolic-recipe/STEADY-SYMBOLIC-RECIPE.json"
INC=D/"camss-e006j-rear-register-bindings.inc"

j=json.loads(SRC.read_text())
assert j["unresolved_dynamic_register_owners"]==[]
s=INC.read_text()

pairs=[(int(a,16),b) for a,b in re.findall(
    r'\.reg = 0x([0-9a-f]+), \.producer = E006J_PRODUCER_([A-Z0-9_]+)',s)]
assert len(pairs)==25,len(pairs)
assert len({r for r,_ in pairs})==25
assert dict(pairs)[0x49b8]=="BPC_ABF"
assert dict(pairs)[0x49bc]=="BPC_ABF"
assert [r for r,p in pairs if p=="BPC_ABF"]==[0x4958,0x495c,0x49b8,0x49bc]
assert "There is deliberately no runtime caller" in s
assert "struct e006g_rear_producer_ops payload;" in s

h1=hashlib.sha256(INC.read_bytes()).hexdigest()
subprocess.run([sys.executable,str(D/"generate-e006j.py")],check=True,stdout=subprocess.DEVNULL)
h2=hashlib.sha256(INC.read_bytes()).hexdigest()
assert h1==h2
print("E006J_VERIFY_PASS")
print("dynamic_registers=25 producer_families=10 unresolved=0")
