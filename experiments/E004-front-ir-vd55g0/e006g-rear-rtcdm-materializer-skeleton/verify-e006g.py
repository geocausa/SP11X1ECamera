#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

D=Path(__file__).resolve().parent
R=D.parents[2]
INC=D/"camss-e006g-rear-materializer.inc"
SRC=R/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/STRUCTURAL-DECODE.json"

s=INC.read_text()
j=json.loads(SRC.read_text())

expected={}
for x in j["steady"]["main_variants"]:
    expected.setdefault(x["main_bytes"], [
        (int(d["dmi_register_offset"],16), int(d["selector"]), int(d["payload_bytes"]))
        for d in x["dmi_shape"]
    ])

names={"ac8":0xac8,"a98":0xa98,"8f0":0x8f0,"658":0x658}
for name,main in names.items():
    m=re.search(
        rf"static const struct e006g_rear_dmi_slot e006g_rear_{name}_slots\[\] = \{{(.*?)\n\}};",
        s,re.S)
    assert m,name
    got=[(int(a,16),int(b),int(c)) for a,b,c in
         re.findall(r"E006G_SLOT\(0x([0-9a-f]+),\s*(\d+),\s*(\d+),",m.group(1))]
    assert got==expected[main],(name,got,expected[main])

assert "E006G_GIC_LSC0_OFFSET   558" in s
assert "E006G_GIC_LSC0_BYTES    326" in s
assert "E006G_GIC_LSC1_BYTES    186" in s
assert "out->len[2] = 0xc;" in s
assert "out->len[5] = 0x14;" in s
assert "There is deliberately no runtime caller" in s

h1=hashlib.sha256(INC.read_bytes()).hexdigest()
subprocess.run([sys.executable,str(D/"generate-e006g.py")],check=True,stdout=subprocess.DEVNULL)
h2=hashlib.sha256(INC.read_bytes()).hexdigest()
assert h1==h2,(h1,h2)

print("E006G_VERIFY_PASS")
print("variants=4 dmi_counts=16,15,13,3")
print("dynamic_producers=LSC/Tintless,GTM/TMC,BFStats25; GIC=LSC alias")
print("runtime_wiring=none")
